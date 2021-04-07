import pytest
import logging

from Shared.endpoint_manager import EndPoints

pytestmark = [pytest.mark.api, pytest.mark.cloudprovider, pytest.mark.aws, pytest.mark.favorites]


logger = logging.getLogger('test')


def _add_and_check_favorite(core_session, entity_id):
    response = core_session.post(EndPoints.SYSTEM_ADD_TO_FAVORITES, {
        'favorites': [entity_id]
    }).json()
    assert response['success'] is True, f'Failed to add cloud provider as a favorite {response}'

    response = core_session.post(EndPoints.SYSTEM_GET_FAVORITES, {'RRFormat': True}).json()
    assert response['success'] is True, f'Failed to retrieve favorites {response}'
    logger.info(f'{response}')
    assert response['Result']['Count'] > 0, f'No favorites found after adding cloud provider as favorite {response}'

    entity_found = False
    favorite_data = None

    for favorite in response['Result']['Results']:
        if favorite['Row']['ID'] == entity_id:
            entity_found = True
            favorite_data = favorite['Row']

    assert entity_found is True, f'Get favorites did not contain the favorite that was just added. {response}'
    return favorite_data


def test_favorite_cloud_provider(core_session, fake_cloud_provider, cloud_provider_type):
    name, desc, cloud_provider_id, cloud_account_id, _test_deleted = fake_cloud_provider
    favorite = _add_and_check_favorite(core_session, cloud_provider_id)
    assert favorite['CloudAccountId'] == cloud_account_id, f'Favorite data contains the wrong cloud account ID for cloud provider'
    assert favorite['Type'] == 'Cloud Provider', f'Favorite data contains the wrong cloud account ID for cloud provider'
    assert favorite['CloudProviderType'] == cloud_provider_type.value, f'Favorite data contains wrong cloud provider type'
    assert favorite['Name'] == name, f'Favorite data contains wrong cloud provider name'


def test_favorite_root_account(core_session, live_aws_cloud_provider_and_accounts, cloud_provider_type, aws_root_user_credentials):
    cloud_provider_ids, iam_account_ids, access_key_ids, root_account_id, cloud_provider_name = live_aws_cloud_provider_and_accounts
    username, password = aws_root_user_credentials
    favorite = _add_and_check_favorite(core_session, root_account_id)
    assert favorite['CloudProviderId'] == cloud_provider_ids[0], f'Favorite data contains the wrong cloud provider ID for the root user'
    assert favorite['Type'] == 'Cloud Provider Account', f'Favorite data contains the wrong Type value for a root account favorite'
    assert favorite['CloudProviderType'] == cloud_provider_type.value, f'Favorite data contains wrong cloud provider type'
    assert favorite['Name'] == username, f'Favorite data contains wrong cloud provider name'
    assert favorite['IsRootAccount'] is True, f'Favorite data does not specify it is a root account'
    assert favorite['CredentialType'] == 'Password', f'Favorite data does not specify a root account has a password credential type'


def test_favorite_iam_user(core_session, live_aws_cloud_provider_and_accounts, cloud_provider_type):
    cloud_provider_ids, iam_account_ids, access_key_ids, root_account_id, cloud_provider_name = live_aws_cloud_provider_and_accounts

    iam_user_favorites = []
    for iam_user_account_id in iam_account_ids:
        iam_user_favorites.append(_add_and_check_favorite(core_session, iam_user_account_id))

    for favorite, iam_user_account_id in zip(iam_user_favorites, iam_account_ids):
        assert favorite['CloudProviderId'] == cloud_provider_ids[0], f'Favorite data contains the wrong cloud account ID for cloud provider'
        assert favorite['Type'] == 'Cloud Provider Account', f'Favorite data contains the wrong cloud account ID for cloud provider'
        assert favorite['CloudProviderType'] == cloud_provider_type.value, f'Favorite data contains wrong cloud provider type'
        assert favorite['IsRootAccount'] is False, f'Favorite data does not specify iam user is not a root account'
        assert favorite['CredentialType'] == 'AwsAccessKey', f'Favorite data does not specify an iam user account has a aws access key credential type'