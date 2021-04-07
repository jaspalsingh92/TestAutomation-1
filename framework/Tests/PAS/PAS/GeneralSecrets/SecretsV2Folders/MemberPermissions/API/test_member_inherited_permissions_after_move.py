import pytest
import logging
from Shared.API.secret import give_user_permissions_to_folder, set_member_permissions_to_folder, move_secret,\
    get_users_effective_secret_permissions

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas_failed
@pytest.mark.bhavna
def test_inherited_permissions_after_move(core_session,
                                          create_secret_inside_folder,
                                          create_secret_folder,
                                          cleanup_secrets_and_folders,
                                          users_and_roles):
    """
            C3058:Inherited permissions after move

    :param core_session: Authenticated Centrify Session
    :param create_secret_inside_folder: Fixture to create secret inside Folder & yields folder & secret related details
    :param create_secret_folder: Fixture to create Folder & yields folder related details
    :param cleanup_secrets_and_folders: Fixture to cleanup the secrets & folder created
    :param users_and_roles: Fixture to create random user
    """
    folder_id_list, folder_name, secret_list = create_secret_inside_folder
    secret_folder_details = create_secret_folder
    folder_id = secret_folder_details['ID']

    # API to get new session for User A
    pas_power_user_session = users_and_roles.get_session_for_user('Privileged Access Service Power User')
    assert pas_power_user_session.auth_details, 'Failed to Login with PAS Power User'
    user_name = pas_power_user_session.auth_details['User']
    user_id = pas_power_user_session.auth_details['UserId']
    logger.info(f'User with PAS Power User Rights login successfully: user_Name: {user_name}')

    # Api to set permissions with folder
    permissions_folder = give_user_permissions_to_folder(core_session,
                                                         user_name,
                                                         user_id,
                                                         folder_id_list[0],
                                                         'View')
    assert permissions_folder['success'], f'Not able to set permissions to folder:{permissions_folder["Result"]}'
    logger.info(f'Permissions to folder: {permissions_folder}')

    # Api to set permissions with folder
    folder_permissions = give_user_permissions_to_folder(core_session,
                                                         user_name, user_id,
                                                         folder_id,
                                                         'View,Add')
    assert folder_permissions['success'], f'Not able to set permissions to folder:{folder_permissions["Result"]}'
    logger.info(f'Permissions to folder: {folder_permissions}')

    # Api to give member permissions to folder
    member_perm_result, member_perm_success = set_member_permissions_to_folder(core_session,
                                                                               user_name,
                                                                               'View,Edit',
                                                                               user_id,
                                                                               folder_id_list[0])
    assert member_perm_success, \
        f'Not Able to set member permissions to Folder, API response result: {member_perm_result}'
    logger.info(f'Member permissions to folder:{member_perm_result}')

    # Api to give member permissions to folder
    member_perm_result, member_perm_success = set_member_permissions_to_folder(core_session,
                                                                               user_name,
                                                                               'View,Edit,Grant,Retrieve,Delete',
                                                                               user_id,
                                                                               folder_id)
    assert member_perm_success, \
        f'Not Able to set member permissions to Folder, API response result: {member_perm_result}'
    logger.info(f'Member permissions to folder:{member_perm_result}')

    # Api to move secret into new Folder
    result_move = move_secret(pas_power_user_session, secret_list[0], folder_id)
    assert result_move['success'], \
        f'Not Able to move secret into new Folder. API response result: {result_move["Result"]}'
    logger.info(f'Able to move the secret into new folder:{result_move["Message"]}')

    # Api to get secret permissions
    get_permission_result = get_users_effective_secret_permissions(core_session, secret_list[0])
    verify_permissions = ['View', 'Edit', 'Delete', 'Grant', 'Retrieve']
    assert get_permission_result == verify_permissions,\
        f'Failed to inherit secret permissions from new parent folder. API response result: {get_permission_result}'
    logger.info(f'Secret permissions are inherited from new parent folder.: {get_permission_result}')
