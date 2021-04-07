import pytest
import logging
from Shared.API.secret import create_folder, give_user_permissions_to_folder, move_folder
from Shared.API.sets import SetsManager
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas_failed
@pytest.mark.bhavna
def test_inherited_folder_permissions_should_be_removed_if_you_move_away_from_parent(core_session,
                                                                                     create_folder_inside_folder,
                                                                                     pas_general_secrets,
                                                                                     cleanup_secrets_and_folders,
                                                                                     users_and_roles):
    """
              C3052: Inherited folder permissions should be removed if you move away from parent
    :param core_session: Authenticated Centrify Session
    :param create_folder_inside_folder: Fixture to create folder inside parent folder
    :param pas_general_secrets: Fixture to read secret data from yaml file
    :param cleanup_secrets_and_folders: Fixture to cleanup the secrets & folders created
    :param users_and_roles: Fixture to create random user with PAS User rights
    """

    parent_folder_info, nested_folder_info, nested_folder_id = create_folder_inside_folder
    parent_folder_id = parent_folder_info['ID']
    folder_prefix = guid()
    params = pas_general_secrets
    folders_list = cleanup_secrets_and_folders[1]

    child_folder_success, child_folder_parameters, child_folder_id = create_folder(
        core_session,
        folder_prefix + params['name'],
        params['description'],
        parent=nested_folder_id
    )
    assert child_folder_success, f'Failed to create child folder, API response result:: {child_folder_id}'
    logger.info(f'Child Folder created successfully: {child_folder_success} & details are {child_folder_id}')
    folders_list.insert(0, child_folder_id)

    # API to get new session for User A
    pas_power_user_session = users_and_roles.get_session_for_user('Privileged Access Service User')
    assert pas_power_user_session.auth_details, 'Failed to Login with PAS User'
    user_name = pas_power_user_session.auth_details['User']
    user_id = pas_power_user_session.auth_details['UserId']
    logger.info(f'User with PAS User Rights login successfully: user_Name:{user_name}')

    # Api to give user permissions to parent folder(View,Delete,Edit)
    user_permissions_result = give_user_permissions_to_folder(core_session, user_name, user_id, parent_folder_id,
                                                              'View,Delete,Edit')
    assert user_permissions_result['success'], \
        f'Not Able to set user permissions to folder, API response result:{user_permissions_result["Result"]}'
    logger.info(f'User Permissions to folder: {user_permissions_result}')

    # Api to give user permissions to nested folder(View,Add )
    user_permissions_result = give_user_permissions_to_folder(core_session, user_name, user_id, nested_folder_id,
                                                              'View,Add')
    assert user_permissions_result['success'], \
        f'Not Able to set user permissions to , API response result: {user_permissions_result["Result"]}'
    logger.info(f'User Permissions to folder: {user_permissions_result}')

    # Getting permissions of child folder(should inherit from parent)
    permissions_yellow = SetsManager.get_collection_rights(pas_power_user_session, child_folder_id)
    verify_permissions_all = 'View, Edit, Delete, Add'
    assert verify_permissions_all == permissions_yellow["Result"], \
        f'Failed to verify permissions for the folder, API response result:{permissions_yellow["Result"]}'
    logger.info(f'Permissions of the folder created: {permissions_yellow}')

    # Moving Nested Folder into Top Level Secrets
    result_move = move_folder(pas_power_user_session, nested_folder_id)
    assert result_move['success'], f'Not Able to Move Folder B1 into B11, API response result:: {result_move["Result"]}'
    logger.info(f'Moving Folder into Sub Folder:{result_move}')

    # Getting permissions of child folder(should inherit from nested folder)
    permissions_yellow = SetsManager.get_collection_rights(pas_power_user_session, child_folder_id)
    verify_permissions_all = 'View, Add'
    assert verify_permissions_all == permissions_yellow["Result"], \
        f'Failed to verify permissions for the folder, API response result:{permissions_yellow["Result"]}'
    logger.info(f'Permissions of the folder created: {permissions_yellow}')
