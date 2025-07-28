MSO44B Oscilloscope
===================

The MSO44B class provides a comprehensive interface for Tektronix MSO44B/MSO46 oscilloscopes with 
automatic discovery, voltage conversion, metadata collection, and flexible data export options.

Basic Usage
-----------

.. code-block:: python

   from MSO44B import MSO44B

   # Consistent usage pattern (no context manager required)
   scope = MSO44B()
   scope.connect()  # Auto-discovers MSO44B/MSO46
   scope.setup_trigger(source_channel=1, level=0.5, slope='rising')
   
   # Flexible capture with options
   result = scope.capture_waveforms(
       channels=[1, 2], 
       variable_samples=25000,
       export_data=True,
       include_metadata=True  # JSON with complete metadata
   )
   
   scope.close()  # Explicit cleanup

Key Features
------------

**Auto-Discovery**
   Automatically finds MSO44B/MSO46 oscilloscopes via VISA device scanning.

**High Resolution Mode**
   16-bit acquisition mode for enhanced measurement precision via ``set_high_resolution_mode(True)``.

**Flexible Data Export**
   Smart export system: JSON with metadata or CSV data-only based on ``include_metadata`` flag.

**Comprehensive Metadata**
   Complete instrument configuration, acquisition settings, channel parameters, and trigger information.

**Variable Sample Length**
   Configurable record length with ``variable_samples`` parameter (1K to 50M samples).

**Direct SCPI Access**
   ``write()``, ``query()``, and ``device_id()`` methods for advanced control alongside high-level methods.

**Voltage Conversion**
   Raw ADC values are automatically converted to actual voltages using scope calibration.

**Multiple Data Formats**
   Supports both ASCII (reliable) and binary (precise) data formats for different precision needs.

Quick Examples
--------------

**JSON Export with Metadata:**

.. code-block:: python

   scope = MSO44B()
   scope.connect()
   scope.set_high_resolution_mode(True)  # Enable 16-bit mode
   scope.setup_trigger(source_channel=1, level=0.5)
   
   result = scope.capture_waveforms(
       channels=[1, 2], 
       variable_samples=50000,
       include_metadata=True  # JSON with complete metadata
   )
   scope.close()

**CSV Export (Data Only):**

.. code-block:: python

   scope = MSO44B()
   scope.connect()
   scope.setup_trigger(source_channel=1, level=0.5)
   
   result = scope.capture_waveforms(
       channels=[1, 2, 3], 
       variable_samples=25000,
       include_metadata=False  # CSV export
   )
   scope.close()

**Metadata Collection:**

.. code-block:: python

   # Get complete scope configuration
   metadata = scope.get_scope_metadata(
       channels=[1, 2], 
       include_global=True
   )
   
   print(f"Sample rate: {metadata['acquisition']['sample_rate']:,.0f} Hz")
   print(f"Trigger: {metadata['trigger']['source']} @ {metadata['trigger']['level']}V")

**Direct SCPI Commands:**

.. code-block:: python

   # Direct instrument control
   scope.write('CH1:SCALE 0.1')  # Set channel 1 to 100mV/div
   scale = scope.query('CH1:SCALE?')  # Query current scale
   device_info = scope.device_id()  # Get instrument ID

**High Precision Binary Data:**

.. code-block:: python

   # Use binary format for maximum precision
   waveform = scope.read_channel_waveform(1, use_binary=True)
   voltages = waveform['voltage_data']
   print(f"Format used: {waveform['format_used']}")

**Individual Method Usage:**

.. code-block:: python

   # Manual processing with individual methods
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
   scope.connect()  # Automatically finds MSO44/MSO46 instruments
   print(f"Connected to: {scope.device_id()}")
   # ... use scope ...
   scope.close()  # Explicit cleanup

**Specific IP Address:**

.. code-block:: python

   scope = MSO44B()
   scope.connect(ip_address="192.168.1.100")
   # ... use scope ...
   scope.close()

**Discovery Methods:**

.. code-block:: python

   # List all available instruments
   MSO44B.list_all_instruments()
   
   # Find MSO44/46 specifically  
   scope = MSO44B()
   mso_instruments = scope._discover_mso44_instruments()
   
   # Connect to discovered instrument
   if mso_instruments and scope.connect():
       print("Auto-discovery successful!")
       scope.close()

Trigger Configuration
---------------------

.. code-block:: python

   # Edge trigger configuration
   scope.setup_trigger(
       source_channel=1,      # Trigger source (1-4)
       trigger_type='edge',   # Currently supports 'edge' 
       level=0.5,            # Trigger level in volts
       slope='rising'        # 'rising' or 'falling'
   )
   
   # Verify trigger setup
   print("Trigger configured successfully")

**Acquisition Modes:**

.. code-block:: python

   # Set high resolution mode for 16-bit precision
   scope.set_high_resolution_mode(True)
   
   # Check current mode
   current_mode = scope.get_acquisition_mode()
   print(f"Current mode: {current_mode}")  # 'sample', 'hires', etc.
   
   # Revert to normal sampling
   scope.set_high_resolution_mode(False)

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

**JSON Format (with Metadata):**
Complete measurement data with full instrument configuration:

.. code-block:: text

   {
     "metadata": {
       "timestamp": "2024-01-15T14:30:45.123456",
       "instrument": {
         "vendor": "TEKTRONIX", 
         "model": "MSO44",
         "serial_number": "C012345",
         "firmware_version": "1.2.3.4"
       },
       "acquisition": {
         "sample_rate": 1000000000.0,
         "record_length": 50000,
         "acquisition_mode": "hires"
       },
       "channels": {
         "CH1": {"scale": 0.1, "coupling": "DC", "enabled": true}
       },
       "trigger": {
         "source": "CH1", "level": 0.5, "slope": "rise"
       }
     },
     "waveforms": {
       "Time": [0.0, 1e-9, 2e-9, 3e-9],
       "CH1": [0.1, 0.15, 0.12, 0.13],
       "CH2": [0.05, 0.08, 0.06, 0.07]
     }
   }

**CSV Format (Data Only):**
Simple time and voltage data for spreadsheet compatibility:

.. code-block:: text

   Time,CH1,CH2,CH3
   0.0,-0.002,1.234,0.567
   1.6e-06,-0.001,1.235,0.568
   ...

**PNG Plot Format:**
Time-domain waveforms with automatic scaling, grid, and channel labels.

API Reference
-------------

.. automodule:: MSO44B
   :members:
   :undoc-members:
   :show-inheritance: