import logging
import pytest
from Shared.API.secret import give_user_permissions_to_folder, del_folder

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_delete_folder_with_child(core_session,
                                  create_folder_inside_folder,
                                  users_and_roles,
                                  cleanup_secrets_and_folders):
    """
        C30821: test method to Login as cloud admin
        1) Enable "Delete" folder permissions on a folder for UserA
        2) Login as UserA
        3) Verify you cannot delete folder with a child inside it

    :param core_session: Authenticated Centrify session
    :param create_folder_inside_folder: Fixture to create folder inside folder & yields nested_folder &
    parent_folder details
    :param users_and_roles: Fixture to create random user with PAS Power Rights
    :param cleanup_secrets_and_folders: Fixture to cleanup the secrets & folders created

    """
    parent_folder_info, nested_folder_info, nested_folder_id = create_folder_inside_folder
    parent_folder_id = parent_folder_info['ID']

    # API to get new session for User A
    pas_power_user_session = users_and_roles.get_session_for_user('Privileged Access Service Power User')
    assert pas_power_user_session.auth_details, 'Failed to Login with PAS Power User'
    user_name = pas_power_user_session.auth_details['User']
    user_id = pas_power_user_session.auth_details['UserId']
    logger.info(f'User with PAS Power User Rights login successfully: user_Name: {user_name}')

    # Api to give user permissions to folder(DELETE Enabled)
    user_permissions_result = give_user_permissions_to_folder(core_session, user_name, user_id, parent_folder_id,
                                                              'View,Delete')
    assert user_permissions_result['success'], \
        f'Not Able to set user permissions to folder{user_permissions_result["Result"]}'
    logger.info(f'User Permissions to folder: {user_permissions_result}')

    # Delete parent folder with child for User A should fail
    del_result = del_folder(pas_power_user_session, parent_folder_id)
    assert del_result['success'] is False, f'Failed to delete Sub folder:{del_result["Message"]}'
    logger.info(f'Able to delete Sub folder:{del_result}')
