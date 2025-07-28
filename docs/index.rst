Copenhagen Carl Control Documentation
=====================================

A Python library for controlling Tektronix AFG31000 function generators and MSO44B oscilloscopes. 
This library provides simple, scientist-friendly interfaces for laboratory instrument control with 
automatic discovery, comprehensive metadata collection, and flexible data export options.

Key Features
------------

**Automatic Instrument Discovery**
   Both AFG31000 and MSO44B classes automatically discover and connect to instruments without manual configuration.

**High Resolution Mode**
   MSO44B supports 16-bit high resolution acquisition mode for enhanced measurement precision.

**Flexible Data Export**
   Choose between CSV (data-only) or JSON (data + complete metadata) export formats for different use cases.

**Comprehensive Metadata**
   JSON exports include complete instrument configuration, acquisition settings, channel parameters, and trigger information.

**Variable Sample Length**
   Configurable record length from 1K to 50M samples depending on your measurement requirements.

**Direct SCPI Access**
   Both classes provide direct SCPI command access for advanced users while maintaining high-level convenience methods.

Quick Start
-----------

**Install dependencies:**

.. code-block:: bash

   pip install -r requirements.txt

Or install individually:

.. code-block:: bash

   pip install pyvisa>=1.11.0 numpy>=1.20.0 matplotlib>=3.5.0 pyMSO4

**Basic usage with enhanced features:**

.. code-block:: python

   from AFG31000 import AFG31000
   from MSO44B import MSO44B

   # Generate a signal with auto-discovery
   afg = AFG31000()  # Automatically discovers AFG instruments
   afg.set_frequency(1, 1000)  # 1 kHz
   afg.set_waveform_type(1, 'SQUare')
   afg.set_output(1, 'ON')
   
   # Capture with metadata and JSON export
   scope = MSO44B()  # Consistent usage pattern
   scope.connect()   # Auto-discovers MSO44/46 instruments
   scope.set_high_resolution_mode(True)  # Enable 16-bit mode
   scope.setup_trigger(source_channel=1, level=0.5)
   
   # Flexible capture options
   result = scope.capture_waveforms(
       channels=[1, 2], 
       variable_samples=50000,        # Custom sample count
       export_data=True,
       include_metadata=True,         # JSON with metadata
       filename="measurement_001"
   )
   
   # Clean up
   afg.close()
   scope.close()

New in 2024
-----------

**Enhanced MSO44B Functionality:**

* **High Resolution Mode**: 16-bit acquisition via ``set_high_resolution_mode(True)``
* **Variable Samples**: Configurable record length with ``variable_samples`` parameter  
* **Smart Export**: JSON with metadata or CSV data-only based on ``include_metadata`` flag
* **Metadata Collection**: Complete scope configuration via ``get_scope_metadata()``
* **Direct SCPI**: ``write()``, ``query()``, and ``device_id()`` methods for advanced control
* **Consistent API**: Unified usage pattern with AFG31000 (direct instantiation + explicit close)

Contents
--------

.. toctree::
   :maxdepth: 2

   afg31000
   mso44b
   examples
   api
   changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`