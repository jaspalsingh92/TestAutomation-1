import logging
import pytest
from Shared.API.secret import del_secret, give_user_permissions_to_folder, set_member_permissions_to_folder

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_have_delete_permission_on_parent_should_be_able_to_delete_child_members(core_session,
                                                                                 users_and_roles,
                                                                                 create_secret_inside_folder,
                                                                                 pas_general_secrets):
    """
        C3000: Have delete permission on parent, should be able to delete child members
    :param core_session: Authenticated Centrify Session.
    :param users_and_roles: Fixture to create New user with PAS Power Rights
    :param create_secret_inside_folder: Fixture to create text type secret inside folder &
                                        yields folder & secret details.
    :param pas_general_secrets: Fixture to read secret data from yaml file.
    """
    folder_id_list, folder_name, secret_id_list = create_secret_inside_folder
    pas_power_user = users_and_roles.get_user('Privileged Access Service Power User')
    user_name = pas_power_user.get_login_name()
    user_id = pas_power_user.get_id()

    # Getting new session for User A
    pas_power_user_session = users_and_roles.get_session_for_user('Privileged Access Service Power User')
    assert pas_power_user_session.auth_details is not None, 'Failed to Login with PAS Power User'
    logger.info(f'User with PAS Power User Rights login successfully :user_Name: {user_name}'
                f' & Password: {pas_power_user.get_password()} ')

    # Api to give user permissions to folder
    user_permissions_result = give_user_permissions_to_folder(core_session,
                                                              user_name,
                                                              user_id,
                                                              folder_id_list[0],
                                                              'View,Grant')
    assert user_permissions_result, f'Not Able to set user permissions to folder{user_permissions_result}'
    logger.info(f'User Permissions to folder: {user_permissions_result}')

    # Api to give member permissions(Delete) to folder
    member_perm_result, member_perm_success = set_member_permissions_to_folder(core_session,
                                                                               user_name,
                                                                               'View,Grant,Delete,Retrieve',
                                                                               user_id,
                                                                               folder_id_list[0])
    assert member_perm_success, f'Not Able to set member permissions to Folder{member_perm_result["Result"]}'
    logger.info(f'Member permissions to folder:{member_perm_result}')

    # Api to delete the child secret
    del_success, del_result = del_secret(pas_power_user_session, secret_id_list[0])
    assert del_success, f'Not Able to delete the child secret: {del_result}'
    for secret_id in secret_id_list:
        secret_id_list.remove(secret_id)
    logger.info(f'Able to delete the child secret:{del_result}')
