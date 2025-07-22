import pyvisa

class MSO44B:
    """This class provides an interface to the MSO44B oscilloscope using the PyVISA library."""
    def __init__(self, resource_name=None, ip_address=None, serial_port=None,timeout=5000):
        """Initialize the MSO44B oscilloscope with the given resource name, IP address, or serial port."""
        self.rm = pyvisa.ResourceManager()
        
        if ip_address:
            # Ethernet connection via TCP/IP
            self.resource_name = f'TCPIP::{ip_address}::INSTR'
        elif serial_port:
            # Serial connection (e.g., 'COM1', 'COM2', etc.)
            self.resource_name = f'ASRL{serial_port}::INSTR'
        elif resource_name:
            # Direct resource name provided
            self.resource_name = resource_name
        else:
            raise ValueError("Must provide either resource_name, ip_address, or serial_port")
        
        self.scope = self.rm.open_resource(self.resource_name)
        
        # Configure serial settings if using serial connection
        if serial_port:
            self.scope.baud_rate = 115200  # Adjust as needed
            self.scope.data_bits = 8
            self.scope.parity = pyvisa.constants.Parity.none
            self.scope.stop_bits = pyvisa.constants.StopBits.one
            self.scope.flow_control = pyvisa.constants.VI_ASRL_FLOW_NONE

    def write(self, command):
        """Send a command to the oscilloscope."""
        self.scope.write(command)
    def query(self, command):
        """Send a command to the oscilloscope and return the response."""
        return self.scope.query(command)
    
    def device_id(self):
        """Return the device ID of the oscilloscope."""
        return self.query('*IDN?')
    def check_device_id(self):
        """Check if the device ID matches the expected MSO44B ID."""
        idn = self.device_id()
        return 'MSO44B' in idn
    def reset(self):
        """Reset the oscilloscope to its default settings."""
        self.write('*RST')
    def clear_status(self):
        """Clear the status of the oscilloscope."""
        self.write('*CLS')
    
    def set_channel_scale(self, channel, scale):
        """Set the vertical scale for a specified channel."""
        if channel not in [1, 2, 3, 4]:
            raise ValueError("Channel must be 1, 2, 3, or 4")
        self.write(f'CH{channel}:SCALE {scale}')
    def get_channel_scale(self, channel):
        """Get the vertical scale for a specified channel."""
        if channel not in [1, 2, 3, 4]:
            raise ValueError("Channel must be 1, 2, 3, or 4")
        return self.query(f'CH{channel}:SCALE?')
    def set_channel_coupling(self, channel, coupling):
        """Set the coupling for a specified channel."""
        if channel not in [1, 2, 3, 4]:
            raise ValueError("Channel must be 1, 2, 3, or 4")
        if coupling not in ['AC', 'DC', 'GND']:
            raise ValueError("Coupling must be 'AC', 'DC', or 'GND'")
        self.write(f'CH{channel}:COUPLING {coupling}')
    def get_channel_coupling(self, channel):
        """Get the coupling for a specified channel."""
        if channel not in [1, 2, 3, 4]:
            raise ValueError("Channel must be 1, 2, 3, or 4")
        return self.query(f'CH{channel}:COUPLING?')
    def set_channel_state(self, channel, state):
        """Set the state (on/off) for a specified channel."""
        if channel not in [1, 2, 3, 4]:
            raise ValueError("Channel must be 1, 2, 3, or 4")
        if state not in ['ON', 'OFF']:
            raise ValueError("State must be 'ON' or 'OFF'")
        self.write(f'CH{channel}:STATE {state}')
    def get_channel_state(self, channel):
        """Get the state (on/off) for a specified channel."""
        if channel not in [1, 2, 3, 4]:
            raise ValueError("Channel must be 1, 2, 3, or 4")
        return self.query(f'CH{channel}:STATE?')
    def set_time_scale(self, scale):
        """Set the horizontal time scale for the oscilloscope."""
        self.write(f'HOR:SCA {scale}')
    def get_time_scale(self):
        """Get the horizontal time scale for the oscilloscope."""
        return self.query('HOR:SCA?')
    def set_trigger(self, channel, level, slope='RISING'):
        """Set the trigger for the oscilloscope."""
        if channel not in [1, 2, 3, 4]:
            raise ValueError("Channel must be 1, 2, 3, or 4")
        if slope not in ['RISING', 'FALLING']:
            raise ValueError("Slope must be 'RISING' or 'FALLING'")
        self.write(f'TRIGGER:EDGE:SOURCE CH{channel}')
        self.write(f'TRIGGER:EDGE:LEVEL {level}')
        self.write(f'TRIGGER:EDGE:SLOPE {slope}')
    def get_trigger(self):
        """Get the current trigger settings of the oscilloscope."""
        source = self.query('TRIGGER:EDGE:SOURCE?')
        level = self.query('TRIGGER:EDGE:LEVEL?')
        slope = self.query('TRIGGER:EDGE:SLOPE?')
        return {
            'source': source,
            'level': level,
            'slope': slope
        }
    def wait_for_trigger(self, timeout=10):
        """Wait for a trigger event to occur."""
        import time
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.query('TRIGger:STATE?').strip() == 'TRIGGER':
                return True
            time.sleep(0.1)
        return False
    def set_sample_rate(self, rate):
        """Set the sample rate for the oscilloscope."""
        self.write(f'HOR:SAMPLER {rate}')
    def get_sample_rate(self):
        """Get the current sample rate of the oscilloscope."""
        return self.query('HOR:SAMPLER?')
    def set_acquisition_state(self, state):
        """Set acquisition state - controls when scope acquires data."""
        if state not in ['RUN', 'STOP', 'SINGLE']:
            raise ValueError("State must be 'RUN', 'STOP', or 'SINGLE'")
        self.write(f'ACQuire:STATE {state}')
    
    def get_acquisition_state(self):
        """Get the current acquisition state."""
        return self.query('ACQuire:STATE?')
    
    def run(self):
        """Start continuous acquisition (autorun)."""
        self.write('ACQuire:STATE RUN')
    
    def stop(self):
        """Stop acquisition."""
        self.write('ACQuire:STATE STOP')
    
    def single(self):
        """Trigger a single acquisition."""
        self.write('ACQuire:STATE SINGLE') 
    def get_waveform_data(self, channel, data_format='ASCII'):
        """Get waveform data from specified channel."""
        if channel not in [1, 2, 3, 4]:
            raise ValueError("Channel must be 1, 2, 3, or 4")
        if data_format not in ['ASCII', 'BINARY']:
            raise ValueError("Data format must be 'ASCII' or 'BINARY'")
        
        # Set data source
        self.write(f'DATa:SOUrce CH{channel}')
        
        # Set data format
        if data_format == 'ASCII':
            self.write('DATa:ENCdg ASCii')
        else:
            self.write('DATa:ENCdg RIBinary')
        
        # Get the waveform data
        waveform_data = self.query('CURVe?')
        
        if data_format == 'ASCII':
            # Convert ASCII data to list of floats
            return [float(x) for x in waveform_data.split(',')]
        else:
            # Return binary data as-is for further processing
            return waveform_data
    
    def get_multiple_waveforms(self, channels, data_format='ASCII'):
        """Get waveform data from multiple channels."""
        if not isinstance(channels, list):
            raise ValueError("Channels must be a list")
        
        for channel in channels:
            if channel not in [1, 2, 3, 4]:
                raise ValueError(f"Channel {channel} must be 1, 2, 3, or 4")
        
        waveforms = {}
        for channel in channels:
            waveforms[f'CH{channel}'] = self.get_waveform_data(channel, data_format)
        
        return waveforms
    
    def save_waveforms_to_csv(self, waveforms, filename=None):
        """Save waveform data to CSV file."""
        import csv
        import datetime
        
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"waveforms_{timestamp}.csv"
        
        # Get time scale for x-axis
        time_scale = float(self.get_time_scale())
        
        # Determine the number of data points
        max_length = max(len(data) for data in waveforms.values())
        
        # Create time array
        time_step = time_scale * 10 / max_length  # 10 divisions across screen
        time_array = [i * time_step - (time_scale * 5) for i in range(max_length)]
        
        with open(filename, 'w', newline='') as csvfile:
            # Create header
            channels = list(waveforms.keys())
            fieldnames = ['Time'] + channels
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            # Write data rows
            for i in range(max_length):
                row = {'Time': time_array[i]}
                for channel in channels:
                    if i < len(waveforms[channel]):
                        row[channel] = waveforms[channel][i]
                    else:
                        row[channel] = ''  # Fill shorter arrays with empty values
                writer.writerow(row)
        
        return filename
    
    def get_triggered_waveforms_and_save(self, channels, filename=None, timeout=10):
        """Wait for trigger, capture waveforms, and save to CSV."""
        if not isinstance(channels, list):
            channels = [channels]  # Convert single channel to list
        
        # Start single acquisition
        self.single()
        
        # Wait for trigger
        if self.wait_for_trigger(timeout):
            # Get waveform data from all specified channels after trigger
            waveforms = self.get_multiple_waveforms(channels)
            
            # Save to CSV
            saved_filename = self.save_waveforms_to_csv(waveforms, filename)
            
            return {
                'waveforms': waveforms,
                'filename': saved_filename
            }
        else:
            raise TimeoutError(f"No trigger occurred within {timeout} seconds")
    
    def get_all_active_waveforms_and_save(self, filename=None, timeout=10):
        """Get waveforms from all active channels after trigger and save to CSV."""
        # Find which channels are currently ON
        active_channels = []
        for channel in [1, 2, 3, 4]:
            state = self.get_channel_state(channel).strip()
            if state == '1' or state.upper() == 'ON':
                active_channels.append(channel)
        
        if not active_channels:
            raise ValueError("No channels are currently active")
        
        return self.get_triggered_waveforms_and_save(active_channels, filename, timeout)
    

    def is_complete(self):
        """Check if the oscilloscope has completed its current operation."""
        return self.query('*OPC?') == '1'
    def close(self):
        """Close the connection to the oscilloscope."""
        self.scope.close()
        self.rm.close()