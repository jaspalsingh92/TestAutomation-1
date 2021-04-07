import pytest
import logging
from Shared.API.secret import give_user_permissions_to_folder, create_text_secret_within_folder

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_user_cannot_create_secret_without_add_permission(core_session, users_and_roles,
                                                          create_secret_folder, pas_general_secrets):
    """
     test method user cannot create secret in the folder without add permission
    """

    application_management_user = users_and_roles.get_user('Privileged Access Service Power User')
    application_management_session = users_and_roles.get_session_for_user('Privileged Access Service Power User')
    user_name = application_management_user.get_login_name()
    user_id = application_management_user.get_id()
    folder_id = create_secret_folder['ID']
    assert application_management_session.auth_details is not None, 'Failed to Login with PAS Power User'
    logger.info(f'User with PAS Power User Rights login successfully :user_Name: {application_management_user.get_login_name()}'
                f' & Password: {application_management_user.get_password()} ')

    give_user_permissions_to_folder(core_session, user_name, user_id, folder_id, 'View')
    secrets_params = pas_general_secrets

    added_text_secret_success, added_text_secret_result = create_text_secret_within_folder(
        application_management_session,
        secrets_params['secret_name'],
        secrets_params['secret_text'],
        secrets_params['secret_description'],
        folder_id)
    assert added_text_secret_success is False, \
        f'Able to create a secret in another user\'s folder. {added_text_secret_result}'
    logger.info(f'Secret Created successfully: {added_text_secret_success}')
    logger.info(
        f'Creating secret in other user folder with no Add permissions: {added_text_secret_success}')
