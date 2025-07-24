from AFG31000 import AFG31000
from MSO44B import SimpleMSO44B
from matplotlib import pyplot as plt
import numpy as np
from pyMSO4 import * # Use pyMSO4 library https://github.com/ceres-c/pyMSO4
class InstrumentTestExperiment:
    """A class to manage the AFG31000 and MSO44B instruments for testing purposes."""
    def __init__(self, afg_address, scope_address):
        self.afg = None
        self.scope = None 
    def afg_setup(self):
        """Set up the AFG31000 instrument.
        Enable output on channel 1, disable on channel 2, and set frequency to 100 kHz.
        Waveform type is set to RAMP, amplitude to 1 Vpp, and offset to 0 V.
        Phase is set to 90 degrees.
        The AFG31000 is reset before configuration.
        """
        # self.afg.reset()
        self.afg.set_output(1, 'OFF')  # Disable output on channel 1
        self.afg.set_output(2, 'OFF')
        self.afg.set_frequency(1, 100e3)  # 100 kHz
        self.afg.set_waveform(1, 'RAMP')
        self.afg.set_amplitude(1, 1.0)  # 1 Vpp
        self.afg.set_offset(1, 0.0)
        self.afg.set_phase(1, 90, 'DEG')  # Set phase to 90 degrees
        self.afg.set_output(1, 'ON')

def scope_setup():
    """Set up the MSO44B instrument.
    Using pyMSO4 library to configure the MSO44B.
    """
    scope = MSO4(trig_type=MSO4EdgeTrigger)  
    scope.con(ip="172.20.3.169") # TODO have a wrapper to automatically find the scope
    scope.trigger.source = 'ch2'  # Set trigger source to channel 2

    scope.ch_a_enable([True,True,True,False])  # Enable all channels
    channels = ['ch1', 'ch2','ch3']
    scope.acq.wfm_src = channels
    scope.acq.wfm_start = 0
    scope.acq.wfm_stop = 1000
    
    # Create subplot for multiple channels
    fig, axes = plt.subplots(len(channels), 1, figsize=(10, 8), sharex=True)
    if len(channels) == 1:
        axes = [axes]  # Make it iterable for single channel
    # Get waveform data for each channel
    for i, channel in enumerate(channels):  # Fixed missing colon
        scope.acq.wfm_src = [channel]  # Set single channel
        wfm = scope.sc.query_binary_values('CURVE?', datatype=scope.acq.get_datatype(), is_big_endian=scope.acq.is_big_endian)

        wfm_array = np.array(wfm)
        print(f"{channel} - Length: {len(wfm)}, Shape: {wfm_array.shape}, Type: {wfm_array.dtype}")
        print(f"{channel} - Min: {wfm_array.min():.4f}V, Max: {wfm_array.max():.4f}V")
        
        # Create time axis (assuming uniform sampling)
        time_axis = np.linspace(0, len(wfm_array)/1e6, len(wfm_array))  # Assuming 1MHz sampling
        
        # Plot waveform
        axes[i].plot(time_axis, wfm_array, label=channel)
        axes[i].set_ylabel(f'{channel} (V)')
        axes[i].grid(True, alpha=0.3)
        axes[i].legend()
        
        # Add statistics text
        mean_val = np.mean(wfm_array)
        std_val = np.std(wfm_array)
        axes[i].text(0.02, 0.95, f'Mean: {mean_val:.3f}V\nStd: {std_val:.3f}V', 
                    transform=axes[i].transAxes, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    axes[-1].set_xlabel('Time (s)')
    plt.suptitle('Oscilloscope Waveform Data')
    plt.tight_layout()
    plt.show()
        


def AFGTestManual():

    """Main function to run the instrument test experiment."""
    resource_name = "USB0::0x0699::0x035E::C019451::INSTR"  # Update this
    afg = AFG31000()
    """Set up the AFG31000 instrument.
    Enable output on channel 1, disable on channel 2, and set frequency to 100 kHz.
    Waveform type is set to RAMP, amplitude to 1 Vpp, and offset to 0 V.
    Phase is set to 90 degrees.
    The AFG31000 is reset before configuration.
    """
    # afg.reset()
    afg.set_output(1, 'OFF')  # Disable output on channel 1
    afg.set_output(2, 'OFF')
    afg.set_frequency(1, 100e3)  # 100 kHz
    afg.set_waveform_type(1, 'RAMP')
    afg.set_amplitude(1, 1.0)  # 1 Vpp
    afg.set_offset(1, 0.0)
    afg.set_phase(1, 90, 'DEG')  # Set phase to 90 degrees
    afg.set_output(1, 'OFF')

    print("AFG31000 setup complete.")
    # while True:
    #     pass  # Keep the script running to maintain the AFG31000 state
    
def simple_mso44b_test():
    """Test the SimpleMSO44B wrapper for easy waveform capture."""
    print("=== SimpleMSO44B Wrapper Test ===\n")
    
    with SimpleMSO44B() as scope:
        # Auto-connect to scope
        if not scope.connect():
            print("Failed to connect to MSO44B. Please check connection.")
            return
        
        # Setup trigger on channel 1, rising edge at 0.5V
        scope.setup_trigger(source_channel=1, level=0.5, slope='rising')
        
        # Capture waveforms from multiple channels
        print("Starting capture (waiting for trigger)...")
        results = scope.capture_waveforms(
            channels=[1, 2, 3], 
            filename="test_capture",
            plot=True, 
            save_csv=True
        )
        
        if results:
            print(f"\nCapture successful!")
            print(f"- Captured {results['sample_points']} points")
            print(f"- Channels: {results['channels']}")
            print(f"- CSV file: {results.get('csv_file', 'Not saved')}")
            print(f"- Plot file: {results.get('plot_file', 'Not saved')}")
            
            # Show some basic statistics
            waveforms = results['waveforms']
            for ch in results['channels']:
                ch_key = f'CH{ch}'
                if ch_key in waveforms:
                    data = np.array(waveforms[ch_key])
                    print(f"- {ch_key}: Mean={np.mean(data):.3f}V, Std={np.std(data):.3f}V")

def combined_test():
    """Combined test of AFG31000 and SimpleMSO44B for complete workflow."""
    print("=== Combined AFG31000 + SimpleMSO44B Test ===\n")
    
    # Setup AFG31000
    print("Setting up AFG31000...")
    afg = AFG31000()
    afg.set_output(1, 'OFF')
    afg.set_output(2, 'OFF')
    afg.set_frequency(1, 1000)  # 1 kHz for easy triggering
    afg.set_waveform_type(1, 'SQUare')
    afg.set_amplitude(1, 2.0)  # 2 Vpp
    afg.set_offset(1, 0.0)
    afg.set_output(1, 'ON')
    print("AFG31000 generating 1kHz square wave, 2Vpp")
    
    # Use SimpleMSO44B to capture
    with SimpleMSO44B() as scope:
        if scope.connect():
            # Setup trigger for the AFG signal
            scope.setup_trigger(source_channel=1, level=1.0, slope='rising')
            
            # Capture the generated waveform
            results = scope.capture_waveforms(
                channels=[1], 
                filename="afg_test_capture",
                plot=True,
                save_csv=True
            )
            
            if results:
                print("Successfully captured AFG-generated waveform!")
    
    # Turn off AFG
    afg.set_output(1, 'OFF')
    afg.close()
    print("Test complete.")

def instrument_discovery_test():
    """Test instrument discovery capabilities."""
    print("=== Instrument Discovery Test ===\n")
    
    print("1. Discovering all instruments:")
    all_instruments = SimpleMSO44B.list_all_instruments()
    
    print("\n2. Discovering MSO44/46 instruments specifically:")
    scope = SimpleMSO44B()
    mso_instruments = scope._discover_mso44_instruments()
    
    if mso_instruments:
        print(f"\nFound {len(mso_instruments)} MSO44/46 instrument(s) ready for connection.")
        
        # Test connection to first discovered instrument
        print("\n3. Testing connection to first discovered MSO44/46...")
        if scope.connect():
            print("✓ Connection successful!")
            scope.disconnect()
        else:
            print("✗ Connection failed.")
    else:
        print("\nNo MSO44/46 instruments found for connection test.")

def main():
    """Main function to run the instrument tests."""
    print("Choose test to run:")
    print("1. AFG31000 manual test")
    print("2. Original pyMSO4 scope test")  
    print("3. SimpleMSO44B wrapper test")
    print("4. Combined AFG + SimpleMSO44B test")
    print("5. Instrument discovery test")
    
    choice = input("Enter choice (1-5) or press Enter for SimpleMSO44B test: ").strip()
    
    if choice == '1':
        AFGTestManual()
    elif choice == '2':
        scope_setup()
    elif choice == '3' or choice == '':
        simple_mso44b_test()
    elif choice == '4':
        combined_test()
    elif choice == '5':
        instrument_discovery_test()
    else:
        print("Invalid choice. Running SimpleMSO44B test...")
        simple_mso44b_test()

if __name__ == "__main__":
    main()