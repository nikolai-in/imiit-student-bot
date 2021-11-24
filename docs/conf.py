"""Sphinx configuration."""
from datetime import datetime


project = "Imiit Student Bot"
author = "Николай Иванов"
copyright = f"{datetime.now().year}, {author}"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
]
autodoc_typehints = "description"
html_theme = "furo"
html_logo = "logo.svg"
