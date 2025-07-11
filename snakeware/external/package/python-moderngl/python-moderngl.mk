PYTHON_MODERNGL_VERSION = 5.12.0  # Latest as of 2025
PYTHON_MODERNGL_SOURCE = moderngl-$(PYTHON_MODERNGL_VERSION).tar.gz
PYTHON_MODERNGL_SITE = https://files.pythonhosted.org/packages/source/m/moderngl
PYTHON_MODERNGL_SETUP_TYPE = setuptools
PYTHON_MODERNGL_DEPENDENCIES = python3 mesa3d libegl libgles
$(eval $(python-package))