import pytest
import logging
from Utils.guid import guid
from Shared.API.redrock import RedrockController
from Shared.API.infrastructure import ResourceManager

logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_update_unmanaged_account_password(core_session, setup_pas_system_for_unix):
    """
    TC: C280138 - Update unmanaged account and check password history

    :param core_session: Authenticated Centrify session
    :param setup_pas_system_for_unix: Yields UUID for an added Unix system and an account associated to it.

    Steps:
    1. Adding a valid system with managed account.
    2. Change the password.
    3. Check password change activity under "Account Activies".
    """

    added_system_id, account_id, sys_info = setup_pas_system_for_unix

    # Updating Password for unmanaged account
    password_result, password_success = ResourceManager.update_password(core_session, account_id, guid())
    assert password_success, f"Password updation failed with API response Result: {password_result}"
    logger.info(f"Password Updated successfully for account {account_id}")

    # Verify Account Activity after password updated
    activity_logs = RedrockController.get_account_activity(core_session, account_id)
    events = []
    for activity in activity_logs:
        events.append(activity['EventType'])
    assert "Cloud.Server.LocalAccount.PasswordUpdate" in events, f"Password update activity not displayed under" \
                                                                 f" Account Activity Section for Account : {account_id}"
    logger.info(f"Password updated record displayed in Account Activity section")

    # Verifying Password History for account
    password_history_records = RedrockController.get_password_history_with_id(core_session, account_id)
    assert password_history_records, f"Password updated history not found for account {account_id}"
    logger.info(f"Password history successfully retrieved for account: {account_id}")
