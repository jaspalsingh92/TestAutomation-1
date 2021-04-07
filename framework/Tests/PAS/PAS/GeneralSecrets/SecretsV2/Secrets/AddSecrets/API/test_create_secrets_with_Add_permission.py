import pytest
import logging
from Shared.API.secret import give_user_permissions_to_folder, create_text_secret_within_folder
logger = logging.getLogger('test')


@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_create_secrets_with_Add_permission(core_session,
                                            users_and_roles,
                                            create_secret_folder,
                                            pas_general_secrets,
                                            cleanup_secrets_and_folders):
    """
        C283792: Users can create secrets at the root or inside a folder if they have Add permission on the folder
    :param core_session: Authenticated Centrify Session
    :param users_and_roles: Fixture to create random user with rights
    :param create_secret_folder: Fixture to create secret folder
    :param pas_general_secrets: Fixture to read secrets data from yaml file
    :param cleanup_secrets_and_folders: Fixture to cleanup the secrets & folders created
    """
    secrets_params = pas_general_secrets
    folder_id = create_secret_folder['ID']
    secrets_list = cleanup_secrets_and_folders[0]

    # Getting new session for UserB with PAS Power User Rights
    pas_power_user_session = users_and_roles.get_session_for_user('Privileged Access Service Power User')
    assert pas_power_user_session.auth_details, 'Failed to Login with PAS Power User'
    user_name = pas_power_user_session.auth_details['User']
    user_id = pas_power_user_session.auth_details['UserId']
    logger.info(f'UserB with PAS Power User Rights login successfully: user_Name: {user_name}')

    # Setting folder permissions(Add, Edit & View) for UserB
    user_permissions_result = give_user_permissions_to_folder(core_session,
                                                              user_name,
                                                              user_id,
                                                              folder_id,
                                                              'View, Add, Edit')
    assert user_permissions_result, f'Failed to set user permissions to folder{user_permissions_result}'
    logger.info(f'User Permissions to folder: {user_permissions_result}')

    # Creating secrets inside folder of UserB
    added_text_secret_success, added_text_secret_result = create_text_secret_within_folder(
        pas_power_user_session,
        secrets_params['secret_name'],
        secrets_params['secret_text'],
        secrets_params['secret_description'],
        folder_id)
    assert added_text_secret_success, f'Failed to create secret in another user\'s folder.{added_text_secret_result}'
    logger.info(f'Secret Created successfully: {added_text_secret_success}')
    logger.info(f'successfully added secret in userB folder with Add permissions: {added_text_secret_result}')
    secrets_list.append(added_text_secret_result)
    logger.info(f'Added Secret deleted successfully: {secrets_list}')
