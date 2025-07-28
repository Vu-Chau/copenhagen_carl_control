Usage Examples
==============

This page shows complete examples for common measurement scenarios.

Basic Signal Generation
-----------------------

Generate a 1 kHz square wave:

.. code-block:: python

   from AFG31000 import AFG31000

   afg = AFG31000()
   afg.set_frequency(1, 1000)        # 1 kHz
   afg.set_waveform_type(1, 'SQUare')
   afg.set_amplitude(1, 2.0)         # 2 Vpp
   afg.set_load(1, 50)               # 50Ω load
   afg.set_output(1, 'ON')
   
   print("Generating 1kHz square wave, 2Vpp into 50Ω")
   # Signal is now active
   
   afg.set_output(1, 'OFF')  # Turn off when done
   afg.close()

Basic Signal Capture
--------------------

Capture waveforms with JSON metadata export:

.. code-block:: python

   from MSO44B import MSO44B

   scope = MSO44B()
   if not scope.connect():
       print("No oscilloscope found")
       return
   
   # Enable high resolution mode
   scope.set_high_resolution_mode(True)
   print(f"Acquisition mode: {scope.get_acquisition_mode()}")
   
   # Setup trigger
   scope.setup_trigger(
       source_channel=1,
       level=0.5,           # 0.5V trigger level
       slope='rising'
   )
   
   # Capture with metadata (JSON export)
   result = scope.capture_waveforms(
       channels=[1, 2, 3],
       variable_samples=25000,   # Custom sample count
       export_data=True,
       include_metadata=True,    # JSON with complete metadata
       filename="my_measurement"
   )
   
   if result:
       print(f"Captured {result['sample_points']} points")
       print(f"JSON file: {result.get('json_file', 'N/A')}")
       
       # Display metadata summary
       if 'metadata' in result:
           metadata = result['metadata']
           print(f"Sample rate: {metadata['acquisition']['sample_rate']:,.0f} Hz")
   
   scope.close()

Complete Test Setup
-------------------

Generate a signal and capture it:

.. code-block:: python

   from AFG31000 import AFG31000
   from MSO44B import MSO44B
   import numpy as np

   # Generate test signal
   afg = AFG31000()
   scope = MSO44B()
   
   try:
       # Configure AFG31000
       afg.set_frequency(1, 5000)      # 5 kHz
       afg.set_waveform_type(1, 'SINusoid')
       afg.set_amplitude(1, 1.0)       # 1 Vpp
       afg.set_output(1, 'ON')
       print("AFG: Generating 5kHz sine wave")
       
       # Capture the signal
       if scope.connect():
           # Trigger on channel 2 (external trigger)
           scope.setup_trigger(source_channel=2, level=0.5)
           
           results = scope.capture_waveforms(
               channels=[1],  # Capture channel 1
               variable_samples=20000,
               export_data=True,
               include_metadata=False,  # CSV export
               filename="sine_wave_test"
           )
           
           if results:
               voltages = results['waveforms']['CH1']
               print(f"Captured sine wave: {np.mean(voltages):.3f}V avg")
               print(f"CSV file: {results.get('csv_file', 'N/A')}")
   
   finally:
       afg.set_output(1, 'OFF')
       afg.close()
       scope.close()

High-Precision Measurement
--------------------------

Use high resolution mode and binary format for maximum precision:

.. code-block:: python

   from MSO44B import MSO44B

   scope = MSO44B()
   try:
       scope.connect()
       
       # Enable high resolution mode for 16-bit precision
       scope.set_high_resolution_mode(True)
       print(f"Acquisition mode: {scope.get_acquisition_mode()}")
       
       scope.setup_trigger(source_channel=1, level=0.0)
       
       # Compare ASCII vs binary precision
       ascii_result = scope.read_channel_waveform(1, use_binary=False)
       binary_result = scope.read_channel_waveform(1, use_binary=True)
       
       ascii_voltages = ascii_result['voltage_data'][:10]
       binary_voltages = binary_result['voltage_data'][:10]
       
       print("ASCII format:", ascii_voltages)
       print("Binary format:", binary_voltages)
       
       # Calculate precision difference
       differences = [abs(a - b) for a, b in zip(ascii_voltages, binary_voltages)]
       max_diff = max(differences)
       print(f"Maximum difference: {max_diff:.2e} V")
       
   finally:
       scope.close()

Custom Data Processing
----------------------

Process waveform data manually with metadata:

.. code-block:: python

   from MSO44B import MSO44B
   import numpy as np
   import matplotlib.pyplot as plt

   scope = MSO44B()
   try:
       scope.connect()
       scope.setup_trigger(source_channel=1, level=0.0)
       
       # Get raw waveform data
       waveform = scope.read_channel_waveform(1)
       voltages = waveform['voltage_data']
       
       # Generate time axis
       time_params = scope.get_time_scaling_params()
       time_axis = scope.generate_time_axis(len(voltages), time_params)
       
       # Get metadata for analysis context
       metadata = scope.get_scope_metadata(channels=[1], include_global=True)
       sample_rate = metadata['acquisition']['sample_rate']
       
       # Custom analysis
       frequency = sample_rate
       rms_voltage = np.sqrt(np.mean(np.array(voltages)**2))
       
       print(f"Sample rate: {frequency:,.0f} Hz")
       print(f"RMS voltage: {rms_voltage:.3f} V")
       print(f"Acquisition mode: {metadata['acquisition']['acquisition_mode']}")
       
       # Custom plot with metadata
       plt.figure(figsize=(12, 6))
       plt.plot(time_axis * 1e3, voltages)  # Convert to milliseconds
       plt.xlabel('Time (ms)')
       plt.ylabel('Voltage (V)')
       plt.title(f'Custom Analysis: RMS = {rms_voltage:.3f}V, {frequency/1e6:.0f} MS/s')
       plt.grid(True)
       plt.savefig('custom_analysis.png')
       
   finally:
       scope.close()

Instrument Discovery
--------------------

Find and list available instruments:

.. code-block:: python

   from AFG31000 import AFG31000
   from MSO44B import MSO44B

   print("=== Available AFG Instruments ===")
   afg_instruments = AFG31000.list_all_instruments()
   
   print("\\n=== Available MSO Instruments ===")
   mso_instruments = MSO44B.list_all_instruments()
   
   # Connect to specific instruments
   if afg_instruments:
       afg = AFG31000()  # Auto-connects to first AFG found
       print(f"Connected to AFG: {afg.device_id()}")
       afg.close()
   
   if mso_instruments:
       scope = MSO44B()
       if scope.connect():
           print(f"Connected to MSO: {scope.device_id()}")
           scope.close()

Running the Examples
--------------------

Use the built-in example runner:

.. code-block:: bash

   python test_instrument.py

This will show a menu of examples:

.. code-block:: text

   Instrument Driver Examples:
   1. AFG31000 Basic Example
   2. Raw pyMSO4 Example
   3. MSO44B Wrapper Example
   4. Combined AFG + MSO Example
   5. Instrument Discovery Example
   6. Reusable Methods Example
   7. ASCII vs Binary Example

Each example demonstrates different aspects of the library and serves as a starting point 
for your own measurement scripts.