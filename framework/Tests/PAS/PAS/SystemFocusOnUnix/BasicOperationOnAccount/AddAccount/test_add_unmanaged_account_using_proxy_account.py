import pytest
import logging
from Shared.API.infrastructure import ResourceManager
from Shared.UI.Centrify.SubSelectors.modals import Modal
from Utils.config_loader import Configs
from Shared.API.redrock import RedrockController
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.api_ui
@pytest.mark.pas
@pytest.mark.pasapi_ui
@pytest.mark.bhavna
@pytest.mark.smoke
def test_add_unmanaged_account_using_proxy_account(core_session, cleanup_accounts, setup_pas_system_for_unix,
                                                   core_admin_ui):
    """
    TC- C2500: Add unmanaged account using proxy account
    :param core_session: Authenticated Centrify session.
    :param setup_pas_system_for_unix: Adds and yields GUID for a unix system and account associated with it.
    :param core_admin_ui: Authenticated Centrify browser session.
    """
    added_system_id, account_id, sys_info = setup_pas_system_for_unix
    test_data = Configs.get_environment_node('resources_data', 'automation_main')
    unix_data = test_data['Unix_infrastructure_data']
    user_name = f"{unix_data['account_name']}{guid()}"
    ui = core_admin_ui
    accounts_list = cleanup_accounts[0]

    result, success = ResourceManager.update_system(core_session, added_system_id, sys_info[0], sys_info[1],
                                                    sys_info[2], proxyuser=unix_data['proxy_user'],
                                                    proxyuserpassword=unix_data['proxy_password'],
                                                    proxyuserismanaged=False)
    assert success, f"Unable to add a managed proxy user for {sys_info[0]}. API response result: {result}"
    logger.info(f"Proxy account {unix_data['proxy_user']} added to Unix system: {sys_info[0]}")

    ui.navigate('Resources', 'Systems')
    ui.search(sys_info[0])
    ui.click_row(sys_info[0])
    ui.launch_modal("Add", "Add Account")
    ui.switch_context(Modal())
    ui.input('User', user_name)
    ui.input('Password', unix_data['password'])
    ui.check('UseWheel')
    ui.button('Add')
    ui._waitUntilSettled()
    ui.remove_context()
    assert ui.check_exists(('XPATH', f'//div[text()="{user_name}"]')), \
        f"Account {user_name} couldn't be added to system: {sys_info[0]} using proxy account: {unix_data['proxy_user']}"
    logger.info(f"Account {user_name} added to system: {sys_info[0]} using proxy account: {unix_data['proxy_user']}.")

    # Teardown for the added account
    added_account_id = RedrockController.get_account_id_by_username(core_session, user_name)
    accounts_list.append(added_account_id)
