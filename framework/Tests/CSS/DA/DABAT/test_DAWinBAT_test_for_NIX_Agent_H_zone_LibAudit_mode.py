"""This module intends to automate DA tests for NIX Agent - Hierarchical Zone LibAudit mode"""

import pytest

from Shared.CSS.css_win_utils import *
from .common import create_query_func, SessionType, ReportType, create_reports_func, login_and_execute_cmds, \
     AuditEventType, create_audit_event_function
from Utils.config_loader import Configs

logger = logging.getLogger('test')


###### Test cases ######
class TestforNixAgentHzoneLibAuditMode:
    """
       To create shared query and report for new sessions
    """

    settings = Configs.get_test_node("da_installation", "settings")
    med_retry = settings['med_retry']
    vry_small_retry = settings['vry_small_retry']
    small_retry = settings['small_retry']
    filename = "test_DAWinBAT_test_for_NIX_Agent_H_zone_LibAudit_mode.py"
    class_name = "TestforNixAgentHzoneLibAuditMode"

    @pytest.mark.bhavna
    @pytest.mark.css
    @pytest.mark.da_win_bat
    def test_master_create_shared_query_for_nix_session_libaudit_mode(self, dawin_testagent_uploaded, dawin_installed,
                                        css_testee_login_as_domain_admin):
        username = r"%s\%s" % (dawin_installed['domain_name'].split('.')[0], "administrator")
        login_and_execute_cmds(username, dawin_installed['admin_password'], dawin_installed['public_ip'],
                               css_testee_login_as_domain_admin, self.filename, self.class_name,
                               'test_create_shared_query_for_nix_session_libaudit_mode')

    @pytest.mark.bhavna
    @pytest.mark.css
    @pytest.mark.da_win_bat
    def test_master_create_file_monitor_report_for_nix_session_libaudit_mode(self, css_testee_machine,\
                                                                css_testee_login_as_domain_admin):
        username = r"%s\%s" % (css_testee_machine['domain_name'].split('.')[0], "administrator")
        login_and_execute_cmds(username, css_testee_machine['admin_password'], css_testee_machine['public_ip'],
                               css_testee_login_as_domain_admin, self.filename, self.class_name, \
                               'test_create_file_monitor_report_for_nix_session_libaudit_mode')

    @pytest.mark.bhavna
    @pytest.mark.css
    @pytest.mark.da_win_bat
    def test_master_create_monitored_execution_for_nix_session_libaudit_mode(self, css_testee_machine, \
                                                                             css_testee_login_as_domain_admin):
        username = r"%s\%s" % (css_testee_machine['domain_name'].split('.')[0], "administrator")
        login_and_execute_cmds(username, css_testee_machine['admin_password'], css_testee_machine['public_ip'],
                               css_testee_login_as_domain_admin, self.filename, self.class_name, \
                               'test_create_monitored_execution_report_for_nix_session_libaudit_mode')

    @pytest.mark.bhavna
    @pytest.mark.css
    @pytest.mark.da_win_bat
    def test_master_create_detailed_report_for_nix_session_libaudit_mode(self, css_testee_machine, \
                                                                         css_testee_login_as_domain_admin):
        username = r"%s\%s" % (css_testee_machine['domain_name'].split('.')[0], "administrator")
        login_and_execute_cmds(username, css_testee_machine['admin_password'], css_testee_machine['public_ip'],
                               css_testee_login_as_domain_admin, self.filename, self.class_name, \
                               'test_create_detailed_execution_report_for_nix_session_libaudit_mode')

    @pytest.mark.bhavna11
    @pytest.mark.css
    @pytest.mark.da_win_bat
    def test_master_audit_event_query_for_nix_session_libaudit_mode(self, css_testee_machine, \
                                                                             css_testee_login_as_domain_admin):
        username = r"%s\%s" % (css_testee_machine['domain_name'].split('.')[0], "administrator")
        login_and_execute_cmds(username, css_testee_machine['admin_password'], css_testee_machine['public_ip'],
                               css_testee_login_as_domain_admin, self.filename, self.class_name, \
                               'test_create_audit_event_query_for_nix_session_libaudit_mode')

    # 3.1.1  New query and report for *NIX session

    def test_create_shared_query_for_nix_session_libaudit_mode(self):

        logger.info("--- Case C1238825")
        
        query_name = 'Test_Unix_session_1'
        desktop = get_desktop()
        shared_query_itm = create_query_func(desktop, query_name, [SessionType.Windows_session, \
                                                                       SessionType.Linux_Desktop_session])
        assert shared_query_itm is not None, f"{query_name} is not found"

    def test_create_file_monitor_report_for_nix_session_libaudit_mode(self, css_testee_machine):

        logger.info("--- Case C1238826")
        report_name = "File_Monitor_report_1"
        desktop = get_desktop()
        reports_tr_itm, main_app_win, main_desktop, report_tr_itm = create_reports_func(ReportType.file_report, desktop)

        file_report_win = try_find_element(main_desktop, FindElementBy.AUTOMATION_ID, 'FileMonitorReportCriteria', \
                                           self.med_retry)

        # Select the machine box and enter full windows machine name
        try_find_element(file_report_win, FindElementBy.AUTOMATION_ID, 'm_machineOption', self.med_retry).click()
        full_machine_name = r"%s.%s" % (css_testee_machine['hostname'], css_testee_machine['domain_name'])

        try_find_element(main_desktop, FindElementBy.AUTOMATION_ID, 'm_machineName',
                         self.med_retry).send_keys(full_machine_name)

        # Check the Event time checkbox and select the time
        try_find_element(file_report_win, FindElementBy.AUTOMATION_ID, 'm_eventTimeOption', self.med_retry).click()

        time_cbox = try_find_element(file_report_win, FindElementBy.AUTOMATION_ID, 'm_timeNormalOpList', self.med_retry)
        click_hold(main_desktop, time_cbox)
        time_lst_itm = try_find_element(main_desktop, FindElementBy.NAME, 'Is after', self.med_retry)
        if time_lst_itm is not None:
            click_hold(main_desktop, time_lst_itm)

        # Save the created Query

        save_query_btn = try_find_element(file_report_win, FindElementBy.AUTOMATION_ID, 'm_saveQuery', self.med_retry)
        click_hold(main_desktop, save_query_btn)

        # Add report name

        try_find_element(main_desktop, FindElementBy.AUTOMATION_ID, 'textBox1',
                         self.med_retry).send_keys("File_Monitor_Report_1")

        try_find_element(main_desktop, FindElementBy.AUTOMATION_ID, 'button2', self.med_retry).click()

        if try_find_element(reports_tr_itm, FindElementBy.NAME, report_name, \
                            self.small_retry, ignore_if_not_found=True) is None:
            double_click(main_desktop, reports_tr_itm)

            double_click(main_desktop, report_tr_itm)

        report_itm = try_find_element(reports_tr_itm, FindElementBy.NAME, report_name, self.med_retry)

        #  Close the Audit Analyzer app
        click_hold(main_desktop, try_find_element(main_app_win, FindElementBy.NAME, 'Close', self.med_retry))

        assert report_itm is not None, "'File_Monitor_Report_1' is not found"

    def test_create_monitored_execution_report_for_nix_session_libaudit_mode(self, css_testee_machine):

        logger.info("--- Case C1238827")
        report_name = "Monitored_Execution_report_1"
        desktop = get_desktop()
        reports_tr_itm, main_app_win, main_desktop, report_tr_itm = create_reports_func(ReportType.monitored_report,\
                                                                                        desktop)

        monitored_report_win = try_find_element(main_desktop, FindElementBy.AUTOMATION_ID, \
                                                'MonitoredCommandReportQueryCriteria', self.med_retry)

        # Select the machine box and enter full windows machine name
        try_find_element(monitored_report_win, FindElementBy.AUTOMATION_ID, 'm_machineOption', self.med_retry).click()
        full_machine_name = r"%s.%s" % (css_testee_machine['hostname'], css_testee_machine['domain_name'])

        try_find_element(main_desktop, FindElementBy.AUTOMATION_ID, 'm_machineName',
                         self.med_retry).send_keys(full_machine_name)

        # Check the Event time checkbox and select the time
        try_find_element(monitored_report_win, FindElementBy.AUTOMATION_ID, 'm_eventTimeOption', self.med_retry).click()

        time_cbox = try_find_element(monitored_report_win, FindElementBy.AUTOMATION_ID, 'm_timeNormalOpList',\
                                     self.med_retry)
        click_hold(main_desktop, time_cbox)
        time_lst_itm = try_find_element(main_desktop, FindElementBy.NAME, 'Is after', self.med_retry)
        if time_lst_itm is not None:
            click_hold(main_desktop, time_lst_itm)

        # Save the created Query

        save_query_btn = try_find_element(monitored_report_win, FindElementBy.AUTOMATION_ID, 'm_saveQuery',\
                                          self.med_retry)
        click_hold(main_desktop, save_query_btn)

        # Add report name

        try_find_element(main_desktop, FindElementBy.AUTOMATION_ID, 'textBox1',
                         self.med_retry).send_keys("Monitored_Execution_report_1")

        try_find_element(main_desktop, FindElementBy.AUTOMATION_ID, 'button2', self.med_retry).click()

        if try_find_element(reports_tr_itm, FindElementBy.NAME, report_name, \
                            self.small_retry, ignore_if_not_found=True) is None:
            double_click(main_desktop, reports_tr_itm)

            double_click(main_desktop, report_tr_itm)

        report_itm = try_find_element(reports_tr_itm, FindElementBy.NAME, report_name, self.med_retry)

        #  Close the Audit Analyzer app
        click_hold(main_desktop, try_find_element(main_app_win, FindElementBy.NAME, 'Close', self.med_retry))

        assert report_itm is not None, "'Monitored_Execution_report_1' is not found"

    def test_create_detailed_execution_report_for_nix_session_libaudit_mode(self, css_testee_machine):

        logger.info("--- Case C1238828")
        report_name = "Detailed_Execution_report_1"
        desktop = get_desktop()
        reports_tr_itm, main_app_win, main_desktop, report_tr_itm = create_reports_func(ReportType.detailed_report, \
                                                                                        desktop)

        detailed_report_win = try_find_element(main_desktop, FindElementBy.AUTOMATION_ID, \
                                               'CommandDetailReportQueryCriteria', self.med_retry)

        # Select the machine box and enter full windows machine name
        try_find_element(detailed_report_win, FindElementBy.AUTOMATION_ID, 'm_machineOption', self.med_retry).click()
        full_machine_name = r"%s.%s" % (css_testee_machine['hostname'], css_testee_machine['domain_name'])

        try_find_element(main_desktop, FindElementBy.AUTOMATION_ID, 'm_machineName',
                         self.med_retry).send_keys(full_machine_name)

        # Check the Event time checkbox and select the time
        try_find_element(detailed_report_win, FindElementBy.AUTOMATION_ID, 'm_eventTimeOption', self.med_retry).click()

        time_cbox = try_find_element(detailed_report_win, FindElementBy.AUTOMATION_ID, 'm_timeNormalOpList', \
                                     self.med_retry)
        click_hold(main_desktop, time_cbox)
        time_lst_itm = try_find_element(main_desktop, FindElementBy.NAME, 'Is after', self.med_retry)
        if time_lst_itm is not None:
            click_hold(main_desktop, time_lst_itm)

        # Save the created Query

        save_query_btn = try_find_element(detailed_report_win, FindElementBy.AUTOMATION_ID, 'm_saveQuery', \
                                          self.med_retry)
        click_hold(main_desktop, save_query_btn)

        # Add report name

        try_find_element(main_desktop, FindElementBy.AUTOMATION_ID, 'textBox1',
                         self.med_retry).send_keys("Detailed_Execution_report_1")

        try_find_element(main_desktop, FindElementBy.AUTOMATION_ID, 'button2', self.med_retry).click()

        if try_find_element(reports_tr_itm, FindElementBy.NAME, report_name, \
                            self.small_retry, ignore_if_not_found=True) is None:
            double_click(main_desktop, reports_tr_itm)

            double_click(main_desktop, report_tr_itm)

        report_itm = try_find_element(reports_tr_itm, FindElementBy.NAME, report_name, self.med_retry)

        #  Close the Audit Analyzer app
        click_hold(main_desktop, try_find_element(main_app_win, FindElementBy.NAME, 'Close', self.med_retry))

        assert report_itm is not None, "'Detailed_Execution_report_1' is not found"

    def test_create_audit_event_query_for_nix_session_libaudit_mode(self, css_testee_machine):

        logger.info("--- Case C1238829")

        audit_event_query_name = "Audit_Event_query_1"
        desktop = get_desktop()
        audit_event_itm = create_audit_event_function(desktop, audit_event_query_name, [AuditEventType.Advanced_Monitoring], \
                                                  css_testee_machine)
        assert audit_event_itm is not None, f"{audit_event_query_name} is not found"


