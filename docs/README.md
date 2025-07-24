# Documentation

This directory contains Sphinx documentation for the Copenhagen Carl Control library.

## Building the Documentation

### Prerequisites

Install Sphinx and dependencies:

```bash
pip install -r requirements.txt
```

### Build HTML Documentation

**Linux/Mac:**
```bash
make html
```

**Windows:**
```bash
make.bat html
```

The generated documentation will be in `_build/html/index.html`.

### Build PDF Documentation

```bash
make latexpdf
```

## Documentation Structure

- `index.rst` - Main documentation page
- `afg31000.rst` - AFG31000 function generator documentation
- `mso44b.rst` - MSO44B oscilloscope documentation  
- `examples.rst` - Usage examples and tutorials
- `api.rst` - Complete API reference
- `conf.py` - Sphinx configuration

## Live Preview

For development, you can use sphinx-autobuild:

```bash
pip install sphinx-autobuild
sphinx-autobuild . _build/html
```

Then open http://localhost:8000 in your browser.