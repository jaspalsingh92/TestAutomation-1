from Shared.API.infrastructure import ResourceManager
from Shared.API.sets import SetsManager
from Shared.UI.Centrify.SubSelectors.grids import GridCell
from Shared.UI.Centrify.SubSelectors.modals import Modal
from Shared.UI.Centrify.SubSelectors.navigation import ActiveMainContentArea
from Shared.UI.Centrify.selectors import LoadingMask, Div
from Utils.config_loader import Configs
from Utils.guid import guid
import logging
import pytest

logger = logging.getLogger("test")


@pytest.mark.ui
@pytest.mark.pasapi_ui
@pytest.mark.bhavna
@pytest.mark.pas121
def test_login_stored_account(core_session, setup_pas_system_for_unix, set_cleaner, core_admin_ui):
    """
    Test Case ID: C2087
    Test Case Description: Login as stored account after proxy account enabled
    :param core_session: Returns API session
    :param setup_pas_system_for_unix: Creates Unix System and Account
    :param set_cleaner: Delete Set
    :param core_admin_ui: Authenticates Centrify UI session
    """
    system_id, account_id, sys_info = setup_pas_system_for_unix
    system_name = sys_info[0]
    FQDN = sys_info[1]
    computer_class = sys_info[2]
    account_name = sys_info[4]
    systems_data = Configs.get_environment_node('resources_data', 'automation_main')
    expected_system_class = systems_data['Unix_infrastructure_data']
    result, success = ResourceManager.update_system(core_session, system_id, system_name, FQDN,
                                                    computer_class, proxyuser=expected_system_class['proxy_user'],
                                                    proxyuserpassword=expected_system_class['proxy_password'],
                                                    proxyuserismanaged=False, allowremote=True)
    assert success, 'Failed to update system'
    logger.info(f'System successfully updated with result: {result}')
    ui = core_admin_ui
    name_of_set = f'Set{guid()}'
    ui.navigate('Resources', 'Systems')
    ui.launch_add('Add', 'Create Set')
    ui.input('Name', name_of_set)
    ui.tab('Members')
    ui.launch_modal('Add', 'Add System')
    ui.search(system_name)
    ui.check_row(system_name)
    ui.close_modal('Add')
    ui.save()
    id_of_set = SetsManager.get_collection_id(core_session, name_of_set, 'Server')
    assert id_of_set, 'Set creation Failed'
    logger.info(f"Set: '{name_of_set}' created successfully")
    set_cleaner.append(id_of_set)

    # Login into Stored Account
    ui._waitUntilSettled()
    ui.switch_context(ActiveMainContentArea())
    ui.right_click_action(Div(system_name), 'Select/Request Account')
    ui.switch_context(Modal(system_name + ' Login'))
    ui.expect_disappear(LoadingMask(), 'Expected to find account but it did not', 30)
    ui.search(account_name)
    ui.expect(GridCell(account_name), 'Expected to find account name but it did not.').try_click()
    ui.close_modal('Select')
    ui.switch_to_pop_up_window()
    ui.expect_disappear(LoadingMask(), 'Expected to login in account but it did not', 30)
    logger.info(f'Successfully logged in Account:{account_name}.')
    ui.switch_to_main_window()
