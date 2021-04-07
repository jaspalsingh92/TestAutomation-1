import pytest
import logging
from Shared.API.infrastructure import ResourceManager
from Shared.API.redrock import RedrockController

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi
@pytest.mark.pas_pdst
def test_add_system_with_unmanaged_proxy_account(core_session, pas_setup):
    """
       Test case : C279342
       :param core_session: Centrify session manager
       :param setup_pas_bat_for_unix: fixture that provide created unix system data
    """
    system_id, account_id, system_info =pas_setup
    system_rows = RedrockController.get_computer_with_ID(core_session, system_id)
    assert system_rows['Name'] == system_info[0], f"failed to find system {system_info[0]} in portal as returned system rows is {system_rows}"
    logger.info(f"system found {system_rows}")

    # Fetching account from added system to validate desired account is added or not
    account, status = ResourceManager.get_accounts_from_resource(core_session, system_id)
    assert status, f'failed to find account in response {account} status is returned {status}'
    logger.info(f"Account {account} found")

    # Fetching account information to validate desired account is unmanaged
    result, status = ResourceManager.get_account_information(core_session, account_id)
    assert status, f"failed to retrieve account information, returned result is {result}"

    is_managed = result['VaultAccount']['Row']['IsManaged']
    assert is_managed is False, f"Added account is not unmanaged account"
