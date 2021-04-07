import pytest
import logging
from Shared.API.infrastructure import ResourceManager
from Shared.API.redrock import RedrockController

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi
def test_system_with_managed_account(core_session, setup_pas_system_for_unix):
    """
    Test case : C279339
    :param core_session: Centrify session manager
    :param setup_pas_system_for_unix: fixture that provide created unix system data
    """
    system_id, account_id, system_info = setup_pas_system_for_unix
    system_rows = RedrockController.get_computer_with_ID(core_session, system_id)
    assert system_rows['Name'] == system_info[0], f"failed to find system {system_info[0]} in portal as returned system result is {system_rows}"
    logger.info(f"system found {system_rows}")

    account, status = ResourceManager.get_accounts_from_resource(core_session, system_id)
    assert status, f"failed to find accounts in system {system_info[0]} as returned account result is {account}"
    logger.info(f"Account found {account}")

    # Fetching account information to validate desired account is unmanaged
    result, status = ResourceManager.get_account_information(core_session, account_id)
    assert status, f"failed to retrieve account information, returned result is {result}"

    is_managed = result['VaultAccount']['Row']['IsManaged']
    assert is_managed is False, f"Added account is not managed account"
