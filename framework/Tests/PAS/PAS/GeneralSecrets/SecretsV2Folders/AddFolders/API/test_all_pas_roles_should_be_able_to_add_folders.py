import logging
import pytest
from Shared.API.secret import create_folder, get_users_effective_folder_permissions
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.parametrize('administrative_right', ['Privileged Access Service Power User',
                                                  'Privileged Access Service Administrator',
                                                  'Privileged Access Service User'])
@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_all_pas_roles_should_be_able_to_add_folders(core_session,
                                                     pas_general_secrets,
                                                     cleanup_secrets_and_folders,
                                                     users_and_roles,
                                                     administrative_right):
    """
        test method to
        1) create folder with PAS Power User should work & verify sys_adm has Grant, View, Edit, and delete
        permissions for same folder
        2) create folder with PAS Admin User should work & verify sys_adm has Grant, View, Edit, and delete
        permissions for same folder
        3)create folder with PAS  User should work & verify sys_adm has Grant, View, Edit, and delete
        permissions for same folder
    :param core_session: Authenticated Centrify Session
    :param pas_general_secrets:  Fixture to read secret data from yaml file
    :param cleanup_secrets_and_folders: Fixture to cleanup the secrets & folder created
    :param users_and_roles: Fixture to create a random user with PAS Power Rights

    """
    folder_params = pas_general_secrets
    folders_list = cleanup_secrets_and_folders[1]
    folder_prefix = guid()

    # API to get new session for User A
    pas_power_user_session = users_and_roles.get_session_for_user(administrative_right)
    assert pas_power_user_session.auth_details, f'Failed to Login with {administrative_right}'
    logger.info(f'{pas_power_user_session}')

    # Creating Folder with all PAS Roles
    folder_success, folder_parameters, folder_id = create_folder(pas_power_user_session,
                                                                 folder_prefix + folder_params['name'],
                                                                 folder_params['description'])
    folders_list.append(folder_id)
    assert folder_success, f'Failed to create Folder with {administrative_right}:{folder_id}'
    logger.info(f'Creating Folder with {administrative_right} : {folder_success}')

    # Getting permissions of the Folder Created
    permissions = get_users_effective_folder_permissions(pas_power_user_session, folder_id)
    verify_permissions = ['View', 'Edit', 'Delete', 'Grant', 'Add']
    assert permissions == verify_permissions, f'Failed to verify {administrative_right} permissions:{permissions}'
    logger.info(f'Permissions for the Folder created:{permissions}')
