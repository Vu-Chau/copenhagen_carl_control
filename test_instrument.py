from AFG31000 import AFG31000
from matplotlib import pyplot as plt
import numpy as np
# from MSO44B import MSO44B
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
    
def main():
    """Main function to run the AFG31000 manual test."""
    AFGTestManual()
    scope_setup()
if __name__ == "__main__":
    main()