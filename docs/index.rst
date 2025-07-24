Copenhagen Carl Control Documentation
=====================================

A Python library for controlling Tektronix AFG31000 function generators and MSO44B oscilloscopes. 
This library provides simple, scientist-friendly interfaces for common measurement tasks.

Quick Start
-----------

**Install dependencies:**

.. code-block:: bash

   pip install pyvisa matplotlib numpy

**Basic usage:**

.. code-block:: python

   from AFG31000 import AFG31000
   from MSO44B import MSO44B

   # Generate a signal
   afg = AFG31000()
   afg.set_frequency(1, 1000)  # 1 kHz
   afg.set_waveform_type(1, 'SQUare')
   afg.set_output(1, 'ON')

   # Capture the signal
   with MSO44B() as scope:
       scope.connect()
       scope.setup_trigger(source_channel=1, level=0.5)
       results = scope.capture_waveforms(channels=[1, 2])

Contents
--------

.. toctree::
   :maxdepth: 2

   afg31000
   mso44b
   examples
   api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`