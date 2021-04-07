import logging
import pytest
from Shared.API.secret import del_secret, give_user_permissions_to_folder, set_users_effective_permissions

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_delete_permission_on_secret_but_not_on_folder(core_session,
                                                       create_secret_inside_folder,
                                                       users_and_roles):
    """
        test method to Delete permission on secret but not on folder
    :param core_session: Authenticated Centrify Session.
    :param create_secret_inside_folder: Fixture to create text type secret inside folder &
                                        yields folder id , folder name & secret id
    :param users_and_roles: Fixture to create New user with PAS Power Rights
    """
    folder_id_list, folder_name, secret_id_list = create_secret_inside_folder
    pas_power_user = users_and_roles.get_user('Privileged Access Service Power User')
    user_name = pas_power_user.get_login_name()
    user_id = pas_power_user.get_id()
    pas_power_user_session = users_and_roles.get_session_for_user('Privileged Access Service Power User')
    assert pas_power_user_session.auth_details is not None, 'Failed to Login with PAS Power User'
    logger.info(f'User with PAS Power User Rights login successfully :user_Name: {user_name}'
                f' & Password: {pas_power_user.get_password()} ')

    # Api to give user permissions to folder
    user_permissions_result = give_user_permissions_to_folder(core_session,
                                                              user_name,
                                                              user_id,
                                                              folder_id_list[0],
                                                              'View')
    assert user_permissions_result, f'Not Able to set user permissions to folder{user_permissions_result}'
    logger.info(f'User Permissions to folder: {user_permissions_result}')

    # Api to set DELETE permissions to secret
    text_type_secret_result, text_type_secret_success = set_users_effective_permissions(core_session,
                                                                                        user_name,
                                                                                        'View,Delete,Retrieve',
                                                                                        user_id,
                                                                                        secret_id_list[0])
    assert text_type_secret_success, f'Failed to Set Member permissions to secret:{text_type_secret_result}'
    logger.info(f'Setting Member permissions for secret: {text_type_secret_success}')

    # Api to delete the child secret
    del_success, del_result = del_secret(pas_power_user_session, secret_id_list[0])
    assert del_success, f'Not Able to delete the child secret: {del_result}'
    secret_id_list.remove(secret_id_list[0])
    logger.info(f'Able to delete the child secret: {del_result}')
