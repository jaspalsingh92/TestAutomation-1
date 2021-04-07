import logging
import pytest
from Shared.API.secret import move_secret, give_user_permissions_to_folder, set_member_permissions_to_folder, \
    create_folder
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_move_secret_to_different_folder_with_member_permission_edit_on_source_folder_for_user_a(
        core_session,
        users_and_roles,
        create_secret_inside_folder,
        pas_general_secrets,
        cleanup_secrets_and_folders):
    """
    test method to move a secret to another folder with "EDIT" member permissions on source folder for User A
    :param core_session: Authenticated Centrify Session.
    :param users_and_roles: Fixture to create New user with PAS Power Rights
    :param create_secret_inside_folder: Fixture to create text type secret inside folder &
    yields folder & secret details.
    :param pas_general_secrets: Fixture to read secret data from yaml file.
    :param cleanup_secrets_and_folders: Fixture to cleanup the secrets & folders created.
    """
    folder_id_list, folder_name, secret_id_list = create_secret_inside_folder
    folders_list = cleanup_secrets_and_folders[1]
    params = pas_general_secrets
    prefix = guid()
    pas_power_user = users_and_roles.get_user('Privileged Access Service Power User')
    user_name = pas_power_user.get_login_name()
    user_id = pas_power_user.get_id()

    # API to get new session for User A
    pas_power_user_session = users_and_roles.get_session_for_user('Privileged Access Service Power User')
    assert pas_power_user_session.auth_details is not None, 'Failed to Login with PAS Power User'
    logger.info(f'User with PAS Power User Rights login successfully :user_Name: {user_name}'
                f' & Password: {pas_power_user.get_password()} ')

    # Api to give user permissions to folder
    user_permissions_result = give_user_permissions_to_folder(core_session, user_name, user_id, folder_id_list[0],
                                                              'View,Grant')
    assert user_permissions_result, f'Not Able to set user permissions to folder{user_permissions_result}'
    logger.info(f'User Permissions to folder: {user_permissions_result}')

    # Api to give member permissions to folder
    member_perm_result, member_perm_success = set_member_permissions_to_folder(core_session,
                                                                               user_name,
                                                                               'View,Grant,Edit',
                                                                               user_id,
                                                                               folder_id_list[0])
    assert member_perm_success, f'Not Able to set member permissions to Folder{member_perm_result["Result"]}'
    logger.info(f'Member permissions to folder:{member_perm_result}')

    # Api to create secret folder for User A
    secret_folder_success, secret_folder_parameters, secret_folder_id = create_folder(pas_power_user_session,
                                                                                      prefix + params['name'],
                                                                                      params['description'])

    logger.info(f' Folder created successfully: {secret_folder_success} & details are {secret_folder_parameters}')
    assert secret_folder_success is True, f'Failed to create a folder {secret_folder_id}'
    folders_list.append(secret_folder_id)

    # Api to move secret into another Folder
    result_move = move_secret(pas_power_user_session, secret_id_list[0], secret_folder_id)
    assert result_move['success'], f'Not Able to move the secret into Folder: {result_move["Result"]}'
    logger.info(f'Moving secret with edit permissions to another folder:{result_move}')
