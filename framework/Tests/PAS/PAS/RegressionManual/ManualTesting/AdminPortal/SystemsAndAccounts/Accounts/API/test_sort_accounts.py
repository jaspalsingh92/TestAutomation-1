from Shared.API.infrastructure import ResourceManager
from Shared.API.server import ServerManager
import logging
import pytest

logger = logging.getLogger("test")


@pytest.mark.api_ui
@pytest.mark.pasapi
@pytest.mark.bhavna
@pytest.mark.pas
def test_sort_accounts(core_session, pas_setup):
    """
    Test Case ID: C2101
    Test Case Description: Sort accounts
    :param core_session: Authenticate API session
    :param pas_setup: Creates System and Account
    """
    system_id, account_id, sys_info = pas_setup
    sorting = ServerManager.get_all_accounts(core_session, sortby='Status', ascending=True)

    get_result_account_health, get_success_account_health = ResourceManager.check_account_health(core_session,
                                                                                                 account_id)
    assert get_success_account_health, f'Account is not reachable due to result: {get_result_account_health}'
    logger.info('Account created successfully')

    # Checking whether the first account's status is blank
    assert sorting[0]['Status'] == "", "Status is not blank because Account is unreachable"
    logger.info('Status is blank and it appears at the top after sorting it in ascending order.')
