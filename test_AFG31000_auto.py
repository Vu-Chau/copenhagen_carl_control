import unittest
import time
import sys
import os

# Add the current directory to the Python path for relative imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from AFG31000 import AFG31000

class TestAFG31000AutoDiscovery(unittest.TestCase):
    """Hardware-in-the-loop tests for AFG31000 auto-discovery functionality"""
    
    def setUp(self):
        """Set up the test - will try auto-discovery first, then fallback"""
        self.afg = None
        self.connected = False
        
        # First try auto-discovery
        try:
            print("\n=== Attempting auto-discovery ===")
            self.afg = AFG31000()  # No parameters - should auto-discover
            self.connected = True
            print("✓ Auto-discovery successful!")
        except Exception as e:
            print(f"✗ Auto-discovery failed: {e}")
            
            # Fallback to manual connection
            print("\n=== Attempting manual fallback ===")
            fallback_resources = [
                "USB0::0x0699::0x035E::C019451::INSTR",  # Common USB resource
                "TCPIP::192.168.1.100::INSTR",           # Common IP
                "ASRL1::INSTR",                          # Serial port
            ]
            
            for resource in fallback_resources:
                try:
                    print(f"Trying: {resource}")
                    self.afg = AFG31000(resource_name=resource)
                    self.connected = True
                    print(f"✓ Connected via fallback: {resource}")
                    break
                except Exception as fallback_error:
                    print(f"✗ Failed: {fallback_error}")
                    continue
                    continue
        
    def tearDown(self):
        """Clean up after each test"""
        if hasattr(self, 'afg') and self.afg:
            try:
                self.afg.close()
            except:
                pass
    
    def _require_connection(self):
        """Helper method to check if connection is available, skip test if not"""
        if not self.connected:
            self.skipTest("No AFG instrument available for testing")
    
    def test_instrument_discovery(self):
        """Test the static method to list all instruments"""
        print("\n=== Testing AFG31000.list_all_instruments() ===")
        try:
            instruments = AFG31000.list_all_instruments()
            self.assertIsInstance(instruments, list)
            
            afg_instruments = [instr for instr in instruments if instr.get('is_afg', False)]
            print(f"Found {len(afg_instruments)} AFG instrument(s) out of {len(instruments)} total")
            
            for afg in afg_instruments:
                print(f"  AFG: {afg['resource']} - {afg['device_id']}")
                
        except Exception as e:
            self.fail(f"Failed to list instruments: {e}")
    
    def test_auto_discovery_connection(self):
        """Test auto-discovery connection functionality"""
        if not self.connected:
            self.skipTest("No AFG instrument available for testing")
        
        print("\n=== Testing auto-discovery connection ===")
        
        # Test device identification
        try:
            device_id = self.afg.device_id()
            print(f"Device ID: {device_id}")
            self.assertIsInstance(device_id, str)
            self.assertTrue(len(device_id) > 0)
            
            # Test device ID validation (flexible check)
            is_afg = self.afg.check_device_id(strict=False)
            self.assertTrue(is_afg, "Device should be recognized as AFG instrument")
            
        except Exception as e:
            self.fail(f"Failed device identification: {e}")
    
    def test_connection(self):
        """Test if we can connect to the AFG31000"""
        if not self.connected:
            self.skipTest("No AFG instrument available for testing")
            
        try:
            device_id = self.afg.device_id()
            print(f"Connected to: {device_id}")
            
            # Test both strict and non-strict device ID checking
            is_any_afg = self.afg.check_device_id(strict=False)
            self.assertTrue(is_any_afg, "Should recognize any AFG instrument")
            
            # Try strict checking (may fail if not AFG31252)
            try:
                is_specific_afg = self.afg.check_device_id(strict=True)
                print(f"Strict AFG31252 check: {'PASS' if is_specific_afg else 'FAIL (different AFG model)'}")
            except:
                print("Strict checking failed - likely different AFG model")
                
        except Exception as e:
            self.fail(f"Failed to connect to AFG31000: {e}")
    
    def test_sine_wave_output(self):
        """Test generating a sine wave"""
        if not self.connected:
            self.skipTest("No AFG instrument available for testing")
            
        # Configure channel 1 for sine wave
        self.afg.set_waveform_type(1, "SINusoid")
        self.afg.set_frequency(1, 1000)  # 1 kHz
        self.afg.set_amplitude(1, 1.0)   # 1V amplitude
        self.afg.set_offset(1, 0.0)      # 0V offset
        
        # Enable output
        self.afg.set_output(1, True)
        
        # Allow time for signal to stabilize
        time.sleep(1)
        
        # Verify settings
        waveform = self.afg.get_waveform_type(1)
        frequency = self.afg.get_frequency(1)
        amplitude = self.afg.get_amplitude(1)
        
        self.assertIn("SIN", waveform)  # May return "SINusoid" or "SIN"
        self.assertAlmostEqual(frequency, 1000, delta=1)
        self.assertAlmostEqual(amplitude, 1.0, delta=0.01)
        
        print(f"Sine wave configured: {frequency} Hz, {amplitude} V")
    
    def test_square_wave_output(self):
        """Test generating a square wave"""
        self._require_connection()
        
        # Configure channel 2 for square wave
        self.afg.set_waveform_type(2, "SQUare")
        self.afg.set_frequency(2, 500)   # 500 Hz
        self.afg.set_amplitude(2, 2.0)   # 2V amplitude
        # Note: duty cycle may need a separate method if available
        
        # Enable output
        self.afg.set_output(2, True)
        
        time.sleep(1)
        
        # Verify settings
        waveform = self.afg.get_waveform_type(2)
        frequency = self.afg.get_frequency(2)
        amplitude = self.afg.get_amplitude(2)
        
        self.assertIn("SQU", waveform)  # May return "SQUare" or "SQU"
        self.assertAlmostEqual(frequency, 500, delta=1)
        self.assertAlmostEqual(amplitude, 2.0, delta=0.01)
        
        print(f"Square wave configured: {frequency} Hz, {amplitude} V")
    
    def test_frequency_sweep(self):
        """Test frequency sweep functionality"""
        self._require_connection()
        
        # Configure for frequency sweep
        self.afg.set_waveform_type(1, "SINusoid")
        self.afg.set_amplitude(1, 1.0)
        
        # Test different frequencies
        test_frequencies = [100, 1000, 10000, 100000]  # Hz
        
        for freq in test_frequencies:
            self.afg.set_frequency(1, freq)
            time.sleep(0.5)  # Allow time for frequency change
            
            actual_freq = self.afg.get_frequency(1)
            self.assertAlmostEqual(actual_freq, freq, delta=freq * 0.01)  # 1% tolerance
            print(f"Frequency set to: {actual_freq} Hz")
    
    def test_output_enable_disable(self):
        """Test enabling and disabling outputs with various input formats"""
        self._require_connection()
        
        print("Testing output enable/disable functionality:")
        
        # Test different ways to enable/disable outputs
        test_cases = [
            (True, "Boolean True"),
            (False, "Boolean False"),
            (1, "Integer 1"),
            (0, "Integer 0"),
            ('ON', "String 'ON'"),
            ('OFF', "String 'OFF'"),
            ('on', "String 'on' (lowercase)"),
            ('off', "String 'off' (lowercase)"),
        ]
        
        for channel in [1, 2]:
            print(f"  Testing Channel {channel}:")
            
            for state, description in test_cases:
                try:
                    # Set the output state
                    self.afg.set_output(channel, state)
                    time.sleep(0.1)
                    
                    # Read back the state
                    output_state = self.afg.get_output(channel).strip()
                    
                    # Determine expected result
                    if state in [True, 1, 'ON', 'on']:
                        expected_on = True
                        self.assertIn("1", output_state, f"Expected ON state, got: {output_state}")
                        print(f"    ✓ {description} -> ON (response: {output_state})")
                    else:
                        expected_on = False
                        self.assertIn("0", output_state, f"Expected OFF state, got: {output_state}")
                        print(f"    ✓ {description} -> OFF (response: {output_state})")
                        
                except Exception as e:
                    self.fail(f"Failed to set output {channel} with {description}: {e}")
        
        # Test that outputs start in known state
        print("  Verifying final state (both channels OFF):")
        for channel in [1, 2]:
            self.afg.set_output(channel, False)
            time.sleep(0.1)
            output_state = self.afg.get_output(channel)
            self.assertIn("0", output_state)
            print(f"    Channel {channel}: OFF")
        
        print("Output enable/disable test passed")
    
    def test_error_checking(self):
        """Test error handling and device status"""
        self._require_connection()
        
        # Clear any existing errors
        self.afg.write("*CLS")
        
        # Check for errors using SCPI command
        error_response = self.afg.query("SYSTEM:ERROR?")
        self.assertIn("0", error_response)  # Should return "0,No error" or similar
        
        # Test invalid parameter (this should generate an error)
        try:
            self.afg.set_frequency(1, -1000)  # Invalid negative frequency
        except ValueError:
            pass  # Expected behavior from our validation
        
        print("Error checking test completed")
    
    def test_phase_adjustment(self):
        """Test phase adjustment functionality"""
        self._require_connection()
        # Configure sine wave on channel 1
        self.afg.set_waveform_type(1, "SINusoid")
        self.afg.set_frequency(1, 1000)
        
        # Test phase setting and getting in degrees (default)
        test_phases_deg = [0, 90, 180, -90, 270]
        
        print("Testing phase in degrees (default):")
        for phase in test_phases_deg:
            # Test default behavior (degrees)
            self.afg.set_phase(1, phase)  # Default is degrees
            time.sleep(0.2)
            
            actual_phase = self.afg.get_phase(1)  # Default is degrees
            
            # Handle 360° wrapping (270° and -90° are equivalent)
            if phase == 270:
                self.assertTrue(abs(actual_phase - 270) < 2 or abs(actual_phase + 90) < 2,
                              f"Expected ~270° or ~-90°, got {actual_phase}°")
            else:
                self.assertAlmostEqual(actual_phase, phase, delta=2,
                                     msg=f"Phase mismatch: expected {phase}°, got {actual_phase}°")
            print(f"  Phase set to: {actual_phase:.1f}° for input {phase}°")
        
        # Test explicit degree specification
        print("Testing phase with explicit unit='DEG':")
        self.afg.set_phase(1, 45, unit='DEG')
        time.sleep(0.2)
        actual_phase = self.afg.get_phase(1, unit='DEG')
        self.assertAlmostEqual(actual_phase, 45, delta=2)
        print(f"  Phase set to: {actual_phase:.1f}° for input 45°")
        
        # Test phase setting and getting in radians
        import math
        test_phases_rad = [0, math.pi/2, math.pi, -math.pi/2, 3*math.pi/2]
        test_phases_rad_names = ["0", "π/2", "π", "-π/2", "3π/2"]
        
        print("Testing phase in radians:")
        for i, phase in enumerate(test_phases_rad):
            # Test using unit='RAD'
            self.afg.set_phase(1, phase, unit='RAD')
            time.sleep(0.2)
            
            actual_phase = self.afg.get_phase(1, unit='RAD')
            
            # Handle 2π wrapping
            if abs(phase) > math.pi:
                # Normalize to -π to π range for comparison
                expected_normalized = ((phase + math.pi) % (2 * math.pi)) - math.pi
                actual_normalized = ((actual_phase + math.pi) % (2 * math.pi)) - math.pi
                self.assertAlmostEqual(actual_normalized, expected_normalized, delta=0.1,
                                     msg=f"Phase mismatch: expected {expected_normalized:.3f} rad, got {actual_normalized:.3f} rad")
            else:
                self.assertAlmostEqual(actual_phase, phase, delta=0.1,
                                     msg=f"Phase mismatch: expected {phase:.3f} rad, got {actual_phase:.3f} rad")
            print(f"  Phase set to: {actual_phase:.3f} rad for input {test_phases_rad_names[i]} ({phase:.3f} rad)")
        
        # Test unit conversion consistency
        print("Testing unit conversion consistency:")
        # Set 60° and read in both units
        self.afg.set_phase(1, 60)  # Default degrees
        time.sleep(0.2)
        actual_deg = self.afg.get_phase(1)  # Default degrees
        actual_rad = self.afg.get_phase(1, unit='RAD')
        
        self.assertAlmostEqual(actual_deg, 60, delta=2)
        self.assertAlmostEqual(actual_rad, math.pi/3, delta=0.1)
        print(f"  60° = {actual_deg:.1f}° = {actual_rad:.3f} rad (expected π/3 = {math.pi/3:.3f})")
        
        # Set π/4 rad and read in both units
        self.afg.set_phase(1, math.pi/4, unit='RAD')
        time.sleep(0.2)
        actual_deg = self.afg.get_phase(1)  # Default degrees
        actual_rad = self.afg.get_phase(1, unit='RAD')
        
        self.assertAlmostEqual(actual_deg, 45, delta=2)
        self.assertAlmostEqual(actual_rad, math.pi/4, delta=0.1)
        print(f"  π/4 rad = {actual_deg:.1f}° = {actual_rad:.3f} rad (expected 45°)")
    
    def test_load_impedance(self):
        """Test load impedance settings"""
        self._require_connection()
        
        # Test setting different load impedances
        test_loads = [
            ("50", 50),                      # Numeric string (common)
            ("75", 75),                      # Numeric string (common)
            ("1", 1),                        # Minimum as string
            ("10000", 10000),                # Maximum as string
            ("INFinity", None),              # High impedance (special case)
            ("HIGHZ", None),                 # High impedance alias (special case)
            ("MINimum", 1),                  # Minimum keyword
            ("MAXimum", 10000),              # Maximum keyword
            (50, 50),                       # Numeric value (common)
            (1, 1),                         # Minimum numeric
            (10000, 10000),                 # Maximum numeric
            (5000, 5000),                   # Mid-range numeric
        ]
        
        for test_value, expected_value in test_loads:
            try:
                self.afg.set_load(1, test_value)
                time.sleep(0.2)
                
                actual_load_str = self.afg.get_load(1).strip()
                
                if expected_value is None:
                    # For INFinity/HIGHZ, check for high impedance (>10k Ohms)
                    try:
                        actual_value = float(actual_load_str)
                        self.assertGreater(actual_value, 10000,
                                         f"Expected high impedance (>10k Ohms), got: {actual_value}")
                        print(f"Load impedance '{test_value}' set successfully (high impedance): {actual_load_str} ({actual_value:.2e} Ohms)")
                    except ValueError:
                        # If parsing fails, check for string indicators
                        self.assertTrue(
                            any(indicator in actual_load_str.upper() for indicator in ["INF", "HIGH"]),
                            f"Expected high impedance indicator or >10k value, got: {actual_load_str}"
                        )
                        print(f"Load impedance '{test_value}' set successfully (high impedance string): {actual_load_str}")
                else:
                    # Parse the returned value (could be in scientific notation)
                    try:
                        actual_value = float(actual_load_str)
                        self.assertAlmostEqual(actual_value, expected_value, delta=1,
                                             msg=f"Expected {expected_value}, got {actual_value}")
                        print(f"Load impedance '{test_value}' set successfully: {actual_load_str} (parsed as {actual_value})")
                    except ValueError:
                        # If parsing fails, fall back to string comparison
                        self.assertIn(str(expected_value), actual_load_str.replace("E", "e"),
                                    f"Expected {expected_value} in response, got: {actual_load_str}")
                        print(f"Load impedance '{test_value}' set successfully (string match): {actual_load_str}")
                        
            except Exception as e:
                self.fail(f"Failed to set load impedance '{test_value}': {e}")
    
    def test_load_impedance_validation(self):
        """Test load impedance input validation"""
        self._require_connection()
        
        # Test invalid numeric values
        invalid_values = [-1, 0, 10001, 15000]
        
        for invalid_value in invalid_values:
            with self.assertRaises(ValueError):
                self.afg.set_load(1, invalid_value)
                print(f"Correctly rejected invalid load: {invalid_value}")
        
        # Test invalid numeric strings
        invalid_numeric_strings = ["-1", "0", "10001", "15000", "-50"]
        
        for invalid_string in invalid_numeric_strings:
            with self.assertRaises(ValueError):
                self.afg.set_load(1, invalid_string)
                print(f"Correctly rejected invalid numeric string: {invalid_string}")
        
        # Test invalid non-numeric strings
        invalid_strings = ["INVALID", "50K", "HIGH", "LOW", "abc", "fifty"]
        
        for invalid_string in invalid_strings:
            with self.assertRaises(ValueError):
                self.afg.set_load(1, invalid_string)
                print(f"Correctly rejected invalid string: {invalid_string}")
        
        print("Load impedance validation test passed")
    
    def test_frequency_lock(self):
        """Test frequency lock functionality"""
        self._require_connection()
        
        # Test enabling frequency lock
        self.afg.set_frequency_lock(True)
        lock_state = self.afg.get_frequency_lock()
        self.assertIn("1", lock_state)  # Device may return "1" for ON
        
        # Test disabling frequency lock
        self.afg.set_frequency_lock(False)
        lock_state = self.afg.get_frequency_lock()
        self.assertIn("0", lock_state)  # Device may return "0" for OFF
        
        print("Frequency lock test passed")

def run_discovery_test():
    """Standalone function to test instrument discovery without full test suite"""
    print("=== Standalone AFG Instrument Discovery Test ===")
    
    # Test 1: List all instruments
    print("\n1. Listing all available instruments:")
    try:
        instruments = AFG31000.list_all_instruments()
        afg_instruments = [instr for instr in instruments if instr.get('is_afg', False)]
        print(f"Summary: {len(afg_instruments)} AFG instruments found out of {len(instruments)} total")
    except Exception as e:
        print(f"Error listing instruments: {e}")
        return False
    
    # Test 2: Auto-discovery
    print("\n2. Testing auto-discovery:")
    try:
        afg = AFG31000()  # Auto-discover
        device_id = afg.device_id()
        print(f"✓ Auto-discovery successful!")
        print(f"  Connected to: {device_id}")
        print(f"  Resource: {afg.resource_name}")
        
        # Test basic functionality
        afg.check_device_id(strict=False)
        
        afg.close()
        return True
    except Exception as e:
        print(f"✗ Auto-discovery failed: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='AFG31000 Auto-Discovery Tests')
    parser.add_argument('--discovery-only', action='store_true', 
                       help='Run only the discovery test (faster)')
    
    args = parser.parse_args()
    
    if args.discovery_only:
        success = run_discovery_test()
        sys.exit(0 if success else 1)
    else:
        # Run full test suite with verbose output
        unittest.main(verbosity=2)