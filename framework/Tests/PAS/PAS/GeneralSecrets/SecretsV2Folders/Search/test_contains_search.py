import logging
import pytest
from Shared.API.secret import create_folder, create_text_secret, get_users_effective_secret_permissions
from Shared.API.sets import SetsManager
from Shared.UI.Centrify.SubSelectors.grids import GridRow, GridRowByGuid
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi_ui
@pytest.mark.bhavna
def test_contains_search(core_session,
                         pas_general_secrets,
                         cleanup_secrets_and_folders,
                         core_admin_ui,
                         users_and_roles):
    """
                C3062: Contains search
    :param core_session: Authenticated Centrify session
    :param pas_general_secrets: Fixture to read secrets data from yaml file
    :param cleanup_secrets_and_folders: Fixture to cleanup the secrets & folders created
    :param core_admin_ui: Fixture to generate browser session
    :param users_and_roles: Fixture to generate random user with restricted rights
    """
    params = pas_general_secrets
    folder_list = cleanup_secrets_and_folders[1]
    secrets_list = cleanup_secrets_and_folders[0]
    suffix = guid()

    # Creating folder
    folder_success, folder_parameters, folder_id = create_folder(core_session,
                                                                 params['name'] + "v1" + suffix,
                                                                 params['description'])
    assert folder_success, f'Failed to create folder, API response result: {folder_id}'
    logger.info(f'Folder created successfully: {folder_id} & details are {folder_parameters}')
    folder_list.append(folder_id)
    folder_name = folder_parameters['Name']

    # Creating secret
    added_secret_success, details, added_secret_id = create_text_secret(core_session,
                                                                        params['secret_name'] + "v1" + suffix,
                                                                        params['secret_text'])
    assert added_secret_success, f"Added Secret Failed, API response result: {added_secret_id}"
    logger.info(f'Added secrets info: {details, added_secret_id}')
    secrets_list.append(added_secret_id)

    ui = core_admin_ui
    ui.navigate('Resources', 'Secrets')
    # Searching for secrets & folder
    ui.search('v1')
    ui.expect(GridRow(folder_name), f' Expect to find folder {folder_name} but could not')
    ui.expect(GridRowByGuid(added_secret_id), f' Expect to find secret with id as {added_secret_id} but could not')

    # Getting permissions of folder
    permissions = SetsManager.get_collection_rights(core_session, folder_id)
    assert permissions["Result"], \
        f'Failed to get permissions for the folder, API response result:{permissions["Result"]}'
    logger.info(f'Permissions of the folder created: {permissions}')

    # Getting permissions of secret
    permissions_secret = get_users_effective_secret_permissions(core_session, added_secret_id)
    assert permissions_secret, \
        f'Failed to get permissions for secret, API response result: {permissions_secret}'
    logger.info(f' Permissions for Secret: {permissions_secret}')
