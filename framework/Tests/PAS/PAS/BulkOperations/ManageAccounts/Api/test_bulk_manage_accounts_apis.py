import time
import pytest
import logging
from Shared.API.sets import SetsManager
from Shared.API.jobs import JobManager
from Shared.API.redrock import RedrockController
from Utils.guid import guid
from Shared.API.infrastructure import ResourceManager
from Shared.endpoint_manager import EndPoints
from Shared.util import Util

logger = logging.getLogger('test')

pytestmark = [pytest.mark.api, pytest.mark.cps, pytest.mark.bulk_manage_accounts]


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.parametrize('change_method', ["ids", "ids_with_invalid", "sql", "group"])  # removing "checkin" since it is out of scope for this story
def test_bulk_manage_works_with_different_methods_of_specifying_systems(
        core_session,
        remote_unmanaged_users_with_mirrored_managed_local_users_qty3,
        windows_test_machine_config, change_method):
    account_ids = remote_unmanaged_users_with_mirrored_managed_local_users_qty3

    job_result = None
    if change_method == "ids":
        job_result, success = ResourceManager.manage_multiple_accounts(core_session, account_ids)
        assert success, "Did not bulk manage account"
    elif change_method == "ids_with_invalid":
        job_result, success = ResourceManager.manage_multiple_accounts(core_session, ["foo"] + list(account_ids))
        assert success, "Did not bulk manage account"
    elif change_method == "sql":
        sql_query = 'SELECT * FROM VaultAccount WHERE ' + ' OR '.join(('VaultAccount.ID = "' + str(n) + '"' for n in account_ids))
        job_result, success = ResourceManager.manage_multiple_accounts(core_session, [], set_query=sql_query)
        assert success, "Did not bulk manage accounts"
    elif change_method == "group":
        some_set_name = "ApiSet" + guid()
        SetsManager.create_manual_collection(core_session, some_set_name, "VaultAccount", None)
        set_id = SetsManager.get_collection_id(core_session, some_set_name, "VaultAccount")
        SetsManager.update_members_collection(core_session, 'add', account_ids, 'VaultAccount', set_id)
        filters = SetsManager.get_object_collection_and_filter_by_name(core_session, some_set_name, "VaultAccount")['Filters']
        job_result, success = ResourceManager.manage_multiple_accounts(core_session, [], set_query=filters)
        assert success, "Did not bulk manage accounts"
    else:
        raise Exception(f"Bad input variable change_method {change_method}")

    _validate_accounts_are_managed(core_session, account_ids, job_result)

    user_info = core_session.get_current_session_user_info().json()['Result']
    username = user_info['Name']
    start_type = 'Cloud.Core.AsyncOperation.AccountBulkManagement.Start.Multi'
    end_type = 'Cloud.Core.AsyncOperation.AccountBulkManagement.Success.Multi'
    start_message = f'{username} initiated management of {len(account_ids)} accounts'
    end_message = f'{username} successfully managed {len(account_ids)} accounts'

    RedrockController.expect_event_message_by_type(core_session, start_type, start_message)
    RedrockController.expect_event_message_by_type(core_session, end_type, end_message)


@pytest.mark.api
@pytest.mark.pas
def test_bulk_manage_works_quickly(core_session, remote_unmanaged_users_with_mirrored_managed_local_users_qty3,
                                   windows_test_machine_config):
    account_ids = remote_unmanaged_users_with_mirrored_managed_local_users_qty3

    reasonable_amount_of_time_to_execute = 90
    start_time = time.time()
    job_result, success = ResourceManager.manage_multiple_accounts(core_session, account_ids, wait_time=600)
    assert success, "Did not bulk manage accounts"
    end_time = time.time()
    elapsed_time = end_time - start_time

    assert elapsed_time < reasonable_amount_of_time_to_execute, f'Failed to manage accounts in a reasonable amount of time. Took {elapsed_time} seconds'
    _validate_accounts_are_managed(core_session, account_ids, job_result)
    assert elapsed_time <= reasonable_amount_of_time_to_execute, "Bulk rotate did not complete in a reasonable amount of time"


@pytest.mark.api
@pytest.mark.pas
def test_bulk_manage_works_with_overlapping_calls(
        core_session, remote_unmanaged_users_with_mirrored_managed_local_users_qty3, windows_test_machine_config):

    account_ids = remote_unmanaged_users_with_mirrored_managed_local_users_qty3

    for i in range(2):
        job_result, success = ResourceManager.manage_multiple_accounts(core_session, account_ids, wait_time=-1)
        assert success, "Did not bulk manage accounts"
    job_result, success = ResourceManager.manage_multiple_accounts(core_session, account_ids, wait_time=60)
    assert success, "Did not bulk manage accounts"

    _validate_accounts_are_managed(core_session, account_ids, job_result)


@pytest.mark.api
@pytest.mark.pas
def test_bulk_manage_fails_with_invalid_query(core_session):
    result, success = ResourceManager.manage_multiple_accounts(core_session, [])
    assert not success, "Call was invalid, should not have succeeded"


@pytest.mark.api
@pytest.mark.pas
def test_bulk_manage_fails_with_invalid_query2(core_session):
    my_data = Util.scrub_dict({})
    request = core_session.apirequest(EndPoints.ACCOUNT_MULTI_MANAGE, my_data)
    request_json = request.json()
    logger.info("Multiple manage accounts returned " + request.text)
    assert not request_json['success'], "Call succeeded and should have failed"


@pytest.mark.api
@pytest.mark.pas
def test_cannot_manage_accounts_without_permission(
        core_session, remote_unmanaged_users_with_mirrored_managed_local_users_qty3, windows_test_machine_config,
        users_and_roles):
    right_data = ["Privileged Access Service Power User", "role_Privileged Access Service Power User"]
    requestor_session = users_and_roles.get_session_for_user(right_data[0])
    results_role = users_and_roles.get_role(right_data[0])

    account_ids = remote_unmanaged_users_with_mirrored_managed_local_users_qty3

    job_id, success = ResourceManager.manage_multiple_accounts(requestor_session, account_ids)
    assert success, "Did not kick off bulk manage accounts job"
    result = ResourceManager.get_job_state(core_session, job_id)
    assert result == "Succeeded", "Job did not execute"

    # Validates accounts are still not managed.
    _validate_accounts_are_not_managed(requestor_session, account_ids, job_id)

    permission_string = "Owner,View,Manage,Delete,Login,Naked,UpdatePassword,RotatePassword,FileTransfer,UserPortalLogin"

    account_id = account_ids[2]  # Grant permission to only one of the accounts, the middle one
    result, success = ResourceManager.assign_account_permissions(core_session, permission_string, results_role['Name'], results_role['ID'], "Role", account_id)
    assert success, "Did not set account permissions " + str(result)

    job_id, success = ResourceManager.manage_multiple_accounts(requestor_session, account_ids)
    assert success, "Did not kick off bulk rotate passwords job"
    result = ResourceManager.get_job_state(core_session, job_id)
    assert result == "Succeeded", "Job did not execute"

    # Validate the one account is managed.
    _validate_accounts_are_not_managed(requestor_session, [account_ids[0], account_ids[1]], job_id)
    _validate_accounts_are_managed(requestor_session, [account_ids[2]], job_id)

    user_info = requestor_session.get_current_session_user_info().json()['Result']
    username = user_info['Name']
    start_type = 'Cloud.Core.AsyncOperation.AccountBulkManagement.Start.Multi'
    end_type = 'Cloud.Core.AsyncOperation.AccountBulkManagement.Failure.Multi'
    start_message = f'{username} initiated management of {len(account_ids)} accounts'
    end_message = f'{username} failed to manage 2 of 3 accounts'

    RedrockController.expect_event_message_by_type(core_session, start_type, start_message)
    RedrockController.expect_event_message_by_type(core_session, end_type, end_message)



def _validate_accounts_are_managed(session, account_ids, job_id):
    rows = RedrockController.get_rows_matching_ids(session, 'VaultAccount', account_ids)
    job_report = JobManager.get_job_report(session, job_id)

    for row in rows:
        assert row['IsManaged'] is True, f'Expected account to be managed after bulk manage account but it was not {row} {job_report}'


def _validate_accounts_are_not_managed(session, account_ids, job_id):
    rows = RedrockController.get_rows_matching_ids(session, 'VaultAccount', account_ids)
    job_report = JobManager.get_job_report(session, job_id)

    for row in rows:
        assert row['IsManaged'] is False, f'Expected account to not be managed after bulk manage account but it was {row} {job_report}'
