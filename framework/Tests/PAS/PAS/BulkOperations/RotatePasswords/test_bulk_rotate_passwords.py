import pytest
import logging
from Shared.API.bulkoperations import BulkOperations
from Shared.API.infrastructure import ResourceManager
from Shared.API.redrock import RedrockController

pytestmark = [pytest.mark.pas, pytest.mark.cps, pytest.mark.bulk_rotate_passwords]

logger = logging.getLogger('test')


def test_bulk_rotate_works(core_session, remote_users_with_mirrored_managed_local_users_qty3,
                           windows_test_machine_config, users_and_roles):
    remote_ip = windows_test_machine_config['ip_address']

    account_ids, accounts = BulkOperations.grab_relevant_users(core_session, remote_users_with_mirrored_managed_local_users_qty3)
    account_names = []
    for i in range(len(accounts)):
        account_names.append(accounts[i][1])

    passwords_fetched = BulkOperations.checkout_users(core_session, accounts)

    result, success = ResourceManager.rotate_multiple_passwords(core_session, account_ids)
    assert success, "Did not bulk rotate passwords"
    job_ids = RedrockController.get_all_running_bulk_rotate_password_jobs(core_session)

    for id in job_ids:
        ResourceManager.wait_for_job_state_succeeded(core_session, id)

    # Verify passwords are no longer right
    BulkOperations.validate_users_with_login(remote_ip, passwords_fetched, [False] * len(passwords_fetched), "E2E")
