import unittest
from unittest.mock import Mock, patch, MagicMock, call
import pyvisa
import time
from MSO44B import MSO44B


class TestMSO44B(unittest.TestCase):
    """Test suite for MSO44B oscilloscope class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock PyVISA components
        self.mock_rm = Mock()
        self.mock_scope = Mock()
        self.mock_rm.open_resource.return_value = self.mock_scope
        
        # Patch PyVISA ResourceManager
        with patch('pyvisa.ResourceManager', return_value=self.mock_rm):
            self.mso = MSO44B(ip_address='192.168.1.100')
    
    def test_init_with_ip_address(self):
        """Test initialization with IP address."""
        with patch('pyvisa.ResourceManager') as mock_rm_class:
            mock_rm = Mock()
            mock_scope = Mock()
            mock_rm_class.return_value = mock_rm
            mock_rm.open_resource.return_value = mock_scope
            
            mso = MSO44B(ip_address='192.168.1.100')
            
            mock_rm.open_resource.assert_called_with('TCPIP::192.168.1.100::INSTR')
            self.assertEqual(mso.resource_name, 'TCPIP::192.168.1.100::INSTR')
    
    def test_init_with_serial_port(self):
        """Test initialization with serial port."""
        with patch('pyvisa.ResourceManager') as mock_rm_class:
            mock_rm = Mock()
            mock_scope = Mock()
            mock_rm_class.return_value = mock_rm
            mock_rm.open_resource.return_value = mock_scope
            
            mso = MSO44B(serial_port='COM1')
            
            mock_rm.open_resource.assert_called_with('ASRLCOM1::INSTR')
            # Check that serial settings are configured
            self.assertEqual(mock_scope.baud_rate, 115200)
            self.assertEqual(mock_scope.data_bits, 8)
    
    def test_init_with_resource_name(self):
        """Test initialization with direct resource name."""
        with patch('pyvisa.ResourceManager') as mock_rm_class:
            mock_rm = Mock()
            mock_scope = Mock()
            mock_rm_class.return_value = mock_rm
            mock_rm.open_resource.return_value = mock_scope
            
            resource_name = 'USB0::0x0699::0x0408::C012345::INSTR'
            mso = MSO44B(resource_name=resource_name)
            
            mock_rm.open_resource.assert_called_with(resource_name)
            self.assertEqual(mso.resource_name, resource_name)
    
    def test_init_no_connection_method(self):
        """Test that initialization fails when no connection method is provided."""
        with patch('pyvisa.ResourceManager'):
            with self.assertRaises(ValueError) as context:
                MSO44B()
            
            self.assertIn("Must provide either resource_name, ip_address, or serial_port", 
                         str(context.exception))
    
    def test_write(self):
        """Test write command."""
        command = 'CH1:SCALE 1.0'
        self.mso.write(command)
        self.mock_scope.write.assert_called_with(command)
    
    def test_query(self):
        """Test query command."""
        command = 'CH1:SCALE?'
        expected_response = '1.0'
        self.mock_scope.query.return_value = expected_response
        
        result = self.mso.query(command)
        
        self.mock_scope.query.assert_called_with(command)
        self.assertEqual(result, expected_response)
    
    def test_device_id(self):
        """Test device ID query."""
        expected_id = 'TEKTRONIX,MSO44B,C012345,CF:91.1CT FV:1.26.6.37'
        self.mock_scope.query.return_value = expected_id
        
        result = self.mso.device_id()
        
        self.mock_scope.query.assert_called_with('*IDN?')
        self.assertEqual(result, expected_id)
    
    def test_check_device_id_success(self):
        """Test successful device ID check."""
        self.mock_scope.query.return_value = 'TEKTRONIX,MSO44B,C012345,CF:91.1CT FV:1.26.6.37'
        
        result = self.mso.check_device_id()
        
        self.assertTrue(result)
    
    def test_check_device_id_failure(self):
        """Test device ID check failure."""
        self.mock_scope.query.return_value = 'SOME,OTHER,DEVICE,ID'
        
        result = self.mso.check_device_id()
        
        self.assertFalse(result)
    
    def test_reset(self):
        """Test reset command."""
        self.mso.reset()
        self.mock_scope.write.assert_called_with('*RST')
    
    def test_clear_status(self):
        """Test clear status command."""
        self.mso.clear_status()
        self.mock_scope.write.assert_called_with('*CLS')
    
    def test_set_channel_scale_valid(self):
        """Test setting valid channel scale."""
        self.mso.set_channel_scale(1, 1.0)
        self.mock_scope.write.assert_called_with('CH1:SCALE 1.0')
    
    def test_set_channel_scale_invalid_channel(self):
        """Test setting channel scale with invalid channel."""
        with self.assertRaises(ValueError) as context:
            self.mso.set_channel_scale(5, 1.0)
        
        self.assertIn("Channel must be 1, 2, 3, or 4", str(context.exception))
    
    def test_get_channel_scale(self):
        """Test getting channel scale."""
        self.mock_scope.query.return_value = '1.0'
        
        result = self.mso.get_channel_scale(1)
        
        self.mock_scope.query.assert_called_with('CH1:SCALE?')
        self.assertEqual(result, '1.0')
    
    def test_set_channel_coupling_valid(self):
        """Test setting valid channel coupling."""
        valid_couplings = ['AC', 'DC', 'GND']
        
        for coupling in valid_couplings:
            self.mso.set_channel_coupling(1, coupling)
            self.mock_scope.write.assert_called_with(f'CH1:COUPLING {coupling}')
    
    def test_set_channel_coupling_invalid(self):
        """Test setting invalid channel coupling."""
        with self.assertRaises(ValueError) as context:
            self.mso.set_channel_coupling(1, 'INVALID')
        
        self.assertIn("Coupling must be 'AC', 'DC', or 'GND'", str(context.exception))
    
    def test_get_channel_coupling(self):
        """Test getting channel coupling."""
        self.mock_scope.query.return_value = 'DC'
        
        result = self.mso.get_channel_coupling(1)
        
        self.mock_scope.query.assert_called_with('CH1:COUPLING?')
        self.assertEqual(result, 'DC')
    
    def test_set_channel_state_valid(self):
        """Test setting valid channel state."""
        valid_states = ['ON', 'OFF']
        
        for state in valid_states:
            self.mso.set_channel_state(1, state)
            self.mock_scope.write.assert_called_with(f'CH1:STATE {state}')
    
    def test_set_channel_state_invalid(self):
        """Test setting invalid channel state."""
        with self.assertRaises(ValueError) as context:
            self.mso.set_channel_state(1, 'INVALID')
        
        self.assertIn("State must be 'ON' or 'OFF'", str(context.exception))
    
    def test_get_channel_state(self):
        """Test getting channel state."""
        self.mock_scope.query.return_value = 'ON'
        
        result = self.mso.get_channel_state(1)
        
        self.mock_scope.query.assert_called_with('CH1:STATE?')
        self.assertEqual(result, 'ON')
    
    def test_set_time_scale(self):
        """Test setting time scale."""
        self.mso.set_time_scale(1e-3)
        self.mock_scope.write.assert_called_with('HOR:SCA 0.001')
    
    def test_get_time_scale(self):
        """Test getting time scale."""
        self.mock_scope.query.return_value = '1E-3'
        
        result = self.mso.get_time_scale()
        
        self.mock_scope.query.assert_called_with('HOR:SCA?')
        self.assertEqual(result, '1E-3')
    
    def test_set_trigger_valid(self):
        """Test setting valid trigger."""
        self.mso.set_trigger(1, 0.5, 'RISING')
        
        expected_calls = [
            call('TRIGGER:EDGE:SOURCE CH1'),
            call('TRIGGER:EDGE:LEVEL 0.5'),
            call('TRIGGER:EDGE:SLOPE RISING')
        ]
        
        self.mock_scope.write.assert_has_calls(expected_calls)
    
    def test_set_trigger_invalid_channel(self):
        """Test setting trigger with invalid channel."""
        with self.assertRaises(ValueError) as context:
            self.mso.set_trigger(5, 0.5)
        
        self.assertIn("Channel must be 1, 2, 3, or 4", str(context.exception))
    
    def test_set_trigger_invalid_slope(self):
        """Test setting trigger with invalid slope."""
        with self.assertRaises(ValueError) as context:
            self.mso.set_trigger(1, 0.5, 'INVALID')
        
        self.assertIn("Slope must be 'RISING' or 'FALLING'", str(context.exception))
    
    def test_get_trigger(self):
        """Test getting trigger settings."""
        self.mock_scope.query.side_effect = ['CH1', '0.5', 'RISING']
        
        result = self.mso.get_trigger()
        
        expected_result = {
            'source': 'CH1',
            'level': '0.5',
            'slope': 'RISING'
        }
        
        self.assertEqual(result, expected_result)
    
    @patch('time.sleep')
    @patch('time.time')
    def test_wait_for_trigger_success(self, mock_time, mock_sleep):
        """Test successful wait for trigger."""
        # Mock time progression
        mock_time.side_effect = [0, 1, 2]  # Start, first check, trigger found
        self.mock_scope.query.side_effect = ['STOP', 'TRIGGER']
        
        result = self.mso.wait_for_trigger(timeout=10)
        
        self.assertTrue(result)
        self.mock_scope.query.assert_called_with('TRIGger:STATE?')
    
    @patch('time.sleep')
    @patch('time.time')
    def test_wait_for_trigger_timeout(self, mock_time, mock_sleep):
        """Test wait for trigger timeout."""
        # Mock time progression that exceeds timeout
        mock_time.side_effect = [0, 5, 11]  # Start, mid, timeout
        self.mock_scope.query.return_value = 'STOP'
        
        result = self.mso.wait_for_trigger(timeout=10)
        
        self.assertFalse(result)
    
    def test_set_sample_rate(self):
        """Test setting sample rate."""
        self.mso.set_sample_rate(1e6)
        self.mock_scope.write.assert_called_with('HOR:SAMPLER 1000000.0')
    
    def test_get_sample_rate(self):
        """Test getting sample rate."""
        self.mock_scope.query.return_value = '1E6'
        
        result = self.mso.get_sample_rate()
        
        self.mock_scope.query.assert_called_with('HOR:SAMPLER?')
        self.assertEqual(result, '1E6')
    
    def test_set_acquisition_state_valid(self):
        """Test setting valid acquisition states."""
        valid_states = ['RUN', 'STOP', 'SINGLE']
        
        for state in valid_states:
            self.mso.set_acquisition_state(state)
            self.mock_scope.write.assert_called_with(f'ACQuire:STATE {state}')
    
    def test_set_acquisition_state_invalid(self):
        """Test setting invalid acquisition state."""
        with self.assertRaises(ValueError) as context:
            self.mso.set_acquisition_state('INVALID')
        
        self.assertIn("State must be 'RUN', 'STOP', or 'SINGLE'", str(context.exception))
    
    def test_get_acquisition_state(self):
        """Test getting acquisition state."""
        self.mock_scope.query.return_value = 'RUN'
        
        result = self.mso.get_acquisition_state()
        
        self.mock_scope.query.assert_called_with('ACQuire:STATE?')
        self.assertEqual(result, 'RUN')
    
    def test_run(self):
        """Test run command."""
        self.mso.run()
        self.mock_scope.write.assert_called_with('ACQuire:STATE RUN')
    
    def test_stop(self):
        """Test stop command."""
        self.mso.stop()
        self.mock_scope.write.assert_called_with('ACQuire:STATE STOP')
    
    def test_single(self):
        """Test single acquisition command."""
        self.mso.single()
        self.mock_scope.write.assert_called_with('ACQuire:STATE SINGLE')
    
    def test_get_waveform_data_ascii(self):
        """Test getting waveform data in ASCII format."""
        mock_data = '1.0,2.0,3.0,4.0,5.0'
        self.mock_scope.query.return_value = mock_data
        
        result = self.mso.get_waveform_data(1, 'ASCII')
        
        expected_calls = [
            call('DATa:SOUrce CH1'),
            call('DATa:ENCdg ASCii')
        ]
        self.mock_scope.write.assert_has_calls(expected_calls)
        self.mock_scope.query.assert_called_with('CURVe?')
        self.assertEqual(result, [1.0, 2.0, 3.0, 4.0, 5.0])
    
    def test_get_waveform_data_binary(self):
        """Test getting waveform data in binary format."""
        mock_data = b'\x01\x02\x03\x04'
        self.mock_scope.query.return_value = mock_data
        
        result = self.mso.get_waveform_data(1, 'BINARY')
        
        expected_calls = [
            call('DATa:SOUrce CH1'),
            call('DATa:ENCdg RIBinary')
        ]
        self.mock_scope.write.assert_has_calls(expected_calls)
        self.assertEqual(result, mock_data)
    
    def test_get_waveform_data_invalid_channel(self):
        """Test getting waveform data with invalid channel."""
        with self.assertRaises(ValueError) as context:
            self.mso.get_waveform_data(5, 'ASCII')
        
        self.assertIn("Channel must be 1, 2, 3, or 4", str(context.exception))
    
    def test_get_waveform_data_invalid_format(self):
        """Test getting waveform data with invalid format."""
        with self.assertRaises(ValueError) as context:
            self.mso.get_waveform_data(1, 'INVALID')
        
        self.assertIn("Data format must be 'ASCII' or 'BINARY'", str(context.exception))
    
    def test_get_multiple_waveforms(self):
        """Test getting waveforms from multiple channels."""
        mock_data = '1.0,2.0,3.0'
        self.mock_scope.query.return_value = mock_data
        
        result = self.mso.get_multiple_waveforms([1, 2])
        
        expected_result = {
            'CH1': [1.0, 2.0, 3.0],
            'CH2': [1.0, 2.0, 3.0]
        }
        
        self.assertEqual(result, expected_result)
    
    def test_get_multiple_waveforms_invalid_input(self):
        """Test getting multiple waveforms with invalid input."""
        with self.assertRaises(ValueError) as context:
            self.mso.get_multiple_waveforms(1)  # Should be a list
        
        self.assertIn("Channels must be a list", str(context.exception))
    
    def test_get_multiple_waveforms_invalid_channel(self):
        """Test getting multiple waveforms with invalid channel."""
        with self.assertRaises(ValueError) as context:
            self.mso.get_multiple_waveforms([1, 5])
        
        self.assertIn("Channel 5 must be 1, 2, 3, or 4", str(context.exception))
    
    @patch('csv.DictWriter')
    @patch('builtins.open')
    @patch('datetime.datetime')
    def test_save_waveforms_to_csv(self, mock_datetime, mock_open, mock_csv_writer):
        """Test saving waveforms to CSV file."""
        # Mock datetime
        mock_datetime.now.return_value.strftime.return_value = '20240722_120000'
        
        # Mock file operations
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        mock_writer = MagicMock()
        mock_csv_writer.return_value = mock_writer
        
        # Mock time scale query
        self.mock_scope.query.return_value = '1E-3'
        
        waveforms = {
            'CH1': [1.0, 2.0, 3.0],
            'CH2': [4.0, 5.0, 6.0]
        }
        
        result = self.mso.save_waveforms_to_csv(waveforms)
        
        self.assertEqual(result, 'waveforms_20240722_120000.csv')
        mock_open.assert_called_once()
        mock_csv_writer.assert_called_once()
        mock_writer.writeheader.assert_called_once()
        self.assertEqual(mock_writer.writerow.call_count, 3)  # 3 data points
    
    @patch('csv.DictWriter')
    @patch('builtins.open')
    def test_save_waveforms_to_csv_custom_filename(self, mock_open, mock_csv_writer):
        """Test saving waveforms to CSV with custom filename."""
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        mock_writer = MagicMock()
        mock_csv_writer.return_value = mock_writer
        
        self.mock_scope.query.return_value = '1E-3'
        
        waveforms = {'CH1': [1.0, 2.0]}
        custom_filename = 'custom_test.csv'
        
        result = self.mso.save_waveforms_to_csv(waveforms, custom_filename)
        
        self.assertEqual(result, custom_filename)
        mock_open.assert_called_with(custom_filename, 'w', newline='')
    
    @patch.object(MSO44B, 'wait_for_trigger')
    @patch.object(MSO44B, 'get_multiple_waveforms')
    @patch.object(MSO44B, 'save_waveforms_to_csv')
    @patch.object(MSO44B, 'single')
    def test_get_triggered_waveforms_and_save_success(self, mock_single, mock_save, 
                                                     mock_get_waveforms, mock_wait):
        """Test successful triggered waveform capture and save."""
        # Mock successful trigger wait
        mock_wait.return_value = True
        
        # Mock waveform data
        mock_waveforms = {'CH1': [1.0, 2.0, 3.0]}
        mock_get_waveforms.return_value = mock_waveforms
        
        # Mock save operation
        mock_save.return_value = 'test_file.csv'
        
        result = self.mso.get_triggered_waveforms_and_save([1])
        
        expected_result = {
            'waveforms': mock_waveforms,
            'filename': 'test_file.csv'
        }
        
        self.assertEqual(result, expected_result)
        mock_single.assert_called_once()
        mock_wait.assert_called_once_with(10)
        mock_get_waveforms.assert_called_once_with([1])
        mock_save.assert_called_once()
    
    @patch.object(MSO44B, 'wait_for_trigger')
    @patch.object(MSO44B, 'single')
    def test_get_triggered_waveforms_and_save_timeout(self, mock_single, mock_wait):
        """Test triggered waveform capture with timeout."""
        # Mock timeout
        mock_wait.return_value = False
        
        with self.assertRaises(TimeoutError) as context:
            self.mso.get_triggered_waveforms_and_save([1])
        
        self.assertIn("No trigger occurred within 10 seconds", str(context.exception))
    
    @patch.object(MSO44B, 'get_channel_state')
    @patch.object(MSO44B, 'get_triggered_waveforms_and_save')
    def test_get_all_active_waveforms_and_save(self, mock_get_triggered, mock_get_state):
        """Test getting waveforms from all active channels."""
        # Mock channel states - channels 1 and 3 are active
        mock_get_state.side_effect = ['1', '0', '1', '0']  # CH1=ON, CH2=OFF, CH3=ON, CH4=OFF
        
        mock_result = {'waveforms': {'CH1': [1.0], 'CH3': [2.0]}, 'filename': 'test.csv'}
        mock_get_triggered.return_value = mock_result
        
        result = self.mso.get_all_active_waveforms_and_save()
        
        self.assertEqual(result, mock_result)
        mock_get_triggered.assert_called_once_with([1, 3], None, 10)
    
    @patch.object(MSO44B, 'get_channel_state')
    def test_get_all_active_waveforms_no_active_channels(self, mock_get_state):
        """Test getting waveforms when no channels are active."""
        # Mock all channels as inactive
        mock_get_state.return_value = '0'
        
        with self.assertRaises(ValueError) as context:
            self.mso.get_all_active_waveforms_and_save()
        
        self.assertIn("No channels are currently active", str(context.exception))
    
    def test_is_complete(self):
        """Test operation completion check."""
        self.mock_scope.query.return_value = '1'
        
        result = self.mso.is_complete()
        
        self.mock_scope.query.assert_called_with('*OPC?')
        self.assertTrue(result)
    
    def test_close(self):
        """Test closing connection."""
        self.mso.close()
        
        self.mock_scope.close.assert_called_once()
        self.mock_rm.close.assert_called_once()
    
    def test_channel_validation_all_methods(self):
        """Test that all methods properly validate channel numbers."""
        invalid_channels = [0, 5, -1]
        
        # Methods that should validate channels
        channel_methods = [
            ('set_channel_scale', [1.0]),
            ('get_channel_scale', []),
            ('set_channel_coupling', ['DC']),
            ('get_channel_coupling', []),
            ('set_channel_state', ['ON']),
            ('get_channel_state', []),
            ('set_trigger', [0.5]),
            ('get_waveform_data', ['ASCII'])
        ]
        
        for channel in invalid_channels:
            for method_name, args in channel_methods:
                with self.assertRaises(ValueError):
                    method = getattr(self.mso, method_name)
                    method(channel, *args)


class TestMSO44BIntegration(unittest.TestCase):
    """Integration tests for MSO44B class."""
    
    def setUp(self):
        """Set up test fixtures for integration tests."""
        self.mock_rm = Mock()
        self.mock_scope = Mock()
        self.mock_rm.open_resource.return_value = self.mock_scope
        
        with patch('pyvisa.ResourceManager', return_value=self.mock_rm):
            self.mso = MSO44B(ip_address='192.168.1.100')
    
    def test_complete_oscilloscope_setup(self):
        """Test complete setup of oscilloscope with all parameters."""
        # Set up mock responses
        self.mock_scope.query.side_effect = [
            'TEKTRONIX,MSO44B,C012345,CF:91.1CT FV:1.26.6.37',  # device_id
            '1.0',    # get_channel_scale
            'DC',     # get_channel_coupling
            '1',      # get_channel_state
            '1E-3'    # get_time_scale
        ]
        
        # Verify device
        device_id = self.mso.device_id()
        self.assertIn('MSO44B', device_id)
        
        # Configure channel 1
        self.mso.set_channel_scale(1, 1.0)
        self.mso.set_channel_coupling(1, 'DC')
        self.mso.set_channel_state(1, 'ON')
        
        # Configure timebase
        self.mso.set_time_scale(1e-3)
        
        # Configure trigger
        self.mso.set_trigger(1, 0.5, 'RISING')
        
        # Verify settings
        self.assertEqual(self.mso.get_channel_scale(1), '1.0')
        self.assertEqual(self.mso.get_channel_coupling(1), 'DC')
        self.assertEqual(self.mso.get_channel_state(1), '1')
        self.assertEqual(self.mso.get_time_scale(), '1E-3')
        
        # Verify all write calls were made
        expected_writes = [
            'CH1:SCALE 1.0',
            'CH1:COUPLING DC',
            'CH1:STATE ON',
            'HOR:SCA 0.001',
            'TRIGGER:EDGE:SOURCE CH1',
            'TRIGGER:EDGE:LEVEL 0.5',
            'TRIGGER:EDGE:SLOPE RISING'
        ]
        
        actual_writes = [call.args[0] for call in self.mock_scope.write.call_args_list]
        self.assertEqual(actual_writes, expected_writes)
    
    @patch.object(MSO44B, 'wait_for_trigger')
    @patch('csv.DictWriter')
    @patch('builtins.open')
    @patch('datetime.datetime')
    def test_complete_measurement_workflow(self, mock_datetime, mock_open, 
                                         mock_csv_writer, mock_wait):
        """Test complete measurement workflow from setup to data acquisition."""
        # Setup mocks
        mock_datetime.now.return_value.strftime.return_value = '20240722_120000'
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        mock_writer = MagicMock()
        mock_csv_writer.return_value = mock_writer
        mock_wait.return_value = True
        
        # Mock scope responses
        self.mock_scope.query.side_effect = [
            '1',      # get_channel_state CH1
            '0',      # get_channel_state CH2
            '0',      # get_channel_state CH3
            '0',      # get_channel_state CH4
            '1E-3',   # get_time_scale for CSV
            '1.0,2.0,3.0,4.0,5.0'  # waveform data
        ]
        
        # Setup oscilloscope
        self.mso.set_channel_scale(1, 1.0)
        self.mso.set_channel_state(1, 'ON')
        self.mso.set_time_scale(1e-3)
        self.mso.set_trigger(1, 0.5)
        
        # Start acquisition and wait for trigger
        result = self.mso.get_all_active_waveforms_and_save()
        
        # Verify results
        self.assertIn('waveforms', result)
        self.assertIn('filename', result)
        self.assertIn('CH1', result['waveforms'])
        self.assertEqual(result['waveforms']['CH1'], [1.0, 2.0, 3.0, 4.0, 5.0])
        
        # Verify acquisition workflow
        expected_writes = [
            'CH1:SCALE 1.0',
            'CH1:STATE ON', 
            'HOR:SCA 0.001',
            'TRIGGER:EDGE:SOURCE CH1',
            'TRIGGER:EDGE:LEVEL 0.5',
            'TRIGGER:EDGE:SLOPE RISING',
            'ACQuire:STATE SINGLE',  # From single() call
            'DATa:SOUrce CH1',       # From get_waveform_data
            'DATa:ENCdg ASCii'       # From get_waveform_data
        ]
        
        actual_writes = [call.args[0] for call in self.mock_scope.write.call_args_list]
        self.assertEqual(actual_writes, expected_writes)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
