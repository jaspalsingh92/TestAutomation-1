import pytest
import logging
from Shared.API.secret import create_folder, set_member_permissions_to_folder, get_secret

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_view_on_members_but_not_on_folders(core_session,
                                            create_secret_inside_folder,
                                            pas_general_secrets,
                                            users_and_roles,
                                            cleanup_secrets_and_folders):
    """
     C3055: test method to View on members but not on folders
        1) create multiple secrets & folders inside parent folder
       2) Login as Admin, set member permissions "View" for parent folder
       3) Login as pas user
       4) Verify can view secrets but not folders

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

    # API to get new session for User with pas user Rights
    pas_power_user_session = users_and_roles.get_session_for_user('Privileged Access Service User')
    assert pas_power_user_session.auth_details, 'Failed to Login with PAS User'
    user_name = pas_power_user_session.auth_details['User']
    user_id = pas_power_user_session.auth_details['UserId']
    logger.info(f'User with PAS User Rights login successfully: user_Name:{user_name}')

    # Api to give member permissions(View) to folder
    member_perm_result, member_perm_success = set_member_permissions_to_folder(core_session,
                                                                               user_name,
                                                                               'View',
                                                                               user_id,
                                                                               folder_id_list[1])
    assert member_perm_success, \
        f'Not Able to set "View" member permissions to Folder, API response result: {member_perm_result["Result"]}'
    logger.info(f'Member permissions to folder:{member_perm_result}')

    # Getting the secret for pas user should pass
    found_secret = get_secret(pas_power_user_session, secret_id[0])
    assert found_secret['success'], \
        f'Unable to find the secret for pas user, API response result:{found_secret["Message"]}'
    logger.info(f'Able to find the secret for pas user: {found_secret}')
