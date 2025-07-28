import unittest
from unittest.mock import Mock, patch, MagicMock
import pyvisa
from AFG31000 import AFG31000


class TestAFG31000(unittest.TestCase):
    """Test suite for AFG31000 arbitrary function generator class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock PyVISA components
        self.mock_rm = Mock()
        self.mock_scope = Mock()
        self.mock_rm.open_resource.return_value = self.mock_scope
        
        # Patch PyVISA ResourceManager
        with patch('pyvisa.ResourceManager', return_value=self.mock_rm):
            self.afg = AFG31000('test_resource', ip_address='192.168.1.100')
    
    def test_init_with_ip_address(self):
        """Test initialization with IP address."""
        with patch('pyvisa.ResourceManager') as mock_rm_class:
            mock_rm = Mock()
            mock_scope = Mock()
            mock_rm_class.return_value = mock_rm
            mock_rm.open_resource.return_value = mock_scope
            
            afg = AFG31000('test', ip_address='192.168.1.100')
            
            mock_rm.open_resource.assert_called_with('TCPIP::192.168.1.100::INSTR')
            self.assertEqual(afg.ip_address, '192.168.1.100')
    
    def test_init_with_serial_port(self):
        """Test initialization with serial port."""
        with patch('pyvisa.ResourceManager') as mock_rm_class:
            mock_rm = Mock()
            mock_scope = Mock()
            mock_rm_class.return_value = mock_rm
            mock_rm.open_resource.return_value = mock_scope
            
            afg = AFG31000('test', serial_port='COM1')
            
            mock_rm.open_resource.assert_called_with('COM1')
            # Check that serial settings are configured
            self.assertEqual(mock_scope.baud_rate, 115200)
            self.assertEqual(mock_scope.data_bits, 8)
    
    def test_init_with_visa_address(self):
        """Test initialization with VISA address."""
        with patch('pyvisa.ResourceManager') as mock_rm_class:
            mock_rm = Mock()
            mock_scope = Mock()
            mock_rm_class.return_value = mock_rm
            mock_rm.open_resource.return_value = mock_scope
            
            afg = AFG31000('test', visa_address='USB0::0x0699::0x0346::C012345::INSTR')
            
            mock_rm.open_resource.assert_called_with('USB0::0x0699::0x0346::C012345::INSTR')
    
    def test_init_no_connection_method(self):
        """Test that initialization fails when no connection method is provided."""
        with patch('pyvisa.ResourceManager'):
            with self.assertRaises(ValueError) as context:
                AFG31000('test')
            
            self.assertIn("At least one of serial_port, ip_address, or visa_address must be provided", 
                         str(context.exception))
    
    def test_device_id(self):
        """Test device ID query."""
        expected_id = 'TEKTRONIX,AFG31252,C123456,SCPI:99.0 FV:1.2.3'
        self.mock_scope.query.return_value = expected_id
        
        result = self.afg.device_id()
        
        self.mock_scope.query.assert_called_with('*IDN?')
        self.assertEqual(result, expected_id)
    
    def test_check_device_id_success(self):
        """Test successful device ID check."""
        self.mock_scope.query.return_value = 'TEKTRONIX,AFG31252,C123456,SCPI:99.0 FV:1.2.3'
        
        result = self.afg.check_device_id()
        
        self.assertIn('AFG31000', result)
    
    def test_check_device_id_failure(self):
        """Test device ID check failure."""
        self.mock_scope.query.return_value = 'SOME,OTHER,DEVICE,ID'
        
        with self.assertRaises(ValueError) as context:
            self.afg.check_device_id()
        
        self.assertIn("Device ID mismatch", str(context.exception))
    
    def test_write(self):
        """Test write command."""
        command = 'SOUR1:FUNC:SHAP SIN'
        self.afg.write(command)
        self.mock_scope.write.assert_called_with(command)
    
    def test_read(self):
        """Test read response."""
        expected_response = 'SIN'
        self.mock_scope.read.return_value = expected_response
        
        result = self.afg.read()
        
        self.mock_scope.read.assert_called_once()
        self.assertEqual(result, expected_response)
    
    def test_query(self):
        """Test query command."""
        command = 'SOUR1:FUNC:SHAP?'
        expected_response = 'SIN'
        self.mock_scope.query.return_value = expected_response
        
        result = self.afg.query(command)
        
        self.mock_scope.query.assert_called_with(command)
        self.assertEqual(result, expected_response)
    
    def test_set_waveform_type_valid(self):
        """Test setting valid waveform types."""
        valid_types = ['SINusoid', 'SQUare', 'PULSe', 'RAMP', 'PRNoise', 'DC', 
                      'SINC', 'GAUSsian', 'LORentz', 'EXPRise', 'EXPDecay', 'HAVersine']
        
        for waveform_type in valid_types:
            self.afg.set_waveform_type(1, waveform_type)
            self.mock_scope.write.assert_called_with(f'SOURce1:FUNCtion:SHAPe {waveform_type}')
    
    def test_set_waveform_type_invalid_type(self):
        """Test setting invalid waveform type."""
        with self.assertRaises(ValueError) as context:
            self.afg.set_waveform_type(1, 'INVALID')
        
        self.assertIn("Waveform type must be one of", str(context.exception))
    
    def test_set_waveform_type_invalid_channel(self):
        """Test setting waveform type on invalid channel."""
        with self.assertRaises(ValueError) as context:
            self.afg.set_waveform_type(3, 'SINusoid')
        
        self.assertIn("Channel must be 1 or 2", str(context.exception))
    
    def test_get_waveform_type(self):
        """Test getting waveform type."""
        self.mock_scope.query.return_value = 'SIN'
        
        result = self.afg.get_waveform_type(1)
        
        self.mock_scope.query.assert_called_with('SOURce1:FUNCtion:SHAPe?')
        self.assertEqual(result, 'SIN')
    
    def test_set_frequency_valid(self):
        """Test setting valid frequency."""
        self.afg.set_frequency(1, 1000.0)
        self.mock_scope.write.assert_called_with('SOURce1:FREQuency 1000.0')
    
    def test_set_frequency_invalid_value(self):
        """Test setting invalid frequency."""
        with self.assertRaises(ValueError) as context:
            self.afg.set_frequency(1, -100)
        
        self.assertIn("Frequency must be positive", str(context.exception))
    
    def test_get_frequency(self):
        """Test getting frequency."""
        self.mock_scope.query.return_value = '1000.0'
        
        result = self.afg.get_frequency(1)
        
        self.mock_scope.query.assert_called_with('SOURce1:FREQuency?')
        self.assertEqual(result, 1000.0)
    
    def test_set_amplitude_valid(self):
        """Test setting valid amplitude."""
        self.afg.set_amplitude(1, 2.5)
        self.mock_scope.write.assert_called_with('SOURce1:VOLTage:LEVel:IMMediate:AMPLitude 2.5')
    
    def test_set_amplitude_invalid(self):
        """Test setting invalid amplitude."""
        with self.assertRaises(ValueError) as context:
            self.afg.set_amplitude(1, -1.0)
        
        self.assertIn("Amplitude must be non-negative", str(context.exception))
    
    def test_get_amplitude(self):
        """Test getting amplitude."""
        self.mock_scope.query.return_value = '2.5'
        
        result = self.afg.get_amplitude(1)
        
        self.mock_scope.query.assert_called_with('SOURce1:VOLTage:LEVel:IMMediate:AMPLitude?')
        self.assertEqual(result, 2.5)
    
    def test_set_offset(self):
        """Test setting DC offset."""
        self.afg.set_offset(1, 0.5)
        self.mock_scope.write.assert_called_with('SOURce1:VOLTage:LEVel:IMMediate:OFFSet 0.5')
    
    def test_get_offset(self):
        """Test getting DC offset."""
        self.mock_scope.query.return_value = '0.5'
        
        result = self.afg.get_offset(1)
        
        self.mock_scope.query.assert_called_with('SOURce1:VOLTage:LEVel:IMMediate:OFFSet?')
        self.assertEqual(result, 0.5)
    
    def test_set_load(self):
        """Test setting load impedance."""
        self.afg.set_load(1, 50)
        self.mock_scope.write.assert_called_with('OUTPut1:LOAD 50')
    
    def test_get_load(self):
        """Test getting load impedance."""
        self.mock_scope.query.return_value = '50'
        
        result = self.afg.get_load(1)
        
        self.mock_scope.query.assert_called_with('OUTPut1:LOAD?')
        self.assertEqual(result, '50')
    
    def test_set_output_on_various_formats(self):
        """Test setting output ON with various input formats."""
        on_values = ['ON', True, 1]
        
        for value in on_values:
            self.afg.set_output(1, value)
            self.mock_scope.write.assert_called_with('OUTPut1:STATe ON')
    
    def test_set_output_off_various_formats(self):
        """Test setting output OFF with various input formats."""
        off_values = ['OFF', False, 0]
        
        for value in off_values:
            self.afg.set_output(1, value)
            self.mock_scope.write.assert_called_with('OUTPut1:STATe OFF')
    
    def test_set_output_invalid_state(self):
        """Test setting invalid output state."""
        with self.assertRaises(ValueError) as context:
            self.afg.set_output(1, 'INVALID')
        
        self.assertIn("State must be", str(context.exception))
    
    def test_get_output(self):
        """Test getting output state."""
        self.mock_scope.query.return_value = '1'
        
        result = self.afg.get_output(1)
        
        self.mock_scope.query.assert_called_with('OUTPut1:STATe?')
        self.assertEqual(result, '1')
    
    def test_set_frequency_lock_on(self):
        """Test setting frequency lock ON."""
        self.afg.set_frequency_lock('ON')
        self.mock_scope.write.assert_called_with('SOURce:FREQuency:CONCurrent ON')
    
    def test_set_frequency_lock_off(self):
        """Test setting frequency lock OFF."""
        self.afg.set_frequency_lock('OFF')
        self.mock_scope.write.assert_called_with('SOURce:FREQuency:CONCurrent OFF')
    
    def test_get_frequency_lock(self):
        """Test getting frequency lock state."""
        self.mock_scope.query.return_value = '1'
        
        result = self.afg.get_frequency_lock()
        
        self.mock_scope.query.assert_called_with('SOURce:FREQuency:CONCurrent?')
        self.assertEqual(result, '1')
    
    def test_set_phase_valid(self):
        """Test setting valid phase."""
        self.afg.set_phase(1, 90)
        self.mock_scope.write.assert_called_with('SOURce1:PHASe:ADJust 90DEG')
    
    def test_set_phase_boundary_values(self):
        """Test setting phase at boundary values."""
        # Test minimum value
        self.afg.set_phase(1, -360)
        self.mock_scope.write.assert_called_with('SOURce1:PHASe:ADJust -360DEG')
        
        # Test maximum value
        self.afg.set_phase(1, 360)
        self.mock_scope.write.assert_called_with('SOURce1:PHASe:ADJust 360DEG')
    
    def test_set_phase_invalid(self):
        """Test setting invalid phase values."""
        invalid_phases = [-361, 361, 400, -400]
        
        for phase in invalid_phases:
            with self.assertRaises(ValueError) as context:
                self.afg.set_phase(1, phase)
            
            self.assertIn("Phase must be between -360 and 360 degrees", str(context.exception))
    
    def test_get_phase(self):
        """Test getting phase."""
        self.mock_scope.query.return_value = '90.0'
        
        result = self.afg.get_phase(1)
        
        self.mock_scope.query.assert_called_with('SOURce1:PHASe:ADJust?')
        self.assertEqual(result, 90.0)
    
    def test_channel_validation_all_methods(self):
        """Test that all methods properly validate channel numbers."""
        invalid_channels = [0, 3, 4, -1, 'invalid']
        
        # Methods that should validate channels
        channel_methods = [
            ('set_waveform_type', ['SINusoid']),
            ('get_waveform_type', []),
            ('set_frequency', [1000]),
            ('get_frequency', []),
            ('set_amplitude', [1.0]),
            ('get_amplitude', []),
            ('set_offset', [0.0]),
            ('get_offset', []),
            ('set_load', [50]),
            ('get_load', []),
            ('set_output', ['ON']),
            ('get_output', []),
            ('set_phase', [90]),
            ('get_phase', [])
        ]
        
        for channel in [0, 3, 4, -1]:  # Skip 'invalid' for numeric-only tests
            for method_name, args in channel_methods:
                with self.assertRaises(ValueError):
                    method = getattr(self.afg, method_name)
                    method(channel, *args)


class TestAFG31000Integration(unittest.TestCase):
    """Integration tests for AFG31000 class."""
    
    def setUp(self):
        """Set up test fixtures for integration tests."""
        self.mock_rm = Mock()
        self.mock_scope = Mock()
        self.mock_rm.open_resource.return_value = self.mock_scope
        
        with patch('pyvisa.ResourceManager', return_value=self.mock_rm):
            self.afg = AFG31000('test_resource', ip_address='192.168.1.100')
    
    def test_complete_channel_setup(self):
        """Test complete setup of a channel with all parameters."""
        # Set up mock responses
        self.mock_scope.query.side_effect = [
            'TEKTRONIX,AFG31252,C123456,SCPI:99.0 FV:1.2.3',  # device_id
            'SIN',     # get_waveform_type
            '1000.0',  # get_frequency
            '2.5',     # get_amplitude
            '0.0',     # get_offset
            '1'        # get_output
        ]
        
        # Verify device
        device_id = self.afg.check_device_id()
        self.assertIn('AFG31252', device_id)
        
        # Configure channel 1
        self.afg.set_waveform_type(1, 'SINusoid')
        self.afg.set_frequency(1, 1000.0)
        self.afg.set_amplitude(1, 2.5)
        self.afg.set_offset(1, 0.0)
        self.afg.set_output(1, 'ON')
        
        # Verify settings
        self.assertEqual(self.afg.get_waveform_type(1), 'SIN')
        self.assertEqual(self.afg.get_frequency(1), 1000.0)
        self.assertEqual(self.afg.get_amplitude(1), 2.5)
        self.assertEqual(self.afg.get_offset(1), 0.0)
        self.assertEqual(self.afg.get_output(1), '1')
        
        # Verify all write calls were made
        expected_writes = [
            'SOURce1:FUNCtion:SHAPe SINusoid',
            'SOURce1:FREQuency 1000.0',
            'SOURce1:VOLTage:LEVel:IMMediate:AMPLitude 2.5',
            'SOURce1:VOLTage:LEVel:IMMediate:OFFSet 0.0',
            'OUTPut1:STATe ON'
        ]
        
        actual_writes = [call.args[0] for call in self.mock_scope.write.call_args_list]
        self.assertEqual(actual_writes, expected_writes)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
