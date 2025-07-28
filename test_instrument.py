from AFG31000 import AFG31000
from MSO44B import MSO44B
import matplotlib.pyplot as plt
import numpy as np
import json


class InstrumentExamples:
    """Examples demonstrating how to use the AFG31000 and MSO44B drivers."""
    
    def __init__(self):
        pass 
    def afg_basic_example(self):
        """Example: Basic AFG31000 configuration with automatic discovery."""
        print("=== AFG31000 Basic Configuration Example ===")
        try:
            # Use automatic discovery (consistent with MSO44B)
            afg = AFG31000()  # Auto-discovers AFG instruments
            print(f"Connected to: {afg.device_id()}")
            
            # Configure channel 1
            afg.set_output(1, 'OFF')
            afg.set_frequency(1, 100e3)  # 100 kHz
            afg.set_waveform_type(1, 'RAMP')
            afg.set_amplitude(1, 1.0)  # 1 Vpp
            afg.set_offset(1, 0.0)
            afg.set_phase(1, 90, 'DEG')
            afg.set_output(1, 'ON')
            
            print("✓ AFG configured: 100kHz ramp, 1Vpp, 90° phase")
            afg.close()
            
        except Exception as e:
            print(f"✗ AFG configuration failed: {e}")
    
    def mso_capture_with_metadata_example(self):
        """Example: MSO44B capture with metadata and JSON export."""
        print("=== MSO44B Capture with Metadata Example ===")
        try:
            # Use consistent pattern with AFG - direct instantiation
            scope = MSO44B()
            if not scope.connect():
                print("✗ Failed to connect to scope")
                return
            
            print(f"Connected to: {scope.device_id()}")
            
            # Enable high resolution mode for better precision
            scope.set_high_resolution_mode(True)
            print(f"Acquisition mode: {scope.get_acquisition_mode()}")
            
            # Configure trigger
            scope.setup_trigger(source_channel=1, level=0.5, slope='rising')
            
            # Capture with metadata and JSON export
            result = scope.capture_waveforms(
                channels=[1, 2], 
                variable_samples=50000,
                export_data=True,
                include_metadata=True,  # Exports as JSON
                filename="metadata_capture"
            )
            
            if result:
                print(f"✓ Captured {result['sample_points']} points from channels {result['channels']}")
                print(f"✓ Data exported to: {result.get('json_file', 'N/A')}")
                
                # Display metadata summary
                if 'metadata' in result:
                    metadata = result['metadata']
                    print(f"Sample rate: {metadata['acquisition']['sample_rate']:,.0f} Hz")
                    print(f"Timebase: {metadata['acquisition']['timebase_scale']:.2e} s/div")
                    print(f"Trigger: {metadata['trigger']['source']} @ {metadata['trigger']['level']}V")
            
            scope.close()
                
        except Exception as e:
            print(f"✗ Metadata capture failed: {e}")
            try:
                scope.close()
            except:
                pass
    
    def mso_simple_wrapper_example(self):
        """Example: MSO44B wrapper usage with CSV export."""
        print("=== MSO44B Simple Wrapper Example ===")
        try:
            scope = MSO44B()
            if not scope.connect():
                print("✗ Failed to connect to scope")
                return
            
            print(f"Connected to: {scope.device_id()}")
            
            # Configure trigger
            scope.setup_trigger(source_channel=1, level=0.5, slope='rising')
            
            # Simple capture with CSV export (no metadata)
            result = scope.capture_waveforms(
                channels=[1, 2, 3], 
                variable_samples=10000,
                export_data=True,
                include_metadata=False,  # Exports as CSV
                filename="simple_capture"
            )
            
            if result:
                print(f"✓ Captured {result['sample_points']} points from channels {result['channels']}")
                print(f"✓ Data exported to: {result.get('csv_file', 'N/A')}")
                
                # Display basic statistics
                for ch in result['channels']:
                    data = np.array(result['waveforms'][f'CH{ch}'])
                    print(f"CH{ch}: Mean={np.mean(data):.3f}V, Std={np.std(data):.3f}V")
            
            scope.close()
            
        except Exception as e:
            print(f"✗ Simple capture failed: {e}")
            try:
                scope.close()  
            except:
                pass

    def combined_afg_mso_example(self):
        """Example: Combined AFG31000 + MSO44B workflow."""
        print("=== Combined AFG + MSO Example ===")
        afg = None
        scope = None
        try:
            # Configure AFG31000
            afg = AFG31000()
            print(f"AFG connected: {afg.device_id()}")
            
            afg.set_output(1, 'OFF')
            afg.set_frequency(1, 1000)  # 1 kHz
            afg.set_waveform_type(1, 'SQUare')
            afg.set_amplitude(1, 2.0)  # 2 Vpp
            afg.set_load(1, '50')
            afg.set_output(1, 'ON')
            print("✓ AFG configured: 1kHz square wave, 2Vpp")
            
            # Configure MSO44B
            scope = MSO44B()
            if not scope.connect():
                print("✗ Failed to connect to scope")
                return
            
            print(f"Scope connected: {scope.device_id()}")
            scope.setup_trigger(source_channel=2, level=0.5, slope='rising')
            
            # Capture with variable samples
            result = scope.capture_waveforms(
                channels=[1, 2, 3], 
                variable_samples=25000,
                export_data=True,
                include_metadata=True,  # JSON with metadata
                filename="combined_capture"
            )
            
            if result:
                print("✓ Successfully captured AFG signal!")
                print(f"✓ Captured {result['sample_points']} points")
                
        except Exception as e:
            print(f"✗ Combined example failed: {e}")
        finally:
            # Clean up both instruments
            if afg:
                try:
                    afg.set_output(1, 'OFF')
                    afg.close()
                except: 
                    pass
            if scope:
                try:
                    scope.close()
                except:
                    pass

    def instrument_discovery_example(self):
        """Example: Instrument discovery and connection."""
        print("=== Instrument Discovery Example ===")
        
        # Show all available instruments
        print("\n--- All Available Instruments ---")
        MSO44B.list_all_instruments()
        
        # Test AFG discovery
        print("\n--- AFG31000 Auto-Discovery ---")
        try:
            AFG31000.list_all_instruments()
        except Exception as e:
            print(f"AFG discovery error: {e}")
        
        # Test MSO discovery and connection
        print("\n--- MSO44B Auto-Discovery ---")
        try:
            scope = MSO44B()
            mso_instruments = scope._discover_mso44_instruments()
            if mso_instruments and scope.connect():
                print("✓ Auto-discovery and connection successful!")
                print(f"Connected to: {scope.device_id()}")
                scope.close()
            else:
                print("✗ No MSO44/46 found or connection failed")
        except Exception as e:
            print(f"MSO discovery error: {e}")

    def reusable_methods_example(self):
        """Example: Using individual reusable methods and metadata collection."""
        print("=== Reusable Methods Example ===")
        try:
            scope = MSO44B()
            if not scope.connect():
                print("✗ Failed to connect to scope")
                return
            
            print(f"Connected to: {scope.device_id()}")
            scope.setup_trigger(source_channel=1, level=0.0, slope='rising')
            
            # Use individual methods
            result = scope.read_channel_waveform(1)
            print(f"✓ Raw points: {len(result['raw_data'])}")
            print(f"✓ Voltage points: {len(result['voltage_data'])}")
            print(f"Sample voltages: {result['voltage_data'][:3]}")
            
            # Generate time axis
            time_params = scope.get_time_scaling_params()
            time_axis = scope.generate_time_axis(len(result['voltage_data']), time_params)
            print(f"Time range: {time_axis[0]:.2e}s to {time_axis[-1]:.2e}s")
            
            # Get metadata without capturing
            metadata = scope.get_scope_metadata(channels=[1], include_global=True)
            print(f"Current mode: {metadata['acquisition']['acquisition_mode']}")
            print(f"Sample rate: {metadata['acquisition']['sample_rate']:,.0f} Hz")
            
            scope.close()
            
        except Exception as e:
            print(f"✗ Reusable methods example failed: {e}")
            try:
                scope.close()
            except:
                pass

    def ascii_vs_binary_example(self):
        """Example: Compare ASCII vs binary data accuracy and demonstrate SCPI access."""
        print("=== ASCII vs Binary + SCPI Access Example ===")
        try:
            scope = MSO44B()
            if not scope.connect():
                print("✗ Failed to connect to scope")
                return
            
            print(f"Connected to: {scope.device_id()}")
            scope.setup_trigger(source_channel=1, level=0.0, slope='rising')
            
            # Compare ASCII vs Binary data formats
            ascii_result = scope.read_channel_waveform(1, use_binary=False)
            binary_result = scope.read_channel_waveform(1, use_binary=True)
            
            ascii_volt = ascii_result['voltage_data'][:5]
            binary_volt = binary_result['voltage_data'][:5]
            
            print(f"ASCII format:  {ascii_volt}")
            print(f"Binary format: {binary_volt}")
            
            if len(ascii_volt) == len(binary_volt):
                differences = [abs(a - b) for a, b in zip(ascii_volt, binary_volt)]
                max_diff = max(differences) if differences else 0
                print(f"Max difference: {max_diff:.2e} V")
                if max_diff < 1e-6:
                    print("✓ Negligible difference")
                else:
                    print("⚠ Consider binary format for higher precision")
            
            # Demonstrate direct SCPI access
            print("\n--- Direct SCPI Commands ---")
            ch1_scale = scope.query('CH1:SCALE?')
            ch1_pos = scope.query('CH1:POSITION?')
            print(f"CH1 Scale: {ch1_scale}")
            print(f"CH1 Position: {ch1_pos}")
            
            # Set and verify a parameter
            scope.write('CH1:SCALE 0.1')
            new_scale = scope.query('CH1:SCALE?')
            print(f"New CH1 Scale: {new_scale}")
            
            scope.close()
            
        except Exception as e:
            print(f"✗ ASCII vs Binary example failed: {e}")
            try:
                scope.close()
            except:
                pass

def main():
    """Run instrument driver examples."""
    examples = InstrumentExamples()
    
    menu = {
        '1': ('AFG31000 Basic Configuration', examples.afg_basic_example),
        '2': ('MSO44B Capture with Metadata (JSON)', examples.mso_capture_with_metadata_example),
        '3': ('MSO44B Simple Capture (CSV)', examples.mso_simple_wrapper_example),
        '4': ('Combined AFG + MSO Workflow', examples.combined_afg_mso_example),
        '5': ('Instrument Auto-Discovery', examples.instrument_discovery_example),
        '6': ('Individual Methods + Metadata', examples.reusable_methods_example),
        '7': ('ASCII vs Binary + SCPI Commands', examples.ascii_vs_binary_example),
    }
    
    print("Instrument Driver Examples:")
    for key, (desc, _) in menu.items():
        print(f"{key}. {desc}")
    
    choice = input("Enter choice (1-7) or press Enter for default: ").strip()
    
    if choice in menu:
        _, method = menu[choice]
        method()
    else:
        print("Running default MSO44B capture example...")
        examples.mso_capture_with_metadata_example()

if __name__ == "__main__":
    main()