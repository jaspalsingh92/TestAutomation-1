import pytest
import logging
from Shared.API.secret import create_folder, give_user_permissions_to_folder, get_secret

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_view_on_folders_but_not_members(core_session,
                                         create_secret_inside_folder,
                                         pas_general_secrets,
                                         users_and_roles,
                                         cleanup_secrets_and_folders):

    """
     C3054: test method to View on folders, but not members
        1) create multiple secrets & folders inside parent folder
       2) Login as Admin, set folder permissions "View" for parent folder
       3) Login as pas user
       4) Verify can view folder but not secrets

    :param core_session:  Authenticated Centrify session
    :param create_secret_inside_folder: Fixture to create secret inside folder
    :param pas_general_secrets: Fixture to read secrets related data from yaml file
    :param users_and_roles: Fixture to create random user with PAS User Rights
    :param cleanup_secrets_and_folders: Fixture to cleanup the secrets & folder created
    """
    folder_id_list, folder_name, secret_id = create_secret_inside_folder
    folders_list = cleanup_secrets_and_folders[1]
    params = pas_general_secrets

    # creating nested folder
    child_folder_success, child_folder_parameters, child_folder_id = create_folder(
        core_session,
        params['name'],
        params['description'],
        parent=folder_id_list[0]
    )
    assert child_folder_success, f'Failed to create nested folder, API response result: {child_folder_id}'
    logger.info(f'Nested Folder created successfully, details are: {child_folder_parameters}')
    folders_list.insert(0, child_folder_id)

    # API to get new session for User A
    pas_power_user_session = users_and_roles.get_session_for_user('Privileged Access Service User')
    assert pas_power_user_session.auth_details, 'Failed to Login with PAS User'
    user_name = pas_power_user_session.auth_details['User']
    user_id = pas_power_user_session.auth_details['UserId']
    logger.info(f'User with PAS User Rights login successfully: user_Name:{user_name}')

    # Api to give user permissions to parent folder
    user_permissions_alpha = give_user_permissions_to_folder(core_session,
                                                             user_name,
                                                             user_id,
                                                             folder_id_list[1],
                                                             'View')
    assert user_permissions_alpha['success'], \
        f'Not Able to set user permissions to folder, API response result:{user_permissions_alpha["Result"]}'
    logger.info(f'User Permissions to folder: {user_permissions_alpha}')

    # Getting the secret for pas user should fail
    found_secret = get_secret(pas_power_user_session, secret_id[0])
    verify_msg = 'You are not authorized to perform this operation.'
    assert found_secret['success'] is False and verify_msg in found_secret["Message"], \
        f'Able to find the secret without view permissions, API response result:{found_secret["Message"]}'
    logger.info(f'Not able to find th secret with pas user: {found_secret["Message"]}')
