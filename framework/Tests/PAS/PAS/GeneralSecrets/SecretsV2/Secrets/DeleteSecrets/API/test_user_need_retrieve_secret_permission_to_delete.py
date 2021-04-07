import logging
import pytest
from Utils.guid import guid
from Shared.API.secret import set_member_permissions_to_folder, give_user_permissions_to_folder, create_folder, \
    create_text_secret_within_folder, retrieve_secret, del_secret

logger = logging.getLogger('test')


@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_user_need_retrieve_secret_permission_to_delete(

        core_session,
        pas_general_secrets,
        cleanup_secrets_and_folders,
        users_and_roles):
    """
         C283961: User needs Retrieve Secret permission to retrieve secret contents

    :param core_session:  Authenticated Centrify Session
    :param users_and_roles: Fixture to create random user with pas user rights
    :param cleanup_secrets_and_folders: Fixture to cleanup the secrets & folders created.
    :param pas_general_secrets: Fixture to read secrets data from yaml file

    """

    folder_params = pas_general_secrets
    folder_prefix = guid()
    folders_list = cleanup_secrets_and_folders[1]

    secret_folder_success, secret_folder_parameters, secret_folder_id = create_folder(
        core_session,
        folder_params['name'] + folder_prefix,
        folder_params['description'])
    assert secret_folder_success, f'Failed to create a folder{secret_folder_id} '
    logger.info(f' Folder created successfully: {secret_folder_success} & details are {secret_folder_parameters}')
    folders_list.append(secret_folder_id)
    added_text_secret_success, added_text_secret_result = create_text_secret_within_folder(
        core_session, folder_prefix + folder_params['secret_name'], folder_params['secret_text'],
        folder_params['secret_description'], secret_folder_id)

    logger.info(f'Secret Created successfully: {added_text_secret_success}')
    assert added_text_secret_success, f'Unable to create secret {added_text_secret_result}'

    # API to get new session for User A
    pas_power_user_session = users_and_roles.get_session_for_user('Privileged Access Service Power User')
    assert pas_power_user_session.auth_details, 'Failed to Login with PAS User'
    user_name = pas_power_user_session.auth_details['User']
    user_id = pas_power_user_session.auth_details['UserId']
    logger.info(f'{pas_power_user_session.auth_details}')
    logger.info(f'User with PAS User Rights login successfully: user_Name:{user_name}')

    # Api to give user permissions to folder
    user_permissions = give_user_permissions_to_folder(core_session, user_name, user_id, secret_folder_id,
                                                       'View')
    assert user_permissions['success'], \
        f'Not Able to set user permissions to folder{user_permissions["Result"]}'
    logger.info(f'User Permissions to folder: {user_permissions}')

    # Api to disable member permissions Retrieve in folder
    member_perm_result, member_perm_success = set_member_permissions_to_folder(core_session,
                                                                               user_name,
                                                                               'View,Delete',
                                                                               user_id,
                                                                               secret_folder_id)
    assert member_perm_success, f'Not Able to set member permissions to Folder: {member_perm_result}'
    logger.info(f'Member permissions to folder:{member_perm_result}')

    # Deleting secret without Retrieve permission in folder.
    retrieve_success, retrieve_result, retrieve_message = retrieve_secret(pas_power_user_session,
                                                                          added_text_secret_result)
    assert retrieve_success is False, f'Users {user_name} have permission to retrieve the secret: {retrieve_result}'
    logger.info(f'No longer to delete as you have "Retrieve" '
                f'permission which is required prior to delete:{retrieve_message}')

    # Api to give member permissions to folder
    member_perm_result, member_perm_success = set_member_permissions_to_folder(core_session,
                                                                               user_name,
                                                                               'View,Delete,Retrieve',
                                                                               user_id,
                                                                               secret_folder_id)
    assert member_perm_success, f'Not Able to set member permissions to Folder: {member_perm_result}'
    logger.info(f'Member permissions to folder:{member_perm_result}')

    del_success, del_result = del_secret(pas_power_user_session, added_text_secret_result)
    assert del_success, f'Not Able to delete the child secret: {del_result}'
    logger.info(f'Secret is Successfully deleted:{del_result}')
