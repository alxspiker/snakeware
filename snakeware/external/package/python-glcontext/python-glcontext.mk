PYTHON_GLCONTEXT_VERSION = 2.5.0
PYTHON_GLCONTEXT_SOURCE = glcontext-$(PYTHON_GLCONTEXT_VERSION).tar.gz
PYTHON_GLCONTEXT_SITE = https://files.pythonhosted.org/packages/source/g/glcontext
PYTHON_GLCONTEXT_SETUP_TYPE = setuptools
PYTHON_GLCONTEXT_DEPENDENCIES = python3
$(eval $(python-package))
