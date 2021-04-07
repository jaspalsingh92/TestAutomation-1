# test_ClassicZoneForUnixAgent_AuditLevel.py

import logging
import pytest

from .common import add_centrifyda_parameters, check_pattern, get_da_session_id

logger = logging.getLogger('test')
COMMAND_LIST_COMMON = ["id", "echo $DA_AUDIT"]


###### Fixtures ######
@pytest.fixture
def zone_name():
    name = "Core_acsz1"
    yield name


@pytest.fixture
def set_alt_zone_auditlevel_noaudit(backup_centrifyda_conf, login_as_root):
    parameters = {
        'nss.alt.zone.auditlevel': "no_audit"
    }
    add_centrifyda_parameters(login_as_root, parameters)
    rc, result, error = login_as_root.send_command("dareload")
    if rc != 0:
        raise Exception("Fail to run 'dareload'")


@pytest.fixture
def set_alt_zone_auditlevel_auditifpossible(backup_centrifyda_conf, login_as_root):
    parameters = {
        'nss.alt.zone.auditlevel': "audit_if_possible"
    }
    add_centrifyda_parameters(login_as_root, parameters)
    rc, result, error = login_as_root.send_command("dareload")
    if rc != 0:
        raise Exception("Fail to run 'dareload'")


##### Test Cases ######


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
@pytest.mark.incomplete
def test_enable_nss_module(log_test_name, dc_is_joined, disable_da_nss, login_as_root):
    """
    Enable NSS module
    """
    logger.info("--- Case C1239009")

    rc, result, error = login_as_root.send_command("dacontrol -e")
    assert rc == 0, f"Failed to run 'dacontrol -e': {error}"

    rc, result, error = login_as_root.send_command("dainfo -q nss_status")
    assert rc == 0, f"NSS module is not enabled successfully: {error}"


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_audit_level_as_no_audit(log_test_name, dc_is_joined, backup_centrifyda_conf, login_as_root):
    """
    Set audit level as "no audit" in centrifyda.conf
    """
    logger.info("--- Case C1239010")

    parameters = {
        'nss.alt.zone.auditlevel': "no_audit"
    }
    add_centrifyda_parameters(login_as_root, parameters)
    rc, result, error = login_as_root.send_command("dareload")
    assert rc == 0, f"Failed to run 'dareload': {error}"

    rc, result, error = login_as_root.send_command("dainfo -c")
    content = ''.join(login_as_root.to_list(result))
    logger.debug(content)
    if not check_pattern(content, r"^\s*nss.alt.zone.auditlevel:\s*no_audit"):
        assert False, f"Failed to set 'nss.alt.zone.auditlevel' to no_audit: {content}"


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_ad_user_audit_status(log_test_name, dc_is_joined, enable_da_nss,
                              set_alt_zone_auditlevel_noaudit, login_as_root):
    """
    Check AD user's audited status
    """
    logger.info("--- Case C1239011")

    rc, result, error = login_as_root.send_command("dainfo -u %s" % dc_is_joined['aduser_0001_name'])
    assert rc == 0, f"Failed to run 'dainfo -u': {error}"
    content = ''.join(login_as_root.to_list(result))
    logger.debug(content)
    if not check_pattern(content, r"audited status:\s*No", True):
        assert False, f"The audited status of %s is unexpected: {content}"


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_ad_user_run_commands(log_test_name, dc_is_installed, dc_is_joined, enable_da_nss,
                              set_alt_zone_auditlevel_noaudit, cda_login_as_aduser_0001):
    """
    Login with AD user to run commands
    """
    logger.info("--- Case C1239013")

    # Get DA_SESSION_ID
    da_session_id = get_da_session_id(cda_login_as_aduser_0001)

    if da_session_id is None:
        logger.info("Environment variable DA_SESSION_ID does not exist in this session, which is expected.")
    else:
        assert False, f"This session is somehow audited (session ID: {da_session_id}), which is unexpected."


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_audit_level_as_audit_if_possible(log_test_name, dc_is_joined, enable_da_nss,
                                          backup_centrifyda_conf, login_as_root):
    """
    Set audit level as "audit if possible" in centrifyda.conf
    """
    logger.info("--- Case C1239016")

    parameters = {
        'nss.alt.zone.auditlevel': "audit_if_possible"
    }
    add_centrifyda_parameters(login_as_root, parameters)
    rc, result, error = login_as_root.send_command("dareload")
    assert rc == 0, f"Failed to run 'dareload': {error}"

    rc, result, error = login_as_root.send_command("dainfo -c")
    content = ''.join(login_as_root.to_list(result))
    logger.debug(content)
    if not check_pattern(content, r"^\s*nss.alt.zone.auditlevel\s*:\s*audit_if_possible"):
        assert False, f"Failed to set 'nss.alt.zone.auditlevel' to audit_if_possible: {content}"


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_local_user_audit_status(log_test_name, dc_is_joined, enable_da_nss,
                                 set_alt_zone_auditlevel_auditifpossible, login_as_root):
    """
    Check local user's audited status
    """
    logger.info("--- Case C1239018")

    rc, result, error = login_as_root.send_command("dainfo -u normal")
    assert rc == 0, error
    content = ''.join(login_as_root.to_list(result))
    logger.debug(content)
    if not check_pattern(content, r"audited status:\s*Yes", True):
        assert False, f"The audited status of normal is unexpected: {error}"


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_local_user_run_commands(log_test_name, dc_is_joined, enable_da_nss,
                                 set_alt_zone_auditlevel_noaudit, cda_login_as_normal):
    """
    Login with local user to run commands
    """
    logger.info("--- Case C1239020")

    # Get DA_SESSION_ID
    da_session_id = get_da_session_id(cda_login_as_normal)

    if da_session_id is None:
        logger.info("Environment variable DA_SESSION_ID does not exist in this session, which is expected.")
    else:
        assert False, f"This session is somehow audited (session ID: {da_session_id}), which is unexpected."


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_core_dump_file(log_test_name, dc_is_joined, login_as_root):
    """
    Check core dump file
    """
    logger.info("--- Case C1239022")

    rc, result, error = login_as_root.send_command("ls -al /var/centrify* | grep core* | wc -l")
    content = ''.join(login_as_root.to_list(result))
    if int(content.strip()) != 0:
        assert False, "There is core dump file is generated. Please check it!!!"


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_leave_domain(log_test_name, dc_is_joined, login_as_root):
    """
    Leave domain
    """
    logger.info("--- Case C1239023")

    rc, result, error = login_as_root.send_command("adleave -u Administrator -p %s" % dc_is_joined['admin_password'])
    assert rc == 0, f"Failed to run 'adleave': {error}"
