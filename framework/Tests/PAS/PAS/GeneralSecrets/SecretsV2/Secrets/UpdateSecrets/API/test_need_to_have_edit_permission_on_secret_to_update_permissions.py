import pytest
import logging
from Shared.API.secret import set_users_effective_permissions, get_users_effective_secret_permissions

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_need_to_have_edit_permission_on_secret_to_update_permissions_case(core_session, users_and_roles,
                                                                           added_secrets_file,
                                                                           added_secrets,
                                                                           pas_general_secrets):
    """
     test method to create 2 secrets with and without edit permissions for UserA & verify the permissions for User A
    """
    added_file_secret_id = added_secrets_file
    added_text_secret_id, added_text_secret_name = added_secrets
    application_management_user = users_and_roles.get_user('Privileged Access Service Power User')
    user_name = application_management_user.get_login_name()
    user_id = application_management_user.get_id()

    """API to set user permissions for file_type_secret"""
    file_type_secret_result, file_type_secret_success = set_users_effective_permissions(core_session,
                                                                                        user_name,
                                                                                        'View,Grant,Edit',
                                                                                        user_id,
                                                                                        added_file_secret_id)
    assert file_type_secret_success, f'setting permissions for file type secret failed: {file_type_secret_result}'
    logger.info(f'setting permissions for file type secret: {file_type_secret_success}')

    """API to set user permissions for text_type_secret"""
    text_type_secret_result, text_type_secret_success = set_users_effective_permissions(core_session,
                                                                                        user_name,
                                                                                        'View,Grant',
                                                                                        user_id,
                                                                                        added_text_secret_id[0])
    assert text_type_secret_success, f'setting permissions for text type secret:{text_type_secret_result}'
    logger.info(f'setting permissions for text type secret: : {text_type_secret_success}')

    """API to get new session for User A"""
    application_management_session = users_and_roles.get_session_for_user('Privileged Access Service Power User')
    assert application_management_session.auth_details is not None, 'Failed to Login with PAS Power User'
    logger.info(f'User with PAS Power User Rights login successfully :user_Name: {user_name}'
                f' & Password: {application_management_user.get_password()} ')

    """API to get "Edit" secret permissions for User A """
    get_permission_result = get_users_effective_secret_permissions(application_management_session, added_file_secret_id)
    assert "Edit" in f'{get_permission_result}', f'verification failed for file type secret{get_permission_result}'
    logger.info(f' Get permission for file type Secret: {get_permission_result}')

    """API to get secret permissions(without Edit for User A)"""
    get_text_permission_result = get_users_effective_secret_permissions(application_management_session,
                                                                        added_text_secret_id[0])
    assert "Edit" not in f'{get_text_permission_result}', \
        f'verification failed for Text type secret{get_text_permission_result}'
    logger.info(f'Get permission for text type Secret: {get_text_permission_result}')
