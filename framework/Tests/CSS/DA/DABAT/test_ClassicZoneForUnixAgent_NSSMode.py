# test_ClassicZoneForUnixAgent_NSSMode.py

import logging
import pytest
import time

from Shared.css_utils import log_assert
from .common import get_da_session_id, verify_shell_audit_session, ssh_login

logger = logging.getLogger('test')
COMMAND_LIST_BASH = ["df", "touch aa", "rm -rf aa", "/usr/sbin/daflush", "kill -l", "adinfo", "/tmp/cda.sh", "find", "ps", "echo", "adinfo", "dainfo", "dzinfo", "dzdo", "sudo"]
COMMAND_LIST_SH = ["df", "echo", "date", "!-2", "touch aa", "rm -rf aa", "adinfo", "/tmp/cda.sh", "sudo"]
COMMAND_LIST_KSH = ["useradd bat_cda", "userdel bat_cda", "sudo", "/tmp/cda.sh", "ps"]

###### Fixtures ######
@pytest.fixture
def zone_name():
    name = "Core_acsz1"
    yield name

##### Test Cases ######


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_4_2_nss_mode_1(
    log_test_name, dc_is_joined, set_da_installation, login_as_root):
    """
    Enable 'dzdo' command
    """
    logger.info("--- Case C1238980")
    
    rc, result, error = login_as_root.send_command("dacontrol -e -c /usr/share/centrifydc/bin/dzdo")
    log_assert(rc == 0, f"Failed to enable command auditing for 'dzdo': {error}")

    # Restore
    login_as_root.send_command("dacontrol -d -c /usr/share/centrifydc/bin/dzdo")


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
@pytest.mark.incomplete
def test_4_2_nss_mode_2(
    log_test_name, dc_is_joined, set_da_installation, disable_da_nss, login_as_root):
    """
    Enable NSS module
    """
    logger.info("--- Case C1238981")
    
    rc, result, error = login_as_root.send_command("dacontrol -e")
    log_assert(rc == 0, f"Failed to run 'dacontrol -e': {error}")
    
    rc, result, error = login_as_root.send_command("dainfo -q nss_status")
    log_assert(rc == 0, f"NSS module is not enabled successfully: {error}")


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_nss_mode_login_with_ad_user_anu0001_shell_bin_bash(
    log_test_name, dc_is_joined, set_da_installation, enable_da_nss,
    create_cda_sh_script, cda_login_as_aduser_0001, cda_login_am_as_domain_admin):
    """
    Login with AD user whose shell is "/bin/bash"
    """
    logger.info("--- Case C1238982")

    # Get DA_SESSION_ID
    da_session_id = get_da_session_id(cda_login_as_aduser_0001)
    assert da_session_id is not None,\
        f"Environment variable 'DA_SESSION_ID' does not exist in this session, which is unexpected."

    # Run some commands
    for command in COMMAND_LIST_BASH:
        cda_login_as_aduser_0001.send_shell_command(command)
        time.sleep(1)

    # Verify shell auditing session
    assert verify_shell_audit_session(dc_is_joined['installation_name'], da_session_id,
                                      COMMAND_LIST_BASH, cda_login_am_as_domain_admin),\
        f"Failed to verify the shell auditing session for user {dc_is_joined['aduser_0001_name']}"


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_nss_mode_login_with_local_user_root(
    log_test_name, dc_is_joined, set_da_installation, enable_da_nss, cda_login_as_root, cda_login_am_as_domain_admin):
    """
    Login with local user "root"
    """
    logger.info("--- Case C1238985")

    # Get DA_SESSION_ID
    da_session_id = get_da_session_id(cda_login_as_root)
    assert da_session_id is not None,\
        f"Environment variable 'DA_SESSION_ID' does not exist in this session, which is unexpected."

    # Run some commands
    for command in COMMAND_LIST_BASH:
        cda_login_as_root.send_shell_command(command)
        time.sleep(1)

    # Verify shell auditing session
    assert verify_shell_audit_session(dc_is_joined['installation_name'], da_session_id, COMMAND_LIST_BASH,\
                                      cda_login_am_as_domain_admin),\
        f"Failed to verify the shell auditing session for user root"


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_4_2_nss_mode_7(
    log_test_name, dc_is_joined, set_da_installation, enable_da_nss, login_as_root):
    """
    Disable NSS module
    """
    logger.info("--- Case C1238988")

    rc, result, error = login_as_root.send_command("dacontrol -d")
    log_assert(rc == 0, f"Failed to run 'dacontrol -d': {error}")

    rc, result, error = login_as_root.send_command("dacontrol -d -a")
    log_assert(rc == 0, f"Failed to run 'dacontrol -d -a': {error}")

    rc, result, error = login_as_root.send_command("dainfo -q nss_status")
    log_assert(rc == 1, f"Failed to get NSS status or NSS module is not disabled successfully: {error}")
