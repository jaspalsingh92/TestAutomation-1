import pytest
import logging
from Utils.config_loader import Configs
from Shared.UI.Centrify.selectors import Selector, Modal
from selenium.webdriver.common.by import By

logger = logging.getLogger('test')


@pytest.mark.api_ui
@pytest.mark.pas
@pytest.mark.pasapi_ui
@pytest.mark.bhavna
def test_checkout_password_for_unmanaged_account_from_system_page(core_session, setup_pas_system_for_unix,
                                                                  core_admin_ui):
    """
    TC: C2506 - Checkout password for unmanaged account from system page
    :param setup_pas_system_for_unix: Adds and yield UUID of a Unix system and account associated to it.
    :param core_admin_ui: Authenticated Centrify browser session with cloud admin credentials from core.yaml
    """
    added_system_id, account_id, sys_info = setup_pas_system_for_unix
    resource_data = Configs.get_environment_node('resources_data', 'automation_main')
    acc_password = resource_data['Unix_infrastructure_data']['password']
    ui = core_admin_ui
    ui.navigate('Resources', 'Systems')
    ui.search(sys_info[0])
    ui.click_row(sys_info[0])
    ui.right_click_action(Selector(By.XPATH, f'//tr[@test-id = "{account_id}"]'), 'Checkout')
    ui._waitUntilSettled()
    logger.info(f'checking out password for "test_user" account from Unix system {sys_info[0]}')
    logger.info(f"Password checkout successful for account: {account_id} from 'Systems' page.")
    ui.switch_context(Modal())
    ui.button('Show Password')
    logger.info("Successfully clicked on 'Show password' button to reveal the password.")
    password_field = ui.check_exists(('XPATH', '//div[@itemid="passwordPlainText"]'))
    assert password_field, "Password field not available even after clicking 'Show password' button"
    logger.info(f"Password is visible after clicking 'Show password' button.")


