"""This module is intended to Automate DA Windows agent"""

import pytest

from Shared.CSS.css_win_utils import *
from .common import create_audit_event_function, AuditEventType, login_and_execute_cmds, \
    create_reports_func, ReportType, validate_login_events_status, AuditType, validate_sessions, \
    validate_unix_command_events, validate_events_of_report, validate_user_reports_exist

logger = logging.getLogger('test')


###### Test cases ######


class TestToVerifyEventAndReport:
    """
    To Verify audited event and report from Audit Analyzer for Nix sessions
    """
    settings = Configs.get_test_node("da_installation", "settings")
    med_retry = settings['med_retry']
    vry_small_retry = settings['vry_small_retry']
    small_retry = settings['small_retry']
    filename = "test_DAWinBAT_Verify_Audited_Event_And_Report_For_Nix_Sessions.py"
    class_name = "TestToVerifyEventAndReport"

    @pytest.mark.bhavna
    @pytest.mark.css
    @pytest.mark.da_win_bat
    def test_master_create_audit_event_query(self, dawin_installed, css_testee_machine, \
                                             css_testee_login_as_domain_admin):
        username = r"%s\%s" % (css_testee_machine['domain_name'].split('.')[0], "administrator")
        login_and_execute_cmds(username, css_testee_machine['admin_password'], css_testee_machine['public_ip'],
                               css_testee_login_as_domain_admin, self.filename, self.class_name,
                               'test_create_audit_event_query')

    @pytest.mark.bhavna
    @pytest.mark.css
    @pytest.mark.da_win_bat
    def test_master_create_audit_query_with_centrify_unix_command(self, dawin_installed, css_testee_machine, \
                                                                  css_testee_login_as_domain_admin):
        username = r"%s\%s" % (css_testee_machine['domain_name'].split('.')[0], "administrator")
        login_and_execute_cmds(username, css_testee_machine['admin_password'], css_testee_machine['public_ip'],
                               css_testee_login_as_domain_admin, self.filename, self.class_name, \
                               'test_create_audit_query_with_centrify_unix_command')

    @pytest.mark.bhavna
    @pytest.mark.css
    @pytest.mark.da_win_bat
    def test_master_create_privileged_activity_report(self, css_testee_machine, css_testee_login_as_domain_admin):
        username = r"%s\%s" % (css_testee_machine['domain_name'].split('.')[0], "administrator")
        login_and_execute_cmds(username, css_testee_machine['admin_password'], css_testee_machine['public_ip'],
                               css_testee_login_as_domain_admin, self.filename, self.class_name, \
                               'test_create_privileged_activity_report')

    @pytest.mark.bhavna
    @pytest.mark.css
    @pytest.mark.da_win_bat
    def test_master_verify_login_audit_event_from_audit_event_query(self, css_testee_machine,
                                                                    css_testee_login_as_domain_admin):
        username = r"%s\%s" % (css_testee_machine['domain_name'].split('.')[0], "administrator")
        login_and_execute_cmds(username, css_testee_machine['admin_password'], css_testee_machine['public_ip'],
                               css_testee_login_as_domain_admin, self.filename, self.class_name, \
                               'test_verify_login_audit_event_from_audit_event_query')

    @pytest.mark.bhavna
    @pytest.mark.css
    @pytest.mark.da_win_bat
    def test_master_verify_centrify_command_audit_event_from_audit_event_query \
                    (self, css_testee_machine, css_testee_login_as_domain_admin):
        username = r"%s\%s" % (css_testee_machine['domain_name'].split('.')[0], "administrator")
        login_and_execute_cmds(username, css_testee_machine['admin_password'], css_testee_machine['public_ip'],
                               css_testee_login_as_domain_admin, self.filename, self.class_name, \
                               'test_verify_centrify_command_audit_event_from_audit_event_query')

    @pytest.mark.bhavna
    @pytest.mark.css
    @pytest.mark.da_win_bat
    def test_master_verify_report_from_privileged_activity_report(self, css_testee_machine,
                                                                  css_testee_login_as_domain_admin):
        username = r"%s\%s" % (css_testee_machine['domain_name'].split('.')[0], "administrator")
        login_and_execute_cmds(username, css_testee_machine['admin_password'], css_testee_machine['public_ip'],
                               css_testee_login_as_domain_admin, self.filename, self.class_name, \
                               'test_verify_report_from_privileged_activity_report')

    @pytest.mark.bhavna
    @pytest.mark.css
    @pytest.mark.da_win_bat
    def test_master_verify_login_by_user_report(self, css_testee_machine,
                                                css_testee_login_as_domain_admin):
        username = r"%s\%s" % (css_testee_machine['domain_name'].split('.')[0], "administrator")
        login_and_execute_cmds(username, css_testee_machine['admin_password'], css_testee_machine['public_ip'],
                               css_testee_login_as_domain_admin, self.filename, self.class_name, \
                               'test_verify_login_by_user_report')

    @pytest.mark.bhavna
    @pytest.mark.css
    @pytest.mark.da_win_bat
    def test_master_verify_report_from_file_monitor_report(self, css_testee_machine, css_testee_login_as_domain_admin):
        username = r"%s\%s" % (css_testee_machine['domain_name'].split('.')[0], "administrator")
        login_and_execute_cmds(username, css_testee_machine['admin_password'], css_testee_machine['public_ip'],
                               css_testee_login_as_domain_admin, self.filename, self.class_name, \
                               'test_verify_report_from_file_monitor_report')

    # 6. Verify audited event and report from Audit Analyzer - For *NIX sessions

    def test_create_audit_event_query(self, css_testee_machine):
        logger.info("--- Case C1239027")

        audit_login_event_query_name = "Audit_Login_Event_query_1"
        desktop = get_desktop()
        audit_event_itm = create_audit_event_function(desktop, audit_login_event_query_name,
                                                      [AuditEventType.Login_Event], css_testee_machine)
        assert audit_event_itm is not None, f"{audit_login_event_query_name} is not found"

    def test_create_audit_query_with_centrify_unix_command(self, css_testee_machine):
        logger.info("--- Case C1239028")

        audit_unix_query_name = "Audit_unix_command_query_1"
        desktop = get_desktop()
        audit_event_itm = create_audit_event_function(desktop, audit_unix_query_name,
                                                      [AuditEventType.Centrify_UNIX_Command], css_testee_machine)
        assert audit_event_itm is not None, f"{audit_unix_query_name} is not found"

    def test_create_privileged_activity_report(self, css_test_machine):
        logger.info("--- Case C1239029")

        report_name = "Privileged_Activity_report_1"
        desktop = get_desktop()
        reports_tr_itm, main_app_win, dsk_session, report_tr_itm = create_reports_func(
            ReportType.privileged_activity_report, desktop)
        privileged_report_win = try_find_element(dsk_session, FindElementBy.AUTOMATION_ID, \
                                                 'PrivilegedActivityReportQueryCriteria', self.med_retry)

        # Select the machine box and enter full windows machine name
        try_find_element(privileged_report_win, FindElementBy.AUTOMATION_ID, 'cb_machine', self.med_retry).click()

        try_find_element(dsk_session, FindElementBy.AUTOMATION_ID, 'm_machineName',
                         self.med_retry).send_keys(css_test_machine['hostname'])

        # Check the Event time checkbox and select the time
        try_find_element(privileged_report_win, FindElementBy.AUTOMATION_ID, 'cb_eventTime', self.med_retry).click()

        try_find_element(privileged_report_win, FindElementBy.AUTOMATION_ID, 'm_timeNormalOpList',
                         self.med_retry).click()
        try_find_element(dsk_session, FindElementBy.NAME, 'Is after', self.med_retry).click()

        # Save the created Query
        try_find_element(privileged_report_win, FindElementBy.AUTOMATION_ID, 'button1', self.med_retry).click()

        # Add report name
        try_find_element(dsk_session, FindElementBy.AUTOMATION_ID, 'textBox1',
                         self.med_retry).send_keys(report_name)

        try_find_element(dsk_session, FindElementBy.AUTOMATION_ID, 'button2', self.med_retry).click()

        if try_find_element(reports_tr_itm, FindElementBy.NAME, report_name, \
                            self.small_retry, ignore_if_not_found=True) is None:
            double_click(dsk_session, reports_tr_itm)

        report_itm = try_find_element(reports_tr_itm, FindElementBy.NAME, report_name, self.med_retry)

        #  Close the Audit Analyzer app
        try_find_element(main_app_win, FindElementBy.NAME, 'Close', self.med_retry).click()

        assert report_itm is not None, f"{report_name} is not found"

    def test_verify_login_audit_event_from_audit_event_query(self, css_test_machine, get_aduser_from_yaml,
                                                             css_test_env):
        logger.info("--- Case C1239030")
        logger.info("--- Step 1")
        query_name = 'Audit_Login_Event_query_1'
        desktop = get_desktop()
        host_name = css_test_machine['hostname']
        domain_name = css_test_env['domain_name']
        expected_login_status = {'root': 'Success', 'anu0001': 'Failed', 'blocal1': 'Failed'}
        actual_login_status = validate_login_events_status(query_name, expected_login_status, desktop, \
                                                           AuditType.audit_event.value, get_aduser_from_yaml, \
                                                           host_name, domain_name)
        for user, status in zip(expected_login_status.keys(), actual_login_status.keys()):
            assert expected_login_status[user] == actual_login_status[
                status], f"Failed to get the expected access status for user: {user}"
        logger.info("--- Step 2")
        command_list = ['adinfo', 'dainfo']
        users = ['root']
        event_attr = validate_sessions(query_name, command_list, host_name, domain_name, users, get_aduser_from_yaml, \
                                       desktop, AuditType.audit_event.value)
        all_false_events = [command for command in event_attr if event_attr[command] == False]
        assert len(all_false_events) == 0, f"Failed to create session for commands: {all_false_events}"

    def test_verify_centrify_command_audit_event_from_audit_event_query(self, css_test_machine, css_test_env):
        logger.info("--- Case C1239031")
        logger.info("--- Step 1")
        query_name = 'Audit_unix_command_query_1'
        desktop = get_desktop()
        event_names = ['Auditing enabled', 'Auditing disabled', 'dzdo granted', 'Joined domain', \
                       'Left domain', 'License modes changed', 'Local cache flushed', \
                       'Configuration settings', 'dzdo command execution starts', \
                       'dzdo command execution ends']
        actual_event_names = validate_unix_command_events(query_name, event_names, desktop,
                                                          AuditType.audit_event.value)
        not_found = list(set(event_names) - set(actual_event_names))
        assert len(not_found) == 0, f"Failed to find the event(s) {not_found}"

    def test_verify_report_from_privileged_activity_report(self, css_test_machine, css_test_env, get_aduser_from_yaml):
        logger.info("--- Case C1239032")
        logger.info("--- Step 1")
        report_name = 'Privileged_Activity_report_1'
        desktop = get_desktop()
        host_name = css_test_machine['hostname']
        domain_name = css_test_env['domain_name']
        user_and_event = {'anu0007': ['dzdo /usr/sbin/dareload ']}
        actual_events = validate_events_of_report(report_name, user_and_event, domain_name, host_name,
                                                  desktop, get_aduser_from_yaml, AuditType.reports.value,
                                                  ReportType.privileged_activity_report.value)
        all_false_events = [event for event in actual_events if actual_events[event] == False]
        assert len(all_false_events) == 0, f"Failed to find the events : {all_false_events}"

    def test_verify_login_by_user_report(self, css_test_machine, css_test_env, get_aduser_from_yaml):
        logger.info("--- Case C1238820")
        logger.info("--- Step 1")
        report_name = 'Audit_Login_Event_query_1'
        desktop = get_desktop()
        host_name = css_test_machine['hostname']
        domain_name = css_test_env['domain_name']
        expected_login_status = {'root': 'Success'}
        actual_login_status = validate_login_events_status(report_name, expected_login_status, desktop, \
                                                           AuditType.reports.value, get_aduser_from_yaml, \
                                                           host_name, domain_name, ReportType.user_report.value)
        for user, status in zip(expected_login_status.keys(), actual_login_status.keys()):
            assert expected_login_status[user] == actual_login_status[
                status], f"Failed to get the expected access status for user: {user}"
        logger.info("--- Step 2")
        command_list = ['adinfo', 'dainfo']
        users = ['root']
        event_attr = validate_sessions(report_name, command_list, host_name, domain_name, users,
                                       get_aduser_from_yaml,
                                       desktop, AuditType.audit_event.value)
        all_false_events = [command for command in event_attr if event_attr[command] == False]
        assert len(all_false_events) == 0, f"Failed to create session for commands: {all_false_events}"

    def test_verify_report_from_file_monitor_report(self, css_test_machine, css_test_env, get_aduser_from_yaml):
        logger.info("--- Case C1238894")
        logger.info("--- Step 1")
        report_name = 'File_Monitor_Report_1'
        desktop = get_desktop()
        host_name = css_test_machine['hostname']
        domain_name = css_test_env['domain_name']
        find_user_report = ['normal', 'anu0001']
        found_reports = validate_user_reports_exist(report_name, find_user_report, domain_name, host_name, desktop,
                                                    get_aduser_from_yaml, AuditType.reports.value,
                                                    ReportType.file_report.value)
        not_found = list(set(find_user_report) - set(found_reports))
        assert len(not_found) != 0, f"Failed to find the reports for Users: {not_found}"

        logger.info("--- Step 2")
        user_and_event = {'root': ['Succeeded', 'Write', '/etc/bb.txt', '/usr/bin/rm']}
        actual_events = validate_events_of_report(report_name, user_and_event, domain_name, host_name, desktop,
                                                  get_aduser_from_yaml, AuditType.reports.value,
                                                  ReportType.file_report.value)
        all_false_events = [event for event in actual_events if actual_events[event] == False]
        assert len(all_false_events) == 0, f"Failed to find the events : {all_false_events}"

