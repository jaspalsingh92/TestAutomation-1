import logging
import pytest
from Shared.API.secret import give_user_permissions_to_folder, create_folder, move_folder
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas_failed
@pytest.mark.bhavna
def test_edit_permission_on_source_to_move_folder(core_session,
                                                  users_and_roles,
                                                  create_secret_folder,
                                                  pas_general_secrets,
                                                  cleanup_secrets_and_folders):
    """
      C3034: test method to Login as Cloud Admin
      1) Enable "Edit" permission on a folder for UserA Then Login as UserA
         Move folder for User A & verify the move is successful
        2) Disable "Edit" permission on a folder for UserA Then Login as UserA
           Move folder for User A & verify the move is unavailable & unsuccessful
    :param core_session: Authenticated Centrify Session
    :param users_and_roles: Fixture to create New user with PAS Power Rights
    :param create_secret_folder: Fixture to create secret Folder & yield folder related details
    :param pas_general_secrets: Fixture to read secrets related data from yaml file
    :param cleanup_secrets_and_folders: Fixture to cleanup the secrets & folders created.
    """

    folders_list = cleanup_secrets_and_folders[1]
    secret_folder_details = create_secret_folder
    folder_id = secret_folder_details['ID']
    folder_params = pas_general_secrets
    folder_prefix = guid()

    # API to get new session for User A
    pas_power_user_session = users_and_roles.get_session_for_user('Privileged Access Service Power User')
    assert pas_power_user_session.auth_details is not None, 'Failed to Login with PAS Power User'
    user_name = pas_power_user_session.auth_details['User']
    user_id = pas_power_user_session.auth_details['UserId']
    logger.info(f'User with PAS Power User Rights login successfully: user_Name: {user_name}')

    # Api to set permissions with folder(without EDIT)
    permissions = give_user_permissions_to_folder(core_session, user_name, user_id, folder_id, 'View')
    assert permissions['success'], f'Not able to set permissions to folder:{permissions["Result"]}'
    logger.info(f'Permissions to folder: {permissions}')

    # Creating new folder with pas_power_user_session
    secret_folder_success, secret_folder_parameters, secret_folder_id = create_folder(
        pas_power_user_session,
        folder_params['name'] + folder_prefix,
        folder_params['description'])
    assert secret_folder_success, f'Failed to create a folder{secret_folder_id} '
    logger.info(f'Folder created for pas_power_user_session: {secret_folder_success}')
    folders_list.append(secret_folder_id)

    # Api to move Folder should Fail
    result_move = move_folder(pas_power_user_session, folder_id, secret_folder_id)
    assert result_move['success'] is False, f'Able to move the Folder: {result_move["Result"]}'
    logger.info(f'Failed to Move the Folder :{result_move["Message"]}')

    # Api to set permissions with folder(with EDIT)
    permissions = give_user_permissions_to_folder(core_session, user_name, user_id, folder_id, 'View,Edit')
    assert permissions['success'], f'Not able to set permissions to folder:{permissions["Result"]}'
    logger.info(f'Permissions to folder: {permissions}')

    # Api to move Folder should pass
    result_move = move_folder(pas_power_user_session, folder_id, secret_folder_id)
    assert result_move['success'], f'Not Able to move the folder: {result_move["Result"]}'
    logger.info(f'Folder Moved successfully :{result_move["Message"]}')
