API Reference
=============

This section provides detailed API documentation for all classes and methods.

Complete API Documentation
--------------------------

For detailed documentation of each class and its methods, see:

* :doc:`afg31000` - AFG31000 Function Generator API
* :doc:`mso44b` - MSO44B Oscilloscope API

Method Summary
--------------

**AFG31000 Function Generator Methods:**

Core Methods:
  * ``__init__(resource_name, serial_port, ip_address, visa_address, timeout)`` - Initialize connection
  * ``device_id()`` - Get device identification string  
  * ``check_device_id(strict)`` - Verify device is AFG31000 series
  * ``close()`` - Close connection and cleanup resources

Waveform Configuration:
  * ``set_waveform_type(channel, waveform_type)`` - Set waveform (SINusoid, SQUare, etc.)
  * ``get_waveform_type(channel)`` - Get current waveform type
  * ``set_frequency(channel, frequency)`` - Set frequency in Hz
  * ``get_frequency(channel)`` - Get current frequency
  * ``set_amplitude(channel, amplitude)`` - Set amplitude in Vpp
  * ``get_amplitude(channel)`` - Get current amplitude
  * ``set_offset(channel, offset)`` - Set DC offset in volts
  * ``get_offset(channel)`` - Get current offset

Output Control:
  * ``set_output(channel, state)`` - Enable/disable output ('ON'/'OFF' or True/False)
  * ``get_output(channel)`` - Get output state
  * ``set_load(channel, impedance)`` - Set load impedance (50, 'INF', 'HIGHZ')
  * ``get_load(channel)`` - Get load impedance

Advanced Features:
  * ``set_phase(channel, phase, unit)`` - Set phase (degrees or radians)
  * ``get_phase(channel, unit)`` - Get current phase
  * ``set_frequency_lock(state)`` - Lock frequencies between channels
  * ``get_frequency_lock()`` - Get frequency lock state

Communication:
  * ``write(command)`` - Send SCPI command
  * ``read()`` - Read response
  * ``query(command)`` - Send command and read response
  * ``list_all_instruments()`` - Find all AFG instruments (static method)

**MSO44B Oscilloscope Methods:**

Core Methods:
  * ``__init__(timeout)`` - Initialize oscilloscope wrapper
  * ``connect(ip_address, auto_discover)`` - Connect to oscilloscope
  * ``setup_trigger(source_channel, trigger_type, level, slope)`` - Configure trigger
  * ``disconnect()`` - Close connection
  * ``__enter__()`` / ``__exit__()`` - Context manager support

Data Acquisition:
  * ``capture_waveforms(channels, filename, plot, save_csv)`` - Capture and process waveforms
  * ``read_channel_waveform(channel, use_binary)`` - Read single channel data
  * ``get_waveform_scaling_params(channel)`` - Get voltage scaling parameters
  * ``get_time_scaling_params()`` - Get time base parameters
  * ``convert_raw_to_voltage(raw_data, scaling_params)`` - Convert ADC to voltage
  * ``generate_time_axis(data_length, time_params)`` - Create time axis

Data Export:
  * ``save_csv(waveform_data, filename)`` - Save data to CSV file
  * ``plot_waveforms(waveform_data, channels, filename)`` - Generate plots

Utility:
  * ``list_all_instruments()`` - Find all MSO44/MSO46 instruments (static method)

**MSO44BLegacy Basic Interface:**

  * ``__init__(resource_name, ip_address, serial_port)`` - Initialize basic connection
  * ``write(command)`` - Send SCPI command
  * ``query(command)`` - Send command and read response  
  * ``device_id()`` - Get device identification
  * ``close()`` - Close connection

Exception Handling
------------------

The library uses standard Python exceptions:

- ``ValueError`` - Invalid parameter values
- ``RuntimeError`` - Connection or communication errors  
- ``TimeoutError`` - Trigger timeout (MSO44B)
- ``OSError`` - VISA communication errors

Example error handling:

.. code-block:: python

   from AFG31000 import AFG31000
   from MSO44B import MSO44B

   try:
       afg = AFG31000()
       afg.set_frequency(1, -1000)  # Invalid negative frequency
   except ValueError as e:
       print(f"Parameter error: {e}")
   
   try:
       with MSO44B() as scope:
           scope.connect(ip_address="192.168.1.999")  # Invalid IP
   except (OSError, RuntimeError) as e:
       print(f"Connection error: {e}")

Data Types
----------

**AFG31000 Parameters:**

- Channel numbers: ``int`` (1 or 2)
- Frequencies: ``float`` (Hz)
- Amplitudes: ``float`` (Volts peak-to-peak)
- Phases: ``float`` (degrees or radians)
- Waveform types: ``str`` ('SINusoid', 'SQUare', etc.)
- Output states: ``str`` or ``bool`` ('ON'/'OFF', True/False)

**MSO44B Parameters:**

- Channel numbers: ``int`` (1-4 for MSO44, 1-6 for MSO46)
- Trigger levels: ``float`` (Volts)
- Slopes: ``str`` ('rising' or 'falling')
- File names: ``str`` (without extension)

**Return Values:**

- Waveform data: ``list[float]`` (voltage values)
- Time data: ``numpy.ndarray`` or ``list[float]`` (time values in seconds)
- Scaling parameters: ``dict`` (calibration constants)
- Capture results: ``dict`` (waveforms, metadata, filenames)

Constants
---------

**AFG31000 Waveform Types:**

.. code-block:: python

   WAVEFORM_TYPES = [
       'SINusoid', 'SQUare', 'PULSe', 'RAMP', 'PRNoise', 'DC',
       'SINC', 'GAUSsian', 'LORentz', 'EXPRise', 'EXPDecay', 'HAVersine'
   ]

**MSO44B Trigger Slopes:**

.. code-block:: python

   TRIGGER_SLOPES = ['rising', 'falling', 'rise', 'fall']

**Data Format Options:**

.. code-block:: python

   DATA_FORMATS = ['ascii', 'binary']

Version Information
-------------------

.. code-block:: python

   import MSO44B
   import AFG31000
   
   print("Library version: 1.0.0")
   print("Supports: AFG31000 series, MSO44B/MSO46")
   print("Dependencies: pyvisa, numpy, matplotlib")