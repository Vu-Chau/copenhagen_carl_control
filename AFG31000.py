import pyvisa

class AFG31000:
    def __init__(self, resource_name=None, serial_port=None, ip_address=None, visa_address=None, timeout=5000):
        """Initialize the AFG31000 class with a resource name and optional serial port, ip address, or VISA address.
        If all parameters are None, it will search for available AFG instruments automatically."""
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
        elif resource_name:
            self.scope = self.rm.open_resource(resource_name)
        else:
            # If all parameters are None, search for AFG instruments
            afg_resource = self._find_afg_instrument()
            if afg_resource:
                self.scope = self.rm.open_resource(afg_resource)
                self.resource_name = afg_resource
                print(f"Automatically connected to AFG instrument at: {afg_resource}")
            else:
                raise ValueError("No AFG instrument found. Please provide serial_port, ip_address, visa_address, or resource_name.")
        self.scope.timeout = timeout

        # Configure serial settings if using serial connection
        # if serial_port:
        #     self.scope.baud_rate = 115200
        #     self.scope.data_bits = 8
        #     self.scope.parity = pyvisa.constants.Parity.none
        #     self.scope.stop_bits = pyvisa.constants.StopBits.one
        #     self.scope.flow_control = pyvisa.constants.VI_ASRL_FLOW_NONE
        # Initialize the device
    
    def _find_afg_instrument(self):
        """Find available AFG instruments by scanning all VISA resources.
        
        Returns:
            str: Resource name of the first AFG instrument found, or None if no AFG found
        """
        try:
            # Get list of all available resources
            resources = self.rm.list_resources()
            print(f"Found {len(resources)} total instruments:")
            
            afg_instruments = []
            
            for resource in resources:
                try:
                    print(f"  Checking: {resource}")
                    # Try to connect to each resource
                    temp_instrument = self.rm.open_resource(resource)
                    temp_instrument.timeout = 2000  # Short timeout for discovery
                    
                    # Query device identification
                    device_id = temp_instrument.query('*IDN?').strip()
                    print(f"    Device ID: {device_id}")
                    
                    # Check if this is an AFG instrument
                    if 'AFG' in device_id.upper():
                        afg_instruments.append({
                            'resource': resource,
                            'device_id': device_id
                        })
                        print(f"    ✓ AFG instrument found!")
                    
                    temp_instrument.close()
                    
                except Exception as e:
                    print(f"    ✗ Could not query {resource}: {e}")
                    try:
                        temp_instrument.close()
                    except:
                        pass
                    continue
            
            if afg_instruments:
                print(f"\nFound {len(afg_instruments)} AFG instrument(s):")
                for i, instr in enumerate(afg_instruments):
                    print(f"  {i+1}. {instr['resource']} - {instr['device_id']}")
                
                # Return the first AFG instrument found
                selected = afg_instruments[0]
                print(f"\nUsing: {selected['resource']}")
                return selected['resource']
            else:
                print("\nNo AFG instruments found.")
                return None
                
        except Exception as e:
            print(f"Error during instrument discovery: {e}")
            return None
        
    def device_id(self):
        """Get the device ID."""
        return self.scope.query('*IDN?')
    
    def check_device_id(self, strict=False):
        """Check if the device ID matches the expected value.
        
        Args:
            strict (bool): If True, checks for specific model 'AFG31252'.
                          If False, checks for any AFG instrument.
        
        Returns:
            bool: True if device ID matches expected pattern, False otherwise
        """
        device_id = self.device_id()
        
        if strict:
            expected_id = 'AFG31252'
            if expected_id not in device_id:
                print(f"Device ID mismatch: expected '{expected_id}', got '{device_id}'")
                return False
        else:
            # Check for any AFG instrument
            if 'AFG' not in device_id.upper():
                print(f"Device ID mismatch: expected AFG instrument, got '{device_id}'")
                return False
            else:
                print(f"AFG instrument detected: {device_id}")
        
        return True
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
        """Set the load impedance for a specified channel in Ohms.
        
        Args:
            channel: Channel number (1 or 2)
            impedance: Load impedance value. Can be:
                      - Numeric value (int/float) between 1 and 10000 Ohms
                      - Numeric string (e.g., "50", "75") between 1 and 10000 Ohms
                      - "INFinity" for >10 kΩ (high impedance)
                      - "MINimum" for 1 Ω
                      - "MAXimum" for 10 kΩ
                      - "HIGHZ" (alias for INFinity)
                      
        The device has 1 Ω resolution with 3 significant digits. Default is 50 Ω.
        """
        if channel not in [1, 2]:
            raise ValueError("Channel must be 1 or 2")
        
        if isinstance(impedance, str):
            # First check if it's a numeric string
            try:
                impedance_val = float(impedance)
                # If it's a valid number, validate the range
                if impedance_val < 1 or impedance_val > 10000:
                    raise ValueError("Numeric impedance must be between 1 and 10000 Ohms")
                impedance = impedance_val
            except ValueError:
                # Not a numeric string, check if it's a valid keyword
                impedance_upper = impedance.upper()
                if impedance_upper in ["HIGHZ", "INFINITY", "INF"]:
                    impedance = "INFinity"
                elif impedance_upper in ["MINIMUM", "MIN"]:
                    impedance = "MINimum"
                elif impedance_upper in ["MAXIMUM", "MAX"]:
                    impedance = "MAXimum"
                else:
                    raise ValueError(f"Invalid impedance value '{impedance}'. Must be a number (1-10000) or one of: INFinity, MINimum, MAXimum, HIGHZ")
        else:
            # Numeric value validation
            try:
                impedance_val = float(impedance)
                if impedance_val < 1 or impedance_val > 10000:
                    raise ValueError("Numeric impedance must be between 1 and 10000 Ohms")
                impedance = impedance_val
            except (ValueError, TypeError):
                raise ValueError("Impedance must be a number between 1-10000 Ohms or one of: INFinity, MINimum, MAXimum, HIGHZ")
        
        self.write(f'OUTPut{channel}:IMP {impedance}')
    
    def get_load(self, channel):
        """Get the load impedance for a specified channel."""
        if channel not in [1, 2]:
            raise ValueError("Channel must be 1 or 2")
        return self.query(f'OUTPut{channel}:IMP?')
    
    # Output State Functions
    def set_output(self, channel, state):
        """Set the output state for a specified channel."""
        if channel not in [1, 2]:
            raise ValueError("Channel must be 1 or 2")
        
        # Normalize string inputs to uppercase for comparison
        if isinstance(state, str):
            state_upper = state.upper()
            if state_upper not in ['ON', 'OFF']:
                raise ValueError("State must be 'ON', 'OFF' (case insensitive), True, False, 1, or 0")
            state = state_upper
        elif state not in [True, False, 1, 0]:
            raise ValueError("State must be 'ON', 'OFF' (case insensitive), True, False, 1, or 0")
        
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
    def set_phase(self, channel, phase, unit='DEG'):
        """Set the phase for a specified channel.
        
        Args:
            channel: Channel number (1 or 2)
            phase: Phase value
            unit: 'DEG' for degrees (default) or 'RAD' for radians
        """
        if channel not in [1, 2]:
            raise ValueError("Channel must be 1 or 2")
        if unit.upper() not in ['DEG', 'RAD']:
            raise ValueError("Unit must be 'DEG' or 'RAD'")
        
        if unit.upper() == 'DEG':
            if not -360 <= phase <= 360:
                raise ValueError("Phase must be between -360 and 360 degrees")
            self.write(f'SOURce{channel}:PHASe:ADJust {phase}DEG')
        else:  # RAD
            if not -6.28 <= phase <= 6.28:  # approximately -2π to 2π
                raise ValueError("Phase must be between -2π and 2π radians")
            self.write(f'SOURce{channel}:PHASe:ADJust {phase}RAD')
    
    def get_phase(self, channel, unit='DEG'):
        """Get the phase for a specified channel.
        
        Args:
            channel: Channel number (1 or 2)
            unit: 'DEG' for degrees (default) or 'RAD' for radians
            
        Returns:
            Phase value in the requested unit
        """
        if channel not in [1, 2]:
            raise ValueError("Channel must be 1 or 2")
        if unit.upper() not in ['DEG', 'RAD']:
            raise ValueError("Unit must be 'DEG' or 'RAD'")
        
        # Query the phase value (device may return in any unit)
        phase_response = self.query(f'SOURce{channel}:PHASe:ADJust?')
        phase_value = float(phase_response)
        
        # Detect if the returned value is in radians or degrees
        is_radians = abs(phase_value) <= 6.28  # 2π ≈ 6.28
        
        if unit.upper() == 'DEG':
            if is_radians:
                # Convert from radians to degrees
                return phase_value * 180 / 3.14159265359
            else:
                # Already in degrees
                return phase_value
        else:  # RAD
            if is_radians:
                # Already in radians
                return phase_value
            else:
                # Convert from degrees to radians
                return phase_value * 3.14159265359 / 180
    
    def close(self):
        """Close the connection to the device."""
        self.scope.close()
        self.rm.close()
    
    @staticmethod
    def list_all_instruments():
        """List all available VISA instruments with their device IDs.
        
        Returns:
            list: List of dictionaries containing 'resource' and 'device_id' keys
        """
        rm = pyvisa.ResourceManager()
        instruments = []
        
        try:
            resources = rm.list_resources()
            print(f"Scanning {len(resources)} available instruments:")
            print("-" * 60)
            
            for resource in resources:
                try:
                    temp_instrument = rm.open_resource(resource)
                    temp_instrument.timeout = 2000
                    
                    device_id = temp_instrument.query('*IDN?').strip()
                    is_afg = 'AFG' in device_id.upper()
                    
                    instruments.append({
                        'resource': resource,
                        'device_id': device_id,
                        'is_afg': is_afg
                    })
                    
                    status = "AFG ✓" if is_afg else "Other"
                    print(f"{resource:<25} | {status:<6} | {device_id}")
                    
                    temp_instrument.close()
                    
                except Exception as e:
                    print(f"{resource:<25} | Error  | Could not query: {e}")
                    try:
                        temp_instrument.close()
                    except:
                        pass
            
            print("-" * 60)
            afg_count = sum(1 for instr in instruments if instr.get('is_afg', False))
            print(f"Total instruments: {len(instruments)}, AFG instruments: {afg_count}")
            
        except Exception as e:
            print(f"Error during instrument scan: {e}")
        finally:
            rm.close()
        
        return instruments
    
    