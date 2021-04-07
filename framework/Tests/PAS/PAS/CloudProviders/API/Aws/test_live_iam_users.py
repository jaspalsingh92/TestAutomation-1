import logging

import pytest

from Shared.API.cloud_provider import CloudProviderManager
from Shared.API.infrastructure import ResourceManager
from Utils.guid import guid

logger = logging.getLogger("test")


pytestmark = [pytest.mark.api, pytest.mark.cloudprovider, pytest.mark.aws]


@pytest.mark.parametrize("iam_user_config_key", ['iam_user_1', 'iam_user_2'])
@pytest.mark.parametrize("access_key_config_key", ['access_key_1', 'access_key_2'])
def test_valid_key(core_session, cloud_provider_ec2_account_config, iam_user_config_key, access_key_config_key):
    iam_user = cloud_provider_ec2_account_config[iam_user_config_key]
    access_key = iam_user[access_key_config_key]
    access_key_id = access_key['id']
    access_key_secret = access_key['secret']
    result, success = CloudProviderManager.verify_aws_access_key(core_session, access_key_id, access_key_secret)
    assert success, f"Expected to validate test key {access_key_id} for iam user {iam_user} but got {result}"


def test_invalid_key(core_session):
    result, success = CloudProviderManager.verify_aws_access_key(core_session, "AKIAUHZ2WLU2F7UABYB6", "AKIAUHZ2WLU2F7UABYB7")
    assert not success, f"Expected to fail validation on invalid test key {result}"


@pytest.mark.parametrize("user", ['iam_user_1', 'iam_user_2'])
def test_live_aws_verify_access_keys(core_session, cloud_provider_ec2_account_config, live_aws_cloud_provider, user):
    cloud_provider_id, test_deleted_provider, _populate_iam_user_with_access_keys = live_aws_cloud_provider

    iam_user = cloud_provider_ec2_account_config[user]
    access_key_1 = iam_user['access_key_1']
    access_key_2 = iam_user['access_key_2']

    username1, success = CloudProviderManager.verify_aws_access_key_for_user_account(core_session, access_key_1['id'], access_key_1['secret'], cloud_provider_id)
    assert success, f"Failed to call verify_aws_access_key_for_user_account {username1}"
    username2, success = CloudProviderManager.verify_aws_access_key_for_user_account(core_session, access_key_2['id'], access_key_2['secret'], cloud_provider_id)
    assert success, f"Failed to call verify_aws_access_key_for_user_account {username2}"

    assert username1 == iam_user['username'], f"Unexpected results from verify_aws_access_key_for_user_account for key1 {username1}"
    assert username2 == iam_user['username'], f"Unexpected results from verify_aws_access_key_for_user_account for key2 {username2}"


@pytest.mark.parametrize("user", ["iam_user_2"])
def test_delete_live_aws_access_keys_stores_secret_when_deleting_account(core_session, cloud_provider_ec2_account_config, live_aws_cloud_provider, secret_cleaner, user):
    cloud_provider_id, test_deleted_provider, _populate_iam_user_with_access_keys = live_aws_cloud_provider

    account_id = _populate_iam_user_with_access_keys(user)

    secret_name = f"aws_cloud_provider_api_{guid()}"

    result, success = ResourceManager.del_multiple_accounts(core_session, [account_id], save_passwords=True, secret_name=secret_name, run_sync=True)
    assert success, "Api did not complete successfully for bulk account delete MSG: " + result

    secret_file_contents = ResourceManager.fetch_and_delete_secret(core_session, secret_name, secret_cleaner)

    iam_user = cloud_provider_ec2_account_config[user]
    access_key_1 = iam_user['access_key_1']
    access_key_2 = iam_user['access_key_2']

    cloud_account_id = cloud_provider_ec2_account_config['id']

    assert cloud_account_id in secret_file_contents, f"Cloud Account ID absent from secret file {secret_file_contents}"

    assert account_id in secret_file_contents, f"Account ID absent from secret file {secret_file_contents}"
    assert access_key_1['id'] in secret_file_contents, f"Access key absent from secret file {secret_file_contents}"
    assert access_key_1['secret'] in secret_file_contents, f"Access key secret absent from secret file {secret_file_contents}"
    assert access_key_2['id'] in secret_file_contents, f"Access key 2 absent from secret file {secret_file_contents}"
    assert access_key_1['secret'] in secret_file_contents, f"Access key 2 secret absent from secret file {secret_file_contents}"


@pytest.mark.parametrize("user", ["iam_user_2"])
def test_delete_live_aws_access_keys_stores_secret_when_deleting_provider(core_session, cloud_provider_ec2_account_config, live_aws_cloud_provider, secret_cleaner, user):
    cloud_provider_id, test_deleted_provider, _populate_iam_user_with_access_keys = live_aws_cloud_provider

    account_id = _populate_iam_user_with_access_keys(user)

    secret_name = f"aws_cloud_provider_api_{guid()}"

    result, success = CloudProviderManager.delete_cloud_providers(core_session, [cloud_provider_id], run_sync=True, save_passwords=True, secret_name=secret_name)
    assert success, f"Failed to delete cloud providers {cloud_provider_id}"
    test_deleted_provider()

    secret_file_contents = ResourceManager.fetch_and_delete_secret(core_session, secret_name, secret_cleaner)

    iam_user = cloud_provider_ec2_account_config[user]
    access_key_1 = iam_user['access_key_1']
    access_key_2 = iam_user['access_key_2']

    assert account_id in secret_file_contents, f"Account ID absent from secret file {secret_file_contents}"
    assert access_key_1['id'] in secret_file_contents, f"Access key absent from secret file {secret_file_contents}"
    assert access_key_1['secret'] in secret_file_contents, f"Access key secret absent from secret file {secret_file_contents}"
    assert access_key_2['id'] in secret_file_contents, f"Access key 2 absent from secret file {secret_file_contents}"
    assert access_key_1['secret'] in secret_file_contents, f"Access key 2 secret absent from secret file {secret_file_contents}"


@pytest.mark.skip("Security is in flux for these methods right now")
@pytest.mark.parametrize('user_rights', ['Privileged Access Service Power User'], indirect=True)
@pytest.mark.parametrize("user", ['iam_user_1'])
def test_cant_add_access_key_without_manage_permission(core_session, cloud_provider_ec2_account_config, live_aws_cloud_provider, user, cds_session):
    cloud_provider_id, test_deleted_provider, _populate_iam_user_with_access_keys = live_aws_cloud_provider
    requester_session, limited_user = cds_session

    iam_user = cloud_provider_ec2_account_config[user]
    access_key_1 = iam_user['access_key_1']

    account_id, success = ResourceManager.add_account_cloud_provider(core_session, iam_user['username'], "", cloud_provider_id)
    assert success, f"Account addition failed with API response result {account_id}"

    result, success = CloudProviderManager.import_aws_access_key(requester_session, access_key_1['id'], access_key_1['secret'])
    assert not success, f"Succeeded to add access key1 when failure was expected {result}"

    result, success = ResourceManager.assign_account_permissions(core_session, "View,Manage", limited_user.get_login_name(), limited_user.get_id(), "User", account_id)
    assert success, f"Failed to execute API call to set permissions {result}"

    result, success = CloudProviderManager.import_aws_access_key(requester_session, access_key_1['id'], access_key_1['secret'])
    assert success, f"Succeeded to add access key1 when failure was expected {result}"


@pytest.mark.parametrize("user", ['iam_user_1'])
def test_aws_access_keys_fetch_properly(core_session, aws_iam_user_credentials, live_aws_cloud_provider, user):
    cloud_provider_id, test_deleted_provider, _populate_iam_user_with_access_keys = live_aws_cloud_provider
    account_id = _populate_iam_user_with_access_keys(user)

    access_key_id, access_key_secret = aws_iam_user_credentials

    rows = CloudProviderManager.get_aws_access_keys(core_session, account_id)
    assert len(rows[0]) == 2, f"Should retrieve 2 keys"
    assert access_key_secret not in str(rows), "get_aws_access_keys should not contain secret"


@pytest.mark.parametrize("user", ['iam_user_1'])
def test_delete_removes_access_key(core_session, live_aws_cloud_provider, user):
    cloud_provider_id, test_deleted_provider, _populate_iam_user_with_access_keys = live_aws_cloud_provider
    account_id = _populate_iam_user_with_access_keys(user)

    rows = CloudProviderManager.get_aws_access_keys(core_session, account_id)

    result, success = CloudProviderManager.delete_aws_access_key(core_session, rows[0][0]['ID'])
    assert success, f"Failed to delete access key1 {result}"

    rows = CloudProviderManager.get_aws_access_keys(core_session, account_id)
    assert len(rows[0]) == 1, f"Should retrieve 1 key"


@pytest.mark.parametrize('user_rights', ['Privileged Access Service Power User'], indirect=True)
@pytest.mark.parametrize("user", ['iam_user_1'])
def test_delete_fails_without_permission(core_session, live_aws_cloud_provider, user, cds_session):
    cloud_provider_id, test_deleted_provider, _populate_iam_user_with_access_keys = live_aws_cloud_provider
    requester_session, limited_user = cds_session
    account_id = _populate_iam_user_with_access_keys(user)

    rows = CloudProviderManager.get_aws_access_keys(core_session, account_id)

    result, success = CloudProviderManager.delete_aws_access_key(requester_session, rows[0][0]['ID'])
    assert not success, f"deleted access key1 when failure was expected {result}"

    rows = CloudProviderManager.get_aws_access_keys(core_session, account_id)
    assert len(rows[0]) == 2, f"Should retrieve 2 key"

    result, success = ResourceManager.assign_account_permissions(core_session, "Manage", limited_user.get_login_name(), limited_user.get_id(), "User", account_id)
    assert success, f"Failed to execute API call to set permissions {result}"

    result, success = CloudProviderManager.delete_aws_access_key(requester_session, rows[0][0]['ID'])
    assert success, f"failed to delete access key {result}"

    rows = CloudProviderManager.get_aws_access_keys(core_session, account_id)
    assert len(rows[0]) == 1, f"Should retrieve 1 key"


@pytest.mark.skip("Security is in flux for these methods right now")
@pytest.mark.parametrize('user_rights', ['Privileged Access Service Power User'], indirect=True)
@pytest.mark.parametrize("user", ['iam_user_2'])
def test_need_naked_permission_to_retrieve_aws_access_key_secret(core_session, cloud_provider_ec2_account_config, live_aws_cloud_provider, user, cds_session):
    cloud_provider_id, test_deleted_provider, _populate_iam_user_with_access_keys = live_aws_cloud_provider
    requester_session, limited_user = cds_session

    iam_user = cloud_provider_ec2_account_config[user]
    access_key_1 = iam_user['access_key_1']

    account_id, success = ResourceManager.add_account_cloud_provider(core_session, iam_user['username'], "", cloud_provider_id)
    assert success, f"Account addition failed with API response result {account_id}"

    result, success = CloudProviderManager.import_aws_access_key(requester_session, access_key_1['id'], access_key_1['secret'])
    assert not success, f"Succeeded to add access key1 when failure was expected {result}"

    result, success = ResourceManager.assign_account_permissions(core_session, "Manage", limited_user.get_login_name(), limited_user.get_id(), "User", account_id)
    assert success, f"Failed to execute API call to set permissions {result}"

    result, success = CloudProviderManager.import_aws_access_key(requester_session, access_key_1['id'], access_key_1['secret'])
    assert success, f"Succeeded to add access key1 when failure was expected {result}"

    rows = CloudProviderManager.get_aws_access_keys(core_session, account_id)[0]

    retrieve_single, success = CloudProviderManager.retrieve_aws_access_key(requester_session, account_id, rows[0]['ID'])
    assert not success, f"Success while expecting failure to retrieve AWS access keys {retrieve_single}"

    result, success = ResourceManager.assign_account_permissions(core_session, "Naked", limited_user.get_login_name(), limited_user.get_id(), "User", account_id)
    assert success, f"Failed to execute API call to set permissions {result}"

    retrieve_single, success = CloudProviderManager.retrieve_aws_access_key(requester_session, account_id, rows[0]['ID'])
    assert success, f"Failed to retrieve AWS access keys {retrieve_single}"

    assert retrieve_single['SecretAccessKey'] == access_key_1['secret'], f"Did not return correct AWS access key secret {retrieve_single}"
    assert retrieve_single['AccessKeyId'] == access_key_1['id'], f"Did not return correct AWS access key id {retrieve_single}"

