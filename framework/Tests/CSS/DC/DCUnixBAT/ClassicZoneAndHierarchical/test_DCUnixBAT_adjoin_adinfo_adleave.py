"""This module will handle the automation of test cases for adjoin, adinfo and adleave functionality"""

import pytest

from .common import *


###### Test cases ######

### 1. Install CDC

@pytest.mark.bhavna
@pytest.mark.css_underconstruction
@pytest.mark.dc_unix_bat
@pytest.mark.css_sanity
def test_1_install_cdc_check_build_number_for_adjoin_and_adleave\
  (dc_is_installed, login_as_root, adjoin, adleave, dc_version):
    """
    Check build number for adjoin and adleave command
    """
    logger.info("--- Case C1267480")
    logger.info("--- Step 1")
    cmd = adjoin
    for option in ["--version", "-v"]:
        check_version_or_assert(cmd, option, dc_version, login_as_root)
    logger.info("--- Step 2")
    cmd = adleave
    for option in ["--version", "-v"]:
        check_version_or_assert(cmd, option, dc_version, login_as_root)

