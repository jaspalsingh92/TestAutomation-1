# test_HierarchicalZoneForUnixAgent_CommandLevelMode.py

import logging
import pytest

from Shared.css_utils import log_assert
from .common import get_datetime, verify_command_audit_session

logger = logging.getLogger('test')

###### Fixtures ######
@pytest.fixture
def zone_name():
    name = "Core_ahsz11"
    yield name


#### Test Cases ######
@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_3_3_command_level_mode_1(
        log_test_name, dc_is_joined, set_da_installation, login_as_root):
    """
    Enable audited commands
    """
    logger.info("--- Case C1238920")

    rc, result, error = login_as_root.send_command("dacontrol -e -c /usr/share/centrifydc/libexec/adinfo")
    log_assert(rc == 0, f"Failed to enable command auditing for 'adinfo': {error}")

    rc, result, error = login_as_root.send_command("dacontrol -e -c `which kill`")
    log_assert(rc == 0, f"Failed to enable command auditing for 'kill': {error}")

    # Restore
    login_as_root.send_command("dacontrol -d -a")


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_command_level_mode_login_with_ad_user_anu0001_to_run_audited_command(
        log_test_name, dc_is_joined, set_da_installation, disable_da_nss, cda_login_as_aduser_0001, login_as_root,
        cda_login_am_as_domain_admin):
    """
    Login with AD user to run audited command
    """
    logger.info("--- Case C1238921")

    # Enable command auditing for 'adinfo'
    rc, result, error = login_as_root.send_command("dacontrol -e -c /usr/share/centrifydc/libexec/adinfo")
    assert rc == 0, f"Failed to enable command auditing for 'adinfo': {error}"

    # Run 'adinfo'
    time_start = get_datetime(cda_login_am_as_domain_admin)
    cda_login_as_aduser_0001.send_shell_command("adinfo")
    time_end = get_datetime(cda_login_am_as_domain_admin)

    # Restore
    rc, result, error = login_as_root.send_command("dacontrol -d -c /usr/share/centrifydc/libexec/adinfo")
    assert rc == 0, f"Failed to disable command auditing for 'adinfo': {error}"

    # Verify command auditing session
    assert verify_command_audit_session(dc_is_joined['installation_name'], "/usr/share/centrifydc/libexec/adinfo",
                                        time_start, time_end, cda_login_am_as_domain_admin), \
        "Failed to verify the command auditing session for 'adinfo'"


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_command_level_mode_login_with_local_user_to_run_audited_command(
        log_test_name, dc_is_joined, set_da_installation, disable_da_nss, cda_login_as_super, login_as_root,
        cda_login_am_as_domain_admin):
    """
    Login with local user to run audited command
    """
    logger.info("--- Case C1238923")

    # Enable command auditing for 'kill'
    rc, result, error = login_as_root.send_command("which kill")
    assert rc == 0, f"It seems there is not command 'kill' exists on the machine: {error}"
    command = (''.join(login_as_root.to_list(result))).strip()
    rc, result, error = login_as_root.send_command("dacontrol -e -c %s" % command)
    assert rc == 0, f"Failed to enable command auditing for 'kill': {error}"

    # Run 'kill -l'
    execute_command = command + " -l"
    time_start = get_datetime(cda_login_am_as_domain_admin)
    cda_login_as_super.send_shell_command(execute_command)
    time_end = get_datetime(cda_login_am_as_domain_admin)

    # Restore
    rc, result, error = login_as_root.send_command("dacontrol -d -c %s" % command)
    assert rc == 0, f"Failed to disable command auditing for 'kill': {error}"

    # Verify command auditing session
    assert verify_command_audit_session(dc_is_joined['installation_name'], execute_command, time_start, time_end,
                                        cda_login_am_as_domain_admin), \
        "Failed to verify the command auditing session for 'kill'"


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_3_3_command_level_mode_5(
        log_test_name, dc_is_joined, set_da_installation, login_as_root):
    """
    Disable audited command
    """
    logger.info("--- Case C1238926")

    login_as_root.send_command("dacontrol -e -c /usr/share/centrifydc/libexec/adinf")
    login_as_root.send_command("dacontrol -e -c `which kill`")

    rc, result, error = login_as_root.send_command("dacontrol -d -a")
    log_assert(rc == 0, f"Failed to disable auditing of all commands: {error}")
