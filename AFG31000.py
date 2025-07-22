import pyvisa

class AFG31000:
    def __init__(self, resource_name, serial_port=None, ip_address=None, visa_address=None, timeout=5000):
        """Initialize the AFG31000 class with a resource name and optional serial port, ip address, or VISA address."""
        self.resource_name = resource_name
        self.serial_port = serial_port
        self.ip_address = ip_address
        self.visa_address = visa_address
        
        # Initialize the VISA resource manager
        self.rm = pyvisa.ResourceManager()
        
        # Open the connection to the device
        if serial_port:
            self.scope = self.rm.open_resource(serial_port)
        elif ip_address:
            self.scope = self.rm.open_resource(f'TCPIP::{ip_address}::INSTR')
        elif visa_address:
            self.scope = self.rm.open_resource(visa_address)
        else:
            raise ValueError("At least one of serial_port, ip_address, or visa_address must be provided.")
        self.scope.timeout = timeout

        # Configure serial settings if using serial connection
        if serial_port:
            self.scope.baud_rate = 115200
            self.scope.data_bits = 8
            self.scope.parity = pyvisa.constants.Parity.none
            self.scope.stop_bits = pyvisa.constants.StopBits.one
            self.scope.flow_control = pyvisa.constants.VI_ASRL_FLOW_NONE
        # Initialize the device
        
    def device_id(self):
        """Get the device ID."""
        return self.scope.query('*IDN?')
    def check_device_id(self):
        """Check if the device ID matches the expected value."""
        expected_id = 'AFG31000'
        device_id = self.device_id()
        if expected_id not in device_id:
            raise ValueError(f"Device ID mismatch: expected '{expected_id}', got '{device_id}'")
        return device_id
    def write(self, command):
        """Write a command to the device."""
        self.scope.write(command)
    def read(self):
        """Read a response from the device."""
        return self.scope.read()
    def query(self, command):
        """Send a command and read the response."""
        return self.scope.query(command)
        # Waveform Type Functions
    def set_waveform_type(self, channel, waveform_type):
        """Set the waveform type for a specified channel."""
        valid_types = ['SINusoid', 'SQUare', 'PULSe', 'RAMP', 'PRNoise', 'DC', 'SINC', 'GAUSsian', 'LORentz', 'EXPRise', 'EXPDecay', 'HAVersine']
        if waveform_type not in valid_types:
            raise ValueError(f"Waveform type must be one of {valid_types}")
        if channel not in [1, 2]:
            raise ValueError("Channel must be 1 or 2")
        self.write(f'SOURce{channel}:FUNCtion:SHAPe {waveform_type}')
    
    def get_waveform_type(self, channel):
        """Get the waveform type for a specified channel."""
        if channel not in [1, 2]:
            raise ValueError("Channel must be 1 or 2")
        return self.query(f'SOURce{channel}:FUNCtion:SHAPe?')
    
    # Frequency Functions
    def set_frequency(self, channel, frequency):
        """Set the frequency for a specified channel in Hz."""
        if channel not in [1, 2]:
            raise ValueError("Channel must be 1 or 2")
        if frequency <= 0:
            raise ValueError("Frequency must be positive")
        self.write(f'SOURce{channel}:FREQuency {frequency}')
    
    def get_frequency(self, channel):
        """Get the frequency for a specified channel."""
        if channel not in [1, 2]:
            raise ValueError("Channel must be 1 or 2")
        return float(self.query(f'SOURce{channel}:FREQuency?'))
    
    # Amplitude Functions
    def set_amplitude(self, channel, amplitude):
        """Set the amplitude for a specified channel in Volts peak-to-peak."""
        if channel not in [1, 2]:
            raise ValueError("Channel must be 1 or 2")
        if amplitude < 0:
            raise ValueError("Amplitude must be non-negative")
        self.write(f'SOURce{channel}:VOLTage:LEVel:IMMediate:AMPLitude {amplitude}')
    
    def get_amplitude(self, channel):
        """Get the amplitude for a specified channel."""
        if channel not in [1, 2]:
            raise ValueError("Channel must be 1 or 2")
        return float(self.query(f'SOURce{channel}:VOLTage:LEVel:IMMediate:AMPLitude?'))
    
    # Offset Functions
    def set_offset(self, channel, offset):
        """Set the DC offset for a specified channel in Volts."""
        if channel not in [1, 2]:
            raise ValueError("Channel must be 1 or 2")
        self.write(f'SOURce{channel}:VOLTage:LEVel:IMMediate:OFFSet {offset}')
    
    def get_offset(self, channel):
        """Get the DC offset for a specified channel."""
        if channel not in [1, 2]:
            raise ValueError("Channel must be 1 or 2")
        return float(self.query(f'SOURce{channel}:VOLTage:LEVel:IMMediate:OFFSet?'))
    
    # Load Functions
    def set_load(self, channel, impedance):
        """Set the load impedance for a specified channel in Ohms."""
        if channel not in [1, 2]:
            raise ValueError("Channel must be 1 or 2")
        self.write(f'OUTPut{channel}:LOAD {impedance}')
    
    def get_load(self, channel):
        """Get the load impedance for a specified channel."""
        if channel not in [1, 2]:
            raise ValueError("Channel must be 1 or 2")
        return self.query(f'OUTPut{channel}:LOAD?')
    
    # Output State Functions
    def set_output(self, channel, state):
        """Set the output state for a specified channel."""
        if channel not in [1, 2]:
            raise ValueError("Channel must be 1 or 2")
        if state not in ['ON', 'OFF', True, False, 1, 0]:
            raise ValueError("State must be 'ON', 'OFF', True, False, 1, or 0")
        
        if state in ['ON', True, 1]:
            self.write(f'OUTPut{channel}:STATe ON')
        else:
            self.write(f'OUTPut{channel}:STATe OFF')
    
    def get_output(self, channel):
        """Get the output state for a specified channel."""
        if channel not in [1, 2]:
            raise ValueError("Channel must be 1 or 2")
        return self.query(f'OUTPut{channel}:STATe?')
    
    # Frequency Lock Functions
    def set_frequency_lock(self, state):
        """Set the frequency lock state for both channels."""
        if state not in ['ON', 'OFF', True, False, 1, 0]:
            raise ValueError("State must be 'ON', 'OFF', True, False, 1, or 0")
        
        if state in ['ON', True, 1]:
            self.write('SOURce:FREQuency:CONCurrent ON')
        else:
            self.write('SOURce:FREQuency:CONCurrent OFF')
    
    def get_frequency_lock(self):
        """Get the frequency lock state."""
        return self.query('SOURce:FREQuency:CONCurrent?')
    
    # Phase Functions
    def set_phase(self, channel, phase):
        """Set the phase for a specified channel in degrees."""
        if channel not in [1, 2]:
            raise ValueError("Channel must be 1 or 2")
        if not -360 <= phase <= 360:
            raise ValueError("Phase must be between -360 and 360 degrees")
        self.write(f'SOURce{channel}:PHASe:ADJust {phase}DEG')
    
    def get_phase(self, channel):
        """Get the phase for a specified channel."""
        if channel not in [1, 2]:
            raise ValueError("Channel must be 1 or 2")
        return float(self.query(f'SOURce{channel}:PHASe:ADJust?'))
    
    