"""This module intends to automate DA tests for NIX Agent - Hierarchical Zone Command level mode"""

import pytest

from Shared.CSS.css_win_utils import *
from .common import create_query_func, SessionType, login_and_execute_cmds, validate_sessions, validate_event_file, \
    AuditType
from Utils.config_loader import Configs

logger = logging.getLogger('test')


###### Test cases ######
class TestforNixAgentHzoneCommandLevelMode:
    """
       To create shared query and report for new sessions
    """

    settings = Configs.get_test_node("da_installation", "settings")
    med_retry = settings['med_retry']
    vry_small_retry = settings['vry_small_retry']
    small_retry = settings['small_retry']
    filename = "test_DAWinBAT_test_for_NIX_Agent_H_zone_CommandLevel_mode.py"
    class_name = "TestforNixAgentHzoneCommandLevelMode"

    @pytest.mark.bhavna
    @pytest.mark.css
    @pytest.mark.da_win_bat
    def test_master_create_shared_query_for_nix_session_commandlevel_mode(self, dawin_testagent_uploaded, dawin_installed,
                                        css_testee_login_as_domain_admin):
        username = r"%s\%s" % (dawin_installed['domain_name'].split('.')[0], "administrator")
        login_and_execute_cmds(username, dawin_installed['admin_password'], dawin_installed['public_ip'],
                               css_testee_login_as_domain_admin, self.filename, self.class_name,
                               'test_create_shared_query_for_nix_session_commandlevel_mode')

    @pytest.mark.bhavna
    @pytest.mark.css
    @pytest.mark.da_win_bat
    def test_replay_session_nix_session_commandlevel_mode(self, dawin_testagent_uploaded, dawin_installed,
                                                 css_testee_login_as_domain_admin):
        username = r"%s\%s" % (dawin_installed['domain_name'].split('.')[0], "administrator")
        login_and_execute_cmds(username, dawin_installed['admin_password'], dawin_installed['public_ip'],
                               css_testee_login_as_domain_admin, self.filename, self.class_name,
                               'test_replay_sessions_which_are_generated_above_commandlevel_mode')

    @pytest.mark.bhavna
    @pytest.mark.css
    @pytest.mark.da_win_bat
    def test_master_verify_audited_sessions_nix_session_commandlevel_mode(self, dawin_testagent_uploaded,
                                                                          dawin_installed,
                                                                          css_testee_login_as_domain_admin):
        username = r"%s\%s" % (dawin_installed['domain_name'].split('.')[0], "administrator")
        login_and_execute_cmds(username, dawin_installed['admin_password'], dawin_installed['public_ip'],
                               css_testee_login_as_domain_admin, self.filename, self.class_name,
                               'test_verify_audited_sessions_commandlevel_mode')

    def test_create_shared_query_for_nix_session_commandlevel_mode(self):
        logger.info("--- Case C1238919")

        query_name = 'percmd'
        desktop = get_desktop()
        shared_query_itm = create_query_func(desktop, query_name, [SessionType.Windows_session, \
                                                                   SessionType.Linux_Desktop_session])
        assert shared_query_itm is not None, f"{query_name} is not found"

    def test_replay_sessions_which_are_generated_above_commandlevel_mode(self, css_test_machine, css_test_env,
                                                                         get_aduser_from_yaml):
        logger.info("--- Case C1238924")
        query_name = 'percmd'
        desktop = get_desktop()
        host_name = css_test_machine['hostname']
        domain_name = css_test_env['domain_name']
        command_list = ['-/bin/bash ', 'kill -l ', 'exit']
        users = ['root']
        session_events = validate_sessions(query_name, command_list, host_name, domain_name, users,
                                          get_aduser_from_yaml , desktop, AuditType.audit_sessions.value,
                                          AuditType.shared_query.value)
        for command, event in session_events.items():
            assert event == True, f"Event for command {command} not created"

    def test_verify_audited_sessions_commandlevel_mode(self, css_test_machine, css_test_env, get_aduser_from_yaml):
        logger.info("--- Case C1238925")
        query_name = 'percmd'
        desktop = get_desktop()
        host_name = css_test_machine['hostname']
        domain_name = css_test_env['domain_name']
        command_list = ['-/bin/bash ', 'kill -l ', 'exit']
        user = 'super'
        audit_session_file, review_comment, review_status = validate_event_file(query_name, domain_name, user,
                                                                                get_aduser_from_yaml, desktop, host_name)

        # Verify session command list, review comment and status
        assert review_comment == True, "Review comment not found"
        assert review_status == True, "Review status not found"
        for command in command_list:
            assert (command in audit_session_file) == True, f"Session for {command} command not created"

