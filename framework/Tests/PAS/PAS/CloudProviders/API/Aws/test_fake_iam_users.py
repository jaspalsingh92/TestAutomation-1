import logging

import pytest

from Shared.API.cloud_provider import CloudProviderManager
from Shared.API.redrock import RedrockController

logger = logging.getLogger("test")


pytestmark = [pytest.mark.api, pytest.mark.cloudprovider, pytest.mark.aws]


def test_iam_account_has_no_access_keys(core_session, fake_cloud_provider_iam_account):
    account_id, username = fake_cloud_provider_iam_account

    access_keys, success = CloudProviderManager.get_aws_access_keys(core_session, account_id)
    assert success, f"Failed to retrieve access keys {access_keys}"

    assert access_keys == [], f"Unexpected results for get_aws_access_keys on root account {access_keys}"


def test_iam_account_correct_data(core_session, fake_cloud_provider_iam_account):
    account_id, username = fake_cloud_provider_iam_account

    query = f"SELECT VaultAccount.CredentialType, VaultAccount.ID, VaultAccount.User FROM VaultAccount WHERE ID='{account_id}'"
    results = RedrockController.get_result_rows(RedrockController.redrock_query(core_session, query))

    assert len(results) == 1, f"Expected exactly one result {results}"

    result = results[0]
    expected_result = {'ID': account_id, 'User': username, 'CredentialType': 'AwsAccessKey'}

    if '_TableName' in result:
        del result['_TableName']

    assert result == expected_result, f"Unexpected data in results {result}"