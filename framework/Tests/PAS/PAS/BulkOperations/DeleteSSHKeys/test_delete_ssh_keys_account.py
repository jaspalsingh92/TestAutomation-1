import pytest
import logging
from Shared.API.infrastructure import ResourceManager
from Shared.API.redrock import RedrockController

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.discovery_failed
@pytest.mark.pasapi
@pytest.mark.managedssh
@pytest.mark.parametrize('remove_related', [True, False])
def test_delete_ssh_keys_and_account(core_session, add_system_with_ssh_account, get_ssh_key_function, remove_related):
    system_id, account_id, ssh_id, system_list, account_list, ssh_list = add_system_with_ssh_account

    # Deleting SSH Account
    all_key_ids = [ssh_id, get_ssh_key_function]
    delete_result, delete_success = ResourceManager.del_multiple_ssh_keys(core_session, all_key_ids,
                                                                          run_sync=True, remove_related_account=remove_related)
    if remove_related:
        assert delete_success, f"SSH key {ssh_id} deletion failed with API response result: {delete_result}"
        logger.info(f"Account{account_id} associated with system {system_id} and SSH key {ssh_id} was deleted successfully")
    else:
        assert not delete_success, "Delete should have failed with attached account {delete_result}"
    account_list.remove(account_id)
    activity = RedrockController.get_ssh_activity(core_session, ssh_id)
    sql_query = RedrockController.get_query_for_ids('VaultAccount', [account_id])
    result = RedrockController.redrock_query(core_session, sql_query)

    if remove_related:
        assert len(result) == 0, f"Account not deleted as expected {result}"
    else:
        assert len(result) == 1, f"Account was delete and should not have been {result} when removed_related_account == False"

    sql_query = RedrockController.get_query_for_ids('SshKeys', all_key_ids)
    result = RedrockController.redrock_query(core_session, sql_query)

    if remove_related:
        assert len(result) == 0, f"SSH keys not deleted as expected {result}"
    else:
        assert len(result) == 1 and ssh_id in str(result), f"Should remain exactly 1 SSH key associated with account {result}"

