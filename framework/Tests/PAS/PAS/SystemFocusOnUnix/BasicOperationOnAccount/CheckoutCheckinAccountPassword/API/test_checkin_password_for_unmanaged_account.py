import pytest
import logging
from Shared.API.infrastructure import ResourceManager

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
@pytest.mark.pas_pdst
def test_checkin_password_for_unmanaged_account(core_session, setup_pas_system_for_unix):
    """
    TC: C279514 - Checkin password for unmanaged account.
    :param core_session: Authenticated Centrify Session.
    :param setup_pas_system_for_unix: Adds and yields uuid of a Unix system and account associated to it.
    """
    added_system_id, account_id, sys_info = setup_pas_system_for_unix
    co_result, co_success = ResourceManager.check_out_password(core_session, 1, account_id, "checkout test")
    assert co_success, f"Account checkout failed with APi response result: {co_result}."

    checkin_result, checkin_success = ResourceManager.check_in_password(core_session, co_result['COID'])
    assert checkin_success, f"Checkin for account {account_id} failed with API response result: {checkin_result}"
    logger.info(f'Successfully checked in the password for account {account_id} with API response result:'
                f' {checkin_result} and success: {checkin_success}')
