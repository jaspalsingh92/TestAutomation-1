import pytest
import logging
from Shared.API.infrastructure import ResourceManager

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi
@pytest.mark.smoke
def test_delete_system_with_account(core_session, pas_setup):
    """
    Test case: C279343
    :param core_session: CENTRIFY session
    :param pas_setup: fixture to add system and account
    :return:
    """
    system_id, account_id, sys_info = pas_setup
    result, status = ResourceManager.del_system(core_session, system_id)
    assert status is False, f'system {sys_info[0]} is deleted despite system having active accounts, returned result is {result}'

    result, status, = ResourceManager.del_account(core_session, account_id)
    assert status, f"Failed to delete account with result {result}"

    result, status = ResourceManager.del_system(core_session, system_id)
    assert status, f"Failed to delete system with status {status}, returned result is {result}"
