"""This module is intended to Automate DA Windows agent"""

import pytest

from Shared.CSS.css_win_utils import *
from .common import create_query_func, SessionType, ReportType, create_reports_func, login_and_execute_cmds, \
    launch_and_close_applications, validate_sessions, AuditType, validate_event_file
from Utils.config_loader import Configs
from Shared.CSS import css_win_constants

logger = logging.getLogger('test')


###### Test cases ######
class TestForWindowsAgent:
    """
       To create shared query and report for new sessions
    """
    settings = Configs.get_test_node("da_installation", "settings")
    med_retry = settings['med_retry']
    vry_small_retry = settings['vry_small_retry']
    small_retry = settings['small_retry']
    filename = "test_DAWinBAT_test_for_windows_agent.py"
    class_name = "TestForWindowsAgent"

    @pytest.mark.bhavna
    @pytest.mark.css
    @pytest.mark.da_win_bat
    def test_master_create_shared_query(self, dawin_testagent_uploaded, dawin_installed,
                                        css_testee_login_as_domain_admin):
        username = r"%s\%s" % (dawin_installed['domain_name'].split('.')[0], "administrator")
        login_and_execute_cmds(username, dawin_installed['admin_password'], dawin_installed['public_ip'],
                               css_testee_login_as_domain_admin, self.filename, self.class_name,
                               'test_create_shared_query')

    @pytest.mark.bhavna
    @pytest.mark.css
    @pytest.mark.da_win_bat
    def test_master_create_report(self, css_testee_machine,
                                  css_testee_login_as_domain_admin):
        username = r"%s\%s" % (css_testee_machine['domain_name'].split('.')[0], "administrator")
        login_and_execute_cmds(username, css_testee_machine['admin_password'], css_testee_machine['public_ip'],
                               css_testee_login_as_domain_admin, self.filename, self.class_name, 'test_create_report')

    @pytest.mark.bhavna
    @pytest.mark.css
    @pytest.mark.da_win_bat
    @pytest.mark.parametrize('admin', ['domain_admin', 'local_admin'])
    def test_master_remote_login_with_domain_and_local_admin_user(self, admin, css_testee_machine,
                                                                  css_testee_login_as_domain_admin):
        if admin == 'domain_admin':
            logger.info("--- Case C1238811")
            username = r"%s\%s" % (css_testee_machine['domain_name'], "administrator")
            password = css_testee_machine['admin_password']
        else:
            logger.info("--- Case C1238814")
            username = r"%s\%s" % (css_testee_machine['hostname'], "administrator")
            password = css_testee_machine['local_password']
        login_and_execute_cmds(username, password, css_testee_machine['public_ip'], css_testee_login_as_domain_admin,
                               self.filename, self.class_name,
                               'test_remote_login_with_domain_and_local_admin_user')
        # To kill the WinAppDriver.exe
        rc, result, error = kill_application(css_testee_login_as_domain_admin, 'WinAppDriver.exe')
        assert rc == 0, "Failed to kill Winappdriver.exe"

    @pytest.mark.bhavna
    @pytest.mark.css
    @pytest.mark.da_win_bat
    def test_master_replay_session_windows_agent(self, dawin_testagent_uploaded, dawin_installed,
                                                        css_testee_login_as_domain_admin):
        username = r"%s\%s" % (dawin_installed['domain_name'].split('.')[0], "administrator")
        login_and_execute_cmds(username, dawin_installed['admin_password'], dawin_installed['public_ip'],
                               css_testee_login_as_domain_admin, self.filename, self.class_name,
                               'test_replay_session_windows_agent')

    @pytest.mark.bhavna
    @pytest.mark.css
    @pytest.mark.da_win_bat
    def test_master_verify_audited_sessions_windows_agent(self, dawin_testagent_uploaded, dawin_installed,
                                                          css_testee_login_as_domain_admin):
        username = r"%s\%s" % (dawin_installed['domain_name'].split('.')[0], "administrator")
        login_and_execute_cmds(username, dawin_installed['admin_password'], dawin_installed['public_ip'],
                               css_testee_login_as_domain_admin, self.filename, self.class_name,
                               'test_verify_audited_sessions_windows_agent')

    @pytest.mark.bhavna
    @pytest.mark.css
    @pytest.mark.da_win_bat
    def test_master_run_ps_cmd_for_windows_session_data(self, dawin_testagent_uploaded, dawin_installed,
                                                        css_testee_login_as_domain_admin):
        username = r"%s\%s" % (dawin_installed['domain_name'].split('.')[0], "administrator")
        login_and_execute_cmds(username, dawin_installed['admin_password'], dawin_installed['public_ip'],
                               css_testee_login_as_domain_admin, self.filename, self.class_name,
                               'test_run_powershell_cmd_to_get_windows_session_data')

    @pytest.mark.bhavna
    @pytest.mark.css
    @pytest.mark.da_win_bat
    def test_master_run_ps_cmd_to_get_user_login_event(self, dawin_testagent_uploaded, dawin_installed,
                                                       css_testee_login_as_domain_admin):
        username = r"%s\%s" % (dawin_installed['domain_name'].split('.')[0], "administrator")
        login_and_execute_cmds(username, dawin_installed['admin_password'], dawin_installed['public_ip'],
                               css_testee_login_as_domain_admin, self.filename, self.class_name,
                               'test_run_powershell_cmd_to_get_user_login_event')

    # 2.1 New query and report for windows session

    def test_create_shared_query(self):
        logger.info("--- Case C1238808")

        query_name = 'Test_window_session_1'
        desktop = get_desktop()
        shared_query_itm = create_query_func(desktop, query_name, [SessionType.UNIX_session, \
                                                                   SessionType.Linux_Desktop_session])
        assert shared_query_itm is not None, f"{query_name} is not found"

    def test_create_report(self, css_testee_machine):
        logger.info("--- Case C1238809")
        report_name = "Test_report_1"
        desktop = get_desktop()
        reports_tr_itm, main_app_win, main_desktop, report_tr_itm = create_reports_func(ReportType.user_report, desktop)

        report_win = try_find_element(main_desktop, FindElementBy.AUTOMATION_ID, 'ReportQueryCriteria',
                                      self.small_retry)

        # Select the machine box and enter full windows machine name
        try_find_element(report_win, FindElementBy.AUTOMATION_ID, 'cb_machine', self.small_retry).click()
        full_machine_name = r"%s.%s" % (css_testee_machine['hostname'], css_testee_machine['domain_name'])

        try_find_element(main_desktop, FindElementBy.AUTOMATION_ID, 'm_machineName',
                         self.med_retry).send_keys(full_machine_name)

        # Check the Event time checkbox and select the time
        try_find_element(report_win, FindElementBy.AUTOMATION_ID, 'cb_eventTime', self.med_retry).click()

        time_criteria_lst_item = try_find_element(report_win, FindElementBy.AUTOMATION_ID,
                                                  'm_timeNormalOpList', self.small_retry)
        click_hold(main_desktop, time_criteria_lst_item)
        time_attribute_itm = try_find_element(main_desktop, FindElementBy.NAME, 'Is after', self.small_retry)
        click_hold(main_desktop, time_attribute_itm)

        # Check the Event level checkbox and select the 'Succeeded' option
        try_find_element(report_win, FindElementBy.AUTOMATION_ID, 'cb_accessGranted', self.small_retry).click()

        # Save the query
        try_find_element(report_win, FindElementBy.AUTOMATION_ID, 'button1', self.small_retry).click()

        # Enter the Report name
        try_find_element(main_desktop, FindElementBy.AUTOMATION_ID, 'textBox1',
                         self.med_retry).send_keys("Test_report_1")

        try_find_element(main_desktop, FindElementBy.AUTOMATION_ID, 'button2', self.small_retry).click()

        if try_find_element(reports_tr_itm, FindElementBy.NAME, report_name, \
                            self.small_retry, ignore_if_not_found=True) is None:
            double_click(main_desktop, reports_tr_itm)

            double_click(main_desktop, report_tr_itm)

        report_itm = try_find_element(reports_tr_itm, FindElementBy.NAME, report_name, self.small_retry)

        #  Close the Audit Analyzer app
        click_hold(main_desktop, try_find_element(main_app_win, FindElementBy.NAME, 'Close', self.small_retry))

        assert report_itm is not None, f"{report_name} is not found"

    def test_remote_login_with_domain_and_local_admin_user(self):
        launch_and_close_applications(css_win_constants.da_auditor_startup_path, 'MMCMainFrame', True)

        launch_and_close_applications(css_win_constants.wf_advanced_security_startup_path, 'MMCMainFrame')

        launch_and_close_applications(css_win_constants.event_viewer_startup_path, 'MMCMainFrame')

        launch_and_close_applications(css_win_constants.cmd_startup_path, 'ConsoleWindowClass')

        launch_and_close_applications(css_win_constants.rdp_startup_path, '#32770')

        launch_and_close_applications(css_win_constants.task_scheduler_startup_path, 'MMCMainFrame')

        launch_and_close_applications(css_win_constants.ie_startup_path, 'IEFrame')

        launch_and_close_applications(css_win_constants.notepad_startup_path, 'Notepad')

        launch_and_close_applications(css_win_constants.powershell_startup_path, 'ConsoleWindowClass')

    # 2.3 Verify audited data from Audit Analyzer

    def test_replay_session_windows_agent(self, css_test_machine, css_client_test_machine, get_aduser_from_yaml):
        logger.info("--- Case C1238818")
        query_name = 'Test_window_session_1'
        desktop = get_desktop()
        host_name = css_test_machine['hostname']
        domain_name = css_client_test_machine['domain_name']
        command_list = ['Notepad', 'Windows PowerShell', 'Task Scheduler', 'Event Viewer', 'Remote Desktop Connection']
        users = ['Administrator']
        session_events = validate_sessions(query_name, command_list, host_name, domain_name, users,
                                           get_aduser_from_yaml, desktop, AuditType.audit_sessions.value,
                                           AuditType.shared_query.value)
        all_false_events = [command for command in session_events if session_events[command] == False]
        assert len(all_false_events) == 0, f"Failed to create session for commands: {all_false_events}"

    def test_verify_audited_sessions_windows_agent(self, css_test_machine, css_client_test_machine, get_aduser_from_yaml):
        logger.info("--- Case C1238819")
        query_name = 'windows sessions'
        desktop = get_desktop()
        host_name = css_test_machine['hostname']
        domain_name = css_client_test_machine['domain_name']
        command_list = ['Notepad', 'Windows PowerShell', 'Task Scheduler', 'Event Viewer', 'Remote Desktop Connection']
        user = 'Administrator'
        audit_session_file, review_comment, review_status = validate_event_file(query_name, domain_name, user,
                                                                                get_aduser_from_yaml, desktop, host_name, True)

        # Verify session command list, review comment and status
        assert review_comment == True, "Review comment not found"
        assert review_status == True, "Review status not found"
        for command in command_list:
            substring_search = command in audit_session_file
            assert substring_search == True, f"Session for {command} command not created"

    # 2.4 Verify audited data from DA powershell

    def test_run_powershell_cmd_to_get_windows_session_data(self, css_testee_login_as_domain_admin):
        logger.info("--- Case C1238821")
        windows_events_file = os.path.join(os.environ["HOMEPATH"], "Desktop", "windowsevent.txt")
        rc, result, error = css_testee_login_as_domain_admin.send_command \
            (("powershell.exe -command \".\windows.ps1\""))

        windows_event_list = ["Windows Firewall", "Event Viewer", "Command Prompt", "Remote Desktop Connection", \
                              "Task Scheduler", "Untitled - Notepad", "Windows PowerShell"]

        events_file_content = file_read(windows_events_file, mode="rb").decode('utf-16-le')
        if rc == 0:
            not_found = []
            for win_event in windows_event_list:
                if win_event not in events_file_content:
                    not_found.append(win_event)

            assert len(not_found) == 0, f"Windows Event(s) {not_found} Not Found"

        else:
            assert False, f"Failed to execute the powershell script, {error,result}"

    def test_run_powershell_cmd_to_get_user_login_event(self, css_testee_machine, css_testee_login_as_domain_admin):
        logger.info("--- Case C1238822")

        domain_admin_user = "administrator" + "@" + css_testee_machine['domain_name']
        login_event_file = os.path.join(os.environ["HOMEPATH"], "Desktop", "windowsloginevents.txt")
        rc, result, error = css_testee_login_as_domain_admin.send_command \
            (("powershell.exe -command \".\windows.ps1\""))

        login_event_list = ["Session auditing started", "Session auditing ended", domain_admin_user]
        login_file_content = file_read(login_event_file, mode="rb").decode('utf-16-le')

        if rc == 0:
            not_found = []
            for login_event in login_event_list:
                if login_event not in login_file_content:
                    not_found.append(login_event)

            assert len(not_found) == 0, f"Login Event(s) {not_found} Not Found"

        else:
            assert False, f"Failed to execute the powershell script, {error, result}"
