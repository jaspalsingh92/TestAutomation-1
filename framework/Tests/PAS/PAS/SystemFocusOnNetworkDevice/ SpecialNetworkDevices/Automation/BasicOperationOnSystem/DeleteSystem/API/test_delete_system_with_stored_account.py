import pytest
import logging
from Shared.API.infrastructure import ResourceManager

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi
def test_delete_system_with_stored_account(core_session, network_device_setup):
    """
    TC: C2608 - Delete system with stored account
    :param core_session: Authenticated Centrify session.
    :param network_device_setup: Adds a network with account and returns UUID of both.
    """
    system_id, account_id, device_data, system_list, account_list = network_device_setup('checkpoint')

    # Deleting system without deleting associated account.
    result, success = ResourceManager.del_system(core_session, system_id)
    assert not success, f"System successfully deleted though system have active accounts. API response result: {result}"
    logger.info("Unable to delete the system. System has active accounts.")

    # Deleting associated account
    result, success = ResourceManager.del_account(core_session, account_id)
    assert success, f"Unable to delete account {account_id}, API response result: {result}."
    logger.info(f"Account :{account_id} successfully deleted.")
    account_list.remove(account_id)  # To avoid error during account cleanup.

    # Deleting system after deleting the associated account.
    result, success = ResourceManager.del_system(core_session, system_id)
    assert success, f"System: {system_id} successfully deleted. API response result: {result}"
    logger.info("System successfully deleted after deleting the associated accounts.")
    system_list.remove(system_id)  # To avoid error during resource cleanup.
