PYTHON_FREETYPE_PY_VERSION = 2.5.1
PYTHON_FREETYPE_PY_SOURCE = freetype-py-$(PYTHON_FREETYPE_PY_VERSION).tar.gz
PYTHON_FREETYPE_PY_SITE = https://files.pythonhosted.org/packages/source/f/freetype-py
PYTHON_FREETYPE_PY_SETUP_TYPE = setuptools
PYTHON_FREETYPE_PY_DEPENDENCIES = python3 freetype
$(eval $(python-package))