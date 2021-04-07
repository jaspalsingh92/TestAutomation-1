import logging
import pytest
from Shared.API.secret import set_users_effective_permissions, del_secret

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_need_delete_permission_on_secret_to_be_able_to_delete_it(core_session,
                                                                  added_secrets,
                                                                  added_secrets_file,
                                                                  users_and_roles):
    """
    test method to delete a secret for User A with/without "DELETE" permissions enabled for User A
    1) with "DELETE" member permissions enabled for User A, verify secret should be deleted.
    2) without "DELETE" member permissions enabled for User A, verify secret should not be deleted.
    :param core_session:  Authenticated Centrify Session.
    :param added_secrets: Fixture to add text type secrets & yields secret related details
    :param added_secrets_file: Fixture to add file type secrets & yields secret related details
    :param users_and_roles: Fixture to create New user with PAS Power Rights
    """
    secret_id_list, secret_name = added_secrets
    added_file_secret_id = added_secrets_file
    pas_power_user = users_and_roles.get_user('Privileged Access Service Power User')
    user_name = pas_power_user.get_login_name()
    user_id = pas_power_user.get_id()
    pas_power_user_session = users_and_roles.get_session_for_user('Privileged Access Service Power User')
    assert pas_power_user_session.auth_details, 'Failed to Login with PAS Power User'
    logger.info(f'User with PAS Power User Rights login successfully :user_Name: {user_name}'
                f' & Password: {pas_power_user.get_password()} ')

    # Api to set permissions(DELETE) for User A
    text_type_secret_result, text_type_secret_success = set_users_effective_permissions(core_session,
                                                                                        user_name,
                                                                                        'View,Grant,Delete,Retrieve',
                                                                                        user_id,
                                                                                        secret_id_list[0])
    assert text_type_secret_success, f'Failed to set permissions for text type secret:{text_type_secret_result}'
    logger.info(f'setting permissions for text type secret: {text_type_secret_success}')

    # Api to delete the secret with DELETE permissions
    del_success, del_result = del_secret(pas_power_user_session, secret_id_list[0])
    assert del_success, f'Not Able to delete the child secret: {del_result}'
    logger.info(f'Able to delete the child secret:{del_result}')
    for secret_id in secret_id_list:
        secret_id_list.remove(secret_id)
    logger.info(f'Successfully Deleted secrets with secret name {secret_name}')

    # Api to set permissions(without DELETE) for User A
    text_type_secret_result, text_type_secret_success = set_users_effective_permissions(core_session,
                                                                                        user_name,
                                                                                        'View,Grant,Retrieve',
                                                                                        user_id,
                                                                                        added_file_secret_id)
    assert text_type_secret_success, f'Failed to set permissions for text type secret:{text_type_secret_result}'
    logger.info(f'setting permissions for text type secret: {text_type_secret_success}')

    # Api to delete the secret without DELETE permissions
    del_success, del_result = del_secret(pas_power_user_session, added_file_secret_id)
    assert del_success is False, f'Able to delete the child secret: {del_result}'
    logger.info(f'Able to delete the child secret:{del_result}{del_success}')
