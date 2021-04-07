# test_HierarchicalZoneForUnixAgent_AuditLevel.py

import logging
import pytest
import time

from Shared.css_utils import log_assert
from .common import check_pattern, get_da_session_id, verify_shell_audit_session, check_ssh_login

logger = logging.getLogger('test')

COMMAND_LIST_COMMON = ["adinfo", "dainfo", "id"]
AUDIT_IF_POSSIBLE_PATTERN = r"Audit level:\s+AuditIfPossible"
AUDIT_REQUIRED_PATTERN = r"Audit level:\s+AuditRequired"
AUDIT_NOT_REQUESTED_PATTERN = r"Audit level:\s+AuditNotRequested"
RESCURE_RIGHT_TRUE_PATTERN = r"Always permit login:\s+true"
RESCURE_RIGHT_FALSE_PATTERN = r"Always permit login:\s+false"


###### Fixtures ######


@pytest.fixture
def zone_name():
    name = "Core_ahsz11"
    yield name


#### Test Cases ######


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_3_4_audit_level_1(
        log_test_name, dc_is_joined, login_as_root):
    """
    Check audit level for different AD users
    """
    logger.info("--- Case C1238934")

    rc, result, error = login_as_root.send_command("dzinfo %s" % dc_is_joined['aduser_0032_name'])
    log_assert(rc == 0, f"Failed to run dzinfo: {error}")
    content = ''.join(login_as_root.to_list(result))
    logger.debug(content)
    if not check_pattern(content, AUDIT_NOT_REQUESTED_PATTERN, True) or not \
            check_pattern(content, RESCURE_RIGHT_FALSE_PATTERN, True):
        log_assert(False, f"Unexpected result from dzinfo: {content}")

    rc, result, error = login_as_root.send_command("dzinfo %s" % dc_is_joined['aduser_0033_name'])
    log_assert(rc == 0, f"Failed to run dzinfo: {error}")
    content = ''.join(login_as_root.to_list(result))
    logger.debug(content)
    if not check_pattern(content, AUDIT_IF_POSSIBLE_PATTERN, True) or not \
            check_pattern(content, RESCURE_RIGHT_FALSE_PATTERN, True):
        log_assert(False, f"Unexpected result from dzinfo: {content}")

    rc, result, error = login_as_root.send_command("dzinfo %s" % dc_is_joined['aduser_2001_name'])
    log_assert(rc == 0, f"Failed to run dzinfo: {error}")
    content = ''.join(login_as_root.to_list(result))
    logger.debug(content)
    if not check_pattern(content, AUDIT_REQUIRED_PATTERN, True) or not \
            check_pattern(content, RESCURE_RIGHT_FALSE_PATTERN, True):
        log_assert(False, f"Unexpected result from dzinfo: {content}")

    rc, result, error = login_as_root.send_command("dzinfo %s" % dc_is_joined['aduser_2002_name'])
    log_assert(rc == 0, f"Failed to run dzinfo: {error}")
    content = ''.join(login_as_root.to_list(result))
    logger.debug(content)
    if not check_pattern(content, AUDIT_REQUIRED_PATTERN, True) or not \
            check_pattern(content, RESCURE_RIGHT_TRUE_PATTERN, True):
        log_assert(False, f"Unexpected result from dzinfo: {content}")

    rc, result, error = login_as_root.send_command("dzinfo %s" % dc_is_joined['aduser_2004_name'])
    log_assert(rc == 0, f"Failed to run dzinfo: {error}")
    content = ''.join(login_as_root.to_list(result))
    logger.debug(content)
    if not check_pattern(content, AUDIT_IF_POSSIBLE_PATTERN, True) or not \
            check_pattern(content, RESCURE_RIGHT_TRUE_PATTERN, True):
        log_assert(False, f"Unexpected result from dzinfo: {content}")


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_check_audit_level_for_different_local_users(
        log_test_name, dc_is_joined, login_as_root):
    """
    Check audit level for different local users
    """
    logger.info("--- Case C1238935")

    rc, result, error = login_as_root.send_command_get_list("dzinfo blocal1")
    assert rc == 0, f"Failed to run dzinfo: {error}"
    content = ''.join(result)
    logger.debug(content)
    assert check_pattern(content, AUDIT_NOT_REQUESTED_PATTERN, True) or\
           check_pattern(content, RESCURE_RIGHT_FALSE_PATTERN, True), f"Unexpected result from dzinfo: {content}"

    rc, result, error = login_as_root.send_command_get_list("dzinfo blocal2")
    assert rc == 0, f"Failed to run dzinfo: {error}"
    content = ''.join(result)
    logger.debug(content)
    assert check_pattern(content, AUDIT_NOT_REQUESTED_PATTERN, True) or\
           check_pattern(content, RESCURE_RIGHT_FALSE_PATTERN, True), f"Unexpected result from dzinfo: {content}"

    rc, result, error = login_as_root.send_command_get_list("dzinfo blocal3")
    assert rc == 0, f"Failed to run dzinfo: {error}"
    content = ''.join(result)
    logger.debug(content)
    assert check_pattern(content, AUDIT_REQUIRED_PATTERN, True) or\
           check_pattern(content, RESCURE_RIGHT_FALSE_PATTERN, True), f"Unexpected result from dzinfo: {content}"

    rc, result, error = login_as_root.send_command_get_list("dzinfo blocal5")
    assert rc == 0, f"Failed to run dzinfo: {error}"
    content = ''.join(result)
    logger.debug(content)
    assert check_pattern(content, AUDIT_REQUIRED_PATTERN, True) or\
           check_pattern(content, RESCURE_RIGHT_TRUE_PATTERN, True), f"Unexpected result from dzinfo: {content}"
    
    rc, result, error = login_as_root.send_command_get_list("dzinfo blocal6")
    assert rc == 0, f"Failed to run dzinfo: {error}"
    content = ''.join(result)
    logger.debug(content)
    assert check_pattern(content, AUDIT_IF_POSSIBLE_PATTERN, True) or\
           check_pattern(content, RESCURE_RIGHT_TRUE_PATTERN, True), f"Unexpected result from dzinfo: {content}"


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_3_4_1_nss_is_active_1(
        log_test_name, dc_is_joined, set_da_installation, login_as_root):
    """
    Enable NSS module
    """
    logger.info("--- Case C1238937")

    rc, result, error = login_as_root.send_command("dacontrol -e")
    log_assert(rc == 0, f"Failed to run 'dacontrol -e': {error}")

    rc, result, error = login_as_root.send_command("dainfo -q nss_status")
    log_assert(rc == 0, f"NSS module is not enabled successfully: {error}")


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_nss_active_login_with_ad_user_anu0032_to_run_commands(
        log_test_name, dc_is_joined, set_da_installation, enable_da_nss, cda_login_as_aduser_0032, adinfo, dainfo):
    """
    Login with AD user who has the following sysrights:
        Audit level: AuditNotRequested
        Always permit login: false
    """
    logger.info("--- Case C1238938")

    rc, result, error = cda_login_as_aduser_0032.send_command(f"{adinfo}")
    assert rc == 0, f"Failed to run '{adinfo}': {error}"

    rc, result, error = cda_login_as_aduser_0032.send_command(f"{dainfo}")
    assert rc == 0, f"Failed to run '{dainfo}': {error}"

    rc, result, error = cda_login_as_aduser_0032.send_command("id")
    assert rc == 0, f"Failed to run 'id': {error}"

    # Get DA_SESSION_ID
    da_session_id = get_da_session_id(cda_login_as_aduser_0032)
    assert da_session_id is None, f"This session is somehow audited (session ID: {da_session_id}), which is unexpected."


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_nss_active_login_with_ad_user_anu0033_to_run_commands(
        log_test_name, dc_is_joined, set_da_installation, enable_da_nss, cda_login_as_aduser_0033,
        cda_login_am_as_domain_admin):
    """
    Login with AD user who has the following sysrights:
        Audit level: AuditIfPossible
        Always permit login: false
    """
    logger.info("--- Case C1238939")

    # Get DA_SESSION_ID
    da_session_id = get_da_session_id(cda_login_as_aduser_0033)
    assert da_session_id is not None,\
        f"Environment variable 'DA_SESSION_ID' does not exist in this session, which is unexpected."

    # Run some commands
    for command in COMMAND_LIST_COMMON:
        cda_login_as_aduser_0033.send_shell_command(command)
        time.sleep(1)

    # Verify shell auditing session
    assert verify_shell_audit_session(dc_is_joined['installation_name'], da_session_id, COMMAND_LIST_COMMON,
                                      cda_login_am_as_domain_admin),\
        f"Failed to verify the shell auditing session for user {dc_is_joined['aduser_0033_name']}"


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_nss_active_login_with_ad_user_anu2001_to_run_commands(
        log_test_name, dc_is_joined, set_da_installation, enable_da_nss, cda_login_as_aduser_2001,
        cda_login_am_as_domain_admin):
    """
    Login with AD user who has the following sysrights:
        Audit level: AuditRequired
        Always permit login: false
    """
    logger.info("--- Case C1238940")

    # Get DA_SESSION_ID
    da_session_id = get_da_session_id(cda_login_as_aduser_2001)
    assert da_session_id is not None, \
        f"Environment variable 'DA_SESSION_ID' does not exist in this session, which is unexpected."

    # Run some commands
    for command in COMMAND_LIST_COMMON:
        cda_login_as_aduser_2001.send_shell_command(command)
        time.sleep(1)

    # Verify shell auditing session
    assert verify_shell_audit_session(dc_is_joined['installation_name'], da_session_id, COMMAND_LIST_COMMON,
                                      cda_login_am_as_domain_admin),\
        f"Failed to verify the shell auditing session for user {dc_is_joined['aduser_2001_name']}"


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_nss_active_login_with_ad_user_anu2002_to_run_commands(
        log_test_name, dc_is_joined, set_da_installation, enable_da_nss, cda_login_as_aduser_2002,
        cda_login_am_as_domain_admin):
    """
    Login with AD user who has the following sysrights:
        Audit level: AuditRequired
        Always permit login: true
    """
    logger.info("--- Case C1238941")

    # Get DA_SESSION_ID
    da_session_id = get_da_session_id(cda_login_as_aduser_2002)
    assert da_session_id is not None, \
        f"Environment variable 'DA_SESSION_ID' does not exist in this session, which is unexpected."

    # Run some commands
    for command in COMMAND_LIST_COMMON:
        cda_login_as_aduser_2002.send_shell_command(command)
        time.sleep(1)

    # Verify shell auditing session
    assert verify_shell_audit_session(dc_is_joined['installation_name'], da_session_id, COMMAND_LIST_COMMON,
                                      cda_login_am_as_domain_admin),\
        f"Failed to verify the shell auditing session for user {dc_is_joined['aduser_2002_name']}"


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_nss_active_login_with_ad_user_anu2004_to_run_commands(
        log_test_name, dc_is_joined, set_da_installation, enable_da_nss, cda_login_as_aduser_2004,
        cda_login_am_as_domain_admin):
    """
    Login with AD user who has the following sysrights:
        Audit level: AuditIfPossible
        Always permit login: true
    """
    logger.info("--- Case C1238942")

    # Get DA_SESSION_ID
    da_session_id = get_da_session_id(cda_login_as_aduser_2004)
    assert da_session_id is not None,\
        f"Environment variable 'DA_SESSION_ID' does not exist in this session, which is unexpected."

    # Run some commands
    for command in COMMAND_LIST_COMMON:
        cda_login_as_aduser_2004.send_shell_command(command)
        time.sleep(1)

    # Verify shell auditing session
    assert verify_shell_audit_session(dc_is_joined['installation_name'], da_session_id, COMMAND_LIST_COMMON,
                                      cda_login_am_as_domain_admin),\
        f"Failed to verify the shell auditing session for user {dc_is_joined['aduser_2004_name']}"


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_nss_is_active_login_with_local_user_blocal1_to_run_commands(
        log_test_name, dc_is_joined, set_da_installation, enable_da_nss, dainfo, adinfo, cda_login_as_blocal1):
    """
    Login with local user who has the following sysrights:
        Audit level: AuditNotRequested
        Always permit login: false
    """
    logger.info("--- Case C1238943")

    rc, result, error = cda_login_as_blocal1.send_command(f"{adinfo}")
    assert rc == 0, f"Failed to run '{adinfo}': {error}"

    rc, result, error = cda_login_as_blocal1.send_command(f"{dainfo}")
    assert rc == 0, f"Failed to run '{dainfo}': {error}"

    rc, result, error = cda_login_as_blocal1.send_command("id")
    assert rc == 0, f"Failed to run 'id': {error}"

    # Get DA_SESSION_ID
    da_session_id = get_da_session_id(cda_login_as_blocal1)

    assert da_session_id is None, f"This session is somehow audited (session ID: {da_session_id}), which is unexpected."


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_nss_active_login_with_local_user_blocal2_to_run_commands(
        log_test_name, dc_is_joined, set_da_installation, enable_da_nss, cda_login_as_blocal2,
        cda_login_am_as_domain_admin):
    """
    Login with local user who has the following sysrights:
        Audit level: AuditIfPossible
        Always permit login: false
    """
    logger.info("--- Case C1238944")

    # Get DA_SESSION_ID
    da_session_id = get_da_session_id(cda_login_as_blocal2)
    assert da_session_id is not None,\
        f"Environment variable 'DA_SESSION_ID' does not exist in this session, which is unexpected."

    # Run some commands
    for command in COMMAND_LIST_COMMON:
        cda_login_as_blocal2.send_shell_command(command)
        time.sleep(1)

    # Verify shell auditing session
    assert verify_shell_audit_session(dc_is_joined['installation_name'], da_session_id, COMMAND_LIST_COMMON,
                                      cda_login_am_as_domain_admin),\
        f"Failed to verify the shell auditing session for user blocal2"


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_nss_active_login_with_local_user_blocal3_to_run_commands(
        log_test_name, dc_is_joined, set_da_installation, enable_da_nss, cda_login_as_blocal3,
        cda_login_am_as_domain_admin):
    """
    Login with local user who has the following sysrights:
        Audit level: AuditRequired
        Always permit login: false
    """
    logger.info("--- Case C1238945")

    # Get DA_SESSION_ID
    da_session_id = get_da_session_id(cda_login_as_blocal3)
    assert da_session_id is not None,\
        f"Environment variable 'DA_SESSION_ID' does not exist in this session, which is unexpected."

    # Run some commands
    for command in COMMAND_LIST_COMMON:
        cda_login_as_blocal3.send_shell_command(command)
        time.sleep(1)

    # Verify shell auditing session
    assert verify_shell_audit_session(dc_is_joined['installation_name'], da_session_id, COMMAND_LIST_COMMON,
                                      cda_login_am_as_domain_admin), \
        f"Failed to verify the shell auditing session for user blocal3"


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_nss_active_login_with_local_user_blocal5_to_run_commands(
        log_test_name, dc_is_joined, set_da_installation, enable_da_nss, cda_login_as_blocal5,
        cda_login_am_as_domain_admin):
    """
    Login with local user who has the following sysrights:
        Audit level: AuditRequired
        Always permit login: true
    """
    logger.info("--- Case C1238946")

    # Get DA_SESSION_ID
    da_session_id = get_da_session_id(cda_login_as_blocal5)
    assert da_session_id is not None,\
        f"Environment variable 'DA_SESSION_ID' does not exist in this session, which is unexpected."

    # Run some commands
    for command in COMMAND_LIST_COMMON:
        cda_login_as_blocal5.send_shell_command(command)
        time.sleep(1)

    # Verify shell auditing session
    assert verify_shell_audit_session(dc_is_joined['installation_name'], da_session_id, COMMAND_LIST_COMMON,
                                      cda_login_am_as_domain_admin),\
        f"Failed to verify the shell auditing session for user blocal5"


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_nss_active_login_with_local_user_blocal6_to_run_commands(
        log_test_name, dc_is_joined, set_da_installation, enable_da_nss, cda_login_as_blocal6,
        cda_login_am_as_domain_admin):
    """
    Login with local user who has the following sysrights:
        Audit level: AuditIfPossible
        Always permit login: true
    """
    logger.info("--- Case C1238947")

    # Get DA_SESSION_ID
    da_session_id = get_da_session_id(cda_login_as_blocal6)
    assert da_session_id is not None,\
        f"Environment variable 'DA_SESSION_ID' does not exist in this session, which is unexpected."

    # Run some commands
    for command in COMMAND_LIST_COMMON:
        cda_login_as_blocal6.send_shell_command(command)
        time.sleep(1)

    # Verify shell auditing session
    assert  verify_shell_audit_session(dc_is_joined['installation_name'], da_session_id, COMMAND_LIST_COMMON,
                                       cda_login_am_as_domain_admin),\
        f"Failed to verify the shell auditing session for user blocal6"


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_3_4_2_nss_is_inactive_1(
        log_test_name, dc_is_joined, set_da_installation, login_as_root):
    """
    Disable NSS module
    """
    logger.info("--- Case C1238952")

    rc, result, error = login_as_root.send_command("dacontrol -d")
    log_assert(rc == 0, f"Failed to run 'dacontrol -d': {error}")

    rc, result, error = login_as_root.send_command("dainfo -q nss_status")
    log_assert(rc == 1, f"NSS module is not disabled successfully: {error}")


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_nss_inactive_login_with_ad_user_anu0032_to_run_commands(
        log_test_name, dc_is_joined, set_da_installation, disable_da_nss, cda_login_as_aduser_0032, adinfo, dainfo):
    """
    Login with AD user who has the following sysrights:
        Audit level: AuditNotRequested
        Always permit login: false
    """
    logger.info("--- Case C1238953")

    # Get DA_SESSION_ID
    da_session_id = get_da_session_id(cda_login_as_aduser_0032)
    assert da_session_id is None, f"This session is somehow audited (session ID: {da_session_id}), which is unexpected."


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_nss_inactive_login_with_ad_user_anu0033_to_run_commands(
        log_test_name, dc_is_joined, set_da_installation, disable_da_nss, cda_login_as_aduser_0033, adinfo, dainfo):
    """
    Login with AD user who has the following sysrights:
        Audit level: AuditIfPossible
        Always permit login: false
    """
    logger.info("--- Case C1238954")

    # Get DA_SESSION_ID
    da_session_id = get_da_session_id(cda_login_as_aduser_0033)
    assert da_session_id is None, f"This session is somehow audited (session ID: {da_session_id}), which is unexpected."


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_3_4_2_nss_is_inactive_4(
        log_test_name, dc_is_joined, set_da_installation, disable_da_nss, css_test_machine):
    """
    Login with AD user who has the following sysrights:
        Audit level: AuditRequired
        Always permit login: false
    """
    logger.info("--- Case C1238955")

    if check_ssh_login(css_test_machine['public_ip'], dc_is_joined['aduser_2001_name'],
                       dc_is_joined['common_password']):
        log_assert(False, "Login the machine as (%s) somehow succeeded, which is unexpected." % dc_is_joined[
            'aduser_2001_name'])


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_nss_inactive_login_with_ad_user_anu2002_to_run_commands(
        log_test_name, dc_is_joined, set_da_installation, disable_da_nss, cda_login_as_aduser_2002):
    """
    Login with AD user who has the following sysrights:
        Audit level: AuditRequired
        Always permit login: true
    """
    logger.info("--- Case C1238956")

    # Get DA_SESSION_ID
    da_session_id = get_da_session_id(cda_login_as_aduser_2002)
    assert da_session_id is None, f"This session is somehow audited (session ID: {da_session_id}), which is unexpected."


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_nss_inactive_login_with_ad_user_anu2004_to_run_commands(
        log_test_name, dc_is_joined, set_da_installation, disable_da_nss, cda_login_as_aduser_2004):
    """
    Login with AD user who has the following sysrights:
        Audit level: AuditIfPossible
        Always permit login: true
    """
    logger.info("--- Case C1238957")

    # Get DA_SESSION_ID
    da_session_id = get_da_session_id(cda_login_as_aduser_2004)
    assert da_session_id is None, f"This session is somehow audited (session ID: {da_session_id}), which is unexpected."


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_nss_inactive_login_with_local_user_blocal1_to_run_commands(
        log_test_name, dc_is_joined, set_da_installation, disable_da_nss, cda_login_as_blocal1):
    """
    Login with local user who has the following sysrights:
        Audit level: AuditNotRequested
        Always permit login: false
    """
    logger.info("--- Case C1238958")

    # Get DA_SESSION_ID
    da_session_id = get_da_session_id(cda_login_as_blocal1)

    assert da_session_id is None, f"This session is somehow audited" \
                                  f" (session ID: {da_session_id}), which is unexpected."


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_nss_inactive_login_with_local_user_blocal2_to_run_commands(
        log_test_name, dc_is_joined, set_da_installation, disable_da_nss, cda_login_as_blocal2):
    """
    Login with local user who has the following sysrights:
        Audit level: AuditIfPossible
        Always permit login: false
    """
    logger.info("--- Case C1238959")

    # Get DA_SESSION_ID
    da_session_id = get_da_session_id(cda_login_as_blocal2)

    assert da_session_id is None, f"This session is somehow audited" \
                                  f" (session ID: {da_session_id}), which is unexpected."


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_3_4_2_nss_is_inactive_9(
        log_test_name, dc_is_joined, set_da_installation, disable_da_nss, css_test_machine):
    """
    Login with local user who has the following sysrights:
        Audit level: AuditRequired
        Always permit login: false
    """
    logger.info("--- Case C1238960")

    if check_ssh_login(css_test_machine['public_ip'], "blocal3", css_test_machine['blocal3_password']):
        log_assert(False, "Login the machine as blocal3 somehow succeeded, which is unexpected.")


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_nss_is_inactive_login_with_local_user_blocal5_to_run_commands(
        log_test_name, dc_is_joined, set_da_installation, disable_da_nss, cda_login_as_blocal5):
    """
    Login with local user who has the following sysrights:
        Audit level: AuditRequired
        Always permit login: true
    """
    logger.info("--- Case C1238961")

    # Get DA_SESSION_ID
    da_session_id = get_da_session_id(cda_login_as_blocal5)

    assert da_session_id is None, f"This session is somehow audited (session ID: {da_session_id}), which is unexpected."


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_nss_is_inactive_login_with_local_user_blocal6_to_run_commands(
        log_test_name, dc_is_joined, set_da_installation, disable_da_nss, cda_login_as_blocal6):
    """
    Login with local user who has the following sysrights:
        Audit level: AuditIfPossible
        Always permit login: true
    """
    logger.info("--- Case C1238962")

    # Get DA_SESSION_ID
    da_session_id = get_da_session_id(cda_login_as_blocal6)
        
    assert da_session_id is None, f"This session is somehow audited (session ID: {da_session_id}), which is unexpected."
