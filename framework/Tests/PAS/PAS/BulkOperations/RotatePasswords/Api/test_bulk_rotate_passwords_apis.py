import time
import pytest
import logging
from future.moves import collections
from requests import HTTPError
from winrm.exceptions import InvalidCredentialsError
from Shared.API.sets import SetsManager
from Utils.guid import guid
from Shared.API.infrastructure import ResourceManager
from Shared.API.bulkoperations import BulkOperations
from Shared.API.server import ServerManager
from Shared.endpoint_manager import EndPoints
from Shared.util import Util
from Shared.API.redrock import RedrockController
from Utils.winrm import WinRM

logger = logging.getLogger('framework')

pytestmark = [pytest.mark.api, pytest.mark.cps, pytest.mark.bulk_rotate_passwords]


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.parametrize('change_method', ["ids", "ids_with_invalid", "sql", "group"])
def test_bulk_rotate_works_with_different_methods_of_specifying_systems(
        core_session,
        remote_users_with_mirrored_managed_local_users_qty3, windows_test_machine_config, change_method):

    remote_ip = windows_test_machine_config['ip_address']

    account_ids, accounts = BulkOperations.grab_relevant_users(core_session, remote_users_with_mirrored_managed_local_users_qty3)
    passwords_fetched = BulkOperations.checkout_users(core_session, accounts)
    BulkOperations.validate_users_with_login(remote_ip, passwords_fetched)

    if change_method == "checkin":   # disabled, out of scope
        BulkOperations.check_in_users(core_session, passwords_fetched)
    elif change_method == "ids":
        result, success = ResourceManager.rotate_multiple_passwords(core_session, account_ids)
        assert success, "Did not bulk rotate passwords"
    elif change_method == "ids_with_invalid":
        result, success = ResourceManager.rotate_multiple_passwords(core_session, account_ids)
        assert success, "Did not bulk rotate passwords"
    elif change_method == "sql":
        sql_query = 'SELECT * FROM VaultAccount ' \
                    'WHERE ' + ' OR '.join(('VaultAccount.ID = "' + str(n) + '"' for n in account_ids))
        result, success = ResourceManager.rotate_multiple_passwords(core_session, [], set_query=sql_query)
        assert success, "Did not bulk rotate passwords"
    elif change_method == "group":
        some_set_name = "ApiSet" + guid()
        SetsManager.create_manual_collection(core_session, some_set_name, "VaultAccount", None)
        set_id = SetsManager.get_collection_id(core_session, some_set_name, "VaultAccount")
        SetsManager.update_members_collection(core_session, 'add', account_ids, 'VaultAccount', set_id)
        filters = SetsManager.get_object_collection_and_filter_by_name(core_session,
                                                                       some_set_name, "VaultAccount")['Filters']
        result, success = ResourceManager.rotate_multiple_passwords(core_session, [], set_query=filters)
        assert success, "Did not bulk rotate passwords"
    else:
        raise Exception(f"Bad input variable change_method {change_method}")

    BulkOperations.validate_users_with_login(remote_ip, passwords_fetched, [False] * len(passwords_fetched), change_method)
    # Verify passwords are no longer right

    user_info = core_session.get_current_session_user_info().json()['Result']
    username = user_info['Name']
    start_type = 'Cloud.Core.AsyncOperation.BulkPasswordRotationJob.Start.Multi'
    end_type = 'Cloud.Core.AsyncOperation.BulkPasswordRotationJob.Success.Multi'
    start_message = f'{username} initiated password rotation of {len(account_ids)} accounts'
    end_message = f'{username} successfully rotated {len(account_ids)} account passwords'

    RedrockController.expect_event_message_by_type(core_session, start_type, start_message)
    RedrockController.expect_event_message_by_type(core_session, end_type, end_message)


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.parametrize('mode', ["Smb", "RpcOverTcp", "WinRMOverHttp"])
def test_bulk_rotate_works_with_different_management_modes(core_session,
                                                           remote_users_with_mirrored_managed_local_users_qty3,
                                                           windows_test_machine_config,
                                                           names_and_ids_of_created_systems_this_method, mode):
    remote_ip = windows_test_machine_config['ip_address']

    account_ids, accounts = BulkOperations.grab_relevant_users(core_session, remote_users_with_mirrored_managed_local_users_qty3)
    passwords_fetched = BulkOperations.checkout_users(core_session, accounts)

    result, success = ResourceManager.update_system(core_session, names_and_ids_of_created_systems_this_method[0][1],
                                                    names_and_ids_of_created_systems_this_method[0][0], remote_ip,
                                                    'Windows', managementmode=mode)
    assert success, f"Did not set {mode} mode"

    result, success = ResourceManager.rotate_multiple_passwords(core_session, account_ids, wait_time=600)
    assert success, "Did not bulk rotate passwords"

    BulkOperations.validate_users_with_login(remote_ip, passwords_fetched, [False] * len(passwords_fetched), "smb by id")
    # Verify passwords are no longer right


@pytest.mark.api
@pytest.mark.pas
def test_bulk_rotate_works_with_proxy_in_smb_mode(core_session,
                                                  remote_users_with_mirrored_managed_local_users_qty3_with_proxy,
                                                  windows_test_machine_config,
                                                  names_and_ids_of_created_systems_this_method):
    remote_ip = windows_test_machine_config['ip_address']

    account_ids, accounts = BulkOperations.grab_relevant_users(core_session,
                                                 remote_users_with_mirrored_managed_local_users_qty3_with_proxy)
    passwords_fetched = BulkOperations.checkout_users(core_session, accounts)

    result, success = ResourceManager.update_system(core_session, names_and_ids_of_created_systems_this_method[0][1],
                                                    names_and_ids_of_created_systems_this_method[0][0], remote_ip,
                                                    'Windows', managementmode="Smb")
    assert success, f"Did not set Smb mode {result}"

    result, success = ResourceManager.rotate_multiple_passwords(core_session, account_ids, wait_time=600)
    assert success, "Did not bulk rotate passwords"

    BulkOperations.validate_users_with_login(remote_ip, passwords_fetched, [False] * len(passwords_fetched), "smb by id")
    # Verify passwords are no longer right


@pytest.mark.api
@pytest.mark.pas
def test_bulk_rotate_works_quickly(core_session, remote_users_with_mirrored_managed_local_users_qty10,
                                   windows_test_machine_config):
    account_ids, accounts = BulkOperations.grab_relevant_users(core_session, remote_users_with_mirrored_managed_local_users_qty10)

    reasonable_amount_of_time_to_execute = 60
    start_time = time.time()
    result, success = ResourceManager.rotate_multiple_passwords(core_session, account_ids, wait_time=600)
    assert success, "Did not bulk rotate passwords"
    end_time = time.time()
    elapsed_time = end_time - start_time

    assert elapsed_time <= reasonable_amount_of_time_to_execute, \
        "Bulk rotate did not complete in a reasonable amount of time"


@pytest.mark.api
@pytest.mark.pas
def test_bulk_rotate_works_with_overlapping_calls(core_session, remote_users_with_mirrored_managed_local_users_qty3,
                                                  windows_test_machine_config):
    remote_ip = windows_test_machine_config['ip_address']

    account_ids, accounts = BulkOperations.grab_relevant_users(core_session, remote_users_with_mirrored_managed_local_users_qty3)

    for i in range(2):
        result, success = ResourceManager.rotate_multiple_passwords(core_session, account_ids, wait_time=-1)
        assert success, "Did not bulk rotate passwords"
    result, success = ResourceManager.rotate_multiple_passwords(core_session, account_ids, wait_time=60)
    assert success, "Did not bulk rotate passwords"

    passwords_fetched = BulkOperations.checkout_users(core_session, accounts)
    BulkOperations.validate_users_with_login(remote_ip, passwords_fetched)


@pytest.mark.api
@pytest.mark.pas
def test_bulk_rotate_fails_with_invalid_query(core_session):
    result, success = ResourceManager.rotate_multiple_passwords(core_session, [])
    assert not success, "Call was invalid, should not have succeeded"


@pytest.mark.api
@pytest.mark.pas
def test_bulk_rotate_fails_with_invalid_query2(core_session):
    my_data = Util.scrub_dict({})
    request = core_session.apirequest(EndPoints.PW_MULTI_ROTATE, my_data)
    request_json = request.json()
    assert not request_json['success'], "Call succeeded and should have failed"


@pytest.mark.api
@pytest.mark.pas
def test_cannot_rotate_passwords_without_permission(core_session, remote_users_with_mirrored_managed_local_users_qty3,
                                                    windows_test_machine_config, users_and_roles):
    right_data = ["Privileged Access Service Power User", "role_Privileged Access Service Power User"]
    requestor_session = users_and_roles.get_session_for_user(right_data[0])
    results_role = users_and_roles.get_role(right_data[0])

    remote_ip = windows_test_machine_config['ip_address']

    account_ids, accounts = BulkOperations.grab_relevant_users(core_session, remote_users_with_mirrored_managed_local_users_qty3)
    passwords_fetched = BulkOperations.checkout_users(core_session, accounts)

    job_id, success = ResourceManager.rotate_multiple_passwords(requestor_session, account_ids)
    assert success, "Did not kick off bulk rotate passwords job"
    result = ResourceManager.get_job_state(core_session, job_id)
    assert result == "Succeeded", "Job did not execute"

    BulkOperations.validate_users_with_login(remote_ip, passwords_fetched)  # Verify passwords are still right
    permission_string = "Owner,View,Manage,Delete,Login,Naked,UpdatePassword,RotatePassword,FileTransfer," \
                        "UserPortalLogin "

    account_id = passwords_fetched[1][3]  # Grant permission to only one of the accounts, the middle one
    result, success = ResourceManager.assign_account_permissions(core_session, permission_string,
                                                                 results_role['Name'], results_role['ID'],
                                                                 "Role", account_id)
    assert success, "Did not set account permissions " + str(result)

    job_id, success = ResourceManager.rotate_multiple_passwords(requestor_session, account_ids)
    assert success, "Did not kick off bulk rotate passwords job"
    result = ResourceManager.get_job_state(core_session, job_id)
    assert result == "Succeeded", "Job did not execute"

    BulkOperations.validate_users_with_login(remote_ip, passwords_fetched, [True, False, True])

    user_info = requestor_session.get_current_session_user_info().json()['Result']
    username = user_info['Name']
    start_type = 'Cloud.Core.AsyncOperation.BulkPasswordRotationJob.Start.Multi'
    end_type = 'Cloud.Core.AsyncOperation.BulkPasswordRotationJob.Failure.Multi'
    start_message = f'{username} initiated password rotation of {len(account_ids)} accounts'
    end_message = f'{username} failed to rotate 2 of 3 account passwords'

    RedrockController.expect_event_message_by_type(core_session, start_type, start_message)
    RedrockController.expect_event_message_by_type(core_session, end_type, end_message)
