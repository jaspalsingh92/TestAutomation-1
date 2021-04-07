import logging
import pytest
from Shared.API.secret import move_secret, give_user_permissions_to_folder, create_text_secret_within_folder, \
    set_member_permissions_to_folder, create_folder
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_move_secret_without_edit_member_permission_on_source_folder_should_not_be_allowed(core_session,
                                                                                           users_and_roles,
                                                                                           create_secret_folder,
                                                                                           pas_general_secrets,
                                                                                           cleanup_secrets_and_folders):
    """
    test method to move a secret to another folder without "EDIT" member permissions & Folder permissions
    on source folder for User A should not be allowed
    :param core_session: Authenticated Centrify Session.
    :param users_and_roles: Fixture to create New user with PAS Power Rights
    :param create_secret_folder: Fixture to create secret folder & yields folder details.
    :param pas_general_secrets: Fixture to read secret data from yaml file.
    :param cleanup_secrets_and_folders: Fixture to cleanup the secrets & folders created.
    """
    secret_folder_details = create_secret_folder
    secret_list = cleanup_secrets_and_folders[0]
    folders_list = cleanup_secrets_and_folders[1]
    params = pas_general_secrets
    prefix = guid()
    folder_id = secret_folder_details['ID']
    pas_power_user = users_and_roles.get_user('Privileged Access Service Power User')
    user_name = pas_power_user.get_login_name()
    user_id = pas_power_user.get_id()

    # Api to create text type secret within folder
    added_text_secret_success, added_text_secret_result = create_text_secret_within_folder(core_session,
                                                                                           prefix + params[
                                                                                               'secret_name'],
                                                                                           params['secret_text'],
                                                                                           params['secret_description'],
                                                                                           folder_id)
    assert added_text_secret_success, f'Unable to create secret {added_text_secret_result}'
    logger.info(f'Secret Created successfully: {added_text_secret_success}')
    secret_list.append(added_text_secret_result)

    # API to get new session for User A
    pas_power_user_session = users_and_roles.get_session_for_user('Privileged Access Service Power User')
    assert pas_power_user_session.auth_details, 'Failed to Login with PAS Power User'
    logger.info(f'User with PAS Power User Rights login successfully :user_Name: {user_name}'
                f' & Password: {pas_power_user.get_password()} ')

    # Api to give user permissions to folder(without EDIT)
    user_permissions_result = give_user_permissions_to_folder(core_session, user_name, user_id, folder_id, 'View,Grant')
    assert user_permissions_result, f'Not Able to set user permissions to folder{user_permissions_result}'
    logger.info(f'User Permissions to folder: {user_permissions_result}')

    # Api to give member permissions to folder(without EDIT)
    member_perm_result, member_perm_success = set_member_permissions_to_folder(core_session,
                                                                               user_name,
                                                                               'View,Grant',
                                                                               user_id,
                                                                               folder_id)
    assert member_perm_success, f'Not Able to set member permissions to Folder{member_perm_result["Result"]}'
    logger.info(f'Member permissions to folder:{member_perm_result}')

    # Api to create secret folder for User A
    secret_folder_success, secret_folder_parameters, secret_folder_id = create_folder(pas_power_user_session,
                                                                                      prefix + params['name'],
                                                                                      params['description'])
    assert secret_folder_success, f'Failed to create a folder:{secret_folder_id}'
    logger.info(f' Folder created successfully: {secret_folder_success} & details are {secret_folder_id}')
    folders_list.append(secret_folder_id)

    # Api to move secret into another Folder
    result_move = move_secret(pas_power_user_session, added_text_secret_result, secret_folder_id)
    assert result_move['success'] is False, f'Able to move the secret into Folder: {result_move["Result"]}'
    logger.info(f'Not Able to move the secret into another folder without Edit permissions:{result_move["Message"]}')
