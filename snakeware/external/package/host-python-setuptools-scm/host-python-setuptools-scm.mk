HOST_PYTHON_SETUPTOOLS_SCM_VERSION = 5.0.1
HOST_PYTHON_SETUPTOOLS_SCM_SOURCE = setuptools_scm-$(HOST_PYTHON_SETUPTOOLS_SCM_VERSION).tar.gz
HOST_PYTHON_SETUPTOOLS_SCM_SITE = https://files.pythonhosted.org/packages/source/s/setuptools_scm
HOST_PYTHON_SETUPTOOLS_SCM_SETUP_TYPE = setuptools
$(eval $(host-python-package))
