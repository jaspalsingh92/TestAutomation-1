import pytest
import logging
from Shared.API.secret import create_folder, get_folder, get_secrets_and_folders_in_folders, \
    give_user_permissions_to_folder
from Shared.API.sets import SetsManager
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_updates_by_admin_are_reflected_on_sub_folders(core_session,
                                                       pas_general_secrets,
                                                       cleanup_secrets_and_folders,
                                                       users_and_roles):
    """
        C3049: test method to Updates and changes by admin are reflected on sub folders through inheritance
        1) create multilevel folder /alpha/beta/charlie/delta
        2)Login as Admin, add & update different folder permissions for alpha
       3) Login as pas user
       4) verify permissions are saved and propagated to the child folders.
    :param core_session: Authenticated Centrify session
    :param pas_general_secrets: Fixture to read secrets related data from yaml file
    :param cleanup_secrets_and_folders: Fixture to cleanup the secrets & folders created
    :param users_and_roles: Fixture to create random user with PAS User Rights

    """
    params = pas_general_secrets
    folder_prefix = guid()
    folders_list = cleanup_secrets_and_folders[1]

    # creating multilevel folder /alpha/beta/charlie/delta
    child_folder_success, child_folder_parameters, child_folder_id = create_folder(
        core_session,
        folder_prefix + params['multi_level_folder_name'],
        params['description'])
    assert child_folder_success, f'Failed to create multilevel folder, API response result: {child_folder_id}'
    logger.info(f'Multilevel Folder created successfully: {child_folder_success} & details are {child_folder_id}')

    # Getting details of Folder Charlie
    charlie_folder = get_folder(core_session, child_folder_id)
    charlie_id = charlie_folder['Result']['Results'][0]['Row']['Parent']

    # Getting details of parent folder
    parent_path = charlie_folder['Result']['Results'][0]['Row']['ParentPath']
    parent_folder_name = parent_path.split('\\')
    parent_folder_sliced = parent_folder_name[0]

    # Getting id of parent folder
    parent_folder = get_folder(core_session, parent_folder_sliced)
    parent_folder_id = parent_folder['Result']['Results'][0]['Row']['ID']

    # Getting details of Folder alpha
    alpha_folder = get_secrets_and_folders_in_folders(core_session, parent_folder_id)
    alpha_folder_id = alpha_folder["Result"]["Results"][0]["Entities"][0]["Key"]

    # Getting details of Folder beta
    folder_beta = get_secrets_and_folders_in_folders(core_session, alpha_folder_id)
    folder_beta_id = folder_beta["Result"]["Results"][0]["Entities"][0]["Key"]

    # API to get new session for User A
    pas_power_user_session = users_and_roles.get_session_for_user('Privileged Access Service User')
    assert pas_power_user_session.auth_details, 'Failed to Login with PAS User'
    user_name = pas_power_user_session.auth_details['User']
    user_id = pas_power_user_session.auth_details['UserId']
    logger.info(f'User with PAS User Rights login successfully: user_Name:{user_name}')

    # Api to assign all the permissions(View, Edit, Delete, Grant, Add) to folder alpha
    user_permissions_alpha = give_user_permissions_to_folder(core_session,
                                                             user_name,
                                                             user_id,
                                                             alpha_folder_id,
                                                             'View, Edit, Delete, Grant, Add')
    assert user_permissions_alpha['success'], \
        f'Not Able to set user permissions to folder, API response result:{user_permissions_alpha["Result"]}'
    logger.info(f'User Permissions to folder: {user_permissions_alpha}')

    # Getting permissions of the folder delta(should inherit from parent)
    permissions_delta = SetsManager.get_collection_rights(pas_power_user_session, child_folder_id)
    verify_permissions_all = 'View, Edit, Delete, Grant, Add'
    assert verify_permissions_all == permissions_delta["Result"], \
        f'Failed to verify permissions for the folder, API response result:{permissions_delta["Result"]}'
    logger.info(f'Permissions of the folder created: {permissions_delta}')

    # Api to assign selected permissions(View, Edit, Delete) to folder alpha
    user_permissions_alpha = give_user_permissions_to_folder(core_session,
                                                             user_name,
                                                             user_id,
                                                             alpha_folder_id,
                                                             'View, Edit, Delete')
    assert user_permissions_alpha['success'], \
        f'Not Able to set user permissions to folder, API response result:{user_permissions_alpha["Result"]}'
    logger.info(f'User Permissions to folder: {user_permissions_alpha}')

    # Getting permissions of the folder delta(should inherit from parent)
    permissions_delta = SetsManager.get_collection_rights(pas_power_user_session, child_folder_id)
    verify_permissions_selected = 'View, Edit, Delete'
    assert verify_permissions_selected == permissions_delta["Result"], \
        f'Failed to verify permissions for the folder, API response result:{permissions_delta["Result"]}'
    logger.info(f'Permissions of the folder created: {permissions_delta}')

    # Api to give permissions(View,Add) to folder alpha
    user_permissions_alpha = give_user_permissions_to_folder(core_session,
                                                             user_name,
                                                             user_id,
                                                             alpha_folder_id,
                                                             'View, Add')
    assert user_permissions_alpha['success'], \
        f'Not Able to set user permissions to folder, API response result:{user_permissions_alpha["Result"]}'
    logger.info(f'User Permissions to folder: {user_permissions_alpha}')

    # Getting permissions of the folder delta(should inherit from parent)
    permissions_delta = SetsManager.get_collection_rights(pas_power_user_session, child_folder_id)
    verify_permissions_view_add = 'View, Add'
    assert verify_permissions_view_add == permissions_delta["Result"], \
        f'Failed to verify permissions for the folder, API response result:{permissions_delta["Result"]}'
    logger.info(f'Permissions of the folder created: {permissions_delta}')

    # cleanup of folders accordingly
    folders_list.append(child_folder_id)
    folders_list.append(charlie_id)
    folders_list.append(folder_beta_id)
    folders_list.append(alpha_folder_id)
    folders_list.append(parent_folder_id)
    logger.info(f'Added Folders deleted successfully: {folders_list}')
