import logging
import pytest
from Shared.API.secret import give_user_permissions_to_folder, del_folder

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_delete_permission_on_folder_you_can_delete_folder(core_session,
                                                           create_secret_folder,
                                                           users_and_roles,
                                                           cleanup_secrets_and_folders):
    """
        C3043: test method to Login as cloud admin
        1) Disable "Delete" permission on a folder for UserA Then Login as UserA
         verify Delete is unavailable for that folder
        2) Enable "Delete" permission on a folder for UserA Then Login as UserA
         verify Delete is available & successful for that folder

    :param core_session: Authenticated Centrify session
    :param create_secret_folder: Fixture to create secret inside folder & yields secret & folder details
    :param users_and_roles: Fixture to create random user with PAS Power Rights
    :param cleanup_secrets_and_folders: Fixture to cleanup the secrets & folders created

    """
    secret_folder_details = create_secret_folder
    folder_id = secret_folder_details['ID']
    folders_list = cleanup_secrets_and_folders[1]

    # API to get new session for User A
    pas_power_user_session = users_and_roles.get_session_for_user('Privileged Access Service Power User')
    assert pas_power_user_session.auth_details, 'Failed to Login with PAS Power User'
    user_name = pas_power_user_session.auth_details['User']
    user_id = pas_power_user_session.auth_details['UserId']
    logger.info(f'User with PAS Power User Rights login successfully: user_Name: {user_name}')

    # Api to give user permissions to folder(DELETE Disabled)
    user_permissions_result = give_user_permissions_to_folder(core_session, user_name, user_id, folder_id,
                                                              'View')
    assert user_permissions_result, f'Not Able to set user permissions to folder{user_permissions_result}'
    logger.info(f'User Permissions to folder: {user_permissions_result}')

    # Delete folder for User A should fail
    del_result = del_folder(pas_power_user_session, folder_id)
    assert del_result['success'] is False, f'Able to delete the folder:{del_result["Result"]}'
    logger.info(f'Failed to delete the folder(DELETE Disabled):{del_result}')

    # Api to give user permissions to folder(DELETE Enabled)
    user_permissions_result = give_user_permissions_to_folder(core_session, user_name, user_id, folder_id,
                                                              'View,Delete')
    assert user_permissions_result, f'Not Able to set user permissions to folder: {user_permissions_result}'
    logger.info(f'User Permissions to folder: {user_permissions_result}')

    # Delete folder for User A should pass
    del_result = del_folder(pas_power_user_session, folder_id)
    assert del_result["success"], f'Failed to delete the folder(DELETE): {del_result["Result"]}'
    logger.info(f'Deleting the folder successfully (DELETE):{del_result}')
    folders_list.remove(folder_id)
