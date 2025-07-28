# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Copenhagen Carl Control is a Python library for controlling laboratory instruments via VISA communication protocols. The project consists of two main instrument control classes:

- **AFG31000**: Controls Tektronix AFG31000 series arbitrary function generators
- **MSO44B**: Controls Tektronix MSO44B mixed signal oscilloscopes (wrapper around pyMSO4 library)

Both classes support multiple connection methods: Ethernet/TCP-IP, Serial (RS-232), and direct VISA addressing.

## Development Commands

### Installation and Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Install VISA runtime (required for instrument communication)
# Download from National Instruments or equivalent vendor
```

### Testing
```bash
# Run unit tests for AFG31000
python -m pytest test_AFG31000.py -v

# Run automated AFG31000 tests  
python test_AFG31000_auto.py

# Run automated MSO44B tests
python test_MSO44B_auto.py

# Run basic instrument test
python test_instrument.py
```

### Documentation
```bash
# Build Sphinx documentation
cd docs
make html

# View documentation 
# Open docs/_build/html/index.html in browser

# Clean documentation build
make clean

# Build specific formats
make latexpdf  # PDF documentation
make epub      # EPUB format

# Check for documentation warnings
make html SPHINXOPTS="-W"
```

#### Documentation Structure
```
docs/
├── index.rst          # Main documentation entry point
├── afg31000.rst       # AFG31000 function generator documentation  
├── mso44b.rst         # MSO44B oscilloscope documentation
├── examples.rst       # Usage examples and tutorials
├── api.rst            # Complete API reference
├── conf.py            # Sphinx configuration
├── requirements.txt   # Documentation build dependencies
├── Makefile          # Build commands (Unix)
├── make.bat          # Build commands (Windows)
├── _build/           # Generated documentation output
├── _static/          # Static assets (images, CSS)
└── _templates/       # Custom documentation templates
```

#### Documentation Updates
When adding new functionality:
1. Update relevant .rst files in docs/
2. Add code examples with docstrings
3. **Update changelog**: Add entry to docs/changelog.rst with:
   - Feature description
   - Breaking changes (if any)
   - Commit ID: `git log --oneline -1` for reference
4. Rebuild documentation: `cd docs && make html`
5. Verify examples work with actual instruments
6. Update API reference if new public methods added

#### Changelog Management
```bash
# Get current commit ID for changelog
git log --oneline -1

# Get commit range for version
git log --oneline v1.0.0..HEAD

# Format for changelog entry:
# * **Feature Name**: Description (commit: abc1234)
# * **Breaking Change**: What changed (commit: def5678)
```

**Changelog Entry Format:**
```rst
Version X.Y.Z (YYYY-MM-DD)
---------------------------

**New Features**
* **Feature Name**: Description of functionality (commit: abc1234)

**API Changes**  
* **Method Updated**: What changed and why (commit: def5678)

**Breaking Changes**
* **Removed Feature**: What was removed (commit: ghi9012)

**Bug Fixes**
* **Issue Fixed**: Description of fix (commit: jkl3456)
```

## Architecture Overview

### Core Classes

**AFG31000 (AFG31000.py)**
- Main class for function generator control
- Features automatic instrument discovery via `_find_afg_instrument()`
- Supports dual-channel waveform generation with frequency locking
- Parameter validation and comprehensive error handling
- Connection methods: IP, serial port, VISA address, or auto-discovery

**MSO44B (MSO44B.py)**  
- Wrapper around pyMSO4 library for oscilloscope control
- Provides simplified interface for waveform capture and analysis
- Includes automatic instrument discovery via `_discover_mso44_instruments()`
- CSV export functionality for measurement data
- Channel configuration and trigger management

### Key Design Patterns

1. **Automatic Instrument Discovery**: Both classes can automatically find and connect to instruments without manual configuration
2. **Multiple Connection Methods**: Flexible connection options (IP, serial, VISA) for different lab setups  
3. **Error Handling**: Comprehensive exception handling for VISA communication errors
4. **Resource Management**: Proper VISA resource cleanup with close() methods

### Dependencies

- **pyvisa**: Core VISA communication library
- **pyMSO4**: Tektronix oscilloscope library (for MSO44B class)
- **numpy**: Numerical operations for waveform data
- **matplotlib**: Plotting capabilities for waveform visualization

### Testing Structure

- Unit tests with mocked VISA resources (test_AFG31000.py)
- Automated hardware tests requiring actual instruments (test_AFG31000_auto.py, test_MSO44B_auto.py)
- Basic connectivity tests (test_instrument.py)

### Subprojects

**pyMSO4/** - Independent oscilloscope control library with its own documentation and examples. Contains the underlying MSO4 class that MSO44B wraps.

## New Features (2024)

### **Enhanced MSO44B Functionality:**

**High Resolution Mode:**
```python
# Enable 16-bit high resolution mode
scope.set_high_resolution_mode(True)

# Check current acquisition mode
mode = scope.get_acquisition_mode()  # Returns 'sample', 'hires', etc.
```

**Flexible Waveform Capture:**
```python
# Basic capture with variable samples
result = scope.capture_waveforms(
    channels=[1, 2], 
    variable_samples=50000,
    export_data=True,
    include_metadata=False  # Exports as CSV
)

# Advanced capture with metadata
result = scope.capture_waveforms(
    channels=[1, 2], 
    variable_samples=100000,
    export_data=True,
    include_metadata=True   # Exports as JSON with full metadata
)

# Capture without saving files (data analysis only)
result = scope.capture_waveforms(
    channels=[1], 
    export_data=False,
    plot=True
)
```

**Comprehensive Metadata Collection:**
```python
# Get complete scope configuration
metadata = scope.get_scope_metadata(
    channels=[1, 2, 3],     # Specific channels
    include_global=True     # Include instrument info, acquisition settings, etc.
)

# Metadata includes:
# - Instrument info (model, serial, firmware)
# - Acquisition settings (sample rate, record length, mode)
# - Channel configurations (scale, position, coupling)
# - Trigger settings (source, level, type, slope)
# - Time scaling parameters
```

**Direct SCPI Access:**
```python
# Send raw SCPI commands
scope.write('CH1:SCALE 0.1')
response = scope.query('CH1:SCALE?')
device_info = scope.device_id()
```

**Export Formats:**
- **JSON**: Complete data + metadata in single file (recommended for analysis)
- **CSV**: Data-only format for spreadsheet compatibility
- **PNG**: Automatic plot generation

## Common Development Tasks

When working with this codebase:

1. **Adding New Instrument Support**: Follow the pattern of AFG31000/MSO44B classes with automatic discovery, multiple connection methods, and comprehensive error handling

2. **Testing Changes**: 
   - Run unit tests: `python -m pytest test_AFG31000.py -v`
   - Run automated tests if instruments available: `python test_AFG31000_auto.py`
   - Test examples: `python test_instrument.py`

3. **Documentation Updates**:
   - Update relevant .rst files in docs/ directory  
   - Add docstrings to new methods following Google/NumPy style
   - **SCPI Commands in Docstrings**: Use double backticks for SCPI commands to avoid Sphinx warnings: ````*IDN?```` instead of `*IDN?`
   - **Update docs/changelog.rst** with new features and commit IDs
   - Rebuild docs: `cd docs && make html`
   - Verify at docs/_build/html/index.rst
   - Check for warnings: `make html SPHINXOPTS="-W"`

4. **VISA Communication**: All instrument communication uses pyvisa - ensure proper resource management and timeout handling

5. **Data Analysis**: Use JSON export format for complete measurement reproducibility with metadata

6. **Code Style**: Follow existing patterns for consistency - direct instantiation, explicit close(), comprehensive error handling

7. **Version Management**:
   - Update version in docs/conf.py: `release = 'X.Y.Z'`
   - Add changelog entry with commit IDs: `git log --oneline -1`
   - Tag releases: `git tag -a vX.Y.Z -m "Release X.Y.Z"`
   - Document breaking changes prominently in changelog

## Git Guidelines

- **NEVER use `git add -A` or `git add .`** - Always add files explicitly to avoid accidentally committing unwanted files
- Use `git add <specific_file>` for individual files
- Use `git status` to review changes before committing
- Check `.gitignore` to ensure build artifacts and temporary files are excluded

## Development Guidance

- **Always update content in /docs accordingly to codebase content.**