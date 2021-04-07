"""This module intends to automate DA tests for NIX Agent - Classic Zone Command level mode"""

import pytest
from pathlib import Path

from Shared.CSS import css_win_constants
from Shared.CSS.css_win_utils import *
from .common import create_query_func, SessionType, login_and_execute_cmds, validate_event_file

logger = logging.getLogger('test')

###### Test cases ######
class TestforNixAgentCzoneCommandLevelMode:
    """
       To create shared query and report for new sessions
    """
    remote_framework_path = css_win_constants.remote_framework_path
    directory_path = Path(__file__).resolve().parent
    file_path = str(directory_path).split("framework\\", maxsplit=1)[1]
    filename = "test_DAWinBAT_test_for_NIX_Agent_C_zone_Command_level_mode.py"
    class_name = "TestforNixAgentCzoneCommandLevelMode"

    @pytest.mark.bhavna
    @pytest.mark.css
    @pytest.mark.da_win_bat
    def test_master_create_shared_query_for_nix_session_command_level_mode(self, dawin_testagent_uploaded, dawin_installed,
                                                                      css_testee_login_as_domain_admin):
        username = r"%s\%s" % (dawin_installed['domain_name'].split('.')[0], "administrator")
        login_and_execute_cmds(username, dawin_installed['admin_password'], dawin_installed['public_ip'],
                               css_testee_login_as_domain_admin, self.filename, self.class_name,
                               'test_create_shared_query_for_nix_session_command_level_mode')

    @pytest.mark.bhavna
    @pytest.mark.css
    @pytest.mark.da_win_bat
    def test_master_verify_audited_sessions_nix_session_session_command_level_mode(self, dawin_testagent_uploaded,
                                                                           dawin_installed,
                                                                           css_testee_login_as_domain_admin):
        username = r"%s\%s" % (dawin_installed['domain_name'].split('.')[0], "administrator")
        login_and_execute_cmds(username, dawin_installed['admin_password'], dawin_installed['public_ip'],
                               css_testee_login_as_domain_admin, self.filename, self.class_name,
                               'test_verify_audited_sessions_nix_session_command_level_mode')

    # 4.3 "Command level" mode
    def test_create_shared_query_for_nix_session_command_level_mode(self):
        logger.info("--- Case C1238994")
        query_name = 'percmd_c'
        desktop = get_desktop()
        shared_query_itm = create_query_func(desktop, query_name, [SessionType.Windows_session, \
                                                                   SessionType.Linux_Desktop_session])
        assert shared_query_itm is not None, f"{query_name} is not found"

    def test_verify_audited_sessions_nix_session_command_level_mode(self, css_test_machine, css_client_test_machine,
                                                                    get_aduser_from_yaml):
        logger.info("--- Case C1239000")
        query_name = 'percmd_c'
        desktop = get_desktop()
        host_name = css_test_machine['hostname']
        domain_name = css_client_test_machine['domain_name']
        command_list = ['rm', 'userdel', 'adjoin']
        user = 'root'
        audit_session_file, review_comment, review_status = validate_event_file(query_name, domain_name, user,
                                                                                get_aduser_from_yaml, desktop, host_name)

        # Verify session command list, review comment and status
        assert review_comment == True, "Review comment not found"
        assert review_status == True, "Review status not found"
        for command in command_list:
            assert (command in audit_session_file) == True, f"Session for {command} command not created"


