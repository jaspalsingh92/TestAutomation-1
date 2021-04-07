# test_DCUnixBAT_AuditLevel_2.py

import pytest
import re

from .common import *


###### Fixtures ######

@pytest.fixture
def install_packages():
    yield ['CentrifyDC', 'CentrifyDA']
    

@pytest.fixture
def da_nss_is_inactive(login_as_root, dacontrol):
    cmd = f"{dacontrol} -d"
    rc, result, error = login_as_root.send_command(cmd)
    if rc != 0:
        raise Exception(f"'{cmd}' returns error code {rc}, message: {error}")

    
###### Test cases ######

### 2. DA is installed, but NSS is inactive

@pytest.mark.bhavna
@pytest.mark.css_underconstruction
@pytest.mark.dc_unix_bat
@pytest.mark.skip_zone_type("classic")
def test_2_DA_is_installed_run_dacontrol_d_to_let_nss_is_inactive\
  (dc_is_joined, login_as_root, dacontrol, dainfo):
    """
    Run "dacontrol -d" to let NSS is inactive
    """
    logger.info("--- Case C1267529")
    logger.info("--- Step 1")
    cmd = f"{dacontrol} -d"
    rc, result, error = login_as_root.send_command(cmd)
    log_ok_or_assert(rc == 0,
                     f"'{cmd}' completes successfully",
                     f"'{cmd}' returns error code {rc}, message: {error}")
    logger.info("--- Step 2")
    cmd = f"{dainfo}"
    rc, result, error = login_as_root.send_command(cmd)
    content = login_as_root.to_string(result)
    nss = None
    x = re.search(r"DirectAudit NSS module:\s*(\w+)", content, re.MULTILINE)
    if x:
        nss = x.group(1)
    log_assert(nss, "Cannot get DA NSS module status")
    log_ok_or_assert(nss == "Inactive",
                     f"'{cmd}' returns expected DA NSS module status '{nss}'",
                     f"'{cmd}' returns unexpected DA NSS module status '{nss}'")


@pytest.mark.bhavna
@pytest.mark.css_underconstruction
@pytest.mark.dc_unix_bat
@pytest.mark.skip_zone_type("classic")
def test_2_DA_is_installed_check_user_which_audit_level_is_set_to_audit_not_requested_required\
  (dc_is_joined, da_nss_is_inactive, login_as_root, dzinfo):
    """
    Check user which audit level is set to "Audit not requested/required"
    """
    logger.info("--- Case C1267530")
    logger.info("--- Step 1")
    user = "anu0021"
    cmd = f"{dzinfo} {user} -f"
    check_dzinfo_f_audit_level_rescue_rights_or_assert(cmd, user, "AuditNotRequested", "false", login_as_root)
    logger.info("--- Step 2")
    check_ssh_login_or_assert(True, dc_is_joined['public_ip'], "AD user", user, dc_is_joined['common_password'])


@pytest.mark.bhavna
@pytest.mark.css_underconstruction
@pytest.mark.dc_unix_bat
@pytest.mark.skip_zone_type("classic")
def test_2_DA_is_installed_check_user_which_audit_level_is_set_to_audit_if_possible\
  (dc_is_joined, da_nss_is_inactive, login_as_root, dzinfo):
    """
    Check user which audit level is set to "Audit if possible"
    """
    logger.info("--- Case C1267531")
    logger.info("--- Step 1")
    user = "anu0022"
    cmd = f"{dzinfo} {user} -f"
    check_dzinfo_f_audit_level_rescue_rights_or_assert(cmd, user, "AuditIfPossible", "false", login_as_root)
    logger.info("--- Step 2")
    check_ssh_login_or_assert(True, dc_is_joined['public_ip'], "AD user", user, dc_is_joined['common_password'])


@pytest.mark.bhavna
@pytest.mark.css_underconstruction
@pytest.mark.dc_unix_bat
@pytest.mark.skip_zone_type("classic")
def test_2_DA_is_installed_check_user_which_audit_level_is_set_to_audit_required_but_without_rescue_rights\
  (dc_is_joined, da_nss_is_inactive, login_as_root, dzinfo):
    """
    Check user which audit level is set to "Audit required" but without "Rescue rights"
    """
    logger.info("--- Case C1267532")
    logger.info("--- Step 1")
    user = "anu0023"
    cmd = f"{dzinfo} {user} -f"
    check_dzinfo_f_audit_level_rescue_rights_or_assert(cmd, user, "AuditRequired", "false", login_as_root)
    logger.info("--- Step 2")
    check_ssh_login_or_assert(False, dc_is_joined['public_ip'], "AD user", user, dc_is_joined['common_password'])


@pytest.mark.bhavna
@pytest.mark.css_underconstruction
@pytest.mark.dc_unix_bat
@pytest.mark.skip_zone_type("classic")
def test_2_DA_is_installed_check_user_which_audit_level_is_set_to_audit_required_and_with_rescue_rights\
  (dc_is_joined, da_nss_is_inactive, login_as_root, dzinfo):
    """
    Check user which audit level is set to "Audit not requested/required"
    """
    logger.info("--- Case C1267533")
    logger.info("--- Step 1")
    user = "anu0024"
    cmd = f"{dzinfo} {user} -f"
    check_dzinfo_f_audit_level_rescue_rights_or_assert(cmd, user, "AuditRequired", "true", login_as_root)
    logger.info("--- Step 2")
    check_ssh_login_or_assert(True, dc_is_joined['public_ip'], "AD user", user, dc_is_joined['common_password'])

