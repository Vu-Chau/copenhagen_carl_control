Changelog
=========

All notable changes to the Copenhagen Carl Control library are documented in this file.

Version 1.1.0 (2024)
---------------------

**New Features**

**MSO44B Oscilloscope:**

* **High Resolution Mode**: Added ``set_high_resolution_mode()`` to enable 16-bit acquisition
* **Variable Samples**: ``capture_waveforms()`` now supports ``variable_samples`` parameter for custom record lengths
* **Smart Export System**: Unified export with ``include_metadata`` flag:
  
  * ``include_metadata=True`` → JSON export with complete metadata
  * ``include_metadata=False`` → CSV export (data only)

* **Comprehensive Metadata**: New ``get_scope_metadata()`` function collects:
  
  * Instrument information (model, serial, firmware)
  * Acquisition settings (sample rate, record length, mode)
  * Channel configurations (scale, position, coupling)
  * Trigger settings (source, level, type, slope)
  * Time scaling parameters

* **Direct SCPI Access**: Added ``write()``, ``query()``, and ``device_id()`` methods
* **Acquisition Mode Control**: ``get_acquisition_mode()`` method added
* **Enhanced Connection**: ``close()`` method for explicit cleanup

**API Improvements:**

* **Consistent Usage Pattern**: Both AFG31000 and MSO44B now use direct instantiation + explicit ``close()``
* **Removed Legacy Code**: Eliminated ``MSO44BLegacy`` class for cleaner API
* **Unified Capture Function**: Single ``capture_waveforms()`` method replaces multiple variants

**Documentation:**

* Updated all examples to use consistent patterns
* Added comprehensive usage examples in ``test_instrument.py``
* Enhanced Sphinx documentation with new features
* Added development workflow documentation

**Breaking Changes:**

* **MSO44B Context Manager**: Removed ``with MSO44B() as scope:`` pattern in favor of explicit ``scope.close()``
* **Legacy Class Removed**: ``MSO44BLegacy`` class no longer available
* **Parameter Changes**: ``capture_waveforms()`` parameters updated for new functionality

Version 1.0.0 (2024)
---------------------

**Initial Release**

* **AFG31000 Function Generator**: Complete control interface with automatic discovery
* **MSO44B Oscilloscope**: Basic wrapper around pyMSO4 with simplified interface
* **Automatic Discovery**: Both instruments support VISA-based auto-discovery
* **Data Export**: CSV export and PNG plotting capabilities
* **Multiple Connection Methods**: IP address, serial port, and VISA resource support
* **Comprehensive Documentation**: Sphinx-based documentation with examples

**Supported Features:**

* Signal generation with multiple waveform types
* Dual-channel function generator control
* Oscilloscope trigger configuration
* Waveform capture and voltage conversion
* Automatic file naming with timestamps
* Connection management and error handling