from AFG31000 import AFG31000
from MSO44B import MSO44B
from matplotlib import pyplot as plt
import numpy as np
from pyMSO4 import *


class InstrumentExamples:
    """Examples demonstrating how to use the AFG31000 and MSO44B drivers."""
    
    def __init__(self):
        pass 
    def afg_basic_example(self):
        """Example: Basic AFG31000 configuration."""
        print("=== AFG31000 Basic Configuration Example ===")
        afg = AFG31000()
        afg.set_output(1, 'OFF')
        afg.set_output(2, 'OFF') 
        afg.set_frequency(1, 100e3)  # 100 kHz
        afg.set_waveform_type(1, 'RAMP')
        afg.set_amplitude(1, 1.0)  # 1 Vpp
        afg.set_offset(1, 0.0)
        afg.set_phase(1, 90, 'DEG')
        afg.set_output(1, 'ON')
        print("AFG configured: 100kHz ramp, 1Vpp, 90° phase")
        afg.close()
    
    def mso_raw_pyMSO4_example(self):
        """Example: Raw pyMSO4 usage for comparison."""
        print("=== Raw pyMSO4 Example ===")
        scope = MSO4(trig_type=MSO4EdgeTrigger)
        scope.con(ip="172.20.3.169")
        scope.trigger.source = 'ch2'
        scope.ch_a_enable([True, True, True, False])
        
        channels = ['ch1', 'ch2', 'ch3']
        scope.acq.wfm_src = channels
        scope.acq.wfm_start = 0
        scope.acq.wfm_stop = 1000
        
        fig, axes = plt.subplots(len(channels), 1, figsize=(10, 8), sharex=True)
        if len(channels) == 1: axes = [axes]
        
        for i, channel in enumerate(channels):
            scope.acq.wfm_src = [channel]
            wfm = scope.sc.query_binary_values('CURVE?', datatype=scope.acq.get_datatype(), 
                                             is_big_endian=scope.acq.is_big_endian)
            wfm_array = np.array(wfm)
            time_axis = np.linspace(0, len(wfm_array)/1e6, len(wfm_array))
            
            axes[i].plot(time_axis, wfm_array, label=channel)
            axes[i].set_ylabel(f'{channel} (V)')
            axes[i].grid(True, alpha=0.3)
            
        axes[-1].set_xlabel('Time (s)')
        plt.suptitle('Raw pyMSO4 Capture')
        plt.tight_layout()
        plt.show()
        scope.dis()
    
    def mso_simple_wrapper_example(self):
        """Example: MSO44B wrapper usage."""
        print("=== MSO44B Wrapper Example ===")
        with MSO44B() as scope:
            if not scope.connect():
                print("Failed to connect")
                return
            scope.setup_trigger(source_channel=1, level=0.5, slope='rising')
            results = scope.capture_waveforms(channels=[1, 2, 3], filename="example_capture")
            if results:
                print(f"Captured {results['sample_points']} points from {results['channels']}")
                for ch in results['channels']:
                    data = np.array(results['waveforms'][f'CH{ch}'])
                    print(f"CH{ch}: Mean={np.mean(data):.3f}V, Std={np.std(data):.3f}V")

    def combined_afg_mso_example(self):
        """Example: Combined AFG31000 + MSO44B workflow."""
        print("=== Combined AFG + MSO Example ===")
        afg = None
        try:
            afg = AFG31000()
            afg.set_output(1, 'OFF')
            afg.set_frequency(1, 1000)  # 1 kHz
            afg.set_waveform_type(1, 'SQUare')
            afg.set_amplitude(1, 2.0)  # 2 Vpp
            afg.set_load(1, '50')
            afg.set_output(1, 'ON')
            print("AFG: 1kHz square wave, 2Vpp")
            
            with MSO44B() as scope:
                if scope.connect():
                    scope.setup_trigger(source_channel=2, level=0.5, slope='rising')
                    results = scope.capture_waveforms(channels=[1,2,3], filename="combined_capture")
                    if results:
                        print("Successfully captured AFG signal!")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            if afg:
                try:
                    afg.set_output(1, 'OFF')
                    afg.close()
                except: pass

    def instrument_discovery_example(self):
        """Example: Instrument discovery and connection."""
        print("=== Instrument Discovery Example ===")
        MSO44B.list_all_instruments()
        scope = MSO44B()
        mso_instruments = scope._discover_mso44_instruments()
        if mso_instruments and scope.connect():
            print("✓ Auto-discovery and connection successful!")
            scope.disconnect()
        else:
            print("✗ No MSO44/46 found or connection failed")

    def reusable_methods_example(self):
        """Example: Using individual reusable methods."""
        print("=== Reusable Methods Example ===")
        with MSO44B() as scope:
            if not scope.connect(): return
            scope.setup_trigger(source_channel=1, level=0.0, slope='rising')
            try:
                result = scope.read_channel_waveform(1)
                print(f"Raw points: {len(result['raw_data'])}")
                print(f"Voltage points: {len(result['voltage_data'])}")
                print(f"Sample voltages: {result['voltage_data'][:3]}")
                
                time_params = scope.get_time_scaling_params()
                time_axis = scope.generate_time_axis(len(result['voltage_data']), time_params)
                print(f"Time range: {time_axis[0]:.2e}s to {time_axis[-1]:.2e}s")
            except Exception as e:
                print(f"Error: {e}")

    def ascii_vs_binary_example(self):
        """Example: Compare ASCII vs binary data accuracy."""
        print("=== ASCII vs Binary Comparison Example ===")
        with MSO44B() as scope:
            if not scope.connect(): return
            scope.setup_trigger(source_channel=1, level=0.0, slope='rising')
            try:
                ascii_result = scope.read_channel_waveform(1, use_binary=False)
                binary_result = scope.read_channel_waveform(1, use_binary=True)
                
                ascii_volt = ascii_result['voltage_data'][:5]
                binary_volt = binary_result['voltage_data'][:5]
                
                print(f"ASCII:  {ascii_volt}")
                print(f"Binary: {binary_volt}")
                
                if len(ascii_volt) == len(binary_volt):
                    differences = [abs(a - b) for a, b in zip(ascii_volt, binary_volt)]
                    max_diff = max(differences) if differences else 0
                    print(f"Max difference: {max_diff:.2e} V")
                    if max_diff < 1e-6:
                        print("✓ Negligible difference")
                    else:
                        print("⚠ Consider binary format for higher precision")
            except Exception as e:
                print(f"Error: {e}")

def main():
    """Run instrument driver examples."""
    examples = InstrumentExamples()
    
    menu = {
        '1': ('AFG31000 Basic Example', examples.afg_basic_example),
        '2': ('Raw pyMSO4 Example', examples.mso_raw_pyMSO4_example),
        '3': ('MSO44B Wrapper Example', examples.mso_simple_wrapper_example),
        '4': ('Combined AFG + MSO Example', examples.combined_afg_mso_example),
        '5': ('Instrument Discovery Example', examples.instrument_discovery_example),
        '6': ('Reusable Methods Example', examples.reusable_methods_example),
        '7': ('ASCII vs Binary Example', examples.ascii_vs_binary_example),
    }
    
    print("Instrument Driver Examples:")
    for key, (desc, _) in menu.items():
        print(f"{key}. {desc}")
    
    choice = input("Enter choice (1-7) or press Enter for default: ").strip()
    
    if choice in menu:
        _, method = menu[choice]
        method()
    else:
        print("Running default MSO44B example...")
        examples.mso_simple_wrapper_example()

if __name__ == "__main__":
    main()