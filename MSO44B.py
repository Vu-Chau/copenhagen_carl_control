import pyvisa
import numpy as np
import matplotlib.pyplot as plt
import csv
import os
from datetime import datetime
from pyMSO4 import MSO4
from pyMSO4.triggers import MSO4EdgeTrigger


class SimpleMSO44B:
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
        
    def connect(self, ip_address=None):
        """
        Automatically find and connect to MSO44B scope.
        
        Args:
            ip_address (str, optional): Specific IP address to connect to.
                                      If None, attempts to auto-discover.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            if ip_address:
                # Connect to specific IP
                self.scope.con(ip=ip_address)
                self.ip_address = ip_address
                self.connected = True
                print(f"Connected to MSO44B at {ip_address}")
                return True
            else:
                # Try common IP addresses for MSO44B
                common_ips = [
                    "192.168.1.100",
                    "192.168.0.100", 
                    "10.0.0.100",
                    "172.16.0.100"
                ]
                
                for ip in common_ips:
                    try:
                        self.scope.con(ip=ip)
                        self.ip_address = ip
                        self.connected = True
                        print(f"Auto-discovered and connected to MSO44B at {ip}")
                        return True
                    except:
                        continue
                
                # Try USB connection as fallback
                try:
                    self.scope.con(usb_vid_pid=(0x0699, 0x0527))  # Tektronix MSO44
                    self.connected = True
                    self.ip_address = "USB"
                    print("Connected to MSO44B via USB")
                    return True
                except:
                    pass
                    
                print("Failed to auto-discover MSO44B. Please specify IP address.")
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
            self.scope.trigger.source = source_channel
            self.scope.trigger.level = level
            
            if slope.lower() == 'rising':
                self.scope.trigger.slope = 'RISing'
            elif slope.lower() == 'falling':
                self.scope.trigger.slope = 'FALling'
            else:
                raise ValueError("Slope must be 'rising' or 'falling'")
                
            print(f"Trigger set: CH{source_channel}, {slope}, {level}V")
            return True
            
        except Exception as e:
            print(f"Trigger setup failed: {e}")
            return False
    
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
            for i in range(1, 5):  # MSO44 has 4 channels
                self.scope.ch_a[i].enable = i in channels
            
            # Start single acquisition and wait for trigger
            print("Waiting for trigger...")
            self.scope.acq.single()
            
            # Wait for acquisition to complete
            while self.scope.busy():
                pass
            
            # Capture waveform data
            waveform_data = {}
            time_data = None
            
            for ch in channels:
                if ch < 1 or ch > 4:
                    print(f"Warning: Invalid channel {ch}. Skipping.")
                    continue
                    
                # Get waveform data
                data = self.scope.ch_a[ch].waveform()
                if time_data is None:
                    time_data = self.scope.ch_a[ch].time()
                
                waveform_data[f'CH{ch}'] = data
                print(f"Captured {len(data)} points from CH{ch}")
            
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


# Legacy compatibility - keep the original minimal class
class MSO44B:
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

