API Reference
=============

This section provides detailed API documentation for all classes and methods.

AFG31000 Class
--------------

.. autoclass:: AFG31000.AFG31000
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: __init__

MSO44B Class  
------------

.. autoclass:: MSO44B.MSO44B
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: __init__

MSO44BLegacy Class
------------------

.. autoclass:: MSO44B.MSO44BLegacy
   :members:
   :undoc-members:
   :show-inheritance:

   .. automethod:: __init__

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