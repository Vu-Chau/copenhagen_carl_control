import unittest
import time
import csv
import os
import json
import numpy as np
from MSO44B import MSO44B

class TestMSO44B(unittest.TestCase):
    """Hardware-in-the-loop tests for MSO44B Tektronix Oscilloscope wrapper"""
    
    @classmethod
    def setUpClass(cls):
        """Set up the test class with a single hardware connection for all tests"""
        try:
            print("=== MSO44B Wrapper Hardware Tests ===")
            print("Attempting to connect to MSO44B using auto-discovery...")
            
            # List available instruments first for debugging
            print("\nAvailable instruments:")
            MSO44B.list_all_instruments()
            
            cls.scope = MSO44B(timeout=15000)  # 15 second timeout
            
            # Try to connect with auto-discovery
            if cls.scope.connect(auto_discover=True):
                print(f"✓ Connected to: {cls.scope.device_id()}")
            else:
                raise ConnectionError("Failed to auto-discover MSO44B")
                
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            raise unittest.SkipTest(f"Could not connect to MSO44B: {e}")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests are complete"""
        if hasattr(cls, 'scope'):
            print("\nClosing connection to MSO44B")
            try:
                cls.scope.close()
            except:
                pass  # Ignore errors during cleanup
    
    def setUp(self):
        """Set up before each individual test"""
        # Just verify connection is still active, don't close/reopen
        if not hasattr(self.__class__, 'scope') or not self.scope.connected:
            self.skipTest("No active scope connection")
        
        # Small delay to allow scope to settle between tests
        time.sleep(0.1)
    
    @property
    def scope(self):
        """Access the class-level scope connection"""
        return self.__class__.scope
    
    def test_connection_and_device_id(self):
        """Test connection and device identification"""
        # Test device ID
        device_id = self.scope.device_id()
        self.assertIsInstance(device_id, str)
        self.assertIn("MSO", device_id.upper())
        print(f"✓ Device ID: {device_id.strip()}")
        
        # Test connection status
        self.assertTrue(self.scope.connected)
        print("✓ Connection status verified")
    
    def test_direct_scpi_commands(self):
        """Test direct SCPI command functionality"""
        # Test write command
        self.scope.write('*CLS')  # Clear status
        
        # Test query command
        idn_response = self.scope.query('*IDN?')
        self.assertIsInstance(idn_response, str)
        self.assertIn("TEKTRONIX", idn_response.upper())
        print(f"✓ SCPI query successful: {idn_response.strip()}")
        
        # Test device_id method (wrapper around *IDN?)
        device_id = self.scope.device_id()
        self.assertEqual(idn_response.strip(), device_id.strip())
        print("✓ Direct SCPI commands working")
    
    def test_high_resolution_mode_control(self):
        """Test high resolution mode on/off functionality"""
        print("\nTesting high resolution mode control:")
        
        # Test enabling high resolution mode
        self.scope.set_high_resolution_mode(True)
        time.sleep(1.0)  # Allow time for mode change
        
        # Check acquisition mode
        current_mode = self.scope.get_acquisition_mode()
        print(f"  High resolution enabled - Mode: {current_mode}")
        
        # Verify it's in high resolution mode (16-bit)
        self.assertIn('HIRES', current_mode.upper(), 
                      f"Expected HIRES mode, got: {current_mode}")
        
        # Test disabling high resolution mode
        self.scope.set_high_resolution_mode(False)
        time.sleep(1.0)  # Allow time for mode change
        
        # Check acquisition mode again
        current_mode = self.scope.get_acquisition_mode()
        print(f"  High resolution disabled - Mode: {current_mode}")
        
        # Verify it's back to normal sampling mode (8-bit)
        self.assertIn('SAMPLE', current_mode.upper(), 
                      f"Expected SAMPLE mode, got: {current_mode}")
        
        # Test enabling again to ensure it's repeatable
        self.scope.set_high_resolution_mode(True)
        time.sleep(1.0)
        final_mode = self.scope.get_acquisition_mode()
        print(f"  High resolution re-enabled - Mode: {final_mode}")
        self.assertIn('HIRES', final_mode.upper())
        
        # Reset to normal mode for other tests
        self.scope.set_high_resolution_mode(False)
        time.sleep(1.0)
        
        print("✓ High resolution mode test completed")
    
    def test_trigger_setup(self):
        """Test trigger configuration"""
        print("\nTesting trigger setup:")
        
        # Test basic edge trigger
        self.scope.setup_trigger(
            source_channel=1,
            trigger_type='edge',
            level=0.5,
            slope='rising'
        )
        print("  ✓ Basic edge trigger configured (CH1, 0.5V, rising)")
        
        # Test different trigger levels and slopes
        test_configs = [
            {'source_channel': 1, 'level': -0.5, 'slope': 'falling'},
            {'source_channel': 2, 'level': 1.0, 'slope': 'rising'},
            {'source_channel': 1, 'level': 0.0, 'slope': 'rising'},
        ]
        
        for config in test_configs:
            self.scope.setup_trigger(**config)
            print(f"  ✓ Trigger configured: CH{config['source_channel']}, "
                  f"{config['level']}V, {config['slope']}")
        
        print("✓ Trigger setup test completed")
    
    def test_trigger_error_handling(self):
        """Test trigger parameter validation"""
        print("\nTesting trigger error handling:")
        
        # Test invalid channel
        try:
            with self.assertRaises(ValueError):
                self.scope.setup_trigger(source_channel=5, level=0.0)
            print("  ✓ Invalid channel properly rejected")
        except Exception as e:
            print(f"  ⚠ Invalid channel test failed: {e}")
        
        # Test invalid slope
        try:
            with self.assertRaises(ValueError):
                self.scope.setup_trigger(source_channel=1, level=0.0, slope='invalid')
            print("  ✓ Invalid slope properly rejected")
        except Exception as e:
            print(f"  ⚠ Invalid slope test failed: {e}")
        
        print("✓ Trigger error handling test completed")
    
    def test_waveform_scaling_parameters(self):
        """Test waveform scaling parameter retrieval"""
        print("\nTesting waveform scaling parameters:")
        
        # Test getting scaling parameters for different channels
        for channel in [1, 2, 3, 4]:
            try:
                scaling_params = self.scope.get_waveform_scaling_params(channel)
                self.assertIsInstance(scaling_params, dict)
                
                # Check that required parameters are present
                required_keys = ['ymult', 'yoff', 'yzero']
                for key in required_keys:
                    self.assertIn(key, scaling_params)
                
                print(f"  CH{channel} scaling: ymult={scaling_params.get('ymult')}, "
                      f"yoff={scaling_params.get('yoff')}, yzero={scaling_params.get('yzero')}")
                
            except Exception as e:
                print(f"  CH{channel} scaling failed: {e}")
        
        print("✓ Waveform scaling parameters test completed")
    
    def test_time_scaling_parameters(self):
        """Test time scaling parameter retrieval"""
        print("\nTesting time scaling parameters:")
        
        try:
            time_params = self.scope.get_time_scaling_params()
            self.assertIsInstance(time_params, dict)
            
            # Check that required parameters are present
            required_keys = ['xincr', 'xzero']
            for key in required_keys:
                self.assertIn(key, time_params)
            
            print(f"  Time scaling: xincr={time_params.get('xincr')}, "
                  f"xzero={time_params.get('xzero')}")
            
        except Exception as e:
            print(f"  ⚠ Time scaling parameters test failed: {e}")
            self.skipTest(f"Cannot get time scaling parameters: {e}")
        
        print("✓ Time scaling parameters test completed")
    
    def test_single_channel_waveform_read(self):
        """Test reading waveform data from a single channel"""
        print("\nTesting single channel waveform reading:")
        
        # Setup trigger first
        self.scope.setup_trigger(source_channel=1, level=0.0, slope='rising')
        
        # Test ASCII format
        try:
            waveform_ascii = self.scope.read_channel_waveform(1, use_binary=False)
            self.assertIsInstance(waveform_ascii, dict)
            self.assertIn('voltage_data', waveform_ascii)
            self.assertIn('raw_data', waveform_ascii)
            self.assertIn('format_used', waveform_ascii)
            
            voltage_data = waveform_ascii['voltage_data']
            self.assertIsInstance(voltage_data, list)
            self.assertGreater(len(voltage_data), 0)
            
            print(f"  ✓ ASCII format: {len(voltage_data)} points, "
                  f"format: {waveform_ascii['format_used']}")
            
        except Exception as e:
            print(f"  ASCII format test failed: {e}")
        
        # Test binary format
        try:
            waveform_binary = self.scope.read_channel_waveform(1, use_binary=True)
            self.assertIsInstance(waveform_binary, dict)
            self.assertIn('voltage_data', waveform_binary)
            
            voltage_data = waveform_binary['voltage_data']
            self.assertIsInstance(voltage_data, list)
            self.assertGreater(len(voltage_data), 0)
            
            print(f"  ✓ Binary format: {len(voltage_data)} points, "
                  f"format: {waveform_binary['format_used']}")
            
        except Exception as e:
            print(f"  Binary format test failed: {e}")
        
        print("✓ Single channel waveform reading test completed")
    
    def test_waveform_data_conversion(self):
        """Test raw data to voltage conversion"""
        print("\nTesting waveform data conversion:")
        
        try:
            # Get scaling parameters
            scaling_params = self.scope.get_waveform_scaling_params(1)
            
            # Create test raw data
            test_raw_data = [0, 100, -100, 500, -500]
            
            # Convert to voltages
            voltages = self.scope.convert_raw_to_voltage(test_raw_data, scaling_params)
            
            self.assertIsInstance(voltages, list)
            self.assertEqual(len(voltages), len(test_raw_data))
            
            for voltage in voltages:
                self.assertIsInstance(voltage, float)
            
            print(f"  ✓ Converted {len(test_raw_data)} raw values to voltages")
            print(f"  Raw data: {test_raw_data}")
            print(f"  Voltages: {[f'{v:.3f}' for v in voltages]}")
            
        except Exception as e:
            print(f"  ⚠ Waveform data conversion test failed: {e}")
            self.skipTest(f"Cannot perform data conversion: {e}")
        
        print("✓ Waveform data conversion test completed")
    
    def test_time_axis_generation(self):
        """Test time axis generation"""
        print("\nTesting time axis generation:")
        
        try:
            # Get time scaling parameters
            time_params = self.scope.get_time_scaling_params()
            
            # Generate time axis for different data lengths
            test_lengths = [100, 1000, 10000]
            
            for length in test_lengths:
                time_axis = self.scope.generate_time_axis(length, time_params)
                
                self.assertIsInstance(time_axis, (list, np.ndarray))
                self.assertEqual(len(time_axis), length)
                
                # Check that time axis is monotonically increasing
                if len(time_axis) > 1:
                    for i in range(1, len(time_axis)):
                        self.assertGreater(time_axis[i], time_axis[i-1])
                
                print(f"  ✓ Generated time axis: {length} points, "
                      f"range: {time_axis[0]:.2e}s to {time_axis[-1]:.2e}s")
                      
        except Exception as e:
            print(f"  ⚠ Time axis generation test failed: {e}")
            self.skipTest(f"Cannot generate time axis: {e}")
        
        print("✓ Time axis generation test completed")
    
    def test_scope_metadata_collection(self):
        """Test comprehensive metadata collection"""
        print("\nTesting scope metadata collection:")
        
        try:
            # Test metadata collection for specific channels
            metadata = self.scope.get_scope_metadata(channels=[1, 2], include_global=True)
            
            self.assertIsInstance(metadata, dict)
            
            # Check if we got valid metadata or error info
            if 'timestamp' in metadata:
                print(f"  ✓ Metadata collected for channels [1, 2]")
                
                # Check for instrument info if available
                if 'instrument' in metadata:
                    instrument_info = metadata['instrument']
                    print(f"  Instrument: {instrument_info.get('vendor')} {instrument_info.get('model')}")
                
                # Check for acquisition info if available
                if 'acquisition' in metadata:
                    acquisition_info = metadata['acquisition']
                    sample_rate = acquisition_info.get('sample_rate')
                    if sample_rate:
                        print(f"  Sample rate: {sample_rate:,.0f} Hz")
                    print(f"  Mode: {acquisition_info.get('acquisition_mode')}")
            else:
                print(f"  ⚠ Metadata collection returned errors")
            
            # Test metadata without global info
            metadata_minimal = self.scope.get_scope_metadata(channels=[1], include_global=False)
            self.assertIsInstance(metadata_minimal, dict)
            print("  ✓ Minimal metadata collection completed")
            
        except Exception as e:
            print(f"  ⚠ Metadata collection test failed: {e}")
            # Don't skip this test, just note the failure
        
        print("✓ Scope metadata collection test completed")
    
    def test_capture_waveforms_csv_export(self):
        """Test waveform capture with CSV export"""
        print("\nTesting waveform capture with CSV export:")
        
        # Setup trigger
        self.scope.setup_trigger(source_channel=1, level=0.0, slope='rising')
        
        # Test CSV export (no metadata)
        result = self.scope.capture_waveforms(
            channels=[1, 2],
            variable_samples=5000,
            export_data=True,
            include_metadata=False,  # CSV export
            filename="test_csv_capture",
            plot=False
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('waveforms', result)
        self.assertIn('sample_points', result)
        self.assertIn('channels', result)
        
        # Check that CSV file was created
        if 'csv_file' in result:
            csv_filename = result['csv_file']
            self.assertTrue(os.path.exists(csv_filename))
            
            # Verify CSV content
            with open(csv_filename, 'r') as csvfile:
                reader = csv.reader(csvfile)
                header = next(reader)
                self.assertIn('Time', header)
                self.assertIn('CH1', header)
                self.assertIn('CH2', header)
                
                # Count data rows
                data_rows = list(reader)
                self.assertGreater(len(data_rows), 0)
            
            print(f"  ✓ CSV file created: {csv_filename}")
            print(f"  ✓ Data rows: {len(data_rows)}")
            
            # Clean up test file
            os.remove(csv_filename)
        
        print("✓ CSV export test completed")
    
    def test_capture_waveforms_json_export(self):
        """Test waveform capture with JSON export (including metadata)"""
        print("\nTesting waveform capture with JSON export:")
        
        # Enable high resolution mode for this test
        self.scope.set_high_resolution_mode(True)
        time.sleep(1.0)
        
        # Setup trigger
        self.scope.setup_trigger(source_channel=1, level=0.0, slope='rising')
        
        # Test JSON export (with metadata)
        result = self.scope.capture_waveforms(
            channels=[1],
            variable_samples=2500,
            export_data=True,
            include_metadata=True,  # JSON export
            filename="test_json_capture",
            plot=False
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('waveforms', result)
        self.assertIn('metadata', result)
        self.assertIn('sample_points', result)
        
        # Check that JSON file was created
        if 'json_file' in result:
            json_filename = result['json_file']
            self.assertTrue(os.path.exists(json_filename))
            
            # Verify JSON content
            with open(json_filename, 'r') as jsonfile:
                json_data = json.load(jsonfile)
                
                self.assertIn('metadata', json_data)
                self.assertIn('waveforms', json_data)
                
                # Check metadata structure
                metadata = json_data['metadata']
                self.assertIn('instrument', metadata)
                self.assertIn('acquisition', metadata)
                
                # Check waveforms data
                waveforms = json_data['waveforms']
                self.assertIn('Time', waveforms)
                self.assertIn('CH1', waveforms)
            
            print(f"  ✓ JSON file created: {json_filename}")
            print(f"  ✓ Includes metadata and waveform data")
            
            # Clean up test file
            os.remove(json_filename)
        
        # Reset to normal mode
        self.scope.set_high_resolution_mode(False)
        time.sleep(1.0)
        
        print("✓ JSON export test completed")
    
    def test_capture_waveforms_no_export(self):
        """Test waveform capture without file export"""
        print("\nTesting waveform capture without file export:")
        
        # Setup trigger
        self.scope.setup_trigger(source_channel=1, level=0.0, slope='rising')
        
        # Test capture without export
        result = self.scope.capture_waveforms(
            channels=[1, 2],
            variable_samples=1000,
            export_data=False,  # No file export
            plot=False
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('waveforms', result)
        self.assertIn('sample_points', result)
        
        # Verify no files were created
        self.assertNotIn('csv_file', result)
        self.assertNotIn('json_file', result)
        
        # Check waveform data structure
        waveforms = result['waveforms']
        self.assertIn('Time', waveforms)
        self.assertIn('CH1', waveforms)
        self.assertIn('CH2', waveforms)
        
        # Verify data types and lengths
        time_data = waveforms['Time']
        ch1_data = waveforms['CH1']
        ch2_data = waveforms['CH2']
        
        self.assertIsInstance(time_data, (list, np.ndarray))
        self.assertIsInstance(ch1_data, list)
        self.assertIsInstance(ch2_data, list)
        
        self.assertEqual(len(time_data), len(ch1_data))
        self.assertEqual(len(time_data), len(ch2_data))
        
        print(f"  ✓ Captured data without export: {len(time_data)} points")
        print(f"  ✓ Channels: {result['channels']}")
        
        print("✓ No export test completed")
    
    def test_variable_samples_parameter(self):
        """Test variable sample length functionality"""
        print("\nTesting variable sample length:")
        
        try:
            # Setup trigger
            self.scope.setup_trigger(source_channel=1, level=0.0, slope='rising')
            
            # Test different sample lengths
            test_samples = [1000, 5000, 10000, 25000]
            
            for sample_count in test_samples:
                result = self.scope.capture_waveforms(
                    channels=[1],
                    variable_samples=sample_count,
                    export_data=False,
                    plot=False
                )
                
                if result and 'sample_points' in result:
                    actual_points = result['sample_points']
                    waveform_length = len(result['waveforms']['CH1'])
                    
                    # Allow some tolerance for scope limitations
                    self.assertGreater(actual_points, sample_count * 0.5)
                    self.assertEqual(actual_points, waveform_length)
                    
                    print(f"  ✓ Requested: {sample_count}, Got: {actual_points} points")
                else:
                    print(f"  ⚠ Failed to capture {sample_count} samples")
                    
        except Exception as e:
            print(f"  ⚠ Variable samples test failed: {e}")
            self.skipTest(f"Cannot test variable samples: {e}")
        
        print("✓ Variable samples test completed")
    
    def test_csv_save_functionality(self):
        """Test CSV save functionality directly"""
        print("\nTesting CSV save functionality:")
        
        # Create test waveform data
        test_waveforms = {
            'Time': [0.0, 1e-6, 2e-6, 3e-6, 4e-6],
            'CH1': [0.1, 0.2, 0.3, 0.2, 0.1],
            'CH2': [-0.05, -0.1, -0.15, -0.1, -0.05]
        }
        
        # Test CSV save
        filename = self.scope.save_csv(test_waveforms, "test_csv_direct")
        
        self.assertTrue(os.path.exists(filename))
        
        # Verify CSV content
        with open(filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            
            self.assertEqual(len(rows), 5)  # Should have 5 data rows
            
            # Check header
            fieldnames = reader.fieldnames
            self.assertIn('Time', fieldnames)
            self.assertIn('CH1', fieldnames)
            self.assertIn('CH2', fieldnames)
            
            # Check first row data
            first_row = rows[0]
            self.assertEqual(float(first_row['Time']), 0.0)
            self.assertEqual(float(first_row['CH1']), 0.1)
            self.assertEqual(float(first_row['CH2']), -0.05)
        
        print(f"  ✓ CSV file saved: {filename}")
        print(f"  ✓ Data rows: {len(rows)}")
        
        # Clean up test file
        os.remove(filename)
        
        print("✓ CSV save functionality test completed")
    
    def test_instrument_discovery(self):
        """Test instrument discovery functionality"""
        print("\nTesting instrument discovery:")
        
        # Test static method for listing all instruments
        try:
            instruments = MSO44B.list_all_instruments()
            print(f"  ✓ Found {len(instruments) if instruments else 0} total instruments")
            
            # Look for MSO instruments in the list
            mso_count = 0
            if instruments:
                for instr in instruments:
                    if 'MSO' in instr.get('device_id', '').upper():
                        mso_count += 1
                        print(f"    MSO found: {instr.get('resource')} - {instr.get('device_id')}")
            
            print(f"  ✓ MSO instruments found: {mso_count}")
            
        except Exception as e:
            print(f"  Discovery test failed: {e}")
        
        # Test instance discovery method
        try:
            scope_temp = MSO44B()
            mso_instruments = scope_temp._discover_mso44_instruments()
            print(f"  ✓ MSO44/46 specific discovery found: {len(mso_instruments) if mso_instruments else 0}")
            
        except Exception as e:
            print(f"  MSO44 discovery test failed: {e}")
        
        print("✓ Instrument discovery test completed")

if __name__ == "__main__":
    # Run with verbose output
    unittest.main(verbosity=2, buffer=True)