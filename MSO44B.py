import pyvisa
import numpy as np
import matplotlib.pyplot as plt
import csv
import os
from datetime import datetime
from pyMSO4 import MSO4
from pyMSO4.triggers import MSO4EdgeTrigger


class MSO44B:
    """
    Simple wrapper for MSO44B oscilloscope control.
    Provides easy-to-use methods for scientists to capture and analyze waveforms.
    """
    
    def __init__(self, timeout=5000):
        """
        Initialize the MSO44B wrapper.
        
        Args:
            timeout (float): VISA timeout in milliseconds (default: 5000)
        """
        self.scope = MSO4(timeout=timeout)
        self.connected = False
        self.ip_address = None
        
    def _discover_mso44_instruments(self):
        """
        Discover MSO44/MSO46 instruments using pyvisa by checking device IDs.
        
        Returns:
            list: List of dictionaries containing 'resource' and 'device_id' keys for MSO44/46 instruments
        """
        rm = pyvisa.ResourceManager()
        mso_instruments = []
        
        try:
            resources = rm.list_resources()
            print(f"Scanning {len(resources)} available instruments for MSO44/MSO46...")
            
            for resource in resources:
                try:
                    temp_instrument = rm.open_resource(resource)
                    temp_instrument.timeout = 2000  # Short timeout for discovery
                    
                    # Query device identification
                    device_id = temp_instrument.query('*IDN?').strip()
                    print(f"  {resource}: {device_id}")
                    
                    # Check if this is an MSO44 or MSO46 instrument
                    if any(model in device_id.upper() for model in ['MSO44', 'MSO46']):
                        mso_instruments.append({
                            'resource': resource,
                            'device_id': device_id
                        })
                        print(f"    ✓ MSO44/46 instrument found!")
                    
                    temp_instrument.close()
                    
                except Exception as e:
                    print(f"    ✗ Could not query {resource}: {e}")
                    try:
                        temp_instrument.close()
                    except:
                        pass
                    continue
            
            if mso_instruments:
                print(f"\nFound {len(mso_instruments)} MSO44/46 instrument(s):")
                for i, instr in enumerate(mso_instruments):
                    print(f"  {i+1}. {instr['resource']} - {instr['device_id']}")
            else:
                print("\nNo MSO44/46 instruments found.")
                
        except Exception as e:
            print(f"Error during instrument discovery: {e}")
        finally:
            rm.close()
        
        return mso_instruments

    def connect(self, ip_address=None, auto_discover=True):
        """
        Connect to MSO44B scope with automatic discovery or specific IP.
        
        Args:
            ip_address (str, optional): Specific IP address to connect to.
            auto_discover (bool): If True and no ip_address given, attempts auto-discovery via pyvisa.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            if ip_address:
                # Connect to specific IP using pyMSO4
                self.scope.con(ip=ip_address)
                self.ip_address = ip_address
                self.connected = True
                print(f"Connected to MSO44B at {ip_address}")
                return True
            elif auto_discover:
                # Use pyvisa to discover MSO44/46 instruments
                mso_instruments = self._discover_mso44_instruments()
                
                if mso_instruments:
                    # Try to connect to each discovered MSO instrument
                    for instr in mso_instruments:
                        try:
                            resource = instr['resource']
                            
                            # Extract connection info from resource string
                            if 'TCPIP' in resource:
                                # Extract IP from TCPIP resource string
                                # Format: TCPIP0::192.168.1.100::inst0::INSTR or TCPIP::192.168.1.100::INSTR
                                parts = resource.split('::')
                                if len(parts) >= 3:
                                    ip = parts[1]
                                    self.scope.con(ip=ip)
                                    self.ip_address = ip
                                    self.connected = True
                                    print(f"Connected to MSO44B at {ip} (discovered via pyvisa)")
                                    return True
                            elif 'USB' in resource:
                                # Extract VID/PID from USB resource string
                                # Format: USB0::0x0699::0x0527::C012345::INSTR
                                parts = resource.split('::')
                                if len(parts) >= 3:
                                    vid = int(parts[1], 16)
                                    pid = int(parts[2], 16)
                                    self.scope.con(usb_vid_pid=(vid, pid))
                                    self.connected = True
                                    self.ip_address = "USB"
                                    print(f"Connected to MSO44B via USB (discovered via pyvisa)")
                                    return True
                        except Exception as e:
                            print(f"  Failed to connect to {resource}: {e}")
                            continue
                
                print("No MSO44/46 instruments discovered or failed to connect to discovered instruments.")
                return False
            else:
                print("No connection method specified. Provide ip_address or enable auto_discover.")
                return False
                
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def setup_trigger(self, source_channel=1, trigger_type='edge', level=0.0, slope='rising'):
        """
        Setup trigger configuration.
        
        Args:
            source_channel (int): Channel number for trigger source (1-4)
            trigger_type (str): Type of trigger ('edge' for now)
            level (float): Trigger level in volts
            slope (str): Trigger slope ('rising' or 'falling')
        
        Returns:
            bool: True if setup successful
        """
        if not self.connected:
            print("Error: Not connected to scope. Call connect() first.")
            return False
            
        try:
            # Set up edge trigger
            self.scope.trigger = MSO4EdgeTrigger
            
            # Convert channel number to string format expected by pyMSO4
            if isinstance(source_channel, int):
                source_str = f'ch{source_channel}'
            else:
                source_str = str(source_channel).lower()
            
            self.scope.trigger.source = source_str
            self.scope.trigger.level = level
            
            # Map slope names to pyMSO4 expected values
            slope_lower = slope.lower()
            if slope_lower in ['rising', 'rise']:
                self.scope.trigger.edge_slope = 'rise'
            elif slope_lower in ['falling', 'fall']:
                self.scope.trigger.edge_slope = 'fall'
            else:
                raise ValueError("Slope must be 'rising' or 'falling'")
                
            print(f"Trigger set: CH{source_channel}, {slope}, {level}V")
            return True
            
        except Exception as e:
            print(f"Trigger setup failed: {e}")
            return False
    
    def get_waveform_scaling_params(self, channel):
        """
        Get voltage scaling parameters for a specific channel.
        
        Args:
            channel (int): Channel number (1-4)
            
        Returns:
            dict: Dictionary with scaling parameters
        """
        if not self.connected:
            raise RuntimeError("Not connected to scope")
            
        # Set data source to the specific channel
        self.scope.acq.wfm_src = [f'ch{channel}']
        
        # Get scaling parameters from WFMOutpre
        scaling_params = {
            'y_mult': float(self.scope.sc.query('WFMOutpre:YMUlt?').strip()),
            'y_zero': float(self.scope.sc.query('WFMOutpre:YZEro?').strip()),
            'y_off': float(self.scope.sc.query('WFMOutpre:YOFf?').strip()),
            'channel_scale': self.scope.ch_a[channel].scale,
            'channel_position': self.scope.ch_a[channel].position
        }
        
        return scaling_params
    
    def get_time_scaling_params(self):
        """
        Get time scaling parameters for waveform data.
        
        Returns:
            dict: Dictionary with time scaling parameters
        """
        if not self.connected:
            raise RuntimeError("Not connected to scope")
            
        time_params = {
            'x_incr': float(self.scope.sc.query('WFMOutpre:XINcr?').strip()),
            'x_zero': float(self.scope.sc.query('WFMOutpre:XZEro?').strip()),
            'pt_off': float(self.scope.sc.query('WFMOutpre:PT_Off?').strip()),
            'sample_rate': self.scope.acq.horiz_sample_rate,
            'horiz_scale': self.scope.acq.horiz_scale
        }
        
        return time_params
    
    def convert_raw_to_voltage(self, raw_data, scaling_params):
        """
        Convert raw ADC values to actual voltages.
        
        Args:
            raw_data (list): Raw ADC values
            scaling_params (dict): Scaling parameters from get_waveform_scaling_params()
            
        Returns:
            list: Voltage values in volts
        """
        y_mult = scaling_params['y_mult']
        y_zero = scaling_params['y_zero']
        y_off = scaling_params['y_off']
        
        # Formula: voltage = (raw - y_off) * y_mult + y_zero
        return [(raw - y_off) * y_mult + y_zero for raw in raw_data]
    
    def generate_time_axis(self, data_length, time_params):
        """
        Generate proper time axis for waveform data.
        
        Args:
            data_length (int): Number of data points
            time_params (dict): Time parameters from get_time_scaling_params()
            
        Returns:
            numpy.array: Time values in seconds
        """
        x_incr = time_params['x_incr']
        x_zero = time_params['x_zero']
        pt_off = time_params['pt_off']
        
        # Formula: time = (index - pt_off) * x_incr + x_zero
        return np.array([(i - pt_off) * x_incr + x_zero for i in range(data_length)])
    
    def read_channel_waveform(self, channel, use_binary=False):
        """
        Read and convert waveform data from a single channel.
        
        Args:
            channel (int): Channel number (1-4)
            use_binary (bool): If True, use binary format for higher precision
            
        Returns:
            dict: Dictionary with 'raw_data', 'voltage_data', and 'scaling_params'
        """
        if not self.connected:
            raise RuntimeError("Not connected to scope")
            
        if channel < 1 or channel > self.scope.ch_a_num:
            raise ValueError(f"Invalid channel {channel}. Must be 1-{self.scope.ch_a_num}")
        
        # Set data source to this channel
        self.scope.acq.wfm_src = [f'ch{channel}']
        
        if use_binary:
            # Configure for binary format with proper settings
            self.scope.acq.wfm_encoding = 'binary'
            self.scope.acq.wfm_binary_format = 'ri'  # Signed integer
            self.scope.acq.wfm_byte_nr = 2  # 2 bytes per sample
            self.scope.acq.wfm_byte_order = 'lsb'
            
            # Get raw waveform data using binary query
            raw_data = self.scope.sc.query_binary_values(
                'CURVE?', 
                datatype=self.scope.acq.get_datatype(), 
                is_big_endian=self.scope.acq.is_big_endian
            )
        else:
            # Use ASCII format (more reliable but potentially less precise)
            self.scope.acq.wfm_encoding = 'ascii'
            wfm_str = self.scope.sc.query('CURVE?').strip()
            raw_data = [float(x) for x in wfm_str.split(',')]
        
        # Get scaling parameters and convert to voltages
        scaling_params = self.get_waveform_scaling_params(channel)
        voltage_data = self.convert_raw_to_voltage(raw_data, scaling_params)
        
        return {
            'raw_data': raw_data,
            'voltage_data': voltage_data,
            'scaling_params': scaling_params,
            'format_used': 'binary' if use_binary else 'ascii'
        }
    
    def capture_waveforms(self, channels=[1], filename=None, plot=True, save_csv=True):
        """
        Capture waveforms from specified channels with trigger.
        
        Args:
            channels (list): List of channel numbers to capture (e.g., [1, 2, 3, 4])
            filename (str, optional): Base filename for saved files. 
                                    If None, uses timestamp.
            plot (bool): Whether to create and save plots
            save_csv (bool): Whether to save data as CSV
        
        Returns:
            dict: Dictionary containing waveform data and metadata
        """
        if not self.connected:
            print("Error: Not connected to scope. Call connect() first.")
            return None
            
        try:
            # Enable requested channels
            for i in range(1, self.scope.ch_a_num + 1):
                if i < len(self.scope.ch_a):
                    self.scope.ch_a[i].enable = i in channels
            
            # Configure acquisition for the channels
            channel_names = [f'ch{ch}' for ch in channels if 1 <= ch <= self.scope.ch_a_num]
            self.scope.acq.wfm_src = channel_names
            
            # Set up acquisition parameters
            self.scope.acq.mode = 'sample'
            self.scope.acq.stop_after = 'sequence'
            self.scope.acq.num_seq = 1
            
            # Configure waveform data format - use ASCII for reliability
            self.scope.acq.wfm_encoding = 'ascii'
            
            # Start single acquisition and wait for trigger
            print("Waiting for trigger...")
            self.scope.sc.write('ACQuire:STATE RUN')
            
            # Wait for acquisition to complete
            while self.scope.busy():
                pass
            
            # Capture waveform data using reusable methods
            waveform_data = {}
            time_data = None
            
            for ch in channels:
                if ch < 1 or ch > self.scope.ch_a_num:
                    print(f"Warning: Invalid channel {ch}. Skipping.")
                    continue
                
                # Use the reusable waveform reading method
                waveform_result = self.read_channel_waveform(ch)
                voltage_data = waveform_result['voltage_data']
                
                # Generate time data once (same for all channels)
                if time_data is None:
                    time_params = self.get_time_scaling_params()
                    time_data = self.generate_time_axis(len(voltage_data), time_params)
                
                waveform_data[f'CH{ch}'] = voltage_data
                print(f"Captured {len(voltage_data)} points from CH{ch}")
            
            waveform_data['Time'] = time_data
            
            # Generate filename if not provided
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"mso44b_capture_{timestamp}"
            
            results = {
                'waveforms': waveform_data,
                'filename': filename,
                'channels': channels,
                'sample_points': len(time_data) if time_data is not None else 0
            }
            
            # Save CSV if requested
            if save_csv:
                csv_filename = self.save_csv(waveform_data, f"{filename}.csv")
                results['csv_file'] = csv_filename
            
            # Create plot if requested
            if plot:
                plot_filename = self.plot_waveforms(waveform_data, channels, f"{filename}.png")
                results['plot_file'] = plot_filename
            
            print(f"Capture complete! Saved as {filename}")
            return results
            
        except Exception as e:
            print(f"Capture failed: {e}")
            return None
    
    def save_csv(self, waveform_data, filename):
        """
        Save waveform data to CSV file.
        
        Args:
            waveform_data (dict): Dictionary containing waveform data
            filename (str): Output CSV filename
        
        Returns:
            str: Filename of saved CSV file
        """
        try:
            with open(filename, 'w', newline='') as csvfile:
                fieldnames = list(waveform_data.keys())
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                
                # Write data row by row
                max_length = max(len(data) for data in waveform_data.values())
                for i in range(max_length):
                    row = {}
                    for key, data in waveform_data.items():
                        if i < len(data):
                            row[key] = data[i]
                        else:
                            row[key] = ''
                    writer.writerow(row)
            
            print(f"Data saved to {filename}")
            return filename
            
        except Exception as e:
            print(f"CSV save failed: {e}")
            return None
    
    def plot_waveforms(self, waveform_data, channels, filename):
        """
        Create and save plots of waveform data.
        
        Args:
            waveform_data (dict): Dictionary containing waveform data
            channels (list): List of channel numbers
            filename (str): Output plot filename
        
        Returns:
            str: Filename of saved plot
        """
        try:
            plt.figure(figsize=(12, 8))
            
            time_data = waveform_data.get('Time')
            if time_data is None:
                print("Warning: No time data available for plotting")
                return None
            
            colors = ['blue', 'red', 'green', 'orange']
            
            for i, ch in enumerate(channels):
                ch_key = f'CH{ch}'
                if ch_key in waveform_data:
                    color = colors[i % len(colors)]
                    plt.plot(time_data * 1e6, waveform_data[ch_key], 
                            label=f'Channel {ch}', color=color, linewidth=1)
            
            plt.xlabel('Time (μs)')
            plt.ylabel('Voltage (V)')
            plt.title('MSO44B Waveform Capture')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"Plot saved to {filename}")
            return filename
            
        except Exception as e:
            print(f"Plot save failed: {e}")
            return None
    
    def disconnect(self):
        """Disconnect from the scope."""
        if self.connected:
            try:
                self.scope.dis()
                self.connected = False
                print("Disconnected from MSO44B")
            except Exception as e:
                print(f"Disconnect warning: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - automatically disconnect."""
        self.disconnect()
    
    @staticmethod
    def list_all_instruments():
        """
        List all available VISA instruments with their device IDs, highlighting MSO44/46.
        
        Returns:
            list: List of dictionaries containing 'resource', 'device_id', and 'is_mso44' keys
        """
        rm = pyvisa.ResourceManager()
        instruments = []
        
        try:
            resources = rm.list_resources()
            print(f"Scanning {len(resources)} available instruments:")
            print("-" * 70)
            
            for resource in resources:
                try:
                    temp_instrument = rm.open_resource(resource)
                    temp_instrument.timeout = 2000
                    
                    device_id = temp_instrument.query('*IDN?').strip()
                    is_mso44 = any(model in device_id.upper() for model in ['MSO44', 'MSO46'])
                    
                    instruments.append({
                        'resource': resource,
                        'device_id': device_id,
                        'is_mso44': is_mso44
                    })
                    
                    status = "MSO44/46 ✓" if is_mso44 else "Other"
                    print(f"{resource:<30} | {status:<10} | {device_id}")
                    
                    temp_instrument.close()
                    
                except Exception as e:
                    print(f"{resource:<30} | Error      | Could not query: {e}")
                    try:
                        temp_instrument.close()
                    except:
                        pass
            
            print("-" * 70)
            mso_count = sum(1 for instr in instruments if instr.get('is_mso44', False))
            print(f"Total instruments: {len(instruments)}, MSO44/46 instruments: {mso_count}")
            
        except Exception as e:
            print(f"Error during instrument scan: {e}")
        finally:
            rm.close()
        
        return instruments


# Legacy compatibility - keep the original minimal class
class MSO44BLegacy:
    """Legacy MSO44B class for backward compatibility."""
    
    def __init__(self, resource_name=None, ip_address=None, serial_port=None):
        if not any([resource_name, ip_address, serial_port]):
            raise ValueError("Must provide either resource_name, ip_address, or serial_port")
        
        self.rm = pyvisa.ResourceManager()
        
        if resource_name:
            self.resource_name = resource_name
        elif ip_address:
            self.resource_name = f'TCPIP::{ip_address}::INSTR'
        elif serial_port:
            self.resource_name = f'ASRL{serial_port}::INSTR'
        
        self.scope = self.rm.open_resource(self.resource_name)
        
        if serial_port:
            self.scope.baud_rate = 115200
            self.scope.data_bits = 8
    
    def write(self, command):
        return self.scope.write(command)
    
    def query(self, command):
        return self.scope.query(command)
    
    def device_id(self):
        return self.query('*IDN?')
    
    def close(self):
        self.scope.close()
        self.rm.close()

