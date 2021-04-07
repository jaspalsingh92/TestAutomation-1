import pytest
import logging
from Shared.API.infrastructure import ResourceManager
from Utils.config_loader import Configs

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.bhavna
def test_checkout_password_for_unmanaged_account_from_account_page(setup_pas_system_for_unix,
                                                                   core_session):
    """
    TC: C2506 - Checkout password for unmanaged account from account page
    :param setup_pas_system_for_unix: Adds and yield UUID of a Unix system and account associated to it.
    :param core_admin_ui: Authenticated Centrify browser session with cloud admin credentials from core.yaml
    """

    added_system_id, account_id, sys_info = setup_pas_system_for_unix

    automation_data = Configs.get_environment_node('resources_data', 'automation_main')
    password = automation_data['Unix_infrastructure_data']['password']

    result, success = ResourceManager.check_out_password(core_session, 1, account_id, "Copy the password")
    assert success, f"Password checkout failed with API response result: {result}"
    logger.info(f"Password successfully checked out for account: '{sys_info[4]}'")

    assert result['Password'] == password, "Clipboard contents didn't change after clicking 'Copy Password' button."
    logger.info("Successfully clicked on 'Copy Password' button to copy the password.")
