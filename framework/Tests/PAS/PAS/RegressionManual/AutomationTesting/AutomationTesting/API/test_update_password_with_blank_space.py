import pytest
import logging
from Shared.API.infrastructure import ResourceManager

logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_update_un_managed_account(pas_windows_setup, core_session):
    """
    :param pas_windows_setup: Fixture for adding a system and an account associated with it.
    :param core_session: Authenticated Centrify Session.
    TC: C2194 - Update password with blank space
    Update unmanaged account password
      Steps:
           Pre: Create system with 1 unmanage account and
            1. Try to update password
    """

    system_id, account_id, sys_info, connector_id, user_password = pas_windows_setup()
    logger.info(f"System: {sys_info[0]} successfully added with UUID: {system_id} and account: {sys_info[4]} "
                f"with UUID: {account_id} associated with it.")
    result, success = ResourceManager.update_password(core_session, account_id, " ")
    assert success, f"Did not update password, API Response: {result}"
    logger.info(f'Update password successfully without error, API Response::{result}')
