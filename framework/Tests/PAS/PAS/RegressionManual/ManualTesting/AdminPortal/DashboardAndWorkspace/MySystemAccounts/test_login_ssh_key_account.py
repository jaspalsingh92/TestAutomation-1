import pytest
import logging
from Shared.UI.Centrify.selectors import LoadingMask
from Shared.API.infrastructure import ResourceManager
from Shared.API.users import UserManager
from Shared.UI.Centrify.SubSelectors.grids import GridRowByGuid

logger = logging.getLogger('test')


@pytest.mark.ui
@pytest.mark.pas
@pytest.mark.bhavna
def test_grant_view_portal_login_permission_to_privileged_access_service_user(core_session, system_with_ssh_account,
                                                                              core_admin_ui):
    """
    TC: C2069
    :param core_session: Authenticated Centrify session.
    :param system_with_ssh_account: Valid unix system with ssh account
    :param core_admin_ui: Authenticated browser session.
    """
    system_id, account_id, ssh_id, system_list, account_list, ssh_list = system_with_ssh_account

    ui = core_admin_ui
    user_id = UserManager.get_user_id(core_session, ui.user.centrify_user['Username'])

    result, status = ResourceManager.assign_account_permissions(core_session, rights="View,Login,UserPortalLogin",
                                                                principal=ui.user.centrify_user['Username'],
                                                                principalid=user_id, pvid=account_id)
    assert status, f'failed to assign UserPortalLogin permission of account to user {ui.user.centrify_user["Username"]}'
    logger.info(f'UserPortalLogin permission of account assigned successfully to user '
                f'{ui.user.centrify_user["Username"]}')

    ui = core_admin_ui
    # "SSH Key" on column "Credential Type"
    result, status = ResourceManager.get_workspace_my_system_account(core_session)
    for account in result:
        if account['Host'] == system_id:
            assert account['CredentialType'] == 'SshKey', f'SSH Key not displayed in CredentialType column in ' \
                                                          f'My System Account'
            logger.info('SSH key displayed in Credential type column.')

    # Login to the ssh account
    ui.navigate(('Workspace', 'My System Accounts'))
    ui.right_click_action(GridRowByGuid(account_id), 'Login')
    ui.switch_to_pop_up_window()
    ui.expect_disappear(LoadingMask(), 'RDP session never exited loading state for system', time_to_wait=60)
    ui.switch_to_main_window()

    status, result = ResourceManager.get_my_active_sessions(core_session, account_id)
    assert status, f'failed to retrieve details for active account session data, return result is {result}'
    logger.info(f'details for active account found in My Active sessions, returned row is {result}.')
