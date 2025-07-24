# Configuration file for the Sphinx documentation builder.

# -- Project information -----------------------------------------------------
project = 'Copenhagen Carl Control'
copyright = '2024, VC'
author = 'VC'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
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