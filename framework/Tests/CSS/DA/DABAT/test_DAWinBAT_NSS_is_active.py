"""This module intends to automate DA tests while NSS is active"""

import pytest

from Shared.CSS.css_win_utils import *
from .common import login_and_execute_cmds, validate_sessions, validate_event_file, AuditType

logger = logging.getLogger('test')


###### Test cases ######
class TestWithNSSIsActive:
    """
    Replay and Verify the sessions
    """
    filename = "test_DAWinBAT_NSS_is_active.py"
    class_name = "TestWithNSSIsActive"


    @pytest.mark.bhavna
    @pytest.mark.css
    @pytest.mark.da_win_bat
    def test_master_replay_sessions_which_are_generated_above(self, dawin_testagent_uploaded, dawin_installed,
                                                              css_testee_login_as_domain_admin):
        username = r"%s\%s" % (dawin_installed['domain_name'].split('.')[0], "administrator")
        login_and_execute_cmds(username, dawin_installed['admin_password'], dawin_installed['public_ip'],
                               css_testee_login_as_domain_admin, self.filename, self.class_name,
                               'test_replay_sessions_which_are_generated_above_nss_is_active')

    @pytest.mark.bhavna
    @pytest.mark.css
    @pytest.mark.da_win_bat
    def test_master_verify_audited_sessions(self, dawin_testagent_uploaded, dawin_installed,
                                            css_testee_login_as_domain_admin):
        username = r"%s\%s" % (dawin_installed['domain_name'].split('.')[0], "administrator")
        login_and_execute_cmds(username, dawin_installed['admin_password'], dawin_installed['public_ip'],
                               css_testee_login_as_domain_admin, self.filename, self.class_name,
                               'test_verify_audited_sessions')

    def test_replay_sessions_which_are_generated_above_nss_is_active(self, css_test_machine, css_test_env,
                                                                     get_aduser_from_yaml):
        logger.info("--- Case C1238948")
        query_name = 'pershell'
        desktop = get_desktop()
        host_name = css_test_machine['hostname']
        domain_name = css_test_env['domain_name']
        command_list = ['-/bin/bash ', 'adinfo', 'dainfo']
        users = ['root']
        session_events = validate_sessions(query_name, command_list, host_name, domain_name, users,
                                          get_aduser_from_yaml , desktop, AuditType.audit_sessions.value,
                                          AuditType.shared_query.value)
        for command, event in session_events.items():
            assert event == True, f"Event for command {command} not created"


    def test_verify_audited_sessions(self, css_test_machine, css_test_env, get_aduser_from_yaml):
        logger.info("--- Case C1238949")
        query_name = 'percmd'
        desktop = get_desktop()
        host_name = css_test_machine['hostname']
        domain_name = css_test_env['domain_name']
        command_list = ['-/bin/bash ', 'adinfo', 'dainfo']
        user = 'blocal6'
        audit_session_file, review_comment, review_status = validate_event_file \
            (query_name, domain_name, user, get_aduser_from_yaml, desktop, host_name)
        
        # Verify session command list, review comment and status
        assert review_comment == True, "Review comment not found"
        assert review_status == True, "Review status not found"
        for command in command_list:
            assert (command in audit_session_file) == True, f"Session for {command} command not created"
