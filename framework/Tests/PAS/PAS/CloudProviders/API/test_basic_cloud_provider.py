import logging

import pytest

from Shared.API.cloud_provider import CloudProviderManager, CloudProviderType
from Shared.API.infrastructure import ResourceManager
from Shared.API.redrock import RedrockController
from Shared.API.secret import set_users_effective_permissions, get_file_secret_contents
from Utils.guid import guid

logger = logging.getLogger("test")


pytestmark = [pytest.mark.api, pytest.mark.cloudprovider]


#@pytest.mark.parametrize("cloud_provider_type", [CloudProviderType.AWS, CloudProviderType.AZURE], indirect=True)
@pytest.mark.parametrize("cloud_provider_type", [CloudProviderType.AWS], indirect=True)  # todo: re-add Azure
def test_add_cloud_provider(core_session, cloud_provider_type, fake_cloud_provider_cleaner):
    name = f"name {guid()}"
    desc = f"desc {guid()}"
    account_id = str(guid())[0:12]
    cloud_provider_id, success = CloudProviderManager.add_cloud_provider(core_session, cloud_provider_type.value, name, description=desc, cloud_account_id=account_id)
    assert success, f"Failed to add cloud provider {cloud_provider_id}"
    fake_cloud_provider_cleaner.append(cloud_provider_id)


@pytest.mark.parametrize('user_rights', ['Privileged Access Service Power User'], indirect=True)
def test_add_cloud_provider_fails_if_not_sys_admin(cds_session, cloud_provider_type):
    name = f"name {guid()}"
    desc = f"desc {guid()}"
    account_id = str(guid())[0:12]

    requester_session, limited_user = cds_session

    cloud_provider_id, success = CloudProviderManager.add_cloud_provider(requester_session, cloud_provider_type.value, name, description=desc, cloud_account_id=account_id)
    assert not success, f"Failed to add cloud provider {cloud_provider_id}"


def test_add_cloud_acct_invalid_name(core_session, cloud_provider_type):
    name = f"name {guid()}"
    desc = f"desc {guid()}"
    account_id = "a" + str(guid())[0:11]
    cloud_provider_id, success = CloudProviderManager.add_cloud_provider(core_session, cloud_provider_type.value, name, description=desc, cloud_account_id=account_id)
    assert not success, f"Expected failure on add of invalid account_id {cloud_provider_id} with id {account_id}"
    account_id = str(guid())[0:11] + 'a'
    cloud_provider_id, success = CloudProviderManager.add_cloud_provider(core_session, cloud_provider_type.value, name, description=desc,
                                                                         cloud_account_id=account_id)
    assert not success, f"Expected failure on add of invalid account_id {cloud_provider_id}"
    account_id = str(guid())[0:11]
    cloud_provider_id, success = CloudProviderManager.add_cloud_provider(core_session, cloud_provider_type.value, name, description=desc,
                                                                         cloud_account_id=account_id)
    assert not success, f"Expected failure on add of invalid account_id {cloud_provider_id} with id {account_id}"

    account_id = str(guid())[0:5] + 'a' + str(guid())[0:7]
    cloud_provider_id, success = CloudProviderManager.add_cloud_provider(core_session, cloud_provider_type.value, name, description=desc,
                                                                         cloud_account_id=account_id)
    assert not success, f"Expected failure on add of invalid account_id {cloud_provider_id} with id {account_id}"

    account_id = str(guid())[0:11]
    cloud_provider_id, success = CloudProviderManager.add_cloud_provider(core_session, cloud_provider_type.value, name, description=desc,
                                                                         cloud_account_id=account_id)
    assert not success, f"Expected failure on add of invalid account_id {cloud_provider_id} with id {account_id}"

    account_id = str(guid())[0:13]
    cloud_provider_id, success = CloudProviderManager.add_cloud_provider(core_session, cloud_provider_type.value, name, description=desc,
                                                                         cloud_account_id=account_id)
    assert not success, f"Expected failure on add of invalid account_id {cloud_provider_id} with id {account_id}"


def test_cant_add_duplicate_name_cloud_resource(core_session, cloud_provider_type, fake_cloud_provider_cleaner):
    name = f"name {guid()}"
    account_id = str(guid())[0:12]
    cloud_provider_id, success = CloudProviderManager.add_cloud_provider(core_session, cloud_provider_type.value, name, cloud_account_id=account_id)
    assert success, f"Failed to add cloud provider {cloud_provider_id}"
    fake_cloud_provider_cleaner.append(cloud_provider_id)
    account_id2 = str(guid())[0:12]
    cloud_id_2, success = CloudProviderManager.add_cloud_provider(core_session, cloud_provider_type.value, name, cloud_account_id=account_id2)
    assert not success, f"Should not have added second cloud provider with duplicate name {cloud_id_2}"


def test_cant_add_duplicate_id_cloud_resource(core_session, cloud_provider_type, fake_cloud_provider_cleaner):
    name = f"name {guid()}"
    account_id = str(guid())[0:12]
    cloud_provider_id, success = CloudProviderManager.add_cloud_provider(core_session, cloud_provider_type.value, name, cloud_account_id=account_id)
    assert success, f"Failed to add cloud provider {cloud_provider_id}"
    fake_cloud_provider_cleaner.append(cloud_provider_id)
    name2 = f"name {guid()}"
    cloud_id_2, success = CloudProviderManager.add_cloud_provider(core_session, cloud_provider_type.value, name2, cloud_account_id=account_id)
    assert not success, f"Should not have added second cloud provider with duplicate name {cloud_id_2}"


@pytest.mark.parametrize('user_rights', ['Privileged Access Service Power User'], indirect=True)
def test_get_cloud_provider(fake_cloud_provider, cds_session):
    aws_name, aws_desc, cloud_provider_id, cloud_account_id, test_did_cleaning = fake_cloud_provider
    requester_session, limited_user = cds_session
    result, success = CloudProviderManager.get_cloud_provider(requester_session, cloud_provider_id)
    assert success, f"Failed to get cloud provider {result}"

    assert aws_name == result['Name'], f"Unexpected data from get_cloud_provider {result}"
    assert aws_desc == result['Description'], f"Unexpected data from get_cloud_provider {result}"
    assert "Aws" == result['Type'], f"Unexpected data from get_cloud_provider {result}"


@pytest.mark.parametrize('user_rights', ['Application Management'], indirect=True)
def test_update_cloud_provider(core_session, cloud_provider_type, fake_cloud_provider, cds_session):
    aws_name, aws_desc, cloud_provider_id, cloud_account_id, test_did_cleaning = fake_cloud_provider

    new_name = guid()
    new_description = guid()

    requester_session, limited_user = cds_session

    result, success =\
        CloudProviderManager.set_cloud_provider_permissions(core_session, "Edit", limited_user.get_login_name(), limited_user.get_id(), "User", cloud_provider_id)
    assert success, f"Failed to execute API call to set permissions {result}"

    result, success = CloudProviderManager.update_cloud_provider(requester_session, cloud_provider_id, cloud_provider_type.value, name=new_name, description=new_description)
    assert not success, f"Succeeded while expecting failure on update cloud provider {result}"

    result, success =\
        CloudProviderManager.set_cloud_provider_permissions(core_session, "View", limited_user.get_login_name(), limited_user.get_id(), "User", cloud_provider_id)
    assert success, f"Failed to execute API call to set permissions {result}"

    result, success = CloudProviderManager.update_cloud_provider(requester_session, cloud_provider_id, cloud_provider_type.value, name=new_name, description=new_description)
    assert not success, f"Succeeded while expecting failure on update cloud provider {result}"

    result, success = CloudProviderManager.set_cloud_provider_permissions(core_session, "View,Edit", limited_user.get_login_name(), limited_user.get_id(), "User", cloud_provider_id)
    assert success, f"Failed to execute API call to set permissions {result}"

    result, success = CloudProviderManager.update_cloud_provider(requester_session, cloud_provider_id, cloud_provider_type.value, name=new_name,
                                                                 description=new_description)
    assert success, f"failure on update cloud provider {result}"

    result, success = CloudProviderManager.get_cloud_provider(core_session, cloud_provider_id)
    assert success, f"Failed to get cloud provider {result}"

    assert new_name == result['Name'], f"Unexpected data from get_cloud_provider {result}"
    assert new_description == result['Description'], f"Unexpected data from get_cloud_provider {result}"
    assert "Aws" == result['Type'], f"Unexpected data from get_cloud_provider {result}"


def test_update_cloud_provider_fails_with_bad_data(core_session, fake_cloud_provider):
    aws_name, aws_desc, cloud_provider_id, cloud_account_id, test_did_cleaning = fake_cloud_provider

    result, success = CloudProviderManager.update_cloud_provider(core_session, cloud_provider_id, guid(), name=guid(), description=guid())
    assert not success, f"Should not have updated cloud provider with bad type parameter {result}"

    result, success = CloudProviderManager.get_cloud_provider(core_session, cloud_provider_id)
    assert success, f"Failed to get cloud provider {result}"

    assert aws_name == result['Name'], f"Unexpected data from get_cloud_provider {result}"
    assert aws_desc == result['Description'], f"Unexpected data from get_cloud_provider {result}"
    assert "Aws" == result['Type'], f"Unexpected data from get_cloud_provider {result}"


def test_delete_cloud_provider_secret(core_session, fake_cloud_provider_root_account, fake_cloud_provider, secret_cleaner):
    account_id, username, password, cloud_provider_id, test_did_cleaning = fake_cloud_provider_root_account
    name, desc, cloud_provider_id, cloud_account_id, test_did_cleaning = fake_cloud_provider
    account_name = f"acctname{guid()}"
    account_id, success = ResourceManager.add_account_cloud_provider(core_session, account_name, "", cloud_provider_id)
    assert success, f"Account addition failed with API response result {account_id}"

    key_secret = "kjshakjsakjasgfkjysgkjagfkjsakjgfakjsf"

    result, success = CloudProviderManager.set_mfa_token(core_session, account_id, key_secret)
    assert success, f"Failed to set mfa token {result}"

    secret_name = f"SecretName{guid()}"

    result, success = CloudProviderManager.delete_cloud_providers(core_session, [cloud_provider_id], save_passwords=True, secret_name=secret_name)
    assert success, f"Failed to delete cloud provider with response {result}"
    test_did_cleaning()

    ResourceManager.wait_for_secret_to_exist_or_timeout(core_session, secret_name)

    secret_id = RedrockController.get_secret_id_by_name(core_session, secret_name)

    assert secret_id is not None, "No secret was created"

    secret_cleaner.append(secret_id)
    user = core_session.get_user()
    user_name = user.get_login_name()
    user_id = user.get_id()

    result, success = set_users_effective_permissions(core_session, user_name, "View,Edit,Retrieve", user_id, secret_id)
    assert success, f"Did not set secret permission successfully with message {result}"

    secret_file_contents = get_file_secret_contents(core_session, secret_id)

    assert username in secret_file_contents, f"username absent from secret file {secret_file_contents}"
    assert password in secret_file_contents, f"password absent from secret file {secret_file_contents}"
    assert cloud_provider_id in secret_file_contents, f"cloud_provider_id absent from secret file {secret_file_contents}"
    assert account_name in secret_file_contents, f"account_name absent from secret file {secret_file_contents}"
    assert key_secret in secret_file_contents, f"mfa secret absent from secret file {secret_file_contents}"


@pytest.mark.parametrize('user_rights', ['Privileged Access Service Power User'], indirect=True)
def test_delete_cloud_provider_fails_without_permission(core_session, fake_cloud_provider_root_account, fake_cloud_provider, cds_session):

    account_id, username, password, cloud_provider_id, test_did_cleaning = fake_cloud_provider_root_account
    name, desc, cloud_provider_id, cloud_account_id, test_did_cleaning = fake_cloud_provider
    account_name = f"acctname{guid()}"

    account_id, success = ResourceManager.add_account_cloud_provider(core_session, account_name, "", cloud_provider_id)
    assert success, f"Account addition failed with API response result {account_id}"

    pas_user_session, limited_user = cds_session

    result, success = CloudProviderManager.delete_cloud_providers(pas_user_session, [cloud_provider_id], save_passwords=False)
    assert not success, f"Delete should not have succeeded {result}"

    result, success = CloudProviderManager.delete_cloud_providers(pas_user_session, cloud_provider_id)
    assert not success, f"Delete should not have succeeded {result}"

    result, success = ResourceManager.del_account(pas_user_session, account_id)
    assert not success, f"Deleting IAM account failed with API response result: {result}"

    result, success = ResourceManager.del_account(pas_user_session, account_id)
    assert not success, f"Deleting IAM account failed with API response result: {result}"


@pytest.mark.parametrize('user_rights', ['Privileged Access Service Power User'], indirect=True)
def test_delete_succeeds_with_permission(core_session, cloud_provider_type, cds_session):
    name = f"name {guid()}"
    desc = f"desc {guid()}"
    account_id = str(guid())[0:12]

    cloud_provider_id, success = CloudProviderManager.add_cloud_provider(core_session, cloud_provider_type.value, name, description=desc,
                                                                         cloud_account_id=account_id)
    assert success, f"Failed to add cloud provider {cloud_provider_id}"

    requester_session, limited_user = cds_session

    result, success = CloudProviderManager.delete_cloud_provider(requester_session, cloud_provider_id)
    assert not success, f"Expected failure deleting without permission {result}"

    result, success = CloudProviderManager.set_cloud_provider_permissions(core_session, "View,Delete",
                                                                          limited_user.get_login_name(), limited_user.get_id(),
                                                                          "User", cloud_provider_id)
    assert success, f"Failed to execute API call to set permissions {result}"

    result, success = CloudProviderManager.delete_cloud_provider(requester_session, cloud_provider_id)
    assert success, f"Expected no failure deleting with permission {result}"


@pytest.mark.parametrize('user_rights', ['Privileged Access Service Power User'], indirect=True)
def test_delete_multiple_succeeds_with_permission(core_session, cloud_provider_type, cds_session):
    name = f"name {guid()}"
    desc = f"desc {guid()}"
    account_id = str(guid())[0:12]

    cloud_provider_id, success = CloudProviderManager.add_cloud_provider(core_session, cloud_provider_type.value, name, description=desc,
                                                                         cloud_account_id=account_id)
    assert success, f"Failed to add cloud provider {cloud_provider_id}"

    requester_session, limited_user = cds_session

    result, success = CloudProviderManager.delete_cloud_providers(requester_session, [cloud_provider_id])
    assert not success, f"Expected failure deleting without permission {result}"

    result, success = CloudProviderManager.set_cloud_provider_permissions(core_session, "View,Delete",
                                                                          limited_user.get_login_name(), limited_user.get_id(),
                                                                          "User", cloud_provider_id)
    assert success, f"Failed to execute API call to set permissions {result}"

    result, success = CloudProviderManager.delete_cloud_providers(requester_session, [cloud_provider_id])
    assert success, f"Expected no failure deleting with permission {result}"


@pytest.mark.parametrize('user_rights', ['Privileged Access Service Power User'], indirect=True)
def test_get_all_cloud_providers_with_view_permission(fake_cloud_provider, cds_session):

    name, desc, cloud_provider_id, cloud_account_id, test_did_cleaning = fake_cloud_provider

    requester_session, limited_user = cds_session

    result, success = CloudProviderManager.get_all_cloud_providers(requester_session)
    assert success, f"Expected to pass get_all_cloud_providers {result}"

    assert sum(p['ID'] == cloud_provider_id for p in result) == 1, f"Expected to get results of cloud providers {result} {cloud_provider_id}"


@pytest.mark.parametrize('user_rights', ['Application Management'], indirect=True)
def test_get_all_cloud_providers_without_view_permission(fake_cloud_provider, cds_session):

    name, desc, cloud_provider_id, cloud_account_id, test_did_cleaning = fake_cloud_provider

    requester_session, limited_user = cds_session

    result, success = CloudProviderManager.get_all_cloud_providers(requester_session)
    assert success, f"Expected to pass get_all_cloud_providers {result}"

    assert sum(p['ID'] == cloud_provider_id for p in result) == 0, f"Expected to get 0 results of cloud providers {result} {cloud_provider_id}"


@pytest.mark.parametrize('user_rights', ['Application Management'], indirect=True)
def test_get_cloud_provider_fails_with_no_permission(fake_cloud_provider, cds_session):
    aws_name, aws_desc, cloud_provider_id, cloud_account_id, test_did_cleaning = fake_cloud_provider
    requester_session, limited_user = cds_session

    result, success = CloudProviderManager.get_cloud_provider(requester_session, cloud_provider_id)
    assert not success, f"Failed to fail to get cloud provider {result}"


@pytest.mark.parametrize('user_rights', ['Application Management'], indirect=True)
def test_set_and_retrieve_mfa(core_session, fake_cloud_provider_root_account, cds_session):
    account_id, username, password, cloud_provider_id, test_did_cleaning = fake_cloud_provider_root_account

    requester_session, limited_user = cds_session

    result, success = CloudProviderManager.set_mfa_token(requester_session, account_id, "kjshakjsakjasgfkjasgkjagfkjsakjgfakjsf")
    assert not success, f"Success when expecting fail to set mfa token {result}"

    result, success = ResourceManager.assign_account_permissions(core_session, "View,Manage", limited_user.get_login_name(), limited_user.get_id(), "User", account_id)
    assert success, f"Failed to execute API call to set permissions {result}"

    result, success = CloudProviderManager.set_mfa_token(requester_session, account_id, "kjshakjsakjasgfkjasgkjagfkjsakjgfakjsf")
    assert success, f"Failed to set mfa token {result}"

    result, success = CloudProviderManager.get_mfa_token(requester_session, account_id)
    assert not success, f"Success while expecting failure get_mfa_token {result}"

    result, success = ResourceManager.assign_account_permissions(core_session, 'View', limited_user.get_login_name(),
                                                                 limited_user.get_id(), "User", account_id)
    assert success, f"Failed to execute API call to set permissions {result}"

    result, success = CloudProviderManager.get_mfa_token_settings(requester_session, account_id)
    assert success, f"failure get_mfa_token_settings {result}"

    result, success = CloudProviderManager.get_mfa_token(requester_session, account_id)
    assert not success, f"success expecting failure get_mfa_token {result}"

    result, success = ResourceManager.assign_account_permissions(core_session, 'View,Naked', limited_user.get_login_name(),
                                                                 limited_user.get_id(), "User",
                                                                 account_id)
    assert success, f"Failed to execute API call to set permissions {result}"

    result, success = CloudProviderManager.get_mfa_token(requester_session, account_id)
    assert success, f"success expecting failure get_mfa_token {result}"


def test_fail_getting_mfa_doesnt_exist(core_session, fake_cloud_provider_root_account):
    account_id, username, password, cloud_provider_id, test_did_cleaning = fake_cloud_provider_root_account

    result, success = CloudProviderManager.get_mfa_token(core_session, account_id)
    assert not success, f"Success on grabbing non existent mfa_token {result}"


def test_root_account(core_session, fake_cloud_provider_root_account):
    account_id, username, password, cloud_provider_id, test_did_cleaning = fake_cloud_provider_root_account

    query = f"SELECT VaultAccount.CredentialType, VaultAccount.ID, VaultAccount.User FROM VaultAccount WHERE ID='{account_id}'"
    results = RedrockController.get_result_rows(RedrockController.redrock_query(core_session, query))

    assert len(results) == 1, f"Expected exactly one result {results}"

    result = results[0]
    expected_result = {'ID': account_id, 'User': username, 'CredentialType': 'Password'}

    if '_TableName' in result:
        del result['_TableName']

    assert result == expected_result, f"Unexpected data in results {result}"


# todo cloud provider ID appears in secret (it doesn't, which is a problem)