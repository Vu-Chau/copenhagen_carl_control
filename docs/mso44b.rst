MSO44B Oscilloscope
===================

The MSO44B class provides a simple interface for Tektronix MSO44B oscilloscopes with automatic 
voltage conversion and easy data export.

Basic Usage
-----------

.. code-block:: python

   from MSO44B import MSO44B

   # Auto-connect and capture
   with MSO44B() as scope:
       scope.connect()  # Auto-discovers MSO44B
       scope.setup_trigger(source_channel=1, level=0.5, slope='rising')
       results = scope.capture_waveforms(channels=[1, 2, 3])
       
   # Results contain voltage data, CSV file, and plot

Key Features
------------

**Auto-Discovery**
   Automatically finds MSO44B/MSO46 oscilloscopes via VISA device scanning.

**Voltage Conversion**
   Raw ADC values are automatically converted to actual voltages using scope calibration.

**One-Step Capture**
   Single method captures waveforms, saves CSV files, and creates plots.

**Multiple Formats**
   Supports both ASCII (reliable) and binary (precise) data formats.

**Context Manager**
   Automatic connection cleanup using ``with`` statement.

Quick Examples
--------------

**Simple Capture:**

.. code-block:: python

   with MSO44B() as scope:
       scope.connect()
       scope.setup_trigger(source_channel=1, level=0.5)
       results = scope.capture_waveforms(channels=[1, 2])

**High Precision Capture:**

.. code-block:: python

   # Use binary format for maximum precision
   waveform = scope.read_channel_waveform(1, use_binary=True)
   voltages = waveform['voltage_data']

**Custom Processing:**

.. code-block:: python

   # Get scaling parameters for manual processing
   scaling = scope.get_waveform_scaling_params(1)
   time_params = scope.get_time_scaling_params()
   
   # Convert raw data to voltages
   voltages = scope.convert_raw_to_voltage(raw_data, scaling)
   time_axis = scope.generate_time_axis(len(voltages), time_params)

Connection Methods
------------------

**Auto-Discovery (Recommended):**

.. code-block:: python

   scope = MSO44B()
   scope.connect()  # Scans for MSO44/MSO46 instruments

**Specific IP Address:**

.. code-block:: python

   scope.connect(ip_address="192.168.1.100")

**Manual Discovery:**

.. code-block:: python

   # List all instruments
   MSO44B.list_all_instruments()
   
   # Find MSO44/46 specifically
   mso_instruments = scope._discover_mso44_instruments()

Trigger Configuration
---------------------

.. code-block:: python

   # Edge trigger on channel 1
   scope.setup_trigger(
       source_channel=1,     # Trigger source (1-4)
       level=0.5,           # Trigger level in volts
       slope='rising'       # 'rising' or 'falling'
   )

Data Formats
------------

**ASCII Format (Default):**
- Reliable and easy to debug
- ~6-7 significant digits precision
- Slower data transfer

**Binary Format (Optional):**
- Full 16-bit precision
- Faster data transfer
- Use ``use_binary=True`` parameter

.. code-block:: python

   # Compare formats
   ascii_data = scope.read_channel_waveform(1, use_binary=False)
   binary_data = scope.read_channel_waveform(1, use_binary=True)

Reusable Methods
----------------

For advanced users who need individual control:

.. code-block:: python

   # Individual waveform reading
   result = scope.read_channel_waveform(1)
   raw_data = result['raw_data']
   voltages = result['voltage_data']
   
   # Get scaling parameters
   scaling = scope.get_waveform_scaling_params(1)
   time_params = scope.get_time_scaling_params()
   
   # Manual conversion
   voltages = scope.convert_raw_to_voltage(raw_data, scaling)
   time_axis = scope.generate_time_axis(len(voltages), time_params)

Output Files
------------

**CSV Format:**
Contains time and voltage data for all captured channels:

.. code-block:: text

   Time,CH1,CH2,CH3
   0.0,-0.002,1.234,0.567
   1.6e-06,-0.001,1.235,0.568
   ...

**Plot Format:**
PNG file with time-domain waveforms, automatically scaled and labeled.

API Reference
-------------

.. automodule:: MSO44B
   :members:
   :undoc-members:
   :show-inheritance: