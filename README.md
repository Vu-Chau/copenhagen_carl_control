# Copenhagen Carl Control

A Python library for controlling laboratory instruments, specifically designed for interfacing with Tektronix AFG31000 series arbitrary function generators and MSO44B oscilloscopes via VISA communication protocols.

## Overview

This project provides Python classes that enable programmatic control of:
- **AFG31000**: Tektronix AFG31000 series arbitrary function generators
- **MSO44B**: Tektronix MSO44B mixed signal oscilloscopes

Both instruments can be controlled via:
- Ethernet/TCP-IP connection
- Serial (RS-232) connection
- Direct VISA resource addressing

## Features

### AFG31000 Function Generator
- **Automatic instrument discovery** - finds AFG instruments automatically
- Device identification and validation
- Waveform generation (sine, square, triangle, etc.)
- Frequency and amplitude control for dual channels
- Phase adjustment and frequency locking
- Output enable/disable control
- Comprehensive parameter validation

### MSO44B Oscilloscope
- Channel configuration (scale, coupling, state)
- Timebase control
- Trigger setup and management
- Waveform data acquisition
- Multi-channel data capture
- CSV export functionality
- Automated triggered measurements

## Requirements

- Python 3.10+
- PyVISA library
- NumPy library  
- Matplotlib library
- pyMSO4 library
- VISA runtime (NI-VISA or similar)

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd copenhagen_carl_control
```

2. Install all dependencies:
```bash
pip install -r requirements.txt
```

3. Install VISA runtime from your instrument vendor (e.g., NI-VISA from National Instruments)

3. Clone this repository:
```bash
git clone https://github.com/Vu-Chau/copenhagen_carl_control.git
cd copenhagen_carl_control
```

## Usage Examples

### AFG31000 Function Generator

```python
from AFG31000 import AFG31000

# NEW: Automatic discovery - no connection parameters needed!
afg = AFG31000()  # Automatically finds and connects to AFG instrument

# Alternative: Connect via IP address
# afg = AFG31000(ip_address="192.168.1.100")

# Check device identity
print(afg.device_id())

# Configure channel 1
afg.set_waveform_type(1, 'SINusoid')    # Sine wave
afg.set_frequency(1, 1000)              # 1 kHz
afg.set_amplitude(1, 2.0)               # 2V amplitude
afg.set_output(1, True)                 # Enable output

# Frequency lock both channels
afg.set_frequency_lock(True)

# Set phase relationship
afg.set_phase(2, 90)  # 90 degree phase shift on channel 2

# Clean up
afg.close()
```

#### List Available Instruments

```python
# List all available instruments (static method)
AFG31000.list_all_instruments()
```

### MSO44B Oscilloscope

```python
from MSO44B import MSO44B

# Connect via IP address
scope = MSO44B(ip_address="192.168.1.101")

# Configure channels
scope.set_channel_scale(1, 0.1)        # 100mV/div
scope.set_channel_coupling(1, 'DC')    # DC coupling
scope.set_channel_state(1, True)       # Enable channel

# Configure timebase and trigger
scope.set_time_scale(0.001)            # 1ms/div
scope.set_trigger(1, 0.5, 'RISING')    # Trigger on rising edge at 0.5V

# Capture and save waveforms
result = scope.get_triggered_waveforms_and_save([1, 2], 'measurement.csv')
print(f"Waveforms saved to: {result['filename']}")
```

## Connection Methods

### Ethernet/TCP-IP
```python
# Using IP address
instrument = AFG31000(resource_name="AFG31000", ip_address="192.168.1.100")
# or
instrument = MSO44B(ip_address="192.168.1.101")
```

### Serial Connection
```python
# Using COM port
instrument = AFG31000(resource_name="AFG31000", serial_port="COM3")
# or
instrument = MSO44B(serial_port="COM4")
```

### Direct VISA Address
```python
# Using full VISA resource string
instrument = AFG31000(resource_name="AFG31000", visa_address="TCPIP::192.168.1.100::INSTR")
```

## Documentation

The project includes comprehensive programming manuals:
- `077147303_AFG31000_Series_User_Manual_EN_Nov2020.pdf` - AFG31000 User Manual
- `077148803_AFG31000_Series_ProgrammersManual_Nov2020.pdf` - AFG31000 Programming Reference
- `4-5-6_MSO_ProgrammerManual-077189800.pdf` - MSO Series Programming Manual

## Error Handling

Both classes include comprehensive error handling:
- Device identification validation
- Parameter range checking
- Connection timeout management
- VISA communication error handling

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source. Please refer to the license file for details.

## Support

For issues related to:
- **Instrument communication**: Check VISA installation and network connectivity
- **Parameter validation**: Refer to the included programming manuals
- **Code functionality**: Open an issue on the GitHub repository

## Acknowledgments

Developed for laboratory automation and instrument control applications at Copenhagen University.
