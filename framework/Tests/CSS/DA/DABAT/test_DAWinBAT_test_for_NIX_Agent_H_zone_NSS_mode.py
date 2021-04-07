"""This module is intended to Automate DA Windows agent"""

import pytest
from pathlib import Path

from Shared.CSS import css_win_constants
from Shared.CSS.css_win_utils import *
from .common import create_query_func, SessionType, login_and_execute_cmds, validate_sessions, validate_event_file, \
    AuditType

logger = logging.getLogger('test')

###### Test cases ######
class TestforNixAgentHzoneNSSMode:
    """
       To create shared query and report for new sessions
    """
    remote_framework_path = css_win_constants.remote_framework_path
    directory_path = Path(__file__).resolve().parent
    file_path = str(directory_path).split("framework\\", maxsplit=1)[1]
    filename = "test_DAWinBAT_test_for_NIX_Agent_H_zone_NSS_mode.py"
    class_name = "TestforNixAgentHzoneNSSMode"

    @pytest.mark.bhavna
    @pytest.mark.css
    @pytest.mark.da_win_bat
    def test_master_create_shared_query_for_nix_session_nss_mode(self, dawin_testagent_uploaded, dawin_installed,
                                                                      css_testee_login_as_domain_admin):
        username = r"%s\%s" % (dawin_installed['domain_name'].split('.')[0], "administrator")
        login_and_execute_cmds(username, dawin_installed['admin_password'], dawin_installed['public_ip'],
                               css_testee_login_as_domain_admin, self.filename, self.class_name,
                               'test_create_shared_query_for_nix_session_nss_mode')

    @pytest.mark.bhavna
    @pytest.mark.css
    @pytest.mark.da_win_bat
    def test_master_replay_session_nix_session_nss_mode(self, dawin_testagent_uploaded, dawin_installed,
                                                                 css_testee_login_as_domain_admin):
        username = r"%s\%s" % (dawin_installed['domain_name'].split('.')[0], "administrator")
        login_and_execute_cmds(username, dawin_installed['admin_password'], dawin_installed['public_ip'],
                               css_testee_login_as_domain_admin, self.filename, self.class_name,
                               'test_replay_sessions_which_are_generated_above')

    @pytest.mark.bhavna
    @pytest.mark.css
    @pytest.mark.da_win_bat
    def test_master_verify_audited_sessions_nix_session_nss_mode(self, dawin_testagent_uploaded, dawin_installed,
                                                 css_testee_login_as_domain_admin):
        username = r"%s\%s" % (dawin_installed['domain_name'].split('.')[0], "administrator")
        login_and_execute_cmds(username, dawin_installed['admin_password'], dawin_installed['public_ip'],
                               css_testee_login_as_domain_admin, self.filename, self.class_name,
                               'test_verify_audited_sessions')

    # 3.2 "NSS" mode
    def test_create_shared_query_for_nix_session_nss_mode(self):
        logger.info("--- Case C1238904")
        query_name = 'pershell'
        desktop = get_desktop()
        shared_query_itm = create_query_func(desktop, query_name, [SessionType.Windows_session, \
                                                                   SessionType.Linux_Desktop_session])
        assert shared_query_itm is not None, f"{query_name} is not found"

    def test_replay_sessions_which_are_generated_above(self, css_test_machine, css_client_test_machine,
                                                       get_aduser_from_yaml):
        logger.info("--- Case C1238914")
        query_name = 'pershell'
        desktop = get_desktop()
        host_name = css_test_machine['hostname']
        domain_name = css_client_test_machine['domain_name']
        command_list = ['-/bin/bash ', 'adinfo', 'dainfo']
        users = ['root']
        session_events = validate_sessions(query_name, command_list, host_name, domain_name, users,
                                          get_aduser_from_yaml , desktop, AuditType.audit_sessions.value,
                                          AuditType.shared_query.value)
        for command, event in session_events.items():
            assert event == True, f"Event for command {command} not created"

    def test_verify_audited_sessions(self, css_test_machine, css_client_test_machine, get_aduser_from_yaml):
        logger.info("--- Case C1238915")
        query_name = 'pershell'
        desktop = get_desktop()
        host_name = css_test_machine['hostname']
        domain_name = css_client_test_machine['domain_name']
        command_list = ['-/bin/bash ', 'adinfo', 'dainfo']
        user = 'root'
        audit_session_file, review_comment, review_status = validate_event_file(query_name, domain_name,user,
                                                                                get_aduser_from_yaml, desktop, host_name)

        # Verify session command list, review comment and status
        assert review_comment == True, "Review comment not found"
        assert review_status == True, "Review status not found"
        for command in command_list:
            substring_search = command in audit_session_file
            assert substring_search == True, f"Session for {command} command not created"
