import pytest
import logging
from Shared.API.infrastructure import ResourceManager
from Shared.UI.Centrify.SubSelectors.grids import GridRowByGuid, GridCell
from Shared.UI.Centrify.SubSelectors.modals import Modal
from Shared.UI.Centrify.selectors import LoadingMask

logger = logging.getLogger('test')


@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.rdp
def test_check_total_session(core_session, pas_setup, get_admin_user_function, users_and_roles):
    """
    Test case: C2117
    :param core_session: Authenticated Centrify session manager
    :param pas_setup: fixture to create system with accounts
    :param users_and_roles: fixture to create user with roles
    """
    system_id, account_id, sys_info = pas_setup

    cloud_user_session, user = get_admin_user_function
    cloud_user, user_id, user_password = user.get_login_name(), user.get_id(), user.get_password()
    user = {
        "Username": cloud_user,
        "Password": user_password
    }

    result, status = ResourceManager.assign_system_permissions(core_session, "View", principal=cloud_user,
                                                               principalid=user_id, pvid=system_id)
    assert status, f'failed to assign view permission to user {cloud_user} for system {sys_info[0]}'
    logger.info(f'View permission assigned to user {cloud_user} for system {sys_info[0]}')

    result, status = ResourceManager.assign_account_permissions(core_session, "View,Login", principal=cloud_user,
                                                                principalid=user_id, pvid=account_id)
    assert status, f'failed to assign view permission to user {cloud_user} for account {sys_info[4]}'
    logger.info(f'View permission assigned to user {cloud_user} for account {sys_info[4]}')

    # update system to allow system for RDP connections
    result, success = ResourceManager.update_system(core_session, system_id, sys_info[0], sys_info[1], sys_info[2],
                                                    allowremote=True)
    assert success, f"failed to update system {sys_info[0]}, result is {result}"
    logger.info('system updated for remote connection')

    ui = users_and_roles.get_ui_as_user(user_properties=user, user_already_exists=True)
    ui.navigate('Resources', 'Systems')
    ui.search(sys_info[0])
    ui.right_click_action(GridRowByGuid(system_id), 'Select/Request Account')
    ui.switch_context(Modal(text=f'{sys_info[0]} Login'))
    account_row = ui.expect(GridCell(sys_info[4]), f'Expected to find account row {sys_info[4]} but did not.')
    account_row.try_click()
    ui.close_modal('Select')
    ui.switch_to_pop_up_window()
    ui.expect_disappear(LoadingMask(), f'RDP session never exited loading state', time_to_wait=60)
    ui.switch_to_main_window()
    ui.user_menu('Reload Rights')

    # Api call to get details of account active session
    result, success = ResourceManager.get_active_sessions(core_session)
    active_session_list = []
    for i in range(len(result)):
        if result[i]["HostName"] == sys_info[0]:
            active_session_list.append(result[i]["SessionID"])
    assert active_session_list, f'Failed to find the login record with "System Name: {active_session_list}"'
    logger.info(f'Active session details:{active_session_list}')
