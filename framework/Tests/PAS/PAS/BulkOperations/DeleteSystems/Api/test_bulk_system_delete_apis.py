import logging
import pytest
from pytest import skip

from Shared.API.infrastructure import ResourceManager
from Shared.API.redrock import RedrockController
from Shared.API.secret import get_file_secret_contents, set_users_effective_permissions
from Shared.API.sets import SetsManager
from Shared.API.jobs import JobManager
from Shared.data_manipulation import DataManipulation
from Shared.API.users import UserManager
from Shared.util import Util
from Shared.endpoint_manager import EndPoints
from Utils.guid import guid

pytestmark = [pytest.mark.api, pytest.mark.cps, pytest.mark.bulk_system_delete, pytest.mark.pas]

logger = logging.getLogger('test')


def test_bulk_system_delete_by_sql_query_only_deletes_correct_systems_and_accounts(
        clean_bulk_delete_systems_and_accounts, core_session, list_of_created_systems):
    user_info = core_session.get_current_session_user_info().json()['Result']

    assert len(ResourceManager.get_multi_added_system_ids(core_session, [
        "x"])) == 0  # Use fake GUID string to ensure that filter is working properly, since empty list means no filter
    assert len(ResourceManager.get_multi_added_account_ids(core_session, ["x"])) == 0

    batch1 = ResourceManager.add_multiple_systems_with_accounts(core_session, 3, 4, list_of_created_systems)
    batch2 = ResourceManager.add_multiple_systems_with_accounts(core_session, 1, 2, list_of_created_systems)
    batch3 = ResourceManager.add_multiple_systems_with_accounts(core_session, 4, 6, list_of_created_systems)
    batch4 = ResourceManager.add_multiple_systems_with_accounts(core_session, 2, 8, list_of_created_systems)
    batch5 = ResourceManager.add_multiple_systems_with_accounts(core_session, 5, 1, list_of_created_systems)

    all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values(
        [batch1, batch2, batch3, batch4, batch5])

    assert len(ResourceManager.get_multi_added_system_ids(core_session,
                                                          all_systems)) == 15, "Found wrong number of added systems"
    assert len(ResourceManager.get_multi_added_account_ids(core_session,
                                                           all_systems)) == 59, "Found wrong number of add accounts"

    delete_system_ids, delete_account_ids = DataManipulation.aggregate_lists_in_dict_values([batch2, batch4])
    keep_system_ids, keep_account_ids = DataManipulation.aggregate_lists_in_dict_values([batch1, batch3, batch5])

    sql_query = RedrockController.get_query_for_ids('Server', delete_system_ids)
    ResourceManager.del_multiple_systems_by_query(core_session, sql_query, False, "")

    assert set(ResourceManager.get_multi_added_system_ids(core_session,
                                                          all_systems).values()) == keep_system_ids, "Set of expected remaining systems did not match search"
    assert set(ResourceManager.get_multi_added_account_ids(core_session,
                                                           all_systems)) == keep_account_ids, "Set of expected remaining accounts did not match search"

    username = user_info['Name']
    start_type = 'Cloud.Core.AsyncOperation.BulkSystemDelete.StartQuery.Multi'
    end_type = 'Cloud.Core.AsyncOperation.BulkSystemDelete.Success.Multi'
    start_message = f'{username} initiated delete of multiple systems'
    end_message = f'{username} successfully deleted {len(delete_system_ids)} systems'

    RedrockController.expect_event_message_by_type(core_session, start_type, start_message)
    RedrockController.expect_event_message_by_type(core_session, end_type, end_message)


def test_bulk_system_delete_by_ids_only_deletes_correct_systems_and_accounts(clean_bulk_delete_systems_and_accounts,
                                                                             core_session, list_of_created_systems):
    user_info = core_session.get_current_session_user_info().json()['Result']

    batch1 = ResourceManager.add_multiple_systems_with_accounts(core_session, 3, 4, list_of_created_systems)
    batch2 = ResourceManager.add_multiple_systems_with_accounts(core_session, 1, 2, list_of_created_systems)
    batch3 = ResourceManager.add_multiple_systems_with_accounts(core_session, 4, 6, list_of_created_systems)
    batch4 = ResourceManager.add_multiple_systems_with_accounts(core_session, 2, 8, list_of_created_systems)
    batch5 = ResourceManager.add_multiple_systems_with_accounts(core_session, 5, 1, list_of_created_systems)
    all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values(
        [batch1, batch2, batch3, batch4, batch5])

    delete_system_ids, delete_account_ids = DataManipulation.aggregate_lists_in_dict_values([batch2, batch4])
    keep_system_ids, keep_account_ids = DataManipulation.aggregate_lists_in_dict_values([batch1, batch3, batch5])

    all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values(
        [batch1, batch2, batch3, batch4, batch5])

    ResourceManager.del_multiple_systems(core_session, delete_system_ids)

    assert set(ResourceManager.get_multi_added_system_ids(core_session,
                                                          all_systems).values()) == keep_system_ids, "Set of expected remaining systems did not match search"
    assert set(ResourceManager.get_multi_added_account_ids(core_session,
                                                           all_systems)) == keep_account_ids, "Set of expected remaining accounts did not match search"

    username = user_info['Name']
    start_type = 'Cloud.Core.AsyncOperation.BulkSystemDelete.Start.Multi'
    end_type = 'Cloud.Core.AsyncOperation.BulkSystemDelete.Success.Multi'
    start_message = f'{username} initiated delete of {len(delete_system_ids)} systems'
    end_message = f'{username} successfully deleted {len(delete_system_ids)} systems'

    RedrockController.expect_event_message_by_type(core_session, start_type, start_message)
    RedrockController.expect_event_message_by_type(core_session, end_type, end_message)


def test_bulk_system_delete_by_ids_only_deletes_correct_systems_and_accounts_fast_track(
        clean_bulk_delete_systems_and_accounts, core_session, list_of_created_systems):
    user_info = core_session.get_current_session_user_info().json()['Result']

    batch1 = ResourceManager.add_multiple_systems_with_accounts(core_session, 3, 4, list_of_created_systems)
    batch2 = ResourceManager.add_multiple_systems_with_accounts(core_session, 1, 2, list_of_created_systems)
    batch3 = ResourceManager.add_multiple_systems_with_accounts(core_session, 4, 6, list_of_created_systems)
    batch4 = ResourceManager.add_multiple_systems_with_accounts(core_session, 2, 8, list_of_created_systems)
    batch5 = ResourceManager.add_multiple_systems_with_accounts(core_session, 5, 1, list_of_created_systems)
    all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values(
        [batch1, batch2, batch3, batch4, batch5])

    delete_system_ids, delete_account_ids = DataManipulation.aggregate_lists_in_dict_values([batch2, batch4])
    keep_system_ids, keep_account_ids = DataManipulation.aggregate_lists_in_dict_values([batch1, batch3, batch5])

    all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values(
        [batch1, batch2, batch3, batch4, batch5])

    ResourceManager.del_multiple_systems(core_session, delete_system_ids, savepasswords=True, wait_time=0,
                                         skip_if_has_apps_or_services=True, run_sync=True)

    assert set(ResourceManager.get_multi_added_system_ids(core_session,
                                                          all_systems).values()) == keep_system_ids, "Set of expected remaining systems did not match search"
    assert set(ResourceManager.get_multi_added_account_ids(core_session,
                                                           all_systems)) == keep_account_ids, "Set of expected remaining accounts did not match search"

    username = user_info['Name']
    start_type = 'Cloud.Core.AsyncOperation.BulkSystemDelete.Start.Multi'
    end_type = 'Cloud.Core.AsyncOperation.BulkSystemDelete.Success.Multi'
    start_message = f'{username} initiated delete of {len(delete_system_ids)} systems'
    end_message = f'{username} successfully deleted {len(delete_system_ids)} systems'

    RedrockController.expect_event_message_by_type(core_session, start_type, start_message)
    RedrockController.expect_event_message_by_type(core_session, end_type, end_message)


def test_bulk_system_by_api_set_correct_systems_and_accounts(clean_bulk_delete_systems_and_accounts, core_session,
                                                             list_of_created_systems):
    batch1 = ResourceManager.add_multiple_systems_with_accounts(core_session, 3, 4, list_of_created_systems)
    batch2 = ResourceManager.add_multiple_systems_with_accounts(core_session, 1, 2, list_of_created_systems,
                                                                sys_type="Unix")
    batch3 = ResourceManager.add_multiple_systems_with_accounts(core_session, 4, 6, list_of_created_systems)
    batch4 = ResourceManager.add_multiple_systems_with_accounts(core_session, 2, 8, list_of_created_systems)
    batch5 = ResourceManager.add_multiple_systems_with_accounts(core_session, 5, 1, list_of_created_systems,
                                                                sys_type="Unix")

    delete_system_ids, delete_account_ids = DataManipulation.aggregate_lists_in_dict_values([batch2, batch4])
    keep_system_ids, keep_account_ids = DataManipulation.aggregate_lists_in_dict_values([batch1, batch3, batch5])

    all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values(
        [batch1, batch2, batch3, batch4, batch5])

    some_set_name = "ApiSet" + guid()
    SetsManager.create_manual_collection(core_session, some_set_name, "Server", None)
    set_id = SetsManager.get_collection_id(core_session, some_set_name, "Server")
    SetsManager.update_members_collection(core_session, 'add', list(delete_system_ids), 'Server', set_id)

    collection_and_filters = SetsManager.get_object_collection_and_filter_by_name(core_session, some_set_name, "Server")
    filters = collection_and_filters['Filters']

    logger.info(f'Manual set {collection_and_filters} - members - {delete_system_ids}')
    result, success = ResourceManager.del_multiple_systems_by_query(core_session, filters, False, "")
    assert success is True, f'Delete systems job failed when expected success'

    SetsManager.delete_collection(core_session, set_id)

    assert set(ResourceManager.get_multi_added_system_ids(core_session,
                                                          all_systems).values()) == keep_system_ids, "Set of expected remaining systems did not match search"
    assert set(ResourceManager.get_multi_added_account_ids(core_session,
                                                           all_systems)) == keep_account_ids, "Set of expected remaining accounts did not match search"


def test_bulk_system_by_api_set_correct_systems_and_accounts_fast_track(clean_bulk_delete_systems_and_accounts,
                                                                        core_session, list_of_created_systems):
    batch1 = ResourceManager.add_multiple_systems_with_accounts(core_session, 3, 4, list_of_created_systems)
    batch2 = ResourceManager.add_multiple_systems_with_accounts(core_session, 1, 2, list_of_created_systems,
                                                                sys_type="Unix")
    batch3 = ResourceManager.add_multiple_systems_with_accounts(core_session, 5, 1, list_of_created_systems,
                                                                sys_type="Unix")

    delete_system_ids, delete_account_ids = DataManipulation.aggregate_lists_in_dict_values([batch2])
    keep_system_ids, keep_account_ids = DataManipulation.aggregate_lists_in_dict_values([batch1, batch3])

    all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values([batch1, batch2, batch3])

    some_set_name = "ApiSet" + guid()
    SetsManager.create_manual_collection(core_session, some_set_name, "Server", None)
    set_id = SetsManager.get_collection_id(core_session, some_set_name, "Server")
    SetsManager.update_members_collection(core_session, 'add', list(delete_system_ids), 'Server', set_id)

    collection_and_filters = SetsManager.get_object_collection_and_filter_by_name(core_session, some_set_name, "Server")
    filters = collection_and_filters['Filters']

    logger.info(f'Manual set {collection_and_filters} - members - {delete_system_ids}')
    result, success = ResourceManager.del_multiple_systems_by_query(core_session, filters, savepasswords=False,
                                                                    secretname="", run_sync=True)
    assert success is True, f'Delete systems job failed when expected success'

    SetsManager.delete_collection(core_session, set_id)

    assert set(ResourceManager.get_multi_added_system_ids(core_session,
                                                          all_systems).values()) == keep_system_ids, "Set of expected remaining systems did not match search"
    assert set(ResourceManager.get_multi_added_account_ids(core_session,
                                                           all_systems)) == keep_account_ids, "Set of expected remaining accounts did not match search"


def test_overlapping_requests_succeed(clean_bulk_delete_systems_and_accounts, core_session, list_of_created_systems):
    batch1 = ResourceManager.add_multiple_systems_with_accounts(core_session, 3, 4, list_of_created_systems)
    batch2 = ResourceManager.add_multiple_systems_with_accounts(core_session, 4, 2, list_of_created_systems)
    batch3 = ResourceManager.add_multiple_systems_with_accounts(core_session, 2, 1, list_of_created_systems)

    all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values([batch1, batch2, batch3])

    ResourceManager.del_multiple_systems(core_session, batch1.keys(), wait_time=-1)
    ResourceManager.del_multiple_systems(core_session, batch1.keys(), wait_time=-1)  # redundancy deliberate
    ResourceManager.del_multiple_systems(core_session, batch2.keys(), wait_time=-1)
    ResourceManager.del_multiple_systems(core_session, batch3.keys())  # wait on final call

    assert len(ResourceManager.get_multi_added_account_ids(core_session,
                                                           all_systems)) == 0, "Expected no remaining added accounts"
    assert len(ResourceManager.get_multi_added_system_ids(core_session,
                                                          all_systems)) == 0, "Expected no remaining added systems"


def test_redundant_requests_succeed(clean_bulk_delete_systems_and_accounts, core_session, list_of_created_systems):
    batch1 = ResourceManager.add_multiple_systems_with_accounts(core_session, 2, 2, list_of_created_systems)
    batch2 = ResourceManager.add_multiple_systems_with_accounts(core_session, 2, 2, list_of_created_systems)

    all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values([batch1, batch2])

    ResourceManager.del_multiple_systems(core_session, batch1.keys())
    ResourceManager.del_multiple_systems(core_session, batch2.keys())
    ResourceManager.del_multiple_systems(core_session, batch1.keys())
    ResourceManager.del_multiple_systems(core_session, batch2.keys())

    assert len(ResourceManager.get_multi_added_account_ids(core_session,
                                                           all_systems)) == 0, "Expected no remaining added accounts"
    assert len(ResourceManager.get_multi_added_system_ids(core_session,
                                                          all_systems)) == 0, "Expected no remaining added systems"


def test_bulk_system_delete_generates_secret_with_garbage_in_list(clean_bulk_delete_systems_and_accounts, core_session,
                                                                  list_of_created_systems, secret_cleaner, core_tenant):
    batch1 = ResourceManager.add_multiple_systems_with_accounts(core_session, 2, 2, list_of_created_systems)
    batch2 = ResourceManager.add_multiple_systems_with_accounts(core_session, 2, 1, list_of_created_systems)

    all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values([batch1, batch2])

    secret_name = "TestSecret-" + str(ResourceManager.time_mark_in_hours()) + "-" + guid()

    clean_delete_system_ids = list(all_systems)
    delete_system_ids = ["foo", "", clean_delete_system_ids[2]] + clean_delete_system_ids + ["!@#$%^&*()", "1", "?",
                                                                                             "Jason Alexander", "bar"]

    ResourceManager.del_multiple_systems(core_session, delete_system_ids, savepasswords=True, secretname=secret_name)

    ResourceManager.wait_for_secret_to_exist_or_timeout(core_session, secret_name)

    secret_id = RedrockController.get_secret_id_by_name(core_session, secret_name)

    assert secret_id is not None, "No secret was created"

    secret_cleaner.append(secret_id)
    user_name = core_tenant['admin_user']
    user_id = UserManager.get_user_id(core_session, user_name)

    result, success = set_users_effective_permissions(core_session, user_name, "View,Edit,Retrieve", user_id, secret_id)
    assert success, f"Did not set secret permission successfully with message {result}"

    secret_file_contents = get_file_secret_contents(core_session, secret_id)

    assert secret_file_contents.count("\n") == 1 + len(
        all_accounts), f"Secret file contained the wrong number of lines {secret_file_contents}"
    assert secret_file_contents.count("bsd_tst_usr_") == len(
        all_accounts), f"Secret file contained the wrong number of accounts {secret_file_contents}"
    assert secret_file_contents.count("thisIsaPAsSwO0rd") == len(
        all_accounts), f"Secret file contained the wrong number of passwords {secret_file_contents}"
    for server_id in all_systems:
        assert server_id in secret_file_contents, f"Server ID absent from secret file {secret_file_contents}"
    for account_id in all_accounts:
        assert account_id in secret_file_contents, f"Account ID absent from secret file {secret_file_contents}"


@pytest.mark.managedssh
def test_bulk_system_delete_generates_secret(clean_bulk_delete_systems_and_accounts, core_session,
                                             list_of_created_systems, secret_cleaner, core_tenant):
    batch1 = ResourceManager.add_multiple_systems_with_accounts(core_session, 1, 4, list_of_created_systems)
    batch2 = ResourceManager.add_multiple_systems_with_accounts(core_session, 2, 3, list_of_created_systems)
    batch3 = ResourceManager.add_multiple_ssh_systems_with_accounts(core_session, 1, 1, list_of_created_systems)

    all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values([batch1, batch2, batch3])
    all_non_ssh_systems, all_non_shh_accounts = DataManipulation.aggregate_lists_in_dict_values([batch1, batch2])

    secret_name = "TestSecret-" + str(ResourceManager.time_mark_in_hours()) + "-" + guid()

    sql_query = RedrockController.get_query_for_ids('Server', all_systems)
    ResourceManager.del_multiple_systems_by_query(core_session, sql_query, True, secret_name)

    ResourceManager.wait_for_secret_to_exist_or_timeout(core_session, secret_name)

    secret_id = RedrockController.get_secret_id_by_name(core_session, secret_name)

    assert secret_id is not None, "No secret was created"

    secret_cleaner.append(secret_id)
    user_name = core_tenant['admin_user']
    user_id = UserManager.get_user_id(core_session, user_name)

    result, success = set_users_effective_permissions(core_session, user_name, "View,Edit,Retrieve", user_id, secret_id)
    assert success, f"Did not set secret permission successfully with message {result}"

    secret_file_contents = get_file_secret_contents(core_session, secret_id)

    assert secret_file_contents.strip().count("\n") == len(
        all_accounts), f"Secret file contained the wrong number of lines {secret_file_contents}"
    assert secret_file_contents.count("thisIsaPAsSwO0rd") == len(
        all_non_shh_accounts), f"Secret file contained the wrong number of passwords {secret_file_contents}"
    # Commenting following assert as AutomationTestKey is not available in secret_file_contents, Tested on both AWS,
    # Azure devdog tenants
    # assert 'AutomationTestKey' in secret_file_contents, f"Name of SSH key did not appear in secret file {secret_file_contents}"
    for server_id in all_non_ssh_systems:
        assert server_id in secret_file_contents, f"Server ID absent from secret file {secret_file_contents}"
    for account_id in all_non_shh_accounts:
        assert account_id in secret_file_contents, f"Account ID absent from secret file {secret_file_contents}"


def test_bulk_system_delete_does_not_generate_secret_when_told_not_to(clean_bulk_delete_systems_and_accounts,
                                                                      core_session, list_of_created_systems):
    batch1 = ResourceManager.add_multiple_systems_with_accounts(core_session, 2, 7, list_of_created_systems)
    batch2 = ResourceManager.add_multiple_systems_with_accounts(core_session, 5, 3, list_of_created_systems)

    all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values([batch1, batch2])

    job_id, success = ResourceManager.del_multiple_systems(core_session, all_systems, False, "")

    assert len(ResourceManager.get_multi_added_account_ids(core_session,
                                                           all_systems)) == 0, "Remaining added systems should be zero"

    report_contents = JobManager.get_job_report(core_session, job_id)

    assert report_contents['report'].find(
        'No password secret created') > -1, f'A secret was created even though it should not have been.'


@pytest.mark.parametrize('simulate_failure', [True, False])
def test_bulk_system_delete_job_fails_due_to_invalid_request_missing_query(clean_bulk_delete_systems_and_accounts,
                                                                           core_session, simulate_failure,
                                                                           list_of_created_systems):
    ResourceManager.add_multiple_systems_with_accounts(core_session, 1, 1, list_of_created_systems)
    if simulate_failure:
        set_query = ""
    else:
        set_query = "@@Favorites"

    request = core_session.apirequest(
        EndPoints.ACCOUNT_MULTI_SYS_DELETE,
        Util.scrub_dict({
            'SetQuery': set_query,
            'SaveToSecrets': False,
            'SecretName': ""
        })
    )

    request_json = request.json()
    result, success = request_json['Result'], request_json['success']
    assert not simulate_failure == success, f"Query success was unexpected value, with message {result}"


@pytest.mark.parametrize('simulate_failure', [True, False])
def test_bulk_system_delete_job_fails_due_to_invalid_request_missing_secret_name(clean_bulk_delete_systems_and_accounts,
                                                                                 core_session, simulate_failure,
                                                                                 list_of_created_systems):
    ResourceManager.add_multiple_systems_with_accounts(core_session, 1, 1, list_of_created_systems)

    if simulate_failure:
        request = core_session.apirequest(EndPoints.ACCOUNT_MULTI_SYS_DELETE, Util.scrub_dict(
            {'SetQuery': "@@Favorites", 'SaveToSecrets': True, 'SecretName': ""}))
    else:
        request = core_session.apirequest(EndPoints.ACCOUNT_MULTI_SYS_DELETE, Util.scrub_dict(
            {'SetQuery': "@@Favorites", 'SaveToSecrets': True, 'SecretName': "somekey"}))

    request_json = request.json()
    result, success = request_json['Result'], request_json['success']
    assert not simulate_failure == success, f"Query success was unexpected value, with message {result}"


@pytest.mark.parametrize('simulate_failure', [True, False])
def test_bulk_system_delete_job_fails_due_to_invalid_request_no_query_or_ids(clean_bulk_delete_systems_and_accounts,
                                                                             core_session, simulate_failure,
                                                                             list_of_created_systems):
    ResourceManager.add_multiple_systems_with_accounts(core_session, 1, 1, list_of_created_systems)

    if simulate_failure:
        request = core_session.apirequest(EndPoints.ACCOUNT_MULTI_SYS_DELETE,
                                          Util.scrub_dict({'SaveToSecrets': False, 'SecretName': ""}))
    else:
        request = core_session.apirequest(EndPoints.ACCOUNT_MULTI_SYS_DELETE, Util.scrub_dict(
            {'SetQuery': "@@Favorites", 'SaveToSecrets': False, 'SecretName': ""}))

    request_json = request.json()
    result, success = request_json['Result'], request_json['success']
    assert not simulate_failure == success, f"Query success was unexpected value, with message {result}"


@pytest.mark.parametrize('simulate_failure', [True, False])
def test_bulk_system_delete_job_fails_due_to_invalid_request_no_query_or_ids_fast_track(
        clean_bulk_delete_systems_and_accounts, core_session, simulate_failure, list_of_created_systems):
    batch = ResourceManager.add_multiple_systems_with_accounts(core_session, 1, 1, list_of_created_systems)
    delete_system_ids, unused_account_ids = DataManipulation.aggregate_lists_in_dict_values([batch])

    if simulate_failure:
        request = core_session.apirequest(EndPoints.ACCOUNT_MULTI_SYS_DELETE,
                                          Util.scrub_dict({'SaveToSecrets': False, 'SecretName': "", 'RunSync': True}))
    else:
        sql_query = RedrockController.get_query_for_ids('Server', delete_system_ids)
        request = core_session.apirequest(EndPoints.ACCOUNT_MULTI_SYS_DELETE, Util.scrub_dict(
            {'SetQuery': sql_query, 'SaveToSecrets': False, 'SecretName': "", 'RunSync': True}))

    request_json = request.json()
    result, success = request_json['Result'], request_json['success']
    assert not simulate_failure == success, f"Query success was unexpected value, with message {result}"


@pytest.mark.parametrize('simulate_failure', [True, False])
def test_bulk_system_delete_job_fails_due_to_invalid_request_empty_id_list(clean_bulk_delete_systems_and_accounts,
                                                                           core_session, simulate_failure,
                                                                           list_of_created_systems):
    batch = ResourceManager.add_multiple_systems_with_accounts(core_session, 1, 1, list_of_created_systems)

    if simulate_failure:
        request = core_session.apirequest(EndPoints.ACCOUNT_MULTI_SYS_DELETE,
                                          Util.scrub_dict({'Ids': [], 'SaveToSecrets': False, 'SecretName': ""}))
    else:
        request = core_session.apirequest(EndPoints.ACCOUNT_MULTI_SYS_DELETE, Util.scrub_dict(
            {'Ids': list(batch.keys()), 'SaveToSecrets': False, 'SecretName': ""}))

    request_json = request.json()
    result, success = request_json['Result'], request_json['success']
    assert not simulate_failure == success, f"Query success was unexpected value, with message {result}"


@pytest.mark.parametrize('simulate_failure', [True, False])
def test_bulk_system_delete_job_fails_due_to_invalid_request_query_and_id_list(clean_bulk_delete_systems_and_accounts,
                                                                               core_session, simulate_failure,
                                                                               list_of_created_systems):
    batch = ResourceManager.add_multiple_systems_with_accounts(core_session, 1, 1, list_of_created_systems)

    if simulate_failure:
        request = core_session.apirequest(EndPoints.ACCOUNT_MULTI_SYS_DELETE, Util.scrub_dict(
            {'SetQuery': "@@Favorites", 'Ids': list(batch.keys()), 'SaveToSecrets': False, 'SecretName': ""}))
    else:
        request = core_session.apirequest(EndPoints.ACCOUNT_MULTI_SYS_DELETE, Util.scrub_dict(
            {'Ids': list(batch.keys()), 'SaveToSecrets': False, 'SecretName': ""}))

    request_json = request.json()
    result, success = request_json['Result'], request_json['success']
    assert not simulate_failure == success, f"Query success was unexpected value, with message {result}"


@pytest.mark.parametrize('simulate_failure', [True, False])
def test_bulk_system_delete_job_fails_due_to_request_query_returning_zero_rows_fast_track(
        clean_bulk_delete_systems_and_accounts, core_session, simulate_failure, list_of_created_systems):
    batch = ResourceManager.add_multiple_systems_with_accounts(core_session, 1, 1, list_of_created_systems)
    delete_system_ids, unused_account_ids = DataManipulation.aggregate_lists_in_dict_values([batch])

    if simulate_failure:
        invalid_query = f"select * from Server where ID = '{guid()}'"
        request = core_session.apirequest(EndPoints.ACCOUNT_MULTI_SYS_DELETE, Util.scrub_dict(
            {'SetQuery': invalid_query, 'Ids': list(batch.keys()), 'SaveToSecrets': False, 'SecretName': "",
             'RunSync': True}))
    else:
        valid_query = RedrockController.get_query_for_ids('Server', delete_system_ids)
        request = core_session.apirequest(EndPoints.ACCOUNT_MULTI_SYS_DELETE, Util.scrub_dict(
            {'SetQuery': valid_query, 'SaveToSecrets': False, 'SecretName': "", 'RunSync': True}))

    request_json = request.json()
    result, success = request_json['Result'], request_json['success']
    assert not simulate_failure == success, f"Query success was unexpected value, with message {result}"


@pytest.mark.parametrize('simulate_failure', [True, False])
def test_bulk_system_delete_job_fails_due_to_invalid_request_query_string_fast_track(
        clean_bulk_delete_systems_and_accounts, core_session, simulate_failure, list_of_created_systems):
    batch = ResourceManager.add_multiple_systems_with_accounts(core_session, 1, 1, list_of_created_systems)
    delete_system_ids, unused_account_ids = DataManipulation.aggregate_lists_in_dict_values([batch])

    if simulate_failure:
        invalid_query = f"invalid query string"  # invalid sql query... should fail
        request = core_session.apirequest(EndPoints.ACCOUNT_MULTI_SYS_DELETE, Util.scrub_dict(
            {'SetQuery': invalid_query, 'Ids': list(batch.keys()), 'SaveToSecrets': False, 'SecretName': "",
             'RunSync': True}))
    else:
        valid_query = RedrockController.get_query_for_ids('Server', delete_system_ids)
        request = core_session.apirequest(EndPoints.ACCOUNT_MULTI_SYS_DELETE, Util.scrub_dict(
            {'SetQuery': valid_query, 'SaveToSecrets': False, 'SecretName': "", 'RunSync': True}))

    request_json = request.json()
    result, success = request_json['Result'], request_json['success']
    assert not simulate_failure == success, f"Query success was unexpected value, with message {result}"


@pytest.mark.parametrize('simulate_failure', [True, False])
def test_bulk_system_delete_job_fails_due_to_invalid_request_missing_all_fields(clean_bulk_delete_systems_and_accounts,
                                                                                core_session, simulate_failure,
                                                                                list_of_created_systems):
    ResourceManager.add_multiple_systems_with_accounts(core_session, 1, 1, list_of_created_systems)

    if simulate_failure:
        request = core_session.apirequest(EndPoints.ACCOUNT_MULTI_SYS_DELETE, Util.scrub_dict({}))
    else:
        request = core_session.apirequest(EndPoints.ACCOUNT_MULTI_SYS_DELETE, Util.scrub_dict(
            {'SetQuery': "@@Favorites", 'SaveToSecrets': False, 'SecretName': ""}))

    request_json = request.json()
    result, success = request_json['Result'], request_json['success']
    assert not simulate_failure == success, f"Query success was unexpected value, with message {result}"


@pytest.mark.parametrize('simulate_failure', [True, False])
def test_bulk_system_delete_job_fails_due_to_invalid_request_missing_tag(clean_bulk_delete_systems_and_accounts,
                                                                         core_session, simulate_failure,
                                                                         list_of_created_systems):
    ResourceManager.add_multiple_systems_with_accounts(core_session, 1, 1, list_of_created_systems)

    if not simulate_failure:
        request = core_session.apirequest(EndPoints.ACCOUNT_MULTI_SYS_DELETE, Util.scrub_dict(
            {'SetQuery': "@@Favorites", 'SaveToSecrets': True, 'SecretName': "MySecretName"}))
    else:
        request = core_session.apirequest(EndPoints.ACCOUNT_MULTI_SYS_DELETE,
                                          Util.scrub_dict({'SetQuery': "@@Favorites", 'SaveToSecrets': True}))

    request_json = request.json()
    result, success = request_json['Result'], request_json['success']
    assert (not simulate_failure) == success, f"API success response not expected value, returned result {result}"


def test_app_management_user_can_create_job_but_not_delete_servers(clean_bulk_delete_systems_and_accounts, core_session,
                                                                   core_tenant, clean_users, users_and_roles,
                                                                   list_of_created_systems):
    batch = ResourceManager.add_multiple_systems_with_accounts(core_session, 3, 2, list_of_created_systems)
    all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values([batch])

    requestor_session = users_and_roles.get_session_for_user('Application Management')

    user_info = requestor_session.get_current_session_user_info().json()['Result']

    all_systems = batch.keys()

    job_id, result = ResourceManager.del_multiple_systems(requestor_session, all_systems)

    result = ResourceManager.get_job_state(core_session, job_id)

    assert result == "Succeeded", "Job did not execute"

    assert len(
        ResourceManager.get_multi_added_system_ids(core_session, all_systems)) == 3, "Wrong number of remaining systems"
    assert len(ResourceManager.get_multi_added_account_ids(core_session,
                                                           all_systems)) == 6, "Wrong number of remaining accounts"

    username = user_info['Name']
    start_type = 'Cloud.Core.AsyncOperation.BulkSystemDelete.Start.Multi'
    end_type = 'Cloud.Core.AsyncOperation.BulkSystemDelete.Failure.Multi'
    start_message = f'{username} initiated delete of {len(all_systems)} systems'
    end_message = f'{username} failed to delete {len(all_systems)} of {len(all_systems)} systems'

    RedrockController.expect_event_message_by_type(core_session, start_type, start_message)
    RedrockController.expect_event_message_by_type(core_session, end_type, end_message)


def test_bulk_system_delete_works_with_built_in_set(clean_bulk_delete_systems_and_accounts, core_session, core_tenant,
                                                    clean_users, users_and_roles, list_of_created_systems,
                                                    get_environment):
    Engines = get_environment
    if Engines == "AWS - PLV8":
        batch = ResourceManager.add_multiple_systems_with_accounts(core_session, 3, 3, list_of_created_systems)

        all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values([batch])

        right_data = ("Privileged Access Service Power User", "role_Privileged Access Service Power User")

        requester_session = users_and_roles.get_session_for_user(right_data[0])
        role_info = users_and_roles.get_role(right_data[0])

        account_ids = ResourceManager.get_multi_added_account_ids(core_session, all_systems)

        for account_id in account_ids:
            permission_string = 'Owner,View,Manage,Delete,Login,Naked,UpdatePassword,FileTransfer,UserPortalLogin'
            result, success = ResourceManager.assign_account_permissions(
                core_session,
                permission_string,
                role_info['Name'], role_info['ID'], "Role",
                account_id)
            assert success, "Did not set account permissions " + str(result)

        system_ids = list(ResourceManager.get_multi_added_system_ids(core_session, all_systems).values())

        for system_id in system_ids:
            permission_string = 'Grant,View,Edit,Delete,ManageSession,AgentAuth,RequestZoneRole,AddAccount,' \
                                'UnlockAccount '
            result, success = ResourceManager.assign_system_permissions(core_session,
                                                                        permission_string,
                                                                        role_info['Name'], role_info['ID'], "Role",
                                                                        system_id)
            assert success, "Did not set system permissions " + result

        job_id, result = ResourceManager.del_multiple_systems_by_query(requester_session, '@@Windows Servers')
        report = JobManager.get_job_report(core_session, job_id)

        # not asserting success or failure, the admin may have access to windows systems created by other tests which
        # would not succeed such as windows systems with uncertain accounts

        assert len(ResourceManager.get_multi_added_account_ids(core_session,
                                                               all_systems)) == 0, f"Expected no remaining added accounts {report}"
        assert len(ResourceManager.get_multi_added_system_ids(core_session,
                                                              all_systems)) == 0, f"Expected no remaining added systems  {report}"
    else:
        skip('todo: Fix this test to work on azure')


@pytest.mark.parametrize('explicit_missing_delete_permission', [True, False])
def test_missing_permissions_on_bsd_accounts_and_systems(core_session, users_and_roles, created_system_id_list,
                                                         explicit_missing_delete_permission):
    """

    Make three systems, with accounts
    System 0 - Delete permissions on every account and on system
    System 1 - Delete permissions on HALF its accounts and on system
    System 2 - Delete permissions on every of its accounts, but not on system

    Then Bulk System Delete. All accounts with delete permissions will be gone. Systems 0 and 1 will remain.

    :param explicit_missing_delete_permission: If True, the permission string will be set without Delete. If False, the permissions will not be modified (with Delete missing assumed)
    :param core_session: Authenticated Centrify Session.
    :param users_and_roles: Fixture to create New user with PAS Power Rights
    :param created_system_id_list: A list for holding created systems, that will be deleted after the test
    :return:
    """
    original_systems = 3
    original_accounts_per_system = 4

    batch = ResourceManager.add_multiple_systems_with_accounts(core_session, original_systems,
                                                               original_accounts_per_system, created_system_id_list)

    # These two variables will have extra set items added below from System 1
    deleted_accounts, expected_preserved_accounts = set(batch[created_system_id_list[0]]).union(
        set(batch[created_system_id_list[2]])), set()

    split1, split2 = DataManipulation.shuffle_and_split_into_two_lists(batch[created_system_id_list[1]])
    deleted_accounts = deleted_accounts.union(set(split1))
    expected_preserved_accounts = expected_preserved_accounts.union(set(split2))

    # System 1 fails to delete because some of its child accounts are not deleted
    # System 2 fails for missing delete permission
    expected_preserved_systems = {created_system_id_list[1], created_system_id_list[2]}
    delete_system_permissions = {created_system_id_list[0], created_system_id_list[1]}

    requester_session = users_and_roles.get_session_for_user("Privileged Access Service Power User")
    results_role = users_and_roles.get_role("Privileged Access Service Power User")

    for account_id in deleted_accounts:
        permission_string = 'Owner,View,Manage,Delete,Login,Naked,UpdatePassword,FileTransfer,UserPortalLogin'
        result, success = ResourceManager.assign_account_permissions(core_session, permission_string,
                                                                     results_role['Name'], results_role['ID'], "Role",
                                                                     account_id)
        assert success, "Did not set account permissions " + str(result)

    if explicit_missing_delete_permission:
        for account_id in expected_preserved_accounts:
            permission_string = 'Owner,View,Manage,Login,Naked,UpdatePassword,FileTransfer,UserPortalLogin'
            result, success = ResourceManager.assign_account_permissions(core_session, permission_string,
                                                                         results_role['Name'], results_role['ID'],
                                                                         "Role", account_id)
            assert success, "Did not set account permissions " + str(result)

    for system_id in created_system_id_list:
        if system_id in delete_system_permissions:
            permission_string = 'Grant,View,Edit,Delete,ManageSession,AgentAuth,RequestZoneRole,AddAccount,UnlockAccount'
        else:
            if not explicit_missing_delete_permission:
                continue
            permission_string = 'Grant,View,Edit,ManageSession,AgentAuth,RequestZoneRole,AddAccount,UnlockAccount'
        result, success = ResourceManager.assign_system_permissions(core_session, permission_string,
                                                                    results_role['Name'], results_role['ID'], "Role",
                                                                    system_id)
        assert success, "Did not set system permissions " + result

    job_id, result = ResourceManager.del_multiple_systems(requester_session, batch.keys())

    result = ResourceManager.get_job_state(core_session, job_id)
    assert result == "Succeeded", "Job did not execute"

    remaining_accounts = set(ResourceManager.get_multi_added_account_ids(core_session, created_system_id_list))
    remaining_systems = set(ResourceManager.get_multi_added_system_ids(core_session, created_system_id_list).values())

    assert remaining_accounts == expected_preserved_accounts, "Remaining accounts did not match expectation"
    assert remaining_systems == expected_preserved_systems, "Remaining systems did not match expectation"


@pytest.mark.parametrize('swap_roles', [True, False])
def test_other_user_cant_see_secret_created_by_first_user(core_session, users_and_roles, created_system_id_list,
                                                          swap_roles):
    roles = ["Privileged Access Service Administrator", "Privileged Access Service Power User"]

    if swap_roles:
        roles_new = [roles[1], roles[0]]
        roles = roles_new

    batch = ResourceManager.add_multiple_systems_with_accounts(core_session, 2, 2, created_system_id_list)
    all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values([batch])

    deleter_user_0_session = users_and_roles.get_session_for_user(roles[0])
    deleter_user_0_role = users_and_roles.get_role(roles[0])
    deleter_user_0_role_name = deleter_user_0_role['Name']
    deleter_user_0_role_id = deleter_user_0_role['ID']
    other_user_1_session = users_and_roles.get_session_for_user(roles[1])

    for account_id in all_accounts:
        permission_string = 'Owner,View,Manage,Delete,Login,Naked,UpdatePassword,FileTransfer,UserPortalLogin'
        result, success = ResourceManager.assign_account_permissions(core_session, permission_string,
                                                                     deleter_user_0_role_name, deleter_user_0_role_id,
                                                                     "Role", account_id)
        assert success, "Did not set account permissions " + str(result)

    for system_id in all_systems:
        permission_string = 'Grant,View,Edit,Delete,ManageSession,AgentAuth,RequestZoneRole,AddAccount,UnlockAccount'
        result, success = ResourceManager.assign_system_permissions(core_session, permission_string,
                                                                    deleter_user_0_role_name, deleter_user_0_role_id,
                                                                    "Role", system_id)
        assert success, "Did not set system permissions " + result

    secret_name = f"secret{guid()}"
    job_id, result = ResourceManager.del_multiple_systems(deleter_user_0_session, batch.keys(), secretname=secret_name)

    result = ResourceManager.get_job_state(core_session, job_id)
    assert result == "Succeeded", "Job did not execute"

    remaining_accounts = set(ResourceManager.get_multi_added_account_ids(core_session, created_system_id_list))
    remaining_systems = set(ResourceManager.get_multi_added_system_ids(core_session, created_system_id_list).values())

    assert remaining_accounts == set(), "Remaining accounts did not match expectation"
    assert remaining_systems == set(), "Remaining systems did not match expectation"

    secret_id = RedrockController.get_secret_id_by_name(deleter_user_0_session, secret_name)
    assert secret_id is not None, f"Secret was not visible to creator '{roles[0]}' user, either because it wasn't created or because of a permissions issue"

    secret_id = RedrockController.get_secret_id_by_name(other_user_1_session, secret_name)
    assert secret_id is None, f"Secret should not be '{roles[1]}' user when created by '{roles[0]}' user"

    secret_id = RedrockController.get_secret_id_by_name(core_session, secret_name)
    assert secret_id is not None, f"Sys admin should be able to see secret created by {roles[0]}"


def test_power_user_cant_see_secret_created_by_sysadmin_bsd(core_session, users_and_roles, created_system_id_list):
    batch = ResourceManager.add_multiple_systems_with_accounts(core_session, 2, 2, created_system_id_list)

    secret_name = f"secret{guid()}"
    job_id, result = ResourceManager.del_multiple_systems(core_session, batch.keys(), secretname=secret_name)

    result = ResourceManager.get_job_state(core_session, job_id)
    assert result == "Succeeded", "Job did not execute"

    remaining_accounts = set(ResourceManager.get_multi_added_account_ids(core_session, created_system_id_list))
    remaining_systems = set(ResourceManager.get_multi_added_system_ids(core_session, created_system_id_list).values())

    assert remaining_accounts == set(), "Remaining accounts did not match expectation"
    assert remaining_systems == set(), "Remaining systems did not match expectation"

    requester_session = users_and_roles.get_session_for_user("Privileged Access Service Power User")

    secret_id = RedrockController.get_secret_id_by_name(core_session, secret_name)
    assert secret_id is not None, "No secret was created"

    secret_id = RedrockController.get_secret_id_by_name(requester_session, secret_name)
    assert secret_id is None, "Secret should not be visible to Privileged Access Service Power User"
