# test_HierarchicalZoneForUnixAgent_Libaudit.py

import logging
import pytest
import time

from .common import add_centrifyda_parameters, check_pattern, get_datetime, verify_audit_event, \
    verify_monitored_file, verify_monitored_execution, verify_detailed_execution, CENTRIFYDA_CONF

logger = logging.getLogger('test')
ADVANCED_MONITORING_EVENT_NAMES = ["Monitored program is executed", "Monitored program failed to execute",
                                   "Monitored file modification attempted",
                                   "Monitored file modification attempt failed", "Command execution is started",
                                   "Command execution fails to start"]
ACCESS_STATUS_SUCCEEDED = "Succeeded"
ACCESS_STATUS_FAILED = "Failed"


###### Fixtures ######
@pytest.fixture
def zone_name():
    name = "Core_ahsz11"
    yield name


###### Helper functions ######
def remove_centrifyda_parameters(ssh, parameters):
    """
    Remove parameters from centrifyda.conf file
    """
    rc, result, error = ssh.send_command(f"cat {CENTRIFYDA_CONF}")
    for param in parameters:
        remove_line = f"{param}:"
        # Using sed -i because this function will use only in this file and this file will run on Rhel OS only
        rc, result, error = ssh.send_command(f"sed -i '/{remove_line}/d' {CENTRIFYDA_CONF}")


#### Test Cases ######

# 3.1.2.1 Enable libaudit without setting any parameters


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_3_1_2_1_enable_advance_monitoring(log_test_name, dc_is_joined, set_da_installation,
                                           login_as_root):
    """
    Enable advanced monitoring
    """
    logger.info("--- Case C1238832")

    rc, result, error = login_as_root.send_command("dacontrol -m")
    assert rc == 0, f"Failed to run 'dacontrol -m': {error}"

    rc, result, error = login_as_root.send_command("dacontrol -e")
    assert rc == 0, f"Failed to run 'dacontrol -e': {error}"

    # validating "result" as there is no value received in variable "error"
    rc, result, error = login_as_root.send_command("dainfo -q nss_status")
    assert rc == 0, f"The status of nss module is unexpected: {result}"

    rc, result, error = login_as_root.send_command("dainfo -q advanced_monitoring")
    assert rc == 0, f"The status of advanced monitoring is unexpected: {error}"

    # Restore
    login_as_root.send_command("dacontrol -n")


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_run_commands_to_generate_file_monitor_report_via_local_user(
        log_test_name, dc_is_joined, enable_advanced_monitoring, cda_login_as_normal, cda_login_am_as_domain_admin):
    """
    Run commands to generate File Monitor report via local user as well as check audit event, monitered file report
    and detailed execution report
    """
    logger.info("--- Case C1238833")

    COMMAND_LIST = ["touch /etc/ff.txt", "rm -rf /etc/ff.txt", "touch /var/centrifyda/ff.txt",
                    "rm -rf /var/centrifyda/ff.txt", "touch /var/centrifydc/ff.txt", "rm -rf /var/centrifydc/ff.txt"]
    for command_with_parameter in COMMAND_LIST:
        # Get the full path of command
        tmp_list = command_with_parameter.split(' ')
        command = tmp_list[0]
        file_path = tmp_list[-1]
        rc, result, error = cda_login_as_normal.send_command_get_list("which %s" % command)
        command_path = (''.join(result)).strip()

        # Run command
        time_start = get_datetime(cda_login_am_as_domain_admin)
        cda_login_as_normal.send_command(command_with_parameter)
        time.sleep(1)
        time_end = get_datetime(cda_login_am_as_domain_admin)

        logger.info("--- Case C1238835")

        # Verify audit event for local user
        assert verify_audit_event(dc_is_joined['installation_name'], ADVANCED_MONITORING_EVENT_NAMES[3], time_start,
                                  time_end, cda_login_am_as_domain_admin),\
            f"Failed to verify audit event for '{command_with_parameter}'"

        logger.info("--- Case C1238836, C1238837 & Case C1238838")

        # Verify report event for local user
        assert verify_monitored_file(dc_is_joined['installation_name'], command_path, file_path, ACCESS_STATUS_FAILED,
                                     time_start, time_end, cda_login_am_as_domain_admin),\
            f"Failed to verify monitored file event for '{command_with_parameter}'"


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_run_commands_to_generate_file_monitor_report_via_normal_ad_user(
        log_test_name, dc_is_joined, enable_advanced_monitoring, cda_login_as_aduser_0001,
        cda_login_am_as_domain_admin):
    """
    Run commands to generate File Monitor report via normal AD user as well as check audit event, monitered file report
    and detailed execution report
    """
    logger.info("--- Case C1238834")

    COMMAND_LIST = ["touch /etc/ff.txt", "rm -rf /etc/ff.txt", "touch /var/centrifyda/ff.txt",
                    "rm -rf /var/centrifyda/ff.txt", "touch /var/centrifydc/ff.txt", "rm -rf /var/centrifydc/ff.txt"]
    for command_with_parameter in COMMAND_LIST:
        # Get the full path of command
        tmp_list = command_with_parameter.split(' ')
        command = tmp_list[0]
        file_path = tmp_list[-1]
        rc, result, error = cda_login_as_aduser_0001.send_command_get_list("which %s" % command)
        command_path = (''.join(result)).strip()

        # Run command
        time_start = get_datetime(cda_login_am_as_domain_admin)
        cda_login_as_aduser_0001.send_command(command_with_parameter)
        time.sleep(1)
        time_end = get_datetime(cda_login_am_as_domain_admin)

        logger.info("--- Case C1238835")

        # Verify audit events for ad user
        assert verify_audit_event(dc_is_joined['installation_name'], ADVANCED_MONITORING_EVENT_NAMES[3], time_start,\
                                  time_end, cda_login_am_as_domain_admin), \
            f"Failed to verify audit event for '{command_with_parameter}'"

        logger.info("--- Case C1238836, C1238837 & Case C1238838")

        # Verify report events for ad user
        assert verify_monitored_file(dc_is_joined['installation_name'], command_path, file_path, ACCESS_STATUS_FAILED,
                                     time_start, time_end, cda_login_am_as_domain_admin),\
            f"Failed to verify monitored file event for '{command_with_parameter}'"


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_3_1_2_1_disable_advance_monitoring(
        log_test_name, dc_is_joined, enable_advanced_monitoring, login_as_root):
    """
    Disable Advanced monitoring
    """
    logger.info("--- Case C1238839")

    rc, result, error = login_as_root.send_command("dacontrol -n")
    assert rc == 0, f"Failed to run 'dacontrol -n': {error}"

    rc, result, error = login_as_root.send_command("dacontrol -d")
    assert rc == 0, f"Failed to run 'dacontrol -d': {error}"


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_enable_advance_monitoring(log_test_name, dc_is_joined, set_da_installation,
                                   login_as_root):
    """
    Enable advance monitoring
    """
    logger.info("--- Case C1238847")

    rc, result, error = login_as_root.send_command("dacontrol -m")
    assert rc == 0, f"Failed to run 'dacontrol -m': {error}"

    rc, result, error = login_as_root.send_command("dacontrol -e")
    assert rc == 0, f"Failed to run 'dacontrol -e': {error}"

    # validating "result" as there is no value received in variable "error"
    rc, result, error = login_as_root.send_command("dainfo -q nss_status")
    assert rc == 0, f"The status of nss module is unexpected: {result}"

    rc, result, error = login_as_root.send_command("dainfo -q advanced_monitoring")
    assert rc == 0, f"The status of advanced monitoring is unexpected: {error}"

    # Restore
    login_as_root.send_command("dacontrol -n")


# 3.1.2.2.1 Enable parameter: event.monitor.commands


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_3_1_2_2_1_set_event_monitor_commands(
        log_test_name, dc_is_joined, enable_advanced_monitoring, backup_centrifyda_conf, login_as_root):
    """
    Set event monitor commands
    """
    logger.info("--- Case C1238848")

    rc, result, error = login_as_root.send_command("which rm")
    assert rc == 0, f"It seems there is not command 'rm' exists on the machine: {error}"
    rm_path = (''.join(login_as_root.to_list(result))).strip()

    # Modify centrifyda.conf
    parameters = {
        'event.monitor.commands': rm_path
    }
    add_centrifyda_parameters(login_as_root, parameters)
    rc, result, error = login_as_root.send_command("dareload -m")
    assert rc == 0, f"Failed to run 'dacontrol -m': {error}"

    # Verify it via 'dainfo -c'
    rc, result, error = login_as_root.send_command("dainfo -c")
    content = ''.join(login_as_root.to_list(result))
    logger.debug(content)
    if not check_pattern(content, r"^\s*event.monitor.commands\s*:\s*{}".format(rm_path)):
        assert False, f"Failed to set 'nss.alt.zone.auditlevel' to audit_if_possible: {content}"


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_enable_event_monitor_generate_events_via_local_user(
        log_test_name, dc_is_joined, enable_advanced_monitoring, backup_centrifyda_conf, cda_login_as_normal,
        login_as_root, cda_login_am_as_domain_admin):
    """
    Run command to generate events via local user
    """
    logger.info("--- Case C1238849")

    rc, result, error = login_as_root.send_command_get_list("which rm")
    assert rc == 0, f"It seems there is not command 'rm' exists on the machine: {error}"
    rm_path = (''.join(result)).strip()

    # Modify centrifyda.conf
    parameters = {
        'event.monitor.commands': rm_path
    }
    add_centrifyda_parameters(login_as_root, parameters)
    rc, result, error = login_as_root.send_command("dareload -m")
    assert rc == 0, f"Failed to run 'dacontrol -m': {error}"

    # Run command
    time_start = get_datetime(cda_login_am_as_domain_admin)
    cda_login_as_normal.send_command("rm -rf aa")
    time.sleep(1)
    time_end = get_datetime(cda_login_am_as_domain_admin)

    # Verify audit event
    assert verify_audit_event(dc_is_joined['installation_name'], ADVANCED_MONITORING_EVENT_NAMES[0], time_start,
                              time_end, cda_login_am_as_domain_admin), "Failed to verify audit event for 'rm -rf aa'"

    logger.info("--- Case C1238852")
    # Verify monitored execution event for normal user
    assert verify_monitored_execution(dc_is_joined['installation_name'], rm_path, "rm -rf aa", ACCESS_STATUS_SUCCEEDED,\
                                      time_start, time_end, cda_login_am_as_domain_admin), \
        "Failed to verify monitored execution event for 'rm -rf aa'"


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_unset_event_monitor_commands(log_test_name, dc_is_joined, enable_advanced_monitoring,
                                      backup_centrifyda_conf, login_as_root, dainfo, dareload):
    """
    Unset event monitor commands
    """
    logger.info("--- Case C1238853")

    # Remove the below parameters if exists in centrifyda.conf file
    parameters = ["event.monitor.commands"]
    remove_centrifyda_parameters(login_as_root, parameters)

    # Reload the advanced monitoring properties via 'dareload -m'
    rc, result, error = login_as_root.send_command(f"{dareload} -m")
    assert rc == 0, f"Failed to run '{dareload} -m': {error}"

    # Verify the removed values via 'dainfo -c'
    rc, result, error = login_as_root.send_command(f"{dainfo} -c")
    expected_value = parameters[0]
    assert expected_value not in result, f"Unset event monitor command value exist '{expected_value}'"


# 3.1.2.2.2 Enable parameters: event.monitor.commands; event.monitor.commands.user.skiplist


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_set_event_monitor_commands_and_skip_users(
        log_test_name, dc_is_joined, enable_advanced_monitoring, backup_centrifyda_conf, login_as_root, dainfo,
        dareload):
    """
    Set event monitor commands and skip users
    """
    logger.info("--- Case C1238855")

    # Modify centrifyda.conf
    parameters = {
        'event.monitor.commands': "/rm_path/rm",
        'event.monitor.commands.user.skiplist': f"normal, {dc_is_joined['aduser_0001_name']}@{dc_is_joined['domain_name']}"
    }
    add_centrifyda_parameters(login_as_root, parameters)
    rc, result, error = login_as_root.send_command(f"{dareload} -m")
    assert rc == 0, f"Failed to run '{dareload} -m': {error}"
    
    # Verify it via 'dainfo -c'
    rc, result, error = login_as_root.send_command(f"{dainfo} -c")
    expected_added_values = [key + ': ' + value for key, value in parameters.items()]
    for value in expected_added_values:
        assert value in result, f"Failed to found related setting {value}"


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_3_1_2_2_2_run_commands_to_generate_events_via_local_user(
        log_test_name, dc_is_joined, enable_advanced_monitoring, backup_centrifyda_conf, cda_login_as_normal,
        login_as_root, cda_login_am_as_domain_admin):
    """
    Run command to generate events via local user
    """
    logger.info("---Case C1238856")

    rc, result, error = login_as_root.send_command("which rm")
    assert rc == 0, f"It seems there is not command 'rm' exists on the machine: {error}"
    rm_path = (''.join(login_as_root.to_list(result))).strip()

    # Modify centrifyda.conf
    parameters = {
        'event.monitor.commands': rm_path,
        'event.monitor.commands.user.skiplist': "normal"
    }
    add_centrifyda_parameters(login_as_root, parameters)
    rc, result, error = login_as_root.send_command("dareload -m")
    assert rc == 0, f"Failed to run 'dacontrol -m': {error}"

    # Run command
    time_start = get_datetime(cda_login_am_as_domain_admin)
    cda_login_as_normal.send_command("rm -rf aa")
    time.sleep(1)
    time_end = get_datetime(cda_login_am_as_domain_admin)

    logger.info("--- Case C1238858")
    # Verify monitored execution event for local user
    if verify_monitored_execution(dc_is_joined['installation_name'], rm_path, "rm -rf aa", ACCESS_STATUS_SUCCEEDED,
                                  time_start, time_end, cda_login_am_as_domain_admin):
        assert False, "The monitored execution event for 'rm -rf aa' somehow is generated, which is unexpected."


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_enable_event_monitor_user_skiplist_generate_events_via_ad_user_anu0001(
        log_test_name, dc_is_joined, enable_advanced_monitoring, backup_centrifyda_conf, cda_login_as_aduser_0001,
        login_as_root, cda_login_am_as_domain_admin):
    """
    Run command to generate events via normal AD user
    """
    logger.info("---Case C1238857")

    rc, result, error = login_as_root.send_command_get_list("which rm")
    assert rc == 0, f"It seems there is not command 'rm' exists on the machine: {error}"
    rm_path = (''.join(result)).strip()

    # Modify centrifyda.conf
    parameters = {
        'event.monitor.commands': rm_path,
        'event.monitor.commands.user.skiplist': dc_is_joined['aduser_0001_name']
    }
    add_centrifyda_parameters(login_as_root, parameters)
    rc, result, error = login_as_root.send_command("dareload -m")
    assert rc == 0, f"Failed to run 'dacontrol -m': {error}"

    # Run command
    time_start = get_datetime(cda_login_am_as_domain_admin)
    cda_login_as_aduser_0001.send_command("rm -rf aa")
    time.sleep(1)
    time_end = get_datetime(cda_login_am_as_domain_admin)

    logger.info("--- Case C1238858")
    # Verify monitored execution event for AD user
    assert not verify_monitored_execution(dc_is_joined['installation_name'], rm_path, "rm -rf aa",\
                                          ACCESS_STATUS_SUCCEEDED, time_start, time_end, cda_login_am_as_domain_admin),\
        "The monitored execution event for 'rm -rf aa' somehow is generated, which is unexpected."


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_unset_event_monitor_commands_and_skip_users(
        log_test_name, dc_is_joined, enable_advanced_monitoring, backup_centrifyda_conf, login_as_root, dainfo,
        dareload):
    """
    Unset event monitor commands and skip users
    """
    logger.info("--- Case C1238859")

    # Remove the below parameters if exists in centrifyda.conf file
    parameters = ["event.monitor.commands", "event.monitor.commands.user.skiplist"]
    remove_centrifyda_parameters(login_as_root, parameters)

    # Reload the advanced monitoring properties via 'dareload -m'
    rc, result, error = login_as_root.send_command(f"{dareload} -m")
    assert rc == 0, f"Failed to run '{dareload} -m': {error}"

    # Verify the removed values via 'dainfo -c'
    rc, result, error = login_as_root.send_command(f"{dainfo} -c")
    for param in parameters:
        assert not (param in result), f"Found the related setting {param}"


# 3.1.2.2.3 Enable parameter: event.execution.monitor


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_set_event_execution_monitor(
        log_test_name, dc_is_joined, enable_advanced_monitoring, backup_centrifyda_conf, login_as_root, dainfo,
        dareload):
    """
    Set event execution monitor
    """
    logger.info("--- Case C1238862")

    # Modify centrifyda.conf
    parameters = {
        'event.execution.monitor': "true"
    }
    add_centrifyda_parameters(login_as_root, parameters)
    rc, result, error = login_as_root.send_command(f"{dareload} -m")
    assert rc == 0, f"Failed to run '{dareload} -m': {error}"

    # Verify the added value via 'dainfo -c'
    rc, result, error = login_as_root.send_command(f"{dainfo} -c")
    expected_value = "event.execution.monitor: true"
    assert expected_value in result, f"Failed to found related setting {expected_value}"


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_enable_event_execution_monitor_generate_events_via_ad_user_anu0001(
        log_test_name, dc_is_joined, enable_da_nss, enable_advanced_monitoring, backup_centrifyda_conf,
        cda_login_as_aduser_0001, login_as_root, cda_login_am_as_domain_admin):
    """
    Run command to generate events via normal AD user
    """
    logger.info("--- Case C1238864")

    rc, result, error = login_as_root.send_command_get_list("which rm")
    assert rc == 0, f"It seems there is not command 'rm' exists on the machine: {error}"
    rm_path = (''.join(result)).strip()

    # Modify centrifyda.conf
    parameters = {
        'event.execution.monitor': "true"
    }
    add_centrifyda_parameters(login_as_root, parameters)
    rc, result, error = login_as_root.send_command("dareload -m")
    assert rc == 0, f"Failed to run 'dacontrol -m': {error}"

    # Run command
    time_start = get_datetime(cda_login_am_as_domain_admin)
    cda_login_as_aduser_0001.send_shell_command("rm -rf aa")
    time.sleep(1)
    time_end = get_datetime(cda_login_am_as_domain_admin)

    logger.info("--- Case C1238865")
    # Verify detailed execution event for AD user
    assert verify_detailed_execution(dc_is_joined['installation_name'], "rm -rf aa", rm_path, ACCESS_STATUS_SUCCEEDED,
                                     time_start, time_end, cda_login_am_as_domain_admin), \
        "Failed to verify detailed execution event for 'rm -rf aa'"


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_unset_event_execution_monitor(
        log_test_name, dc_is_joined, enable_advanced_monitoring, backup_centrifyda_conf, login_as_root, dainfo,
        dareload):
    """
    Unset event execution monitor
    """
    logger.info("--- Case C1238866")

    # Remove the below parameters if exists in centrifyda.conf file
    parameters = ["event.execution.monitor"]
    remove_centrifyda_parameters(login_as_root, parameters)

    # Reload the advanced monitoring properties via 'dareload -m'
    rc, result, error = login_as_root.send_command(f"{dareload} -m")
    assert rc == 0, f"Failed to run '{dareload} -m': {error}"

    # Verify the removed values via 'dainfo -c'
    rc, result, error = login_as_root.send_command(f"{dainfo} -c")
    expected_value = parameters[0]
    assert not (expected_value in result), f"Found the related setting {expected_value}"


# 3.1.2.2.4 Enable parameters: event.execution.monitor; event.execution.monitor.user.skiplist


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_set_event_execution_monitor_and_skip_users(
        log_test_name, dc_is_joined, enable_advanced_monitoring, backup_centrifyda_conf, login_as_root, dainfo,
        dareload):
    """
    Set event execution monitor and skip users
    """
    logger.info("--- Case C1238869")

    # Modify centrifyda.conf
    parameters = {
        'event.execution.monitor': "true",
        'event.execution.monitor.user.skiplist': f"normal, {dc_is_joined['aduser_0001_name']}@{dc_is_joined['domain_name']}"
    }
    add_centrifyda_parameters(login_as_root, parameters)
    rc, result, error = login_as_root.send_command(f"{dareload} -m")
    assert rc == 0, f"Failed to run '{dareload} -m': {error}"

    # Verify the added value via 'dainfo -c'
    rc, result, error = login_as_root.send_command(f"{dainfo} -c")
    expected_added_values = [key + ': ' + value for key, value in parameters.items()]
    for value in expected_added_values:
        assert value in result, f"Failed to found related setting {value}"


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_3_1_2_2_4_run_commands_to_generate_events_via_local_user(
        log_test_name, dc_is_joined, enable_da_nss, enable_advanced_monitoring, backup_centrifyda_conf,
        cda_login_as_normal, login_as_root, cda_login_am_as_domain_admin):
    """
    Run command to generate events via local user
    """
    logger.info("--- Case C1238870")

    rc, result, error = login_as_root.send_command("which rm")
    assert rc == 0, f"It seems there is not command 'rm' exists on the machine: {error}"
    rm_path = (''.join(login_as_root.to_list(result))).strip()

    # Modify centrifyda.conf
    parameters = {
        'event.execution.monitor': "true",
        'event.execution.monitor.user.skiplist': "normal"
    }
    add_centrifyda_parameters(login_as_root, parameters)
    rc, result, error = login_as_root.send_command("dareload -m")
    assert rc == 0, f"Failed to run 'dacontrol -m': {error}"

    # Run command
    time_start = get_datetime(cda_login_am_as_domain_admin)
    cda_login_as_normal.send_shell_command("rm -rf aa")
    time.sleep(1)
    time_end = get_datetime(cda_login_am_as_domain_admin)

    logger.info("--- Case C1238872")
    # Verify detailed execution event for normal user
    if verify_detailed_execution(dc_is_joined['installation_name'], "rm -rf aa", rm_path, ACCESS_STATUS_SUCCEEDED,
                                 time_start, time_end, cda_login_am_as_domain_admin):
        assert False, "The detailed execution event for 'rm -rf aa' somehow is generated, which is unexpected."


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_run_command_to_generate_events_via_ad_user_anu0001(
        log_test_name, dc_is_joined, enable_da_nss, enable_advanced_monitoring, backup_centrifyda_conf,
        cda_login_as_aduser_0001, login_as_root, cda_login_am_as_domain_admin):
    """
    Run command to generate events via normal AD user
    """
    logger.info("--- Case C1238871")

    rc, result, error = login_as_root.send_command_get_list("which rm")
    assert rc == 0, f"It seems there is not command 'rm' exists on the machine: {error}"
    rm_path = (''.join(result)).strip()

    # Modify centrifyda.conf
    parameters = {
        'event.execution.monitor': "true",
        'event.execution.monitor.user.skiplist': f"{dc_is_joined['aduser_0001_name']}@{dc_is_joined['domain_name']}"
    }
    add_centrifyda_parameters(login_as_root, parameters)
    rc, result, error = login_as_root.send_command("dareload -m")
    assert rc == 0, f"Failed to run 'dacontrol -m': {error}"

    # Run command
    time_start = get_datetime(cda_login_am_as_domain_admin)
    cda_login_as_aduser_0001.send_shell_command("rm -rf aa")
    time.sleep(1)
    time_end = get_datetime(cda_login_am_as_domain_admin)

    logger.info("--- Case C1238872")
    # Verify detailed execution event for AD user
    assert not verify_detailed_execution(dc_is_joined['installation_name'], "rm -rf aa", rm_path,
                                         ACCESS_STATUS_SUCCEEDED,
                                         time_start, time_end, cda_login_am_as_domain_admin), \
        "The detailed execution event for 'rm -rf aa' somehow is generated, which is unexpected."


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_enable_event_execution_monitor_and_skip_users_unset(
        log_test_name, dc_is_joined, enable_advanced_monitoring, backup_centrifyda_conf, login_as_root, dainfo,
        dareload):
    """
    Unset event execution monitor and skip users
    """
    logger.info("--- Case C1238873")

    # Remove the below parameters if exists in centrifyda.conf file
    parameters = ["event.execution.monitor", "event.execution.monitor.user.skiplist"]
    remove_centrifyda_parameters(login_as_root, parameters)

    # Reload the advanced monitoring properties via 'dareload -m'
    rc, result, error = login_as_root.send_command(f"{dareload} -m")
    assert rc == 0, f"Failed to run '{dareload} -m': {error}"

    # Verify the removed values via 'dainfo -c'
    rc, result, error = login_as_root.send_command(f"{dainfo} -c")
    for param in parameters:
        assert not (param in result), f"Found the related setting {param}"


# 3.1.2.2.5 Disable with parameter: event.file.monitor


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_set_event_file_monitor(
        log_test_name, dc_is_joined, enable_advanced_monitoring, backup_centrifyda_conf, login_as_root, dainfo,
        dareload):
    """
    Set event file monitor
    """
    logger.info("--- Case C1238876")

    # Modify centrifyda.conf
    parameters = {
        'event.file.monitor': "false"
    }
    add_centrifyda_parameters(login_as_root, parameters)
    rc, result, error = login_as_root.send_command(f"{dareload} -m")
    assert rc == 0, f"Failed to run '{dareload} -m': {error}"

    # Verify the added value via 'dainfo -c'
    rc, result, error = login_as_root.send_command(f"{dainfo} -c")
    expected_value = "event.file.monitor: false"
    assert expected_value in result, f"Failed to found related setting {expected_value}"


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_3_1_2_2_5_run_command_to_generate_events_via_local_user(
        log_test_name, dc_is_joined, enable_advanced_monitoring, backup_centrifyda_conf,
        cda_login_as_normal, login_as_root, cda_login_am_as_domain_admin):
    """
    Run command to generate events via local user
    """
    logger.info("--- Case C1238877")

    rc, result, error = login_as_root.send_command("which rm")
    assert rc == 0, f"It seems there is not command 'rm' exists on the machine: {error}"
    rm_path = (''.join(login_as_root.to_list(result))).strip()

    # Modify centrifyda.conf
    parameters = {
        'event.file.monitor': "false",
    }
    add_centrifyda_parameters(login_as_root, parameters)
    rc, result, error = login_as_root.send_command("dareload -m")
    assert rc == 0, f"Failed to run 'dacontrol -m': {error}"

    # Run command
    time_start = get_datetime(cda_login_am_as_domain_admin)
    cda_login_as_normal.send_command("rm -rf /etc/bb.txt")
    time.sleep(1)
    time_end = get_datetime(cda_login_am_as_domain_admin)

    logger.info("--- Case C1238879")
    # Verify monitored file event for normal user
    if verify_monitored_file(dc_is_joined['installation_name'], rm_path, "/etc/bb.txt", ACCESS_STATUS_FAILED,
                             time_start, time_end, cda_login_am_as_domain_admin):
        assert False, "The monitored file event for (rm -rf /etc/bb.txt) somehow is generated, which is unexpected."


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_disable_event_file_monitor_unset(
        log_test_name, dc_is_joined, enable_advanced_monitoring, backup_centrifyda_conf,
        login_as_root, dainfo, dareload):
    """
    Unset event file monitor
    """
    logger.info("--- Case C1238880")

    # Remove the below parameters if exists in centrifyda.conf file
    parameters = ["event.file.monitor"]
    remove_centrifyda_parameters(login_as_root, parameters)
    rc, result, error = login_as_root.send_command(f"{dareload} -m")
    assert rc == 0, f"Failed to run '{dareload} -m': {error}"

    # Verify the removed value via 'dainfo -c'
    rc, result, error = login_as_root.send_command(f"{dainfo} -c")
    expected_value = parameters[0]
    assert expected_value not in result, f"Unset event file monitor value exist '{expected_value}'"


# 3.1.2.2.6 Enable with parameter: event.file.monitor


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_set_event_file_monitor_1(
        log_test_name, dc_is_joined, enable_advanced_monitoring, backup_centrifyda_conf, login_as_root, dainfo,
        dareload):
    """
    Set event file monitor
    """
    logger.info("--- Case C1238883")

    # Modify centrifyda.conf
    parameters = {
        'event.file.monitor': "true"
    }
    add_centrifyda_parameters(login_as_root, parameters)
    rc, result, error = login_as_root.send_command(f"{dareload} -m")
    assert rc == 0, f"Failed to run '{dareload} -m': {error}"

    # Verify the added value via 'dainfo -c'
    rc, result, error = login_as_root.send_command(f"{dainfo} -c")
    expected_value = "event.file.monitor: true"
    assert expected_value in result, f"Failed to found related setting {expected_value}"


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_enable_event_file_monitor_generate_events_via_ad_user_anu0001(
        log_test_name, dc_is_joined, enable_advanced_monitoring, backup_centrifyda_conf,
        cda_login_as_aduser_0001, login_as_root, cda_login_am_as_domain_admin):
    """
    Run command to generate events via normal AD user
    """
    logger.info("--- Case C1238885")

    rc, result, error = login_as_root.send_command_get_list("which rm")
    assert rc == 0, f"It seems there is not command 'rm' exists on the machine: {error}"
    rm_path = (''.join(result)).strip()

    # Modify centrifyda.conf
    parameters = {
        'event.file.monitor': "true",
    }
    add_centrifyda_parameters(login_as_root, parameters)
    rc, result, error = login_as_root.send_command("dareload -m")
    assert rc == 0, f"Failed to run 'dacontrol -m': {error}"

    # Run command
    time_start = get_datetime(cda_login_am_as_domain_admin)
    cda_login_as_aduser_0001.send_command("rm -rf /etc/bb.txt")
    time.sleep(1)
    time_end = get_datetime(cda_login_am_as_domain_admin)

    logger.info("--- Case C1238886")
    # Verify monitored file event for AD user
    assert not verify_monitored_file(dc_is_joined['installation_name'], rm_path, "/etc/bb.txt", ACCESS_STATUS_FAILED,
                                 time_start, time_end, cda_login_am_as_domain_admin),\
        "Failed to verify monitored file event for 'rm -rf /etc/bb.txt'"


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_enable_event_file_monitor_unset(log_test_name, dc_is_joined, enable_advanced_monitoring, backup_centrifyda_conf,\
                                  login_as_root, dainfo, dareload):
    """
    Unset event file monitor
    """
    logger.info("--- Case C1238887")

    # Remove the below parameters from centrifyda.conf file
    parameters = ["event.file.monitor"]
    remove_centrifyda_parameters(login_as_root, parameters)

    # Reload the advanced monitoring properties via 'dareload -m'
    rc, result, error = login_as_root.send_command(f"{dareload} -m")
    assert rc == 0, f"Failed to run '{dareload} -m': {error}"

    # Verify the removed values via 'dainfo -c'
    rc, result, error = login_as_root.send_command(f"{dainfo} -c")
    expected_value = parameters[0]
    assert expected_value not in result, f"Unset event file monitor value exist '{expected_value}'"


# 3.1.2.2.7 Enable with parameters: event.file.monitor; event.file.monitor.user.skiplist

@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_set_event_file_monitor_event_file_monitor_user_skiplist(
        log_test_name, dc_is_joined, enable_advanced_monitoring,
        backup_centrifyda_conf, login_as_root, dainfo, dareload):
    """
    Set event file monitor and event.file.monitor.user.skiplist
    """
    logger.info("--- Case C1238890")

    # Modify centrifyda.conf
    parameters = {
        'event.file.monitor': "true",
        'event.file.monitor.user.skiplist':
            f"normal, {dc_is_joined['aduser_0001_name']}@{dc_is_joined['domain_name']}"
    }
    add_centrifyda_parameters(login_as_root, parameters)
    rc, result, error = login_as_root.send_command(f"{dareload} -m")
    assert rc == 0, f"Failed to run '{dareload} -m': {error}"

    # Verify the added value using 'dainfo -c'
    rc, result, error = login_as_root.send_command(f"{dainfo} -c")
    expected_added_values = [key + ': ' + value for key, value in parameters.items()]
    for value in expected_added_values:
        assert value in result, f"Failed to set event file monitor '{value}'"


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_3_1_2_2_7_run_command_to_generate_events_via_local_user(
        log_test_name, dc_is_joined, enable_advanced_monitoring, backup_centrifyda_conf,
        cda_login_as_normal, login_as_root, cda_login_am_as_domain_admin):
    """
    Run command to generate events via local user
    """
    logger.info("--- Case C1238891")

    rc, result, error = login_as_root.send_command("which rm")
    assert rc == 0, f"It seems there is not command 'rm' exists on the machine: {error}"
    rm_path = (''.join(login_as_root.to_list(result))).strip()

    # Modify centrifyda.conf
    parameters = {
        'event.file.monitor': "true",
        'event.file.monitor.user.skiplist': "normal"
    }
    add_centrifyda_parameters(login_as_root, parameters)
    rc, result, error = login_as_root.send_command("dareload -m")
    assert rc == 0, f"Failed to run 'dacontrol -m': {error}"

    # Run command
    time_start = get_datetime(cda_login_am_as_domain_admin)
    cda_login_as_normal.send_command("rm -rf /etc/cc.txt")
    time.sleep(1)
    time_end = get_datetime(cda_login_am_as_domain_admin)

    # Verify monitored file event
    if verify_monitored_file(dc_is_joined['installation_name'], rm_path, "/etc/cc.txt", ACCESS_STATUS_FAILED,
                             time_start, time_end, cda_login_am_as_domain_admin):
        assert False, "The monitored file event for (rm -rf /etc/cc.txt) somehow is generated, which is unexpected."


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_enable_event_file_monitor_user_skiplist_generate_events_via_ad_user_anu0001(
        log_test_name, dc_is_joined, enable_advanced_monitoring, backup_centrifyda_conf,
        cda_login_as_aduser_0001, login_as_root, cda_login_am_as_domain_admin):
    """
    Run command to generate events via normal AD user
    """
    logger.info("--- Case C1238892")

    rc, result, error = login_as_root.send_command_get_list("which rm")
    assert rc == 0, f"It seems there is not command 'rm' exists on the machine: {error}"
    rm_path = (''.join(result)).strip()

    # Modify centrifyda.conf
    parameters = {
        'event.file.monitor': "true",
        'event.file.monitor.user.skiplist': dc_is_joined['aduser_0001_name']
    }
    add_centrifyda_parameters(login_as_root, parameters)
    rc, result, error = login_as_root.send_command("dareload -m")
    assert rc == 0, f"Failed to run 'dacontrol -m': {error}"

    # Run command
    time_start = get_datetime(cda_login_am_as_domain_admin)
    cda_login_as_aduser_0001.send_command("rm -rf /etc/cc.txt")
    time.sleep(1)
    time_end = get_datetime(cda_login_am_as_domain_admin)

    # Verify monitored file event
    assert not verify_monitored_file(dc_is_joined['installation_name'], rm_path, "/etc/cc.txt", ACCESS_STATUS_FAILED,
                             time_start, time_end, cda_login_am_as_domain_admin),\
        "The monitored file event for (rm -rf /etc/cc.txt) somehow is generated, which is unexpected."


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_3_1_2_2_7_run_command_to_generate_events_via_root(
        log_test_name, dc_is_joined, enable_advanced_monitoring, backup_centrifyda_conf,
        cda_login_as_normal, login_as_root, cda_login_am_as_domain_admin):
    """
    Run command to generate events via root
    """
    logger.info("--- Case C1238893")

    rc, result, error = login_as_root.send_command("which rm")
    assert rc == 0, f"It seems there is not command 'rm' exists on the machine: {error}"
    rm_path = (''.join(login_as_root.to_list(result))).strip()

    # Modify centrifyda.conf
    parameters = {
        'event.file.monitor': "true",
        'event.file.monitor.process.skiplist': rm_path
    }
    add_centrifyda_parameters(login_as_root, parameters)
    rc, result, error = login_as_root.send_command("dareload -m")
    assert rc == 0, f"Failed to run 'dacontrol -m': {error}"

    # Run command
    time_start = get_datetime(cda_login_am_as_domain_admin)
    cda_login_as_normal.send_command("rm -rf /etc/cc.txt")
    time.sleep(1)
    time_end = get_datetime(cda_login_am_as_domain_admin)

    # Verify monitored file event
    if verify_monitored_file(dc_is_joined['installation_name'], rm_path, "/etc/cc.txt", ACCESS_STATUS_FAILED,
                             time_start, time_end, cda_login_am_as_domain_admin):
        assert False, "The monitored file event for (rm -rf /etc/cc.txt) somehow is generated, which is unexpected."


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_enable_event_file_monitor_and_user_skiplist_unset(
        log_test_name, dc_is_joined, enable_advanced_monitoring, backup_centrifyda_conf, login_as_root, dainfo,
        dareload):
    """
    Unset event file monitor and event.file.monitor.user.skiplist
    """
    logger.info("--- Case C1238895")

    # Remove the below parameters if exists in centrifyda.conf file
    parameters = ["event.file.monitor", "event.file.monitor.user.skiplist"]
    remove_centrifyda_parameters(login_as_root, parameters)

    # Reload the advanced monitoring properties via 'dareload -m'
    rc, result, error = login_as_root.send_command(f"{dareload} -m")
    assert rc == 0, f"Failed to run '{dareload} -m': {error}"

    # Verify the removed values via 'dainfo -c'
    rc, result, error = login_as_root.send_command(f"{dainfo} -c")
    for param in parameters:
        assert not (param in result), f"Found the related setting {param}"


# 3.1.2.2.8 Enable with parameters: event.file.monitor; event.file.monitor.process.skiplist

@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_set_event_file_monitor_event_file_monitor_process_skiplist(
        log_test_name, dc_is_joined, enable_advanced_monitoring,
        backup_centrifyda_conf, login_as_root, dainfo, dareload):
    """
    Set event file monitor and event.file.monitor.process.skiplist
    """
    logger.info("--- Case C1238897")
    # Modify centrifyda.conf
    parameters = {
        'event.file.monitor': "true",
        'event.file.monitor.process.skiplist': "/usr/bin/touch"
    }
    add_centrifyda_parameters(login_as_root, parameters)
    rc, result, error = login_as_root.send_command(f"{dareload} -m")
    assert rc == 0, f"Failed to run '{dareload} -m': {error}"
    # Verify the added value using 'dainfo -c'
    rc, result, error = login_as_root.send_command(f"{dainfo} -c")
    expected_added_values = [key + ': ' + value for key, value in parameters.items()]
    for value in expected_added_values:
        assert value in result, f"Failed to set event file monitor and process '{value}'"


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_enable_event_file_monitor_process_skiplist_generate_events_via_local_user_normal(
        log_test_name, dc_is_joined, enable_advanced_monitoring, backup_centrifyda_conf,
        cda_login_as_normal, login_as_root, cda_login_am_as_domain_admin):
    """
    Run command to generate events via local user
    """
    logger.info("--- Case C1238898")

    # Modify centrifyda.conf
    parameters = {
        'event.file.monitor': "true",
        'event.file.monitor.process.skiplist': "/usr/bin/touch"
    }
    add_centrifyda_parameters(login_as_root, parameters)
    rc, result, error = login_as_root.send_command("dareload -m")
    assert rc == 0, f"Failed to run 'dacontrol -m': {error}"

    commands = ["touch /etc/rr.txt", "rm -rf /etc/rr.txt"]
    for cmd in commands:
        # Get the full path of command
        tmp_list = cmd.split(' ')
        command = tmp_list[0]
        file_path = tmp_list[-1]
        rc, result, error = cda_login_as_normal.send_command_get_list("which %s" % command)
        command_path = (''.join(result)).strip()

        # Run command
        time_start = get_datetime(cda_login_am_as_domain_admin)
        cda_login_as_normal.send_command(cmd)
        time.sleep(1)
        time_end = get_datetime(cda_login_am_as_domain_admin)

        logger.info("--- Case C1238901")
        
        # Verify monitored file event for normal user
        assert not verify_monitored_file(dc_is_joined['installation_name'], command_path, file_path,\
                                         ACCESS_STATUS_FAILED, time_start, time_end, cda_login_am_as_domain_admin), \
            f"The monitored file event for '{cmd}' somehow is generated, which is unexpected."


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_enable_event_file_monitor_process_skiplist_unset_user_skiplist(
        log_test_name, dc_is_joined, enable_advanced_monitoring,
        backup_centrifyda_conf, login_as_root, dainfo, dareload):
    """
    Unset event file monitor and event.file.monitor.user.skiplist
    """
    logger.info("--- Case C1238902")

    # Remove the below parameters if exists in centrifyda.conf file
    parameters = ["event.file.monitor", "event.file.monitor.process.skiplist"]

    # Remove the added parameters from centrifyda.conf file
    remove_centrifyda_parameters(login_as_root, parameters)

    # Reload the advanced monitoring using 'dareload -m'
    rc, result, error = login_as_root.send_command(f"{dareload} -m")
    assert rc == 0, f"Failed to run '{dareload} -m': {error}"

    # Verify the removed values using 'dainfo -c'
    rc, result, error = login_as_root.send_command(f"{dainfo} -c")
    for param in parameters:
        assert not (param in result), f"Event file monitor value exist '{param}'"


@pytest.mark.bhavna
@pytest.mark.css
@pytest.mark.da_unix_bat
def test_disable_advance_monitoring(log_test_name, dc_is_joined, enable_advanced_monitoring,
                                    login_as_root, dacontrol):
    """
    Disable Advance monitoring
    """
    logger.info("--- Case C1238903")

    # To disable Advance Monitoring
    rc, result, error = login_as_root.send_command(f"{dacontrol} -n")
    assert rc == 0, f"Failed to run '{dacontrol} -n': {error}"

    # To disable Direct Audit
    rc, result, error = login_as_root.send_command(f"{dacontrol} -d")
    assert rc == 0, f"Failed to run '{dacontrol} -d': {error}"
