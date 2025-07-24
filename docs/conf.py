# Configuration file for the Sphinx documentation builder.

import os
import sys
sys.path.insert(0, os.path.abspath('..'))

# -- Project information -----------------------------------------------------
project = 'Copenhagen Carl Control'
copyright = '2024, VC'
author = 'VC'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output ------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# -- Extension configuration -------------------------------------------------
napoleon_google_style = True
napoleon_numpy_style = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False

# Mock imports for problematic packages during documentation build
autodoc_mock_imports = ['matplotlib', 'matplotlib.pyplot', 'pyMSO4', 'pyMSO4.triggers']

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
}