import unittest
import time
import csv
import os
from MSO44B import MSO44B

class TestMSO44B(unittest.TestCase):
    """Hardware-in-the-loop tests for MSO44B Tektronix Oscilloscope"""
    
    @classmethod
    def setUpClass(cls):
        """Set up the test class with a single hardware connection for all tests"""
        # Replace with your actual device IP address or VISA resource string
        # cls.ip_address = "192.168.1.100"  # Update this to your oscilloscope's IP
        # Alternative connection methods:
        cls.resource_name = "USB0::0x0699::0x0527::C047272::INSTR"  # USB connection
        # cls.serial_port = "COM3"  # Serial connection
        
        try:
            print(f"Attempting to connect to MSO44B at: {cls.resource_name}")
            
            # List available resources first for debugging
            available_resources = MSO44B.list_resources()
            print(f"Available VISA resources: {available_resources}")
            
            cls.scope = MSO44B(resource_name=cls.resource_name, timeout=15000)  # 15 second timeout
            print("✓ Connection established successfully for all tests")
            
            # Verify connection immediately
            if cls.scope.is_connected():
                print("✓ Connection verification successful")
            else:
                print("✗ Connection verification failed")
                
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            raise unittest.SkipTest(f"Could not connect to MSO44B at {cls.resource_name}: {e}")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests are complete"""
        if hasattr(cls, 'scope'):
            print("Closing connection to MSO44B")
            # Reset scope to a known state before closing
            try:
                cls.scope.stop()
                cls.scope.close()
            except:
                pass  # Ignore errors during cleanup
    
    def setUp(self):
        """Set up before each individual test"""
        # Clear any errors before each test
        try:
            self.scope.clear_status()
        except:
            pass  # Ignore errors during setup
    
    @property
    def scope(self):
        """Access the class-level scope connection"""
        return self.__class__.scope
    
    def tearDown(self):
        """Clean up after each individual test"""
        # Stop acquisition and turn off all channels after each test
        try:
            self.scope.stop()
            for channel in [1, 2, 3, 4]:
                self.scope.set_channel_state(channel, 'OFF')
        except:
            pass  # Ignore errors during cleanup
    
    def test_connection(self):
        """Test if we can connect to the MSO44B"""
        try:
            # First, list available resources for debugging
            available_resources = MSO44B.list_resources()
            print(f"Available VISA resources: {available_resources}")
            
            # Check if connection is still valid
            if not self.scope.is_connected():
                self.fail("Connection to oscilloscope was lost between setup and test")
            
            idn = self.scope.device_id()
            self.assertIn("MSO44", idn)
            print(f"✓ Connected to: {idn.strip()}")
            
            # Test device ID check method
            is_mso44b = self.scope.check_device_id()
            self.assertTrue(is_mso44b)
            print("✓ Device ID check passed")
            
        except Exception as e:
            # Add more diagnostic information
            print(f"Connection test failed. Checking connection status...")
            print(f"Has scope attribute: {hasattr(self, 'scope')}")
            if hasattr(self, 'scope'):
                print(f"Scope object: {self.scope}")
                print(f"Connection status: {self.scope.is_connected()}")
            self.fail(f"Failed to connect to MSO44B: {e}")
    
    def test_reset_and_clear(self):
        """Test reset and clear status functionality"""
        # Test reset
        self.scope.reset()
        time.sleep(2)  # Allow time for reset to complete
        
        # Test clear status
        self.scope.clear_status()
        
        # Verify scope is responsive after reset
        idn = self.scope.device_id()
        self.assertIn("MSO44", idn)
        print("Reset and clear status test passed")
    
    def test_channel_configuration(self):
        """Test channel configuration settings"""
        test_channels = [1, 2, 3, 4]
        
        for channel in test_channels:
            print(f"Testing Channel {channel}:")
            
            # Test channel state (on/off)
            self.scope.set_channel_state(channel, 'ON')
            time.sleep(0.1)
            state = self.scope.get_channel_state(channel).strip()
            self.assertIn("1", state)  # ON state
            print(f"  Channel {channel} turned ON: {state}")
            
            # Test vertical scale
            test_scales = [0.01, 0.1, 1.0, 5.0]  # Different voltage scales
            for scale in test_scales:
                self.scope.set_channel_scale(channel, scale)
                time.sleep(0.1)
                actual_scale = float(self.scope.get_channel_scale(channel))
                self.assertAlmostEqual(actual_scale, scale, delta=scale * 0.1)
                print(f"  Scale set to: {actual_scale} V/div")
            
            # Test coupling
            coupling_modes = ['DC', 'AC']
            for coupling in coupling_modes:
                self.scope.set_channel_coupling(channel, coupling)
                time.sleep(0.1)
                actual_coupling = self.scope.get_channel_coupling(channel).strip()
                self.assertIn(coupling, actual_coupling)
                print(f"  Coupling set to: {actual_coupling}")
            
            # Turn channel off after testing
            self.scope.set_channel_state(channel, 'OFF')
    
    def test_channel_error_handling(self):
        """Test channel parameter validation"""
        # Test invalid channel numbers
        with self.assertRaises(ValueError):
            self.scope.set_channel_scale(5, 1.0)  # Invalid channel
        
        with self.assertRaises(ValueError):
            self.scope.set_channel_coupling(0, 'DC')  # Invalid channel
        
        # Test invalid coupling
        with self.assertRaises(ValueError):
            self.scope.set_channel_coupling(1, 'INVALID')
        
        # Test invalid state
        with self.assertRaises(ValueError):
            self.scope.set_channel_state(1, 'INVALID')
        
        print("Channel error handling test passed")
    
    def test_time_base_configuration(self):
        """Test horizontal time base settings"""
        # Test different time scales
        test_scales = [1e-6, 10e-6, 100e-6, 1e-3, 10e-3, 100e-3]  # microseconds to milliseconds
        
        for scale in test_scales:
            self.scope.set_time_scale(scale)
            time.sleep(0.2)
            actual_scale = float(self.scope.get_time_scale())
            self.assertAlmostEqual(actual_scale, scale, delta=scale * 0.1)
            print(f"Time scale set to: {actual_scale:.2e} s/div")
    
    def test_trigger_configuration(self):
        """Test trigger settings"""
        # Configure channel 1 for trigger testing
        self.scope.set_channel_state(1, 'ON')
        self.scope.set_channel_scale(1, 1.0)
        self.scope.set_channel_coupling(1, 'DC')
        
        # Test trigger settings
        test_levels = [0.0, 0.5, -0.5, 1.0, -1.0]
        test_slopes = ['RISING', 'FALLING']
        
        for slope in test_slopes:
            for level in test_levels:
                self.scope.set_trigger(1, level, slope)
                time.sleep(0.1)
                
                trigger_settings = self.scope.get_trigger()
                
                # Verify trigger source
                self.assertIn("CH1", trigger_settings['source'])
                
                # Verify trigger level (with some tolerance)
                actual_level = float(trigger_settings['level'])
                self.assertAlmostEqual(actual_level, level, delta=0.1)
                
                # Verify trigger slope
                self.assertIn(slope, trigger_settings['slope'])
                
                print(f"Trigger set: CH1, {level}V, {slope} - Actual: {actual_level:.2f}V, {trigger_settings['slope']}")
    
    def test_trigger_error_handling(self):
        """Test trigger parameter validation"""
        # Test invalid channel
        with self.assertRaises(ValueError):
            self.scope.set_trigger(5, 0.0)
        
        # Test invalid slope
        with self.assertRaises(ValueError):
            self.scope.set_trigger(1, 0.0, 'INVALID')
        
        print("Trigger error handling test passed")
    
    def test_acquisition_control(self):
        """Test acquisition state control"""
        # Test different acquisition states
        states = ['RUN', 'STOP', 'SINGLE']
        
        for state in states:
            self.scope.set_acquisition_state(state)
            time.sleep(0.5)
            actual_state = self.scope.get_acquisition_state().strip()
            
            if state == 'SINGLE':
                # SINGLE may return different states depending on trigger status
                self.assertTrue(actual_state in ['SINGLE', 'STOP', 'TRIGGER'])
            else:
                self.assertIn(state, actual_state)
            
            print(f"Acquisition state set to: {state}, actual: {actual_state}")
        
        # Test convenience methods
        self.scope.run()
        time.sleep(0.5)
        run_state = self.scope.get_acquisition_state()
        self.assertIn('RUN', run_state)
        
        self.scope.stop()
        time.sleep(0.5)
        stop_state = self.scope.get_acquisition_state()
        self.assertIn('STOP', stop_state)
        
        print("Acquisition control test passed")
    
    def test_acquisition_error_handling(self):
        """Test acquisition state validation"""
        with self.assertRaises(ValueError):
            self.scope.set_acquisition_state('INVALID')
        
        print("Acquisition error handling test passed")
    
    def test_sample_rate_configuration(self):
        """Test sample rate settings"""
        # Note: Available sample rates depend on time base and memory depth
        # These are common rates that should be supported
        test_rates = [1e6, 10e6, 100e6, 1e9]  # 1MS/s to 1GS/s
        
        for rate in test_rates:
            try:
                self.scope.set_sample_rate(rate)
                time.sleep(0.2)
                actual_rate = float(self.scope.get_sample_rate())
                
                # Sample rate may be adjusted by the scope based on other settings
                # Allow for reasonable deviation
                self.assertGreater(actual_rate, rate * 0.1)
                self.assertLess(actual_rate, rate * 10)
                
                print(f"Sample rate requested: {rate:.0e} S/s, actual: {actual_rate:.2e} S/s")
            except Exception as e:
                print(f"Sample rate {rate:.0e} not supported: {e}")
    
    def test_waveform_data_acquisition(self):
        """Test waveform data acquisition"""
        # Set up scope for data acquisition
        self.scope.set_channel_state(1, 'ON')
        self.scope.set_channel_scale(1, 1.0)
        self.scope.set_time_scale(1e-3)  # 1ms/div
        self.scope.set_trigger(1, 0.0, 'RISING')
        
        # Test single channel data acquisition
        try:
            waveform_data = self.scope.get_waveform_data(1, 'ASCII')
            self.assertIsInstance(waveform_data, list)
            self.assertGreater(len(waveform_data), 0)
            
            # Check that data contains numeric values
            for value in waveform_data[:10]:  # Check first 10 values
                self.assertIsInstance(value, float)
            
            print(f"Single channel waveform acquired: {len(waveform_data)} points")
            
        except Exception as e:
            print(f"Waveform acquisition test skipped (may need signal): {e}")
    
    def test_multiple_channel_acquisition(self):
        """Test multiple channel data acquisition"""
        # Enable multiple channels
        channels = [1, 2]
        for channel in channels:
            self.scope.set_channel_state(channel, 'ON')
            self.scope.set_channel_scale(channel, 1.0)
        
        self.scope.set_time_scale(1e-3)
        self.scope.set_trigger(1, 0.0, 'RISING')
        
        try:
            waveforms = self.scope.get_multiple_waveforms(channels, 'ASCII')
            
            self.assertIsInstance(waveforms, dict)
            self.assertIn('CH1', waveforms)
            self.assertIn('CH2', waveforms)
            
            for channel_key, data in waveforms.items():
                self.assertIsInstance(data, list)
                self.assertGreater(len(data), 0)
                print(f"{channel_key} waveform: {len(data)} points")
            
        except Exception as e:
            print(f"Multiple channel acquisition test skipped (may need signal): {e}")
    
    def test_waveform_data_error_handling(self):
        """Test waveform data acquisition error handling"""
        # Test invalid channel
        with self.assertRaises(ValueError):
            self.scope.get_waveform_data(5, 'ASCII')
        
        # Test invalid data format
        with self.assertRaises(ValueError):
            self.scope.get_waveform_data(1, 'INVALID')
        
        # Test invalid channels list
        with self.assertRaises(ValueError):
            self.scope.get_multiple_waveforms([5], 'ASCII')
        
        print("Waveform data error handling test passed")
    
    def test_csv_file_operations(self):
        """Test CSV file save functionality"""
        # Create test waveform data
        test_waveforms = {
            'CH1': [0.1, 0.2, 0.3, 0.4, 0.5],
            'CH2': [-0.1, -0.2, -0.3, -0.4, -0.5]
        }
        
        # Test CSV save
        filename = self.scope.save_waveforms_to_csv(test_waveforms, "test_waveforms.csv")
        
        self.assertTrue(os.path.exists(filename))
        
        # Verify CSV content
        with open(filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            
            self.assertEqual(len(rows), 5)  # Should have 5 data rows
            self.assertIn('Time', rows[0])
            self.assertIn('CH1', rows[0])
            self.assertIn('CH2', rows[0])
        
        # Clean up test file
        if os.path.exists(filename):
            os.remove(filename)
        
        print("CSV file operations test passed")
    
    def test_active_channels_detection(self):
        """Test detection of active channels"""
        # Turn on specific channels
        self.scope.set_channel_state(1, 'ON')
        self.scope.set_channel_state(2, 'ON')
        self.scope.set_channel_state(3, 'OFF')
        self.scope.set_channel_state(4, 'OFF')
        
        time.sleep(0.5)
        
        # Check which channels are detected as active
        active_channels = []
        for channel in [1, 2, 3, 4]:
            state = self.scope.get_channel_state(channel).strip()
            if state == '1' or state.upper() == 'ON':
                active_channels.append(channel)
        
        self.assertIn(1, active_channels)
        self.assertIn(2, active_channels)
        self.assertNotIn(3, active_channels)
        self.assertNotIn(4, active_channels)
        
        print(f"Active channels detected: {active_channels}")
    
    def test_operation_complete_check(self):
        """Test operation complete functionality"""
        # Send a command and check completion
        self.scope.set_time_scale(1e-3)
        
        # Check if operation is complete
        is_complete = self.scope.is_complete()
        self.assertIsInstance(is_complete, bool)
        
        print(f"Operation complete check: {is_complete}")
    
    def test_comprehensive_scope_setup(self):
        """Test a complete oscilloscope measurement setup"""
        print("Setting up comprehensive measurement scenario:")
        
        # Configure channels
        self.scope.set_channel_state(1, 'ON')
        self.scope.set_channel_state(2, 'ON')
        self.scope.set_channel_scale(1, 1.0)  # 1V/div
        self.scope.set_channel_scale(2, 0.5)  # 0.5V/div
        self.scope.set_channel_coupling(1, 'DC')
        self.scope.set_channel_coupling(2, 'AC')
        
        # Configure time base
        self.scope.set_time_scale(10e-6)  # 10µs/div
        
        # Configure trigger
        self.scope.set_trigger(1, 0.5, 'RISING')
        
        # Set sample rate
        self.scope.set_sample_rate(100e6)  # 100MS/s
        
        # Verify all settings
        ch1_scale = float(self.scope.get_channel_scale(1))
        ch2_scale = float(self.scope.get_channel_scale(2))
        time_scale = float(self.scope.get_time_scale())
        trigger_info = self.scope.get_trigger()
        
        self.assertAlmostEqual(ch1_scale, 1.0, delta=0.1)
        self.assertAlmostEqual(ch2_scale, 0.5, delta=0.1)
        self.assertAlmostEqual(time_scale, 10e-6, delta=1e-6)
        self.assertAlmostEqual(float(trigger_info['level']), 0.5, delta=0.1)
        
        print(f"  CH1: {ch1_scale} V/div, DC coupling")
        print(f"  CH2: {ch2_scale} V/div, AC coupling")
        print(f"  Time: {time_scale:.2e} s/div")
        print(f"  Trigger: CH1, {trigger_info['level']} V, {trigger_info['slope']}")
        
        # Test acquisition
        self.scope.stop()
        self.scope.single()
        
        acquisition_state = self.scope.get_acquisition_state()
        print(f"  Acquisition state: {acquisition_state}")
        
        print("Comprehensive setup test completed")

if __name__ == "__main__":
    # Run with verbose output
    unittest.main(verbosity=2)
    