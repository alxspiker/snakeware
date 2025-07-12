PYTHON_FREETYPE_PY_VERSION = 2.5.1
PYTHON_FREETYPE_PY_SOURCE = freetype-py-$(PYTHON_FREETYPE_PY_VERSION).zip
PYTHON_FREETYPE_PY_SITE = https://files.pythonhosted.org/packages/d0/9c/61ba17f846b922c2d6d101cc886b0e8fb597c109cedfcb39b8c5d2304b54
PYTHON_FREETYPE_PY_SETUP_TYPE = setuptools
PYTHON_FREETYPE_PY_DEPENDENCIES = python3 freetype host-python-setuptools-scm
define PYTHON_FREETYPE_PY_EXTRACT_CMDS
 $(UNZIP) $(DL_DIR)/$(PYTHON_FREETYPE_PY_SOURCE) -d $(@D)/extract && \
 mv $(@D)/extract/freetype-py-$(PYTHON_FREETYPE_PY_VERSION)/* $(@D) && \
 rm -rf $(@D)/extract
endef
$(eval $(python-package))