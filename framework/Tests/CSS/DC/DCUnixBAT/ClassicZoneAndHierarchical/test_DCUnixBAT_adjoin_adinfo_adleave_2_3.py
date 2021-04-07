"""This module will handle the automation of test cases for adjoin, adinfo and adleave functionality"""

import pytest

from Shared.dc_functions import join_domain
from .common import *


###### Test constants ######

NON_PERMISSION_USER = "nonpermissionuser"


###### Test cases ######

### 2. Join domain and leave domain

@pytest.mark.bhavna
@pytest.mark.css_underconstruction
@pytest.mark.dc_unix_bat
def test_2_3_join_domain_with_non_permission_user_join_domain\
  (dc_is_installed, login_as_root, css_test_env, dc_join_func, zone_name):
    """
    Join domain with non-permission user
    """
    logger.info("--- Case C1267493")
    logger.info("--- Step 1")
    # Use the join command as the signature
    command = "adjoin %s -u %s -p %s -z %s" % \
      (css_test_env['domain_name'], NON_PERMISSION_USER, css_test_env['common_password'], zone_name)
    rc, result, error = join_domain(command, dc_join_func, login_as_root)
    log_ok_or_assert(rc != 0,
                     f"'{command}' returns error code {rc} as expected",
                     f"'{command}' joins domain successfully and this is not expected")

