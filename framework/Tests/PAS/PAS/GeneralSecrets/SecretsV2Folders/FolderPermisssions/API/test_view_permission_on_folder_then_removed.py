import pytest
import logging
from Shared.API.secret import give_user_permissions_to_folder, create_folder, get_secrets_and_folders_in_folders, \
    get_folder
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_view_permission_on_folder_then_removed(core_session,
                                                create_folder_inside_folder,
                                                users_and_roles,
                                                pas_general_secrets,
                                                cleanup_secrets_and_folders):
    """
        C3047: test method to create a multilevel folder
        Case I  1) As an admin disable "View" folder permission for a pas user.
                 2)  Login as pas user & verify Should not be able to view folders
         Case II 1) As an admin enable "View" folder permission for a pas user.
                 2)  Login as pas user & verify Should be able to view folders & sub folders.

    :param core_session: Authenticated Centrify session
    :param create_folder_inside_folder: Fixture to create folder inside folder & yields nested_folder &
                parent_folder details
    :param users_and_roles: Fixture to create random user with PAS User Rights
    :param pas_general_secrets: Fixture to read secrets related data from yaml file
    :param cleanup_secrets_and_folders: Fixture to cleanup the secrets & folders created
    """

    parent_folder_info, nested_folder_info, nested_folder_id = create_folder_inside_folder
    parent_folder_id = parent_folder_info['ID']
    params = pas_general_secrets
    folder_prefix = guid()
    folders_list = cleanup_secrets_and_folders[1]

    child_folder_success, child_folder_parameters, child_folder_id = create_folder(
        core_session,
        folder_prefix + params['nested_folder_name'],
        params['description'],
        parent=nested_folder_id)
    assert child_folder_success, f'Failed to create nested folder: {child_folder_id}'
    logger.info(f'Nested Folder created successfully: {child_folder_success} & details are {child_folder_id}')
    folders_list.insert(0, child_folder_id)

    # API to get new session for User A
    pas_power_user_session = users_and_roles.get_session_for_user('Privileged Access Service User')
    assert pas_power_user_session.auth_details, 'Failed to Login with PAS User'
    user_name = pas_power_user_session.auth_details['User']
    user_id = pas_power_user_session.auth_details['UserId']
    logger.info(f'User with PAS User Rights login successfully: user_Name:{user_name}')

    # Getting details of Parent Folder with PAS User (with View Disabled)
    result_folder = get_folder(pas_power_user_session, parent_folder_id)
    assert result_folder['success'] is False, f'Able to find Parent folder:{result_folder["Message"]}'
    logger.info(f'Unable to find Parent Folder with (View Disabled):{result_folder}')

    # Api to give user permissions to folder(View Enabled)
    user_permissions_result = give_user_permissions_to_folder(core_session, user_name, user_id, parent_folder_id,
                                                              'View')
    assert user_permissions_result['success'], \
        f'Not Able to set user permissions to folder{user_permissions_result["Result"]}'
    logger.info(f'User Permissions to folder: {user_permissions_result}')

    # Api to get pas user nested folder details
    pas_nested_folder = get_secrets_and_folders_in_folders(pas_power_user_session, parent_folder_id)
    pas_nested_folder_id = pas_nested_folder["Result"]["Results"][0]["Row"]["ID"]
    assert pas_nested_folder_id == nested_folder_id, \
        f'Failed to retrieve nested folder with PAS User:{pas_nested_folder_id}'
    logger.info(f'Able to find Nested Folder with (View Enabled):{pas_nested_folder_id}')

    # Api to get pas user child folder details
    pas_child_folder = get_secrets_and_folders_in_folders(pas_power_user_session, nested_folder_id)
    pas_child_folder_id = pas_child_folder["Result"]["Results"][0]["Row"]["ID"]
    assert pas_child_folder_id == child_folder_id, \
        f'Failed to retrieve child folder with PAS User:{pas_child_folder_id}'
    logger.info(f'Able to find child Folder with (View Enabled):{pas_child_folder_id}')
