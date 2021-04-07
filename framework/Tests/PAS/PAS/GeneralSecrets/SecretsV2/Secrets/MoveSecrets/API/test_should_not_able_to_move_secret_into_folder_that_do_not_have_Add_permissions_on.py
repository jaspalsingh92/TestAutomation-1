import logging
import pytest

from Shared.API.secret import set_users_effective_permissions, move_secret, give_user_permissions_to_folder

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_should_not_able_to_move_secret_into_folder_that_do_not_have_add_permissions_on(core_session,
                                                                                        users_and_roles,
                                                                                        added_secrets,
                                                                                        create_secret_folder):
    """
    test method to not able to move a secret(with EDIT permissions) to a folder( with no ADD permissions)
    :param core_session: Authenticated Centrify Session
    :param users_and_roles: Fixture to create New user with PAS Power Rights
    :param added_secrets: Fixture to create text type secret & yield secret id, secret_name
    :param create_secret_folder: Fixture to create secret Folder & yield folder related details
    """
    added_text_secret_id, added_text_secret_name = added_secrets
    secret_folder_details = create_secret_folder
    folder_id = secret_folder_details['ID']
    application_management_user = users_and_roles.get_user('Privileged Access Service Power User')
    user_name = application_management_user.get_login_name()
    user_id = application_management_user.get_id()

    # Api to set Edit permissions to secret
    text_type_secret_result, text_type_secret_success = set_users_effective_permissions(core_session,
                                                                                        user_name,
                                                                                        'View,Grant,Edit',
                                                                                        user_id,
                                                                                        added_text_secret_id[0])
    assert text_type_secret_success, f'setting permissions for text type secret:{text_type_secret_result}'
    logger.info(f'setting permissions for text type secret: : {text_type_secret_success}')

    # Api to set permissions with folder
    permissions = give_user_permissions_to_folder(core_session, user_name, user_id, folder_id, 'View,Grant')
    assert permissions['success'], f'Not able to set permissions to folder:{permissions["Result"]}'
    logger.info(f'Permissions to folder: {permissions}')

    # API to get new session for User A
    application_management_session = users_and_roles.get_session_for_user('Privileged Access Service Power User')
    assert application_management_session.auth_details is not None, 'Failed to Login with PAS Power User'
    logger.info(f'User with PAS Power User Rights login successfully :user_Name: {application_management_user.get_login_name()}'
                f' & Password: {application_management_user.get_password()} ')

    # Api to move secret into Folder
    result_move = move_secret(application_management_session, added_text_secret_id[0], folder_id)
    assert result_move['success'] is False, f'Able to move the secret into Folder: {result_move["Result"]}'
    logger.info(f'Moving secret with edit permissions:{result_move["Message"]}')
