import time
import pytest
from Shared.API.infrastructure import ResourceManager
from Shared.API.redrock import RedrockController
from Shared.API.secret import set_users_effective_permissions, get_file_secret_contents, get_folder
from Shared.API.sets import SetsManager
from Shared.API.users import UserManager
from Shared.data_manipulation import DataManipulation
from Shared.util import Util
from Shared.endpoint_manager import EndPoints
import random
from Utils.guid import guid

pytestmark = [pytest.mark.api, pytest.mark.cps, pytest.mark.bulk_account_delete, pytest.mark.pas]


def test_bulk_account_delete_by_ids_only_deletes_correct_accounts(clean_bulk_delete_systems_and_accounts, core_session,
                                                                  list_of_created_systems):
    batch1 = ResourceManager.add_multiple_systems_with_accounts(core_session, 3, 4, list_of_created_systems)
    batch2 = ResourceManager.add_multiple_systems_with_accounts(core_session, 1, 2, list_of_created_systems)
    batch3 = ResourceManager.add_multiple_systems_with_accounts(core_session, 4, 6, list_of_created_systems)
    batch4 = ResourceManager.add_multiple_systems_with_accounts(core_session, 2, 8, list_of_created_systems)
    batch5 = ResourceManager.add_multiple_systems_with_accounts(core_session, 5, 2, list_of_created_systems)

    all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values(
        [batch1, batch2, batch3, batch4, batch5])
    delete_ids, keep_ids = DataManipulation.shuffle_and_split_into_two_lists(all_accounts)

    result, success = ResourceManager.del_multiple_accounts(core_session, delete_ids)
    assert success, "Api did not complete successfully for bulk account delete MSG: " + result

    assert set(ResourceManager.get_multi_added_system_ids(core_session, all_systems).values()) == set(
        all_systems), "Wrong set of added systems found"
    assert set(ResourceManager.get_multi_added_account_ids(core_session, all_systems)) == set(
        keep_ids), "Wrong set of added accounts found"

    user_info = core_session.get_current_session_user_info().json()['Result']
    username = user_info['Name']
    start_type = 'Cloud.Core.AsyncOperation.BulkAccountDelete.Start.Multi'
    end_type = 'Cloud.Core.AsyncOperation.BulkAccountDelete.Success.Multi'
    start_message = f'{username} initiated delete of {len(delete_ids)} accounts'
    end_message = f'{username} successfully deleted {len(delete_ids)} accounts'

    RedrockController.expect_event_message_by_type(core_session, start_type, start_message)
    RedrockController.expect_event_message_by_type(core_session, end_type, end_message)


def test_bulk_account_delete_by_ids_only_deletes_correct_accounts_fast_track(clean_bulk_delete_systems_and_accounts,
                                                                             core_session, list_of_created_systems):
    batch1 = ResourceManager.add_multiple_systems_with_accounts(core_session, 3, 4, list_of_created_systems)
    batch2 = ResourceManager.add_multiple_systems_with_accounts(core_session, 1, 2, list_of_created_systems)
    batch3 = ResourceManager.add_multiple_systems_with_accounts(core_session, 4, 6, list_of_created_systems)
    batch4 = ResourceManager.add_multiple_systems_with_accounts(core_session, 2, 8, list_of_created_systems)
    batch5 = ResourceManager.add_multiple_systems_with_accounts(core_session, 5, 2, list_of_created_systems)

    all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values([batch1, batch2, batch3,
                                                                                 batch4, batch5])
    delete_ids, keep_ids = DataManipulation.shuffle_and_split_into_two_lists(all_accounts)

    result, success = ResourceManager.del_multiple_accounts(core_session, delete_ids, run_sync=True)
    assert success, f"Api did not complete successfully for bulk account delete MSG: {result}."

    assert set(ResourceManager.get_multi_added_system_ids(core_session, all_systems).values()) == set(all_systems), \
        "Wrong set of added systems found"
    assert set(ResourceManager.get_multi_added_account_ids(core_session, all_systems)) == set(keep_ids), \
        "Wrong set of added accounts found"

    user_info = core_session.get_current_session_user_info().json()['Result']
    username = user_info['Name']
    start_type = 'Cloud.Core.AsyncOperation.BulkAccountDelete.Start.Multi'
    end_type = 'Cloud.Core.AsyncOperation.BulkAccountDelete.Success.Multi'
    start_message = f'{username} initiated delete of {len(delete_ids)} accounts'
    end_message = f'{username} successfully deleted {len(delete_ids)} accounts'

    RedrockController.expect_event_message_by_type(core_session, start_type, start_message)
    RedrockController.expect_event_message_by_type(core_session, end_type, end_message)


def test_bulk_account_delete_by_sql_query_only_deletes_correct_accounts(clean_bulk_delete_systems_and_accounts,
                                                                        core_session, list_of_created_systems):
    batch = ResourceManager.add_multiple_systems_with_accounts(core_session, 2, 12, list_of_created_systems)

    all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values([batch])
    delete_ids, keep_ids = DataManipulation.shuffle_and_split_into_two_lists(all_accounts)

    sql_query = 'SELECT * FROM VaultAccount WHERE ' + ' OR '.join(
        ('VaultAccount.ID = "' + str(n) + '"' for n in list(delete_ids)))

    result, success = ResourceManager.del_multiple_accounts_by_query(core_session, sql_query)
    assert success, "del_multiple_accounts_by_query failed " + result

    assert set(ResourceManager.get_multi_added_system_ids(core_session, all_systems).values()) == set(
        all_systems), "Wrong set of added systems found"
    assert set(ResourceManager.get_multi_added_account_ids(core_session, all_systems)) == set(
        keep_ids), "Wrong set of added accounts found"

    user_info = core_session.get_current_session_user_info().json()['Result']
    username = user_info['Name']
    start_type = 'Cloud.Core.AsyncOperation.BulkAccountDelete.StartQuery.Multi'
    end_type = 'Cloud.Core.AsyncOperation.BulkAccountDelete.Success.Multi'
    start_message = f'{username} initiated delete of multiple accounts'
    end_message = f'{username} successfully deleted {len(delete_ids)} accounts'

    RedrockController.expect_event_message_by_type(core_session, start_type, start_message)
    RedrockController.expect_event_message_by_type(core_session, end_type, end_message)


@pytest.mark.pas_failed
def test_bulk_account_delete_by_sql_query_only_deletes_correct_accounts_fast_track(
        clean_bulk_delete_systems_and_accounts, core_session, list_of_created_systems):
    batch = ResourceManager.add_multiple_systems_with_accounts(core_session, 2, 12, list_of_created_systems)

    all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values([batch])
    delete_ids, keep_ids = DataManipulation.shuffle_and_split_into_two_lists(all_accounts)

    sql_query = 'SELECT * FROM VaultAccount WHERE ' + ' OR '.join(('VaultAccount.ID = "' + str(n) + '"'
                                                                   for n in list(delete_ids)))

    result, success = ResourceManager.del_multiple_accounts_by_query(core_session, sql_query, run_sync=True)
    assert success, "del_multiple_accounts_by_query failed " + result

    assert set(ResourceManager.get_multi_added_system_ids(core_session, all_systems).values()) == set(all_systems), \
        "Wrong set of added systems found"
    assert set(ResourceManager.get_multi_added_account_ids(core_session, all_systems)) == set(keep_ids), \
        "Wrong set of added accounts found"

    user_info = core_session.get_current_session_user_info().json()['Result']
    username = user_info['Name']
    start_type = 'Cloud.Core.AsyncOperation.BulkAccountDelete.StartQuery.Multi'
    end_type = 'Cloud.Core.AsyncOperation.BulkAccountDelete.Success.Multi'
    start_message = f'{username} initiated delete of multiple accounts'
    end_message = f'{username} successfully deleted {len(delete_ids)} accounts'

    RedrockController.expect_event_message_by_type(core_session, start_type, start_message)
    RedrockController.expect_event_message_by_type(core_session, end_type, end_message)


def test_bulk_account_delete_performs_quickly(clean_bulk_delete_systems_and_accounts, core_session,
                                              list_of_created_systems):
    # test constants
    large_number_for_stress_testing = 50  # tested once with higher numbers but reduced for quick execution
    reasonable_amount_of_time_to_execute = 90

    batch1 = ResourceManager.add_multiple_systems_with_accounts(core_session, 1, large_number_for_stress_testing // 2,
                                                                list_of_created_systems)
    batch2 = ResourceManager.add_multiple_systems_with_accounts(core_session, 1, large_number_for_stress_testing // 2,
                                                                list_of_created_systems)
    all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values([batch1, batch2])
    start_time = time.time()
    result, success = ResourceManager.del_multiple_accounts(core_session, all_accounts)
    assert success, "Api did not complete successfully for bulk account delete " + result
    end_time = time.time()
    elapsed_time = end_time - start_time

    assert elapsed_time <= reasonable_amount_of_time_to_execute, \
        "Did not complete operation in a reasonable amount of time"
    assert len(
        ResourceManager.get_multi_added_account_ids(core_session, all_systems)) == 0, "Expected 0 added accounts found"
    assert len(
        ResourceManager.get_multi_added_system_ids(core_session, all_systems)) == 2, "Expected 2 added systems found"


def test_overlapping_redundant_requests_succeed(clean_bulk_delete_systems_and_accounts, core_session,
                                                list_of_created_systems):
    batch1 = ResourceManager.add_multiple_systems_with_accounts(core_session, 1, 16, list_of_created_systems)
    batch2 = ResourceManager.add_multiple_systems_with_accounts(core_session, 1, 15, list_of_created_systems)

    all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values([batch1, batch2])
    all_accounts_list = list(all_accounts)
    random.shuffle(all_accounts_list)

    delete_ids1, keep_ids1 = DataManipulation.shuffle_and_split_into_two_lists(
        all_accounts_list[1::])  # by excluding the first, we ensure one account is guaranteed to remain
    delete_ids2, _ = DataManipulation.shuffle_and_split_into_two_lists(all_accounts_list[1::])
    delete_ids3, _ = DataManipulation.shuffle_and_split_into_two_lists(all_accounts_list[1::])

    ResourceManager.del_multiple_accounts(core_session, delete_ids1, wait_time=-60)
    ResourceManager.del_multiple_accounts(core_session, delete_ids2, wait_time=-60)
    ResourceManager.del_multiple_accounts(core_session, delete_ids3)  # wait on final call

    all_delete = set(delete_ids1).union(delete_ids2).union(delete_ids3)

    assert len(ResourceManager.get_multi_added_account_ids(core_session, all_systems)) == len(all_accounts) - len(
        all_delete), "Wrong number of remaining added accounts found"
    assert len(ResourceManager.get_multi_added_system_ids(core_session, all_systems)) == 2, \
        "Wrong number of remaining added systems found"


def test_bulk_account_delete_generates_secret_with_garbage_in_list(clean_bulk_delete_systems_and_accounts, core_session,
                                                                   list_of_created_systems, secret_cleaner,
                                                                   core_tenant):
    batch1 = ResourceManager.add_multiple_systems_with_accounts(core_session, 1, 4, list_of_created_systems)
    batch2 = ResourceManager.add_multiple_systems_with_accounts(core_session, 2, 3, list_of_created_systems)

    all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values([batch1, batch2])

    secret_name = "TestSecret-" + str(ResourceManager.time_mark_in_hours()) + "-" + guid()

    extra_stuff_in_list = ["foo", "", "Rock Lee", list(all_systems)[0], list(all_accounts)[0], "!!!!!"] + list(
        all_accounts)

    result, success = ResourceManager.del_multiple_accounts(core_session, extra_stuff_in_list, save_passwords=True,
                                                            secret_name=secret_name)
    assert success, "Api did not complete successfully for bulk account delete MSG: " + result

    ResourceManager.wait_for_secret_to_exist_or_timeout(core_session, secret_name)

    secret_id = RedrockController.get_secret_id_by_name(core_session, secret_name)
    assert secret_id is not None, "Secret not found"
    secret_cleaner.append(secret_id)
    assert len(ResourceManager.get_multi_added_account_ids(core_session,
                                                           all_systems)) == 0, "Expected zero added accounts remain"

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
def test_bulk_account_delete_generates_secret_with_ssh_accounts(clean_bulk_delete_systems_and_accounts, core_session,
                                                                list_of_created_systems, secret_cleaner, core_tenant):
    batch1 = ResourceManager.add_multiple_ssh_systems_with_accounts(core_session, 2, 2, list_of_created_systems,
                                                                    system_prefix=f'test_ssh',
                                                                    user_prefix=f'test_usr_ssh')
    all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values([batch1])

    secret_name = "TestSecret-" + str(ResourceManager.time_mark_in_hours()) + "-" + guid()

    result, success = ResourceManager.del_multiple_accounts(core_session, all_accounts, save_passwords=True,
                                                            secret_name=secret_name)
    assert success, "Api did not complete successfully for bulk account delete MSG: " + result

    ResourceManager.wait_for_secret_to_exist_or_timeout(core_session, secret_name)

    secret_id = RedrockController.get_secret_id_by_name(core_session, secret_name)
    assert secret_id is not None, "Secret not found"
    secret_cleaner.append(secret_id)
    assert len(ResourceManager.get_multi_added_account_ids(core_session,
                                                           all_systems)) == 0, "Expected zero added accounts remain"

    user_name = core_tenant['admin_user']
    user_id = UserManager.get_user_id(core_session, user_name)
    result, success = set_users_effective_permissions(core_session, user_name, "View,Edit,Retrieve", user_id, secret_id)
    assert success, f"Did not set secret permission successfully with message {result}"

    secret_file_contents = get_file_secret_contents(core_session, secret_id)

    assert secret_file_contents.count("\n") == 1 + len(
        all_accounts), f"Secret file contained the wrong number of lines {secret_file_contents}"
    assert secret_file_contents.count("AutomationTestKey") == len(
        all_accounts), f"Secret file contained the wrong number of keys {secret_file_contents}"
    for server_id in all_systems:
        assert server_id in secret_file_contents, f"Server ID absent from secret file {secret_file_contents}"
    for account_id in all_accounts:
        assert account_id in secret_file_contents, f"Account ID absent from secret file {secret_file_contents}"


def test_bulk_account_delete_generates_secret(clean_bulk_delete_systems_and_accounts, core_session,
                                              list_of_created_systems, secret_cleaner):
    batch1 = ResourceManager.add_multiple_systems_with_accounts(core_session, 1, 4, list_of_created_systems)
    batch2 = ResourceManager.add_multiple_systems_with_accounts(core_session, 2, 3, list_of_created_systems)

    all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values([batch1, batch2])

    secret_name = "TestSecret-" + str(ResourceManager.time_mark_in_hours()) + "-" + guid()

    sql_query = 'SELECT * FROM VaultAccount WHERE ' + ' OR '.join(
        ('VaultAccount.ID = "' + str(n) + '"' for n in list(all_accounts)))
    ResourceManager.del_multiple_accounts_by_query(core_session, sql_query, True, secret_name)

    ResourceManager.wait_for_secret_to_exist_or_timeout(core_session, secret_name)

    secret_id = RedrockController.get_secret_id_by_name(core_session, secret_name)
    assert secret_id is not None, "Secret not found"
    secret_cleaner.append(secret_id)
    assert len(ResourceManager.get_multi_added_account_ids(core_session,
                                                           all_systems)) == 0, "Expected zero added accounts remain"


def test_bulk_account_delete_does_not_generate_secret_when_told_not_to(clean_bulk_delete_systems_and_accounts,
                                                                       core_session, list_of_created_systems):
    batch1 = ResourceManager.add_multiple_systems_with_accounts(core_session, 1, 4, list_of_created_systems)
    batch2 = ResourceManager.add_multiple_systems_with_accounts(core_session, 2, 3, list_of_created_systems)

    all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values([batch1, batch2])

    secret_name = "TestSecret-" + str(ResourceManager.time_mark_in_hours()) + "-" + guid()

    sql_query = 'SELECT * FROM VaultAccount WHERE ' + ' OR '.join(
        ('VaultAccount.ID = "' + str(n) + '"' for n in list(all_accounts)))
    ResourceManager.del_multiple_accounts_by_query(core_session, sql_query, False, secret_name)

    ResourceManager.wait_for_secret_to_exist_or_timeout(core_session, secret_name, intervals_to_wait=60)
    # set low intervals to wait, since secret should not be generated

    secret_id = RedrockController.get_secret_id_by_name(core_session, secret_name)
    assert secret_id is None, "Secret not found!"

    assert len(ResourceManager.get_multi_added_account_ids(core_session, all_systems)) == 0, \
        "Expected zero remaining added accounts remain"


def test_bulk_account_delete_single_account_activity(clean_bulk_delete_systems_and_accounts, core_session,
                                                     list_of_created_systems):
    batch = ResourceManager.add_multiple_systems_with_accounts(core_session, 1, 1, list_of_created_systems)

    all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values([batch])
    delete_ids, _ = DataManipulation.shuffle_and_split_into_two_lists(all_accounts)

    ResourceManager.del_multiple_accounts(core_session, delete_ids)
    row = ResourceManager.get_system_activity(core_session, all_systems.pop())

    activity_details = []
    for system_activity in row:
        if system_activity['EventType'] == "Cloud.Server.ServerAdd":
            activity_details.append(system_activity["Detail"])
    assert len(activity_details) == 1, "Wrong number of delete activities for the account"


def test_bulk_account_delete_accounts_activity_fast_track(clean_bulk_delete_systems_and_accounts, core_session,
                                                          list_of_created_systems):
    batch = ResourceManager.add_multiple_systems_with_accounts(core_session, 1, 1, list_of_created_systems)

    all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values([batch])
    delete_ids, _ = DataManipulation.shuffle_and_split_into_two_lists(all_accounts)

    ResourceManager.del_multiple_accounts(core_session, delete_ids)
    row = ResourceManager.get_system_activity(core_session, all_systems.pop())

    activity_details = []
    for system_activity in row:
        if system_activity['EventType'] == "Cloud.Server.ServerAdd":
            activity_details.append(system_activity["Detail"])
    assert len(activity_details) == 1, "Wrong dumber of delete activities for the account"


def test_bulk_account_delete_multiple_accounts_activity(clean_bulk_delete_systems_and_accounts, core_session,
                                                        list_of_created_systems):
    batch = ResourceManager.add_multiple_systems_with_accounts(core_session, 1, 3, list_of_created_systems)

    all_systems, _ = DataManipulation.aggregate_lists_in_dict_values([batch])
    delete_ids = ResourceManager.get_multi_added_account_ids(core_session, all_systems)

    ResourceManager.del_multiple_accounts(core_session, delete_ids)
    system_activities = ResourceManager.get_system_activity(core_session, all_systems.pop())

    activity_details = []
    for activity in system_activities:
        if activity['EventType'] == "Cloud.Server.ServerAdd":
            activity_details.append(activity["Detail"])

    assert len(activity_details) == 1, "Wrong number of delete activities for the account"


@pytest.mark.parametrize('simulate_failure', [True, False])
def test_bulk_account_delete_job_fails_due_to_invalid_request_missing_query(core_session, simulate_failure):
    if simulate_failure:
        set_query = ""
    else:
        set_query = "@@Favorites"

    params = Util.scrub_dict({
        'Ids': list(),
        'SaveToSecrets': False,
        'SecretName': "",
        'SetQuery': set_query
    })

    request = core_session.apirequest(EndPoints.ACCOUNT_MULTI_DELETE, params)
    request_json = request.json()
    result, success = request_json['Result'], request_json['success']
    assert not simulate_failure == success, f"Query success was unexpected value, with message {result}"


def test_bulk_account_delete_job_fails_with_empty_request(core_session):
    params = Util.scrub_dict({
        'Ids': [],
        'SaveToSecrets': False,
        'SecretName': "",
        'SetQuery': ""
    })

    request = core_session.apirequest(EndPoints.ACCOUNT_MULTI_DELETE, params)
    request_json = request.json()
    result, success = request_json['Result'], request_json['success']
    assert success is False, f'Empty bulk account delete request succeeded even though it should fail {result}'


def test_bulk_account_delete_job_fails_with_empty_request_fast_track(core_session):
    params = Util.scrub_dict({
        'Ids': [],
        'SaveToSecrets': False,
        'SecretName': "",
        'SetQuery': "",
        'RunSync': True
    })

    request = core_session.apirequest(EndPoints.ACCOUNT_MULTI_DELETE, params)
    request_json = request.json()
    result, success = request_json['Result'], request_json['success']
    assert success is False, f'Empty bulk account delete request succeeded even though it should fail {result}'


def test_bulk_account_delete_job_fails_with_invalid_query_request_fast_track(core_session):
    params = Util.scrub_dict({
        'Ids': [],
        'SaveToSecrets': False,
        'SecretName': "",
        'SetQuery': "Invalid query text",
        'RunSync': True
    })

    request = core_session.apirequest(EndPoints.ACCOUNT_MULTI_DELETE, params)
    request_json = request.json()
    result, success = request_json['Result'], request_json['success']
    assert success is False, f'Empty bulk account delete request succeeded even though it should fail {result}'


@pytest.mark.parametrize('simulate_failure', [True, False])
def test_bulk_account_delete_job_fails_with_request_query_returning_zero_rows_fast_track(
        clean_bulk_delete_systems_and_accounts, core_session, simulate_failure, list_of_created_systems):
    batch = ResourceManager.add_multiple_systems_with_accounts(core_session, 1, 1, list_of_created_systems)
    _, delete_account_ids = DataManipulation.aggregate_lists_in_dict_values([batch])
    # Invalid query for the failure case.
    if simulate_failure:
        sql_query = f"select * from VaultAccount where ID = '{guid()}'"
    else:
        sql_query = RedrockController.get_query_for_ids('VaultAccount', delete_account_ids)

    params = Util.scrub_dict({
        'Ids': [],
        'SaveToSecrets': False,
        'SecretName': "",
        'SetQuery': sql_query,
        'RunSync': True
    })

    request = core_session.apirequest(EndPoints.ACCOUNT_MULTI_DELETE, params)
    request_json = request.json()
    result, success = request_json['Result'], request_json['success']
    assert not simulate_failure == success, \
        f'Invalid query bulk account delete request succeeded even though it should fail {result}'


@pytest.mark.parametrize('simulate_failure', [True, False])
def test_bulk_account_delete_job_fails_due_to_invalid_request_missing_secret_with_ids(
        clean_bulk_delete_systems_and_accounts, core_session, simulate_failure, list_of_created_systems):
    batch = ResourceManager.add_multiple_systems_with_accounts(core_session, 1, 1, list_of_created_systems)
    all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values([batch])
    params = Util.scrub_dict({
        'Ids': list(all_accounts),
        'SaveToSecrets': simulate_failure,
        'SecretName': "Bulk Account Delete",
        'SetQuery': "",
        'SkipIfHasAppsOrServices': simulate_failure
    })

    request = core_session.apirequest(EndPoints.ACCOUNT_MULTI_DELETE, params)
    request_json = request.json()
    result, success = request_json['Result'], request_json['success']
    ResourceManager.wait_for_job_state_succeeded(core_session, result, exception_on_timeout_or_failure=False)

    if simulate_failure:
        request = core_session.apirequest(EndPoints.ACCOUNT_MULTI_DELETE, params)
        request_json = request.json()
        result, success = request_json['Result'], request_json['success']
        ResourceManager.wait_for_job_state_succeeded(core_session, result)
        assert simulate_failure == success, f"Query success was unexpected value, with message {result}"
    else:
        request = core_session.apirequest(EndPoints.ACCOUNT_MULTI_DELETE, params)
        request_json = request.json()
        result, success = request_json['Result'], request_json['success']
        ResourceManager.wait_for_job_state_succeeded(core_session, result)
        assert not simulate_failure == success, f"Query success was unexpected value, with message {result}"
    total_account = RedrockController.get_accounts(core_session)
    list_account = []
    for get_account in total_account:
        if get_account['ID'] == all_accounts:
            list_account.append(get_account['ID'])
    assert 0 == len(list_account), "Number of remaining added accounts was unexpected number"


@pytest.mark.parametrize('simulate_failure', [False])
def test_bulk_account_delete_job_fails_due_to_invalid_request_missing_secret(clean_bulk_delete_systems_and_accounts,
                                                                             core_session, simulate_failure,
                                                                             list_of_created_systems):
    batch = ResourceManager.add_multiple_systems_with_accounts(core_session, 1, 1, list_of_created_systems)
    all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values([batch])
    some_set_name = "ApiSet" + guid()
    success, set_id = SetsManager.create_manual_collection(core_session, some_set_name, "VaultAccount", None)
    assert success, "Did not create collection"

    SetsManager.update_members_collection(core_session, 'add', list(all_accounts), 'VaultAccount', set_id)

    params = Util.scrub_dict({
        'Ids': list(all_accounts),
        'SaveToSecrets': simulate_failure,
        'SecretName': "Bulk Account Delete",
        'SetQuery': "",
        'SkipIfHasAppsOrServices': simulate_failure
    })

    if simulate_failure:
        request = core_session.apirequest(EndPoints.ACCOUNT_MULTI_DELETE, params)
        request_json = request.json()
        result, success = request_json['Result'], request_json['success']
        ResourceManager.wait_for_job_state_succeeded(core_session, result)
        assert simulate_failure == success, f"Query success was unexpected value, with message {result}"
    else:
        request = core_session.apirequest(EndPoints.ACCOUNT_MULTI_DELETE, params)
        request_json = request.json()
        result, success = request_json['Result'], request_json['success']
        ResourceManager.wait_for_job_state_succeeded(core_session, result)
        assert not simulate_failure == success, f"Query success was unexpected value, with message {result}"

    total_account = RedrockController.get_accounts(core_session)
    SetsManager.delete_collection(core_session, set_id)
    list_account = []
    for get_account in total_account:
        if get_account['ID'] == all_accounts:
            list_account.append(get_account['ID'])
    assert 0 == len(list_account), "Number of remaining added accounts was unexpected number"


def test_app_management_user_can_create_job_but_not_delete_accounts(clean_bulk_delete_systems_and_accounts,
                                                                    core_session, core_tenant, clean_users,
                                                                    users_and_roles, list_of_created_systems):
    batch = ResourceManager.add_multiple_systems_with_accounts(core_session, 2, 2, list_of_created_systems)
    all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values([batch])

    assert len(ResourceManager.get_multi_added_system_ids(core_session,
                                                          all_systems)) == 2, "Added systems not reflected in search"
    assert len(ResourceManager.get_multi_added_account_ids(core_session,
                                                           all_systems)) == 4, "Added accounts not reflected in search"

    requestor_session = users_and_roles.get_session_for_user('Application Management')

    job_id, result = ResourceManager.del_multiple_accounts(requestor_session, all_accounts)

    result = ResourceManager.get_job_state(core_session, job_id)

    assert result == "Succeeded", "Job did not execute"

    assert len(ResourceManager.get_multi_added_system_ids(core_session,
                                                          all_systems)) == 2, \
        "Expected 2 added systems to be found, but received different number"
    assert len(ResourceManager.get_multi_added_account_ids(core_session,
                                                           all_systems)) == 4, \
        "Expected 4 added accounts to be found, but received different number"

    user_info = requestor_session.get_current_session_user_info().json()['Result']
    username = user_info['Name']
    start_type = 'Cloud.Core.AsyncOperation.BulkAccountDelete.Start.Multi'
    end_type = 'Cloud.Core.AsyncOperation.BulkAccountDelete.Failure.Multi'
    start_message = f'{username} initiated delete of {len(all_accounts)} accounts'
    end_message = f'{username} failed to delete {len(all_accounts)} of {len(all_accounts)} accounts'

    RedrockController.expect_event_message_by_type(core_session, start_type, start_message)
    RedrockController.expect_event_message_by_type(core_session, end_type, end_message)


def test_missing_permissions_on_bulk_account_delete(clean_bulk_delete_systems_and_accounts, core_session, core_tenant,
                                                    clean_users, users_and_roles, list_of_created_systems):
    right_data = ["Privileged Access Service Power User", "role_Privileged Access Service Power User"]

    batch = ResourceManager.add_multiple_systems_with_accounts(core_session, 3, 3, list_of_created_systems)
    all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values([batch])
    has_permission_ids, missing_permission_ids = DataManipulation.shuffle_and_split_into_two_lists(all_accounts)

    requester_session = users_and_roles.get_session_for_user(right_data[0])
    results_role = users_and_roles.get_role(right_data[0])

    permissions_dict = dict.fromkeys(has_permission_ids,
                                     'Owner,View,Manage,Delete,Login,Naked,UpdatePassword,FileTransfer,UserPortalLogin')
    permissions_dict.update(dict.fromkeys(missing_permission_ids,
                                          'Owner,View,Manage,Login,Naked,UpdatePassword,FileTransfer,'
                                          'UserPortalLogin'))

    for account_id, permission_string in permissions_dict.items():
        result, success = ResourceManager.assign_account_permissions(core_session, permission_string,
                                                                     results_role['Name'], results_role['ID'], "Role",
                                                                     account_id)
        assert success, "Did not set account permissions " + str(result)

    api_results, success = ResourceManager.del_multiple_accounts(requester_session, all_accounts, run_sync=True)
    assert not success, f"Expected fail result from missing permissions during test_missing_permissions_on_bulk_account_delete {api_results}"

    assert set(ResourceManager.get_multi_added_account_ids(core_session, all_systems)) == set(missing_permission_ids)


@pytest.mark.parametrize('swap_roles', [True, False])
def test_other_user_cant_see_secret_created_by_first_user_in_bad(core_session, users_and_roles, created_system_id_list,
                                                                 swap_roles):
    roles = ["Privileged Access Service Administrator", "Privileged Access Service Power User"]

    if swap_roles:
        roles_new = [roles[1], roles[0]]
        roles = roles_new

    batch = ResourceManager.add_multiple_systems_with_accounts(core_session, 2, 2, created_system_id_list)
    all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values([batch])

    deleter_user_0_session = users_and_roles.get_session_for_user(roles[0])
    deleter_user_0_role = users_and_roles.get_role(roles[0])
    other_user_1_session = users_and_roles.get_session_for_user(roles[1])

    for account_id in all_accounts:
        permission_string = 'Owner,View,Manage,Delete,Login,Naked,UpdatePassword,FileTransfer,UserPortalLogin'
        result, success = ResourceManager.assign_account_permissions(core_session, permission_string,
                                                                     deleter_user_0_role['Name'],
                                                                     deleter_user_0_role['ID'], "Role", account_id)
        assert success, "Did not set account permissions " + str(result)

    for system_id in all_systems:
        permission_string = 'Grant,View,Edit,Delete,ManageSession,AgentAuth,RequestZoneRole,AddAccount,UnlockAccount'
        result, success = ResourceManager.assign_system_permissions(core_session, permission_string,
                                                                    deleter_user_0_role['Name'],
                                                                    deleter_user_0_role['ID'], "Role", system_id)
        assert success, "Did not set system permissions " + result

    parent_folder = get_folder(deleter_user_0_session, "Bulk Delete")
    assert not parent_folder['success'], "Should not be able to see folder before bulk delete operation as new user"

    secret_name = f"secret{guid()}"
    job_id, result = ResourceManager.del_multiple_accounts(deleter_user_0_session, all_accounts, save_passwords=True,
                                                           secret_name=secret_name)

    result = ResourceManager.get_job_state(core_session, job_id)
    assert result == "Succeeded", "Job did not execute"

    parent_folder = get_folder(deleter_user_0_session, "Bulk Delete")
    assert parent_folder['success'], "Should be able to see folder before bulk delete operation as new user"

    remaining_accounts = set(ResourceManager.get_multi_added_account_ids(core_session, created_system_id_list))

    assert remaining_accounts == set(), "Remaining accounts did not match expectation"

    secret_id = RedrockController.get_secret_id_by_name(deleter_user_0_session, secret_name)
    assert secret_id is not None, f"Secret was not visible to creator '{roles[0]}' user, either because it " \
                                  f"wasn't created or because of a permissions issue"

    secret_id = RedrockController.get_secret_id_by_name(other_user_1_session, secret_name)
    assert secret_id is None, f"Secret should not be '{roles[1]}' user when created by '{roles[0]}' user"

    secret_id = RedrockController.get_secret_id_by_name(core_session, secret_name)
    assert secret_id is not None, f"Sys admin should be able to see secret created by {roles[0]}"
