import pytest
import logging
from Shared.API.infrastructure import ResourceManager

logger = logging.getLogger("test")


@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi
def test_check_account_name_delete_user_account_dialog(core_session, pas_windows_setup):
    """
    TC:C2193 Check account name on Delete User Account dialog.
    :param core_session: Returns a API session.
    :param pas_windows_setup: Returns a fixture.
    """
    # Creating a system and account.
    system_id, account_id, sys_info, connector_id, user_password = pas_windows_setup()

    # Deleting account from above system
    success, result = ResourceManager.del_account(core_session, account_id)
    assert success, f'failed to delete account with response {result}'
    logger.info(f"un managed account deleted successfully from the System.")
