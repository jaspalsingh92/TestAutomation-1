import pytest
import logging
from Shared.API.redrock import RedrockController
from Utils.guid import guid
from Shared.API.infrastructure import ResourceManager
from Shared.API.server import ServerManager
from Shared.API.users import UserManager
from Shared.UI.Centrify.SubSelectors.forms import ActiveSessionTextCount
from Shared.UI.Centrify.SubSelectors.grids import GridRowByGuid
from Shared.UI.Centrify.selectors import GridRow, LoadingMask

logger = logging.getLogger('test')


@pytest.mark.api_ui
@pytest.mark.pas
@pytest.mark.bhavna
def test_cloud_admin_login_from_my_system_account(core_session, pas_config, core_admin_ui, cleanup_accounts,
                                                  cleanup_resources, remote_users_qty1):
    """
    Test case: C14831
    :param core_session: centrify session
    :param core_admin_ui: Centrify UI session
    """
    maximum_event_wait_time = 120
    account_list = cleanup_accounts[0]
    system_list = cleanup_resources[0]

    systems = ServerManager.get_all_resources(core_session)
    accounts = ServerManager.get_all_accounts(core_session)

    for system in systems:
        system_list.append(system['ID'])
    for account in accounts:
        account_list.append(account['ID'])

    system_list = cleanup_resources[0]
    accounts_list = cleanup_accounts[0]
    # Getting system details.
    sys_name = f'{"Win-2012"}{guid()}'
    user_password = 'Hello123'
    sys_details = pas_config
    add_user_in_target_system = remote_users_qty1
    fdqn = sys_details['Windows_infrastructure_data']['FQDN']
    # Adding system.
    add_sys_result, add_sys_success = ResourceManager.add_system(core_session, sys_name,
                                                                 fdqn,
                                                                 'Windows',
                                                                 "Rdp")
    assert add_sys_success, f"failed to add system:API response result:{add_sys_result}"
    logger.info(f"Successfully added system:{add_sys_result}")
    system_list.append(add_sys_result)

    # Adding account in portal.
    acc_result, acc_success = ResourceManager.add_account(core_session, add_user_in_target_system[0],
                                                          password=user_password, host=add_sys_result)
    assert acc_success, f"Failed to add account in the portal: {acc_result}"
    logger.info(f"Successfully added account {add_user_in_target_system[0]} in the portal")
    accounts_list.append(acc_result)

    ui = core_admin_ui
    admin_user_uuid = UserManager.get_user_id(core_session, ui.user.centrify_user["Username"])

    # assigning cloud admin workspace login permission
    rights = "View,Login,UserPortalLogin"
    result, status = ResourceManager.assign_account_permissions(core_session, rights, ui.user.centrify_user["Username"],
                                                                admin_user_uuid, pvid=acc_result)
    assert status, f'failed to assign {rights} permission to cloud admin {ui.user.centrify_user["Username"]}.' \
                   f'returned result is: {result}'

    # Updating allow remote to enable RDP session for targeted system
    result, success = ResourceManager.update_system(core_session, add_sys_result, sys_name,
                                                    fdqn, "Windows",
                                                    allowremote=True)
    assert success, f'failed to assign rdp policy to account {add_user_in_target_system[0]} of system {sys_name}'

    ui.navigate(('Workspace', 'My System Accounts'))
    ui.expect(GridRow(sys_name), f'Expected to find system {sys_name} in My System Account but did not')
    ui.right_click_action(GridRow(sys_name), 'Login')

    ui.switch_to_pop_up_window()
    ui.expect_disappear(LoadingMask(), 'Error occurred while launching workspace login session', time_to_wait=250)
    ui.switch_to_main_window()

    # wait for manged password change event
    filter = [['AccountName', add_user_in_target_system[0]]]
    RedrockController.wait_for_event_by_type_filter(core_session, "Cloud.Server.LocalAccount.RDPSession.Start",
                                                    filter=filter,
                                                    maximum_wait_second=maximum_event_wait_time)  # wait for 20 seonds
    # Api call to get details of account active session
    status, result = ResourceManager.get_my_active_sessions(core_session, acc_result)
    assert status, f'failed to retrieve details for active account session data, return result is {result}'
    logger.info(f'details for active account {add_user_in_target_system[0]} are {result}')

    ui.navigate('Resources', 'Systems')
    ui.search(sys_name)
    ui.expect(GridRowByGuid(add_sys_result),
              expectation_message=f'failed to search for the system by id {add_sys_result}')
    ui.click_row(GridRowByGuid(add_sys_result))

    # fetching Active session value from system view page
    ui.inner_text_of_element(ActiveSessionTextCount(), expectation_message='1',
                             warning_message="RDP Not taken from user")
    logger.info(f'Active session value incremented to 1: Active Sessions:1')
