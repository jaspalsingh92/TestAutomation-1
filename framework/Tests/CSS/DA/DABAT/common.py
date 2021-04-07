# common.py for DABAT

import collections
import logging
import pytest
import re
from pathlib import Path
from uuid import UUID


from Utils.putty_util import pexpect_ssh_login
from Utils.ssh_util import SshUtil
from Utils.config_loader import Configs
from .constants import CENTRIFYDA_CONF
from Shared.CSS import css_win_constants
from Shared.CSS.css_win_utils import *



logger = logging.getLogger('framework')

settings = Configs.get_test_node("da_installation", "settings")
med_retry = settings['med_retry']
vry_small_retry = settings['vry_small_retry']
small_retry = settings['small_retry']
remote_framework_path = css_win_constants.remote_framework_path
directory_path = Path(__file__).resolve().parent
file_path = str(directory_path).split("framework\\", maxsplit=1)[1]

def ssh_login(hostname, user, password):
    """
    Ssh login to the machine with username/password

    :param hostname: Machine hostname or IP
    :param user: User that logs in the machine
    :param password: User password
    :return: SshUtil object
    """
    ssh_config = collections.namedtuple('ssh_config',
                                        ('hostname port username '
                                         'rsa_key_file password'))
    config = ssh_config(hostname = hostname,
                        port = 22,
                        username = user,
                        rsa_key_file = "",
                        password = password)
    logger.debug("ssh instantiated for user %s" % user)
    return SshUtil(config)

def add_centrifyda_parameters(ssh, parameters):
    """
    Add parameters to centrifyda.conf

    :param ssh: ssh session to be used
    :param parameters: Parameters to be added as dictionary
    """
    for key in parameters:
        line = "%s: %s" % (key, parameters[key])
        logger.debug("Add parameter %s" % line)
        ssh.send_command("echo %s >> %s" % (line, CENTRIFYDA_CONF))

def check_ssh_login(hostname, user, password):
    """
    Check if ssh login is OK

    :param hostname: Machine hostname or IP
    :param user: User that logs in the machine
    :param password: User password
    :return: True if user can log in the machine
    """
    child = pexpect_ssh_login(hostname, user, password)
    if child:
        child.sendline("exit")
    return child is not None


def get_da_session_id(ssh):
    """
    Get the value of environment variable DA_SESSION_ID

    :param ssh: ssh session to be used
    :return: the vaule of environment variable DA_SESSION_ID or None
    """
    result = ssh.send_shell_command("echo $DA_SESSION_ID")
    logger.debug("The output of 'echo $DA_SESSION_ID': %s" % result)
    # The second element of output is supposed to be the value of DA_SESSION_ID
    # , the last one is the shell prompt.
    if len(result) < 2:
        return None
    da_session_id = result[1]
    try:
        UUID(da_session_id)
    except Exception:
        return None

    return da_session_id


def verify_shell_audit_session(
    installation_name, da_session_id, command_list, winrm):
    """
    Verify if the shell audit session with specified session Id is generated on Windows side

    :param installation_name: DA installation name
    :param da_session_id: DA session ID
    :param command_list: The commands are ran in the session
    :param winrm: winrm session to be used
    :return: True if the audit session can be found and the indexed commands are matched
    """
    rc, result, error = winrm.send_command(("powershell.exe -command \"Get-CdaAuditSession -Installation %s " 
                                            "-SessionId %s | Get-CdaUnixCommand | foreach {$_.Command}\"")
                                            % (installation_name, da_session_id))
    logger.debug("CMD: Get-CdaAuditSession, OUT: {}, ERR: {}, RET: {}".format(result, error, rc))
    if rc != 0:
        logger.info("Failed to get the shell audit session.")
        return False

    command_list_result = result.decode('utf-8').splitlines()

    # remove the commands with the beginning '!' (e.g. !d, !-2 ...)
    for command in command_list[:]:
        if command[0] == '!':
            command_list.remove(command)

    logger.debug("The indexed commands: %s" % command_list_result)
    if set(command_list).issubset(set(command_list_result)):
        logger.debug("The audit session with session ID (%s) is generated successfully." % da_session_id)
        return True
    else:
        logger.debug("The audit session with session ID (%s) is not generated or the indexed commands are unexpected." % da_session_id)
        return False

def verify_command_audit_session(
    installation_name, command, time_start, time_end, winrm):
    """
    Verify if the command audit session is generated on Windows side

    :param installation_name: DA installation name
    :param command: Audited command
    :param time_start: The timestamp of starting to run the command
    :param time_end: The timestamp of ending to run the command
    :param winrm: winrm session to be used
    :return: True if the session can be found in the specified time interval and the indexed command is matched
    """
    rc, result, error = winrm.send_command(("powershell.exe -command \"Get-CdaAuditSession -Installation %s "
                                            "-TimeBetween \'%s\',\'%s\' | Get-CdaUnixCommand | foreach {$_.Command}\"")
                                            % (installation_name, time_start, time_end))
    logger.debug("CMD: Get-CdaAuditSession, TimeBetween: {} - {}, OUT: {}, ERR: {}, RET: {}".format(time_start, time_end, result, error, rc))
    if rc != 0:
        logger.info("Failed to get the command audit session.")
        return False

    command_result = result.strip().decode('utf-8')
    logger.debug("The indexed command: %s" % command_result)
    if command_result == command:
        logger.debug("The command (%s) audit session is generated successfully." % command)
        return True
    else:
        logger.debug("The command (%s) audit session is not generated or the indexed command is unexpected." % command)
        return False

def verify_monitored_file(
    installation_name, command_path, file_name, access_status, time_start, time_end, winrm):
    """
    Verify if the specified monitored file event is generated on Windows side

    :param installation_name: DA installation name
    :param command_path: The path of command
    :param file_name: The file name
    :param access_status: The status of accessing (e.g. Succeeded or Failed)
    :param time_start: The timestamp of starting to run the command
    :param time_end: The timestamp of ending to run the command
    :param winrm: winrm session to be used
    :return: True if the monitored file event can be found in the specified timeinterval
    """
    rc, result, error = winrm.send_command(("powershell.exe -command \"Get-CdaMonitoredFile -Installation %s "
                                            "-TimeBetween \'%s\',\'%s\' | foreach {$_.Command + ',' + $_.FileName + ',' + $_.AccessStatus}\"")
                                            % (installation_name, time_start, time_end))
    logger.debug("CMD: Get-CdaMonitoredFile, TimeBetween: {} - {}, OUT: {}, ERR: {}, RET: {}".format(time_start, time_end, result, error, rc))
    if rc != 0:
        logger.info("Failed to get the monitored file event.")
        return False

    monitored_file_result = result.decode('utf-8').splitlines()
    logger.debug("The monitored file event: %s" % monitored_file_result)
    for monitored_file in monitored_file_result:
        properties = monitored_file.split(',')
        if command_path == properties[0].strip() and file_name == properties[1].strip() and access_status == properties[2].strip():
            logger.debug("The monitored file event (%s) is generated successfully." % command_path)
            return True

    logger.debug("The monitored file event (%s) is not generated." % command_path)
    return False

def verify_audit_event(
    installation_name, event_name, time_start, time_end, winrm):
    """
    Verify if the specified audit event is generated on Windows side

    :param installation_name: DA installation name
    :param event_name: The name of audit event
    :param time_start: The timestamp of starting to run the command
    :param time_end: The timestamp of ending to run the command
    :param winrm: winrm session to be used
    :return: True if the audit event can be found in the specified timeinterval
    """
    rc, result, error = winrm.send_command(("powershell.exe -command \"Get-CdaAuditEvent -Installation %s "
                                            "-TimeBetween \'%s\',\'%s\' | foreach {$_.EventName}\"")
                                            % (installation_name, time_start, time_end))
    logger.debug("CMD: Get-CdaAuditEvent, TimeBetween: {} - {}, OUT: {}, ERR: {}, RET: {}".format(time_start, time_end, result, error, rc))
    if rc != 0:
        logger.info("Failed to get the audit event.")
        return False

    event_name_result = result.decode('utf-8').splitlines()
    logger.debug("The audit event name: %s" % event_name_result)
    if event_name in event_name_result:
        logger.debug("The audit event (%s) is generated successfully." % event_name)
        return True
    else:
        logger.debug("The audit event (%s) is not generated." % event_name)
        return False

def verify_monitored_execution(
    installation_name, command_path, command_arguments, access_status, time_start, time_end, winrm):
    """
    Verify if the specified monitored execution event is generated on Windows side

    :param installation_name: DA installation name
    :param command_path: The path of command
    :param command_arguments: The argument of the command
    :param access_status: The status of accessing (e.g. Succeeded or Failed)
    :param time_start: The timestamp of starting to run the command
    :param time_end: The timestamp of ending to run the command
    :param winrm: winrm session to be used
    :return: True if the monitored file event can be found in the specified timeinterval
    """
    rc, result, error = winrm.send_command(("powershell.exe -command \"Get-CdaMonitoredExecution -Installation %s "
                                            "-TimeBetween \'%s\',\'%s\' | foreach {$_.Command + ',' + $_.CommandArguments + ',' + $_.AccessStatus}\"")
                                            % (installation_name, time_start, time_end))
    logger.debug("CMD: Get-CdaMonitoredExecution, TimeBetween: {} - {}, OUT: {}, ERR: {}, RET: {}".format(time_start, time_end, result, error, rc))
    if rc != 0:
        logger.info("Failed to get the monitored execution event.")
        return False

    monitored_execution_result = result.decode('utf-8').splitlines()
    logger.debug("The monitored execution event: %s" % monitored_execution_result)
    for monitored_execution in monitored_execution_result:
        properties = monitored_execution.split(',')
        if command_path == properties[0].strip() and command_arguments == properties[1].strip() and access_status == properties[2].strip():
            logger.debug("The monitored execution event (%s) is generated successfully." % command_path)
            return True

    logger.debug("The monitored execution event (%s) is not generated." % command_path)
    return False

def verify_detailed_execution(
    installation_name, entered_command, executed_command, access_status, time_start, time_end, winrm):
    """
    Verify if the specified detailed execution event is generated on Windows side

    :param installation_name: DA installation name
    :param entered_command: The full command was ran
    :param executed_command: The command path
    :param access_status: The status of accessing (e.g. Succeeded or Failed)
    :param time_start: The timestamp of starting to run the command
    :param time_end: The timestamp of ending to run the command
    :param winrm: winrm session to be used
    :return: True if the monitored file event can be found in the specified timeinterval
    """
    rc, result, error = winrm.send_command(("powershell.exe -command \"Get-CdaDetailedExecution -Installation %s "
                                            "-TimeBetween \'%s\',\'%s\' | foreach {$_.EnteredCommand + ',' + $_.ExecutedCommand + ',' + $_.AccessStatus}\"")
                                            % (installation_name, time_start, time_end))
    logger.debug("CMD: CdaDetailedExecution, TimeBetween: {} - {}, OUT: {}, ERR: {}, RET: {}".format(time_start, time_end, result, error, rc))
    if rc != 0:
        logger.info("Failed to get the detailed execution event.")
        return False

    detailed_execution_result = result.decode('utf-8').splitlines()
    logger.debug("The detailed execution event name: %s" % detailed_execution_result)
    for detailed_execution in detailed_execution_result:
        properties = detailed_execution.split(',')
        if entered_command == properties[0].strip() and executed_command == properties[1].strip() and access_status == properties[2].strip():
            logger.debug("The detailed execution event (%s) is generated successfully." % entered_command)
            return True

    logger.debug("The detailed execution event (%s) is not generated." % entered_command)
    return False

def check_pattern(content, pattern, ignorecase = False):
    """
    Check if the regular expression pattern exist in the content.

    :param content: The content to be checked
    :param pattern: the regular expression pattern
    :return: True if the pattern is in the content.
    """
    found = False
    flags = re.MULTILINE
    if ignorecase:
        flags |= re.IGNORECASE
    x = re.search(pattern, content, flags)
    if x:
        found = True
    return found

def get_datetime(winrm):
    """
    Get the current date and time of the winrm target machine

    :param winrm: winrm session to be used
    :return: The current date and time
    """
    rc, result, error = winrm.send_command("powershell.exe -command Get-Date")
    result = result.strip().decode('utf-8')
    return result


class SessionType(Enum):
    """
    This enum is use for session type
    """
    UNIX_session = "UNIX session"
    Linux_Desktop_session = "Linux Desktop session"
    Windows_session = "Windows session"


def create_query_func(dsk_session, query_name, session_list: list) -> WebElement:
    """
    Use this function to create shared query with specific type and time
    """
    logger.info("Launching the Analyzer")
    launch_application(css_win_constants.da_auditor_startup_path)
    ok_centrify_license_dlg(dsk_session)
    main_desktop = get_desktop()

    main_app_win = try_find_element(main_desktop, FindElementBy.CLASS, 'MMCMainFrame', small_retry)
    console_win = try_find_element(main_app_win, FindElementBy.AUTOMATION_ID, '12785', med_retry)
    click_hold(main_desktop, console_win)
    audit_session_tr_itm = try_find_element(console_win, FindElementBy.NAME, 'Audit Sessions', small_retry)

    # Create new shared query
    click_context_menu(main_desktop, audit_session_tr_itm, "New Shared Query...")
    shared_query_win = try_find_element(main_desktop, FindElementBy.AUTOMATION_ID, 'NewQuery', small_retry)
    try_find_element(shared_query_win, FindElementBy.AUTOMATION_ID, 'm_nameTxt', small_retry).send_keys(
        query_name)

    # Select the session for this shared query
    for session in session_list:
        double_click(main_desktop, try_find_element(shared_query_win, FindElementBy.NAME, session.value, small_retry))

    # Add time and type criteria for shared query
    query_criteria_btn = try_find_element(shared_query_win, FindElementBy.AUTOMATION_ID,
                                          'm_btnAddCriteria', small_retry)
    double_click(main_desktop, query_criteria_btn)
    criteria_win = try_find_element(shared_query_win, FindElementBy.CLASS,
                                    'WindowsForms10.Window.8.app.0.141b42a_r43_ad1', small_retry)

    time_cbox = try_find_element(criteria_win, FindElementBy.AUTOMATION_ID, 'm_timeNormalOpList',
                                 small_retry)
    click_hold(main_desktop, time_cbox)
    time_attribute_itm = try_find_element(main_desktop, FindElementBy.NAME, 'Is after', small_retry)
    if time_attribute_itm is not None:
        click_hold(main_desktop, time_attribute_itm)

    click_hold(main_desktop,
               try_find_element(criteria_win, FindElementBy.AUTOMATION_ID, 'm_btnOK', med_retry))
    double_click(main_desktop, query_criteria_btn)

    attribute_cbox = try_find_element(criteria_win, FindElementBy.AUTOMATION_ID, 'm_attrBox', small_retry)

    click_hold(main_desktop, attribute_cbox)
    review_status_itm = try_find_element(main_desktop, FindElementBy.NAME, 'Review Status', med_retry)
    click_hold(main_desktop, review_status_itm)

    equality_cbox = try_find_element(criteria_win, FindElementBy.AUTOMATION_ID, 'm_opBox', small_retry)
    click_hold(main_desktop, equality_cbox)
    not_equals_itm = try_find_element(main_desktop, FindElementBy.NAME, 'Not equals', med_retry)
    click_hold(main_desktop, not_equals_itm)

    review_value_itm = try_find_element(criteria_win, FindElementBy.NAME, 'None', small_retry)
    click_hold(main_desktop, review_value_itm)
    review_itm = try_find_element(main_desktop, FindElementBy.NAME, 'Reviewed', med_retry)
    click_hold(main_desktop, review_itm)

    click_hold(main_desktop,
               try_find_element(criteria_win, FindElementBy.AUTOMATION_ID, 'm_btnOK', med_retry))
    click_hold(main_desktop, try_find_element(shared_query_win, FindElementBy.AUTOMATION_ID, 'm_okBtn', med_retry))

    # Check the console node tree
    console_win = try_find_element(main_desktop, FindElementBy.AUTOMATION_ID, '12785', med_retry)
    double_click(main_desktop, console_win)
    if try_find_element(console_win, FindElementBy.NAME, query_name, small_retry, ignore_if_not_found=True) is None:
        double_click(main_desktop, audit_session_tr_itm)
        shared_queries_tr_itm = try_find_element(audit_session_tr_itm, FindElementBy.NAME, 'Shared Queries',
                                                 small_retry)
        double_click(main_desktop, shared_queries_tr_itm)
    else:
        pass
    shared_query_itm = try_find_element(console_win, FindElementBy.NAME, query_name, small_retry)

    #  Close the Audit Analyzer app
    click_hold(main_desktop, try_find_element(main_app_win, FindElementBy.NAME, 'Close', small_retry))

    return shared_query_itm


class ReportType(Enum):
    """
    This enum use for report type
    """
    user_report = "Login by User Report"
    file_report = "File Monitor Report"
    monitored_report = "Monitored Execution Report"
    detailed_report = "Detailed Execution Report"
    privileged_activity_report = "Privileged Activity Report"


def create_reports_func(report_type, dsk_session: WebDriver) -> tuple:
    """
    To create the any type of reports (User report, File monitor report, etc.)
    """
    launch_application(css_win_constants.da_auditor_startup_path)
    ok_centrify_license_dlg(dsk_session)
    main_desktop = get_desktop()
    main_app_win = try_find_element(main_desktop, FindElementBy.CLASS, 'MMCMainFrame', small_retry)
    console_win = try_find_element(main_app_win, FindElementBy.AUTOMATION_ID, '12785', small_retry)
    reports_tr_itm = try_find_element(console_win, FindElementBy.NAME, 'Reports', med_retry)

    # Open the report page
    if try_find_element(reports_tr_itm, FindElementBy.NAME, report_type.value, small_retry, True) is None:
        double_click(main_desktop, reports_tr_itm)

    report_tr_itm = try_find_element(reports_tr_itm, FindElementBy.NAME, report_type.value, small_retry)
    click_context_menu(main_desktop, report_tr_itm, "Create New Report")

    return reports_tr_itm, main_app_win, main_desktop, report_tr_itm


def launch_and_close_applications(application_path, class_name, dialog=False):
    """
    To launch the application and close it
    """
    main_desktop = get_desktop()
    logger.info("Launching the application")
    launch_application(application_path)
    if dialog:
        ok_centrify_license_dlg(main_desktop)
    main_app_win = try_find_element(main_desktop, FindElementBy.CLASS, class_name, small_retry)
    #  Close the app
    logger.info("Closing the application")
    click_hold(main_desktop, try_find_element(main_app_win, FindElementBy.NAME, 'Close', med_retry))


def login_and_execute_cmds(user_name, user_password, public_ip, css_win_login, file_name, class_name, func_name):
    """
    To open the rdp session of machine and execute the command
    """
    try:
        # close all the running RDP session
        rdp_kill_all()
        error_list = []
        start_slave_cmd = f"cd {remote_framework_path} & " \
                          f"python -m pytest {file_path}\\{file_name}::" \
                          f"{class_name}::{func_name}"
        # Initiating the RDP session of test machine
        rdp_session(user_name, user_password, public_ip)
        # Execute the command on slave machine
        rc, result, error = css_win_login.send_command(start_slave_cmd)
        if rc == 0:
            logger.info("Test Passed: " + str(result))
        else:
            logger.info("Test Failed: " + str(error))
            error_list.append([rc, result, error])
        assert len(error_list) == 0, "Test Failed"
    except Exception as error:
        raise Exception(f"{class_name}/{func_name} : {error}")
    finally:
        rdp_kill_all()
        for data in error_list:
            logger.info("Info: rc=%s  result=%  error=%s", str(data[0]), str(data[1]), str(data[2]))
        logger.info(f"{func_name} finished")


class AuditEventType(Enum):
    """
    This enum is used for audit event type
    """
    Advanced_Monitoring = "Advanced Monitoring"
    Login_Event = "Login Event"
    Centrify_UNIX_Command = "Centrify UNIX Command"


def select_audit_tree_item(dsk_session, tree_item_val) -> tuple:
    """
    Use this function to launch audit analyzer and open tree item nodes to operate on
    """
    logger.info("Launching the Analyzer")
    launch_application(css_win_constants.da_auditor_startup_path)
    ok_centrify_license_dlg(dsk_session)
    audit_tr_itm = get_da_analyser_node(dsk_session, tree_item_val)
    open_tree_node(dsk_session, audit_tr_itm)

    return audit_tr_itm


def create_audit_event_function(dsk_session, audit_event_query_name, audit_event_list: list, css_testee_machine) -> WebElement:
    """
    Use this function to create audit event with specific type and time
    """
    audit_tr_itm = select_audit_tree_item(dsk_session, 'Audit Events')
    click_context_menu(dsk_session, audit_tr_itm, "Query Audit Events...")
    audit_event_query_win = try_find_element(dsk_session, FindElementBy.NAME, 'Query Audit Events',\
                                             small_retry)
    try_find_element(audit_event_query_win, FindElementBy.AUTOMATION_ID, 'm_nameTxt', small_retry).send_keys(
        audit_event_query_name)

    # Select the machine box and enter full windows machine name
    full_machine_name = r"%s.%s" % (css_testee_machine['hostname'], css_testee_machine['domain_name'])
    try_find_element(dsk_session, FindElementBy.AUTOMATION_ID, 'm_machineName',
                     med_retry).send_keys(full_machine_name)

    # Check the Event time checkbox and select the time
    try_find_element(audit_event_query_win, FindElementBy.AUTOMATION_ID, 'cb_eventTime', med_retry).click()
    try_find_element(audit_event_query_win, FindElementBy.AUTOMATION_ID, 'm_timeNormalOpList', med_retry).click()
    time_lst_itm = try_find_element(dsk_session, FindElementBy.NAME, 'Is after', med_retry)
    if time_lst_itm is not None:
        time_lst_itm.click()

    # Select Audit Event Type
    try_find_element(dsk_session, FindElementBy.AUTOMATION_ID, 'cb_eventType', med_retry).click()
    try_find_element(dsk_session, FindElementBy.AUTOMATION_ID, 'btn_eventType', med_retry).click()

    # Select the session for this  query

    audit_event_type_win = try_find_element(dsk_session, FindElementBy.NAME, 'Select Audit Event Type(s)', small_retry)
    audit_event_options_win = try_find_element(dsk_session, FindElementBy.AUTOMATION_ID, 'checkedListBox1', small_retry)
    for audit_event in audit_event_list:
        double_click(dsk_session, try_find_element(audit_event_options_win, FindElementBy.NAME, audit_event.value,\
                                                    small_retry))
    try_find_element(audit_event_type_win, FindElementBy.AUTOMATION_ID, 'btn_OK', small_retry).click()

    try_find_element(audit_event_query_win, FindElementBy.AUTOMATION_ID, 'btn_Ok', small_retry).click()

    # Check the console node tree
    console_win = try_find_element(dsk_session, FindElementBy.AUTOMATION_ID, '12785', med_retry)
    double_click(dsk_session, console_win)
    if try_find_element(audit_tr_itm, FindElementBy.NAME, audit_event_query_name, \
                        small_retry, ignore_if_not_found=True) is None:
        double_click(dsk_session, audit_tr_itm)
    audit_event_itm = try_find_element(audit_tr_itm, FindElementBy.NAME, audit_event_query_name, med_retry)

    #  Close the Audit Analyzer app
    main_app_win = try_find_element(dsk_session, FindElementBy.CLASS, 'MMCMainFrame', small_retry)
    try_find_element(main_app_win, FindElementBy.NAME, 'Close', small_retry).click()
    return audit_event_itm


class AuditType(Enum):
    audit_event = "Audit Events"
    shared_query = "Shared Queries"
    audit_sessions = "Audit Sessions"
    reports = "Reports"


def validate_sessions(query_name, command_list, host_name, domain_name, users: list, get_user, dsk_session: WebDriver, \
                     audit_type, sub_type=None):
    """
    To replay audit session and verify audit event commands
    """
    audit_tr_itm = select_audit_tree_item(dsk_session, audit_type)
    if sub_type:
        shared_queries_tr_itm = try_find_element(audit_tr_itm, FindElementBy.NAME, sub_type, small_retry)
        double_click(dsk_session, shared_queries_tr_itm)

    shared_query_itm = try_find_element(audit_tr_itm, FindElementBy.NAME, query_name, small_retry)
    double_click(dsk_session, shared_query_itm)
    session_list_win = try_find_element(dsk_session, FindElementBy.AUTOMATION_ID, '12786', med_retry)
    double_click(dsk_session, session_list_win)

    for user in users:
        if user in get_user or user == 'Administrator':
            username = user + "@" + domain_name
        elif audit_type == 'Audit Sessions' and user == 'root':
            username = user + "@" + host_name + "." + domain_name
        else:
            username = user + "@" + host_name

        user_txt = try_find_element(session_list_win, FindElementBy.NAME, username, small_retry)
        assert user_txt.is_displayed() == True, "Machine name is not displaying"

        # Open session replay
        double_click(dsk_session, user_txt)
        session_player_win = try_find_element(dsk_session, FindElementBy.NAME, 'Centrify DirectAudit Session Player',
                                              small_retry)

        # Verify audit event commands of the session
        events_lstview = try_find_element(session_player_win, FindElementBy.CLASS, 'ListView', small_retry)
        double_click(dsk_session, events_lstview)
        session_events = {}
        for cmd in command_list:
            cmd_txt = try_find_element(session_player_win, FindElementBy.NAME, cmd, small_retry).is_displayed()
            session_events[cmd] = cmd_txt

        # Close replay session player
        try_find_element(session_player_win, FindElementBy.AUTOMATION_ID, 'CloseButton', small_retry).click()

    #  Close the Audit Analyzer app
    main_app_win = try_find_element(dsk_session, FindElementBy.CLASS, "MMCMainFrame", small_retry)
    try_find_element(main_app_win, FindElementBy.NAME, 'Close', small_retry).click()
    return session_events


def validate_event_file(query_name, domain_name, user, get_user, dsk_session: WebDriver, host_name=None,
                        windows_session=False):
    """
    Get event list from exported file
    """
    status_file = os.path.join(os.environ["HOMEPATH"], "Desktop", "session.csv")
    if os.path.exists(status_file):
        os.remove(status_file)
    audit_tr_itm = select_audit_tree_item(dsk_session, 'Audit Sessions')
    shared_queries_tr_itm = try_find_element(audit_tr_itm, FindElementBy.NAME, 'Shared Queries',
                                             small_retry)
    double_click(dsk_session, shared_queries_tr_itm)
    shared_query_itm = try_find_element(audit_tr_itm, FindElementBy.NAME, query_name, small_retry)
    double_click(dsk_session, shared_query_itm)
    session_list_win = try_find_element(dsk_session, FindElementBy.AUTOMATION_ID, '12786', med_retry)
    double_click(dsk_session, session_list_win)

    # Verify user name
    if user in get_user or user == 'Administrator':
        username = user + "@" + domain_name
    else:
        username = user + "@" + host_name + "." + domain_name
    user_txt = try_find_element(dsk_session, FindElementBy.NAME, username, small_retry)

    # Export audit session
    if windows_session:
        click_context_menu(dsk_session, user_txt, 'Export to Event List...')
        export_win = try_find_element(dsk_session, FindElementBy.NAME, 'Export to Event List', med_retry)
    else:
        click_context_menu(dsk_session, user_txt, 'Export to Command List...')
        export_win = try_find_element(dsk_session, FindElementBy.NAME, 'Export to Command List', med_retry)
    double_click(dsk_session, export_win)
    file_name_txt = try_find_element(export_win, FindElementBy.CLASS, 'Edit', small_retry)
    clear_txtbox(file_name_txt)
    file_name_txt.send_keys(status_file)
    try_find_element(export_win, FindElementBy.NAME, 'Save', small_retry).click()

    # Update review status to Reviewed
    double_click(dsk_session, session_list_win)
    click_context_menu(dsk_session, user_txt, 'Update Review Status', 'Reviewed')
    add_comments_win = try_find_element(dsk_session, FindElementBy.AUTOMATION_ID, 'AddComments', small_retry)

    # Enter review comment
    try_find_element(add_comments_win, FindElementBy.AUTOMATION_ID, 'comment', small_retry).send_keys('Reviewed by tester')
    try_find_element(add_comments_win, FindElementBy.AUTOMATION_ID, 'okButton', small_retry).click()
    review_comment = try_find_element(dsk_session, FindElementBy.NAME, 'Reviewed by tester', small_retry, True)
    right_scroll_arrow = try_find_element(session_list_win, FindElementBy.NAME, 'Column right', small_retry)

    # Scroll to comment column and get Review status and comment column value
    while not review_comment.is_displayed():
        double_click(dsk_session, right_scroll_arrow)
    review_comment = review_comment.is_displayed()
    review_status = try_find_element(session_list_win, FindElementBy.NAME, 'Reviewed', small_retry).is_displayed()

    # Close audit analyzer
    try_find_element(dsk_session, FindElementBy.NAME, 'Close', small_retry).click()

    # Get content from exported file
    file_content = file_read(status_file)
    return file_content, review_comment, review_status


def validate_session_exist(query_name, display_name_lst, dsk_session: WebDriver):
    """
    Return list of boolean values, true if session is not created else return false on the basis of display name list
    """
    audit_tr_itm = select_audit_tree_item(dsk_session, 'Audit Sessions')
    shared_queries_tr_itm = try_find_element(audit_tr_itm, FindElementBy.NAME, 'Shared Queries',
                                             small_retry)
    double_click(dsk_session, shared_queries_tr_itm)
    shared_query_itm = try_find_element(audit_tr_itm, FindElementBy.NAME, query_name, small_retry)
    double_click(dsk_session, shared_query_itm)
    session_list_win = try_find_element(dsk_session, FindElementBy.AUTOMATION_ID, '12786', small_retry)
    double_click(dsk_session, session_list_win)
    user_session = {}
    for display_name in display_name_lst:
        display_name_attr = try_find_element(dsk_session, FindElementBy.NAME, display_name, small_retry, True) is None
        user_session[display_name] = display_name_attr
    main_app_win = try_find_element(dsk_session, FindElementBy.CLASS, "MMCMainFrame", small_retry)
    try_find_element(main_app_win, FindElementBy.NAME, 'Close', small_retry).click()
    return user_session


def validate_login_events_status(name, user_and_status: dict, dsk_session: WebDriver, audit_type, getuser,
                                 host_name, domain_name, sub_type=None) -> dict:
    """
    Validate the event login status for query and report
    """
    audit_tr_itm = select_audit_tree_item(dsk_session, audit_type)
    if sub_type:
        audit_sub_itm = try_find_element(audit_tr_itm, FindElementBy.NAME, sub_type, small_retry)
        double_click(dsk_session, audit_sub_itm)
    audit_query_itm = try_find_element(audit_tr_itm, FindElementBy.NAME, name, small_retry)
    double_click(dsk_session, audit_query_itm)
    session_list_win = try_find_element(dsk_session, FindElementBy.AUTOMATION_ID, '12786', small_retry)
    double_click(dsk_session, session_list_win)
    for user in user_and_status.keys():
        if user in getuser:
            username = user + "@" + domain_name
        else:
            username = user + "@" + host_name
        machine_txt = try_find_element(session_list_win, FindElementBy.NAME, username, small_retry)
        if sub_type:
            double_click(dsk_session, machine_txt)
        # Verify access status for Users
        if machine_txt is not None:
            actual_status = {}
            access_status = try_find_element(session_list_win, FindElementBy.NAME, 'Failed', small_retry, True)
            if access_status is not None:
                if access_status.is_displayed():
                    access_status.click()
                    actual_status[user] = 'Failed'
            else:
                access_status = try_find_element(session_list_win, FindElementBy.NAME, 'Succeeded', small_retry)
                if access_status.is_displayed():
                    access_status.click()
                    actual_status[user] = 'Success'
    # Close the Audit Analyzer app
    main_app_win = try_find_element(dsk_session, FindElementBy.CLASS, "MMCMainFrame", small_retry)
    try_find_element(main_app_win, FindElementBy.NAME, 'Close', small_retry).click()
    return actual_status


def validate_unix_command_events(query_name, event_names, dsk_session: WebDriver, audit_type) -> list:
    """
    Validate the unix command event status from audit event query
    """
    audit_tr_itm = select_audit_tree_item(dsk_session, audit_type)
    audit_query_itm = try_find_element(audit_tr_itm, FindElementBy.NAME, query_name, small_retry)
    double_click(dsk_session, audit_query_itm)
    session_list_win = try_find_element(dsk_session, FindElementBy.AUTOMATION_ID, '12786', small_retry)
    double_click(dsk_session, session_list_win)
    actual_status = []
    for eventname in event_names:
        event_found = try_find_element(session_list_win, FindElementBy.NAME, eventname, small_retry, True)
        if event_found is not None:
            event_found.click()
            actual_status.append(eventname)
    # Close the Audit Analyzer app
    main_app_win = try_find_element(dsk_session, FindElementBy.CLASS, "MMCMainFrame", small_retry)
    try_find_element(main_app_win, FindElementBy.NAME, 'Close', small_retry).click()
    return actual_status


def validate_user_reports_exist(report_name, users, domain_name, host_name, dsk_session: WebDriver, getuser, \
                                audit_type, report_type) -> list:
    """
    Check the specified report for specified user
    """
    audit_tr_itm = select_audit_tree_item(dsk_session, audit_type)
    audit_sub_itm = try_find_element(audit_tr_itm, FindElementBy.NAME, report_type, small_retry)
    if audit_sub_itm is None:
        double_click(dsk_session, audit_tr_itm)
    double_click(dsk_session, audit_sub_itm)
    audit_query_itm = try_find_element(audit_tr_itm, FindElementBy.NAME, report_name, small_retry)
    double_click(dsk_session, audit_query_itm)
    session_list_win = try_find_element(dsk_session, FindElementBy.AUTOMATION_ID, '12786', small_retry)
    double_click(dsk_session, session_list_win)
    found_reports = []
    for user in users:
        if user in getuser:
            username = user + "@" + domain_name
        else:
            username = user + "@" + host_name
    if try_find_element(session_list_win, FindElementBy.NAME, username, small_retry, True) is not None:
        found_reports.append(user)
    # Close the Audit Analyzer app
    main_app_win = try_find_element(dsk_session, FindElementBy.CLASS, "MMCMainFrame", small_retry)
    try_find_element(main_app_win, FindElementBy.NAME, 'Close', small_retry).click()
    return found_reports


def validate_events_of_report(report_name, user_and_event, domain_name, host_name, dsk_session: WebDriver,
                              getuser, audit_type, report_type) -> dict:
    """
    Validate the events for specified user from any report
    """
    audit_tr_itm = select_audit_tree_item(dsk_session, audit_type)
    audit_sub_itm = try_find_element(audit_tr_itm, FindElementBy.NAME, report_type, small_retry)
    if audit_sub_itm is None:
        double_click(dsk_session, audit_tr_itm)
    double_click(dsk_session, audit_sub_itm)
    audit_query_itm = try_find_element(audit_tr_itm, FindElementBy.NAME, report_name, small_retry)
    double_click(dsk_session, audit_query_itm)
    session_list_win = try_find_element(dsk_session, FindElementBy.AUTOMATION_ID, '12786', small_retry)
    double_click(dsk_session, session_list_win)
    actual_event_status = {}
    for user in user_and_event.keys():
        if user in getuser:
            username = user + "@" + domain_name
        else:
            username = user + "@" + host_name
        user_element = try_find_element(session_list_win, FindElementBy.NAME, username, small_retry)
        if user_element is not None:
            double_click(dsk_session, user_element)
            for event in user_and_event[user]:
                event_found = try_find_element(session_list_win, FindElementBy.NAME, event, med_retry, \
                                               ignore_if_not_found=True)
                if event_found is not None:
                    event_found.click()
                    actual_event_status[event] = True
                else:
                    actual_event_status[event] = False
    # Close the Audit Analyzer app
    main_app_win = try_find_element(dsk_session, FindElementBy.CLASS, "MMCMainFrame", small_retry)
    try_find_element(main_app_win, FindElementBy.NAME, 'Close', small_retry).click()
    return actual_event_status