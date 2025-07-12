PYTHON_PYRR_VERSION = 0.10.3
PYTHON_PYRR_SOURCE = pyrr-$(PYTHON_PYRR_VERSION).tar.gz
PYTHON_PYRR_SITE = https://files.pythonhosted.org/packages/source/p/pyrr
PYTHON_PYRR_SETUP_TYPE = setuptools
PYTHON_PYRR_DEPENDENCIES = python3 python-numpy
$(eval $(python-package))
