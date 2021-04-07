import logging
import pytest
from Shared.API.secret import give_user_permissions_to_folder, create_folder, update_folder
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_edit_folder_permission_to_update_folder(core_session,
                                                 create_secret_folder,
                                                 pas_general_secrets,
                                                 users_and_roles,
                                                 cleanup_secrets_and_folders):
    """
        C3030:test method to login with cloud admin
        1) Disable Edit folder permission for UserA, Login with User A and verify that "Edit" is not visible
        2) Enable Edit folder permission for UserA, Login with User A and verify that "Edit" is  visible

    :param core_session: Authenticated Centrify session
    :param create_secret_folder: Fixture to create secret inside folder & yields secret & folder details
    :param pas_general_secrets: Fixture to read secrets related data from yaml file
    :param users_and_roles: Fixture to create random user with PAS Power Rights
    :param cleanup_secrets_and_folders: Fixture to cleanup the secrets & folders created

    """
    secret_folder_details = create_secret_folder
    folder_id = secret_folder_details['ID']
    folder_name = secret_folder_details['Name']
    folder_prefix = guid()
    folder_params = pas_general_secrets
    folders_list = cleanup_secrets_and_folders[1]

    # API to get new session for User A
    pas_power_user_session = users_and_roles.get_session_for_user('Privileged Access Service Power User')
    assert pas_power_user_session.auth_details is not None, 'Failed to Login with PAS Power User'
    user_name = pas_power_user_session.auth_details['User']
    user_id = pas_power_user_session.auth_details['UserId']
    logger.info(f'User with PAS Power User Rights login successfully: user_Name: {user_name}')

    # Api to give user permissions to folder(EDIT Disabled)
    user_permissions_result = give_user_permissions_to_folder(core_session, user_name, user_id, folder_id,
                                                              'View')
    assert user_permissions_result, f'Not Able to set user permissions to folder{user_permissions_result}'
    logger.info(f'User Permissions to folder: {user_permissions_result}')

    # Checking EDIT permission is Disabled
    result = update_folder(pas_power_user_session, folder_id,
                           folder_name,
                           folder_params['mfa_folder_name_update'],
                           description=folder_params['mfa_folder_description'])

    assert result['success'] is False, f'Edit is Enabled: {result["Message"]} '
    logger.info(f'Edit is Not Visible: {result["success"]} {result["Message"]}')

    secret_folder_success, secret_folder_parameters, secret_folder_id = create_folder(
        core_session,
        folder_params['name'] + folder_prefix,
        folder_params['description'])
    assert secret_folder_success is True, f'Failed to create a folder{secret_folder_id} '
    logger.info(f' Folder created successfully: {secret_folder_success} & details are {secret_folder_parameters}')
    folders_list.append(secret_folder_id)
    secret_folder_name = secret_folder_parameters['Name']

    # Api to give user permissions to folder(EDIT Enabled)
    user_permissions_result = give_user_permissions_to_folder(core_session,
                                                              user_name,
                                                              user_id,
                                                              secret_folder_id,
                                                              'View,Edit')
    assert user_permissions_result, f'Not Able to set user permissions to folder{user_permissions_result}'
    logger.info(f'User Permissions to folder: {user_permissions_result}')

    # Checking EDIT permission is Enabled
    result = update_folder(pas_power_user_session,
                           secret_folder_id,
                           secret_folder_name,
                           folder_prefix + folder_params['mfa_folder_name_update'],
                           description=folder_params['mfa_folder_description'])
    assert result['success'], f'Edit is not enabled: {result["Message"]} '
    logger.info(f'Edit is Visible: {result["success"]} {result["Message"]}')
