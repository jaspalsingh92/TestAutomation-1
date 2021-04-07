import pytest
import logging
from Shared.API.infrastructure import ResourceManager

logger = logging.getLogger('test')


@pytest.mark.api_ui
@pytest.mark.pas
@pytest.mark.pasapi_ui
@pytest.mark.bhavna
def test_checkin_password_for_managed_account_from_workspace(core_session, setup_pas_system_for_unix, core_admin_ui):
    """
    TC: C2503 - Checkin password for managed account from Workspace page
    :param core_session: Authenticated Centrify Session.
    :param setup_pas_system_for_unix: Adds and yields uuid of a Unix system and account associated to it.
    """
    added_system_id, account_id, sys_info = setup_pas_system_for_unix
    co_result, co_success = ResourceManager.check_out_password(core_session, 1, account_id, "checkout test")
    assert co_success, f"Account checkout failed with APi response result: {co_result}."
    ui = core_admin_ui
    ui.navigate(['Workspace', 'My Password Checkouts'])
    ui.check_row_by_guid(co_result["COID"])
    ui.action('Checkin')
    logger.info(f'Password for {account_id} has been checked-in from workspace page.')
    result, success = ResourceManager.check_in_password(core_session, account_id)
    assert success is False, "Password checkin from workspace page failed"
    logger.info('Password successfully checked-in from workspace page.')
    

