import pytest
import logging
from Shared.API.secret import create_folder, get_folder, get_secrets_and_folders_in_folders, \
    give_user_permissions_to_folder, create_text_secret_within_folder, del_secret, \
    update_secret, get_secret_contents, set_member_permissions_to_folder
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_union_of_all_its_permissions(core_session,
                                      pas_general_secrets,
                                      cleanup_secrets_and_folders,
                                      users_and_roles):
    """
        C3056: test method Union of all its permissions
        1)create multilevel folder /alpha/beta/charlie/delta
       2) Login as Admin, set folder permissions "View" for alpha,"Edit" for beta, "Delete" for charlie,"Add" for delta
       3) Login as pas user
       4) verify sub folder permissions will have a union of all parent folders

    :param core_session: Authenticated Centrify session
    :param pas_general_secrets: Fixture to read secrets related data from yaml file
    :param cleanup_secrets_and_folders: Fixture to cleanup the secrets & folders created
    :param users_and_roles: Fixture to create random user with PAS User Rights

    """
    params = pas_general_secrets
    folder_prefix = guid()
    folders_list = cleanup_secrets_and_folders[1]
    secrets_list = cleanup_secrets_and_folders[0]

    # creating multilevel folder /alpha/beta/charlie/delta
    child_folder_success, child_folder_parameters, child_folder_id = create_folder(
        core_session,
        folder_prefix + params['multi_level_folder_name'],
        params['description'])
    assert child_folder_success, f'Failed to create multilevel folder, API response result: {child_folder_id}'
    logger.info(f'Multilevel Folder created successfully: {child_folder_success} & details are {child_folder_id}')

    # Getting details of Folder Charlie
    charlie_folder = get_folder(core_session, child_folder_id)
    assert charlie_folder['success'], \
        f'Failed to retrieve charlie folder details, API response result:{charlie_folder["Message"]}'
    logger.info(f'charlie folder details:{charlie_folder}')
    charlie_id = charlie_folder['Result']['Results'][0]['Row']['Parent']

    # Getting details of parent folder
    parent_path = charlie_folder['Result']['Results'][0]['Row']['ParentPath']
    parent_folder_name = parent_path.split('\\')
    parent_folder_sliced = parent_folder_name[0]

    # Getting id of parent folder
    parent_folder = get_folder(core_session, parent_folder_sliced)
    assert parent_folder['success'], \
        f'Failed to retrieve parent folder details, API response result:{parent_folder["Message"]}'
    logger.info(f'Parent folder details:{parent_folder}')
    parent_folder_id = parent_folder['Result']['Results'][0]['Row']['ID']

    # Getting details of Folder alpha
    alpha_folder = get_secrets_and_folders_in_folders(core_session, parent_folder_id)
    assert alpha_folder['success'], f'Failed to retrieve alpha folder id, API response result: {alpha_folder["Result"]}'
    logger.info(f'Details of Alpha Folder Retrieved:{alpha_folder}')
    alpha_folder_id = alpha_folder["Result"]["Results"][0]["Entities"][0]["Key"]

    # Getting details of Folder beta
    folder_beta = get_secrets_and_folders_in_folders(core_session, alpha_folder_id)
    assert folder_beta['success'], f'Failed to retrieve beta folder id, API response result: {folder_beta["Result"]}'
    logger.info(f'Details of Beta Folder Retrieved:{folder_beta}')
    folder_beta_id = folder_beta["Result"]["Results"][0]["Entities"][0]["Key"]

    # API to get new session for User A
    pas_power_user_session = users_and_roles.get_session_for_user('Privileged Access Service User')
    assert pas_power_user_session.auth_details, 'Failed to Login with PAS User'
    user_name = pas_power_user_session.auth_details['User']
    user_id = pas_power_user_session.auth_details['UserId']
    logger.info(f'User with PAS User Rights login successfully: user_Name:{user_name}')

    # Adding secrets inside child folder
    added_secret_success, added_secret_id = create_text_secret_within_folder(core_session,
                                                                             params['mfa_secret_name'] + folder_prefix,
                                                                             params['secret_text'],
                                                                             params['secret_description'],
                                                                             child_folder_id)
    assert added_secret_success, f"Added Secret Failed, API response result {added_secret_id}"
    logger.info(f'Added secrets info: {added_secret_id}')

    # Api to give user permissions to folder alpha
    user_permissions_alpha = give_user_permissions_to_folder(core_session, user_name, user_id, alpha_folder_id, 'View')
    assert user_permissions_alpha['success'], \
        f'Not Able to set user permissions to folder, API response result: {user_permissions_alpha["Result"]}'
    logger.info(f'User Permissions to folder: {user_permissions_alpha}')

    # Api to give user permissions to folder beta
    user_permissions_beta = give_user_permissions_to_folder(core_session, user_name, user_id, folder_beta_id, 'Edit')
    assert user_permissions_beta['success'], \
        f'Not Able to set user permissions to folder, API response result: {user_permissions_beta["Result"]}'
    logger.info(f'User Permissions to folder: {user_permissions_beta}')

    # Api to give member permissions(View, Edit) to folder beta
    member_perm_result, member_perm_success = set_member_permissions_to_folder(core_session,
                                                                               user_name,
                                                                               'View, Edit',
                                                                               user_id,
                                                                               folder_beta_id)
    assert member_perm_success,\
        f'Not Able to set "View" member permissions to Folder, API response result: {member_perm_result}'
    logger.info(f'Member permissions to folder:{member_perm_result}')

    # Api to give member permissions(Delete, Retrieve) to folder
    member_perm_result, member_perm_success = set_member_permissions_to_folder(core_session,
                                                                               user_name,
                                                                               'Delete,Retrieve',
                                                                               user_id,
                                                                               charlie_id)
    assert member_perm_success,\
        f'Not Able to set "View" member permissions to Folder, API response result: {member_perm_result}'
    logger.info(f'Member permissions to folder:{member_perm_result}')

    # Updating the secret name & description
    result = update_secret(pas_power_user_session,
                           added_secret_id,
                           folder_prefix + params['mfa_secret_name_update'],
                           description=params['mfa_secret_description'])
    assert result['success'], f'Not Able to update the secret, API response result: {result["Message"]} '
    logger.info(f'Secret Updated Details: {result}')

    # Getting details of the Secret updated
    get_secret_details, get_secret_success, get_secret_created_date, get_secret_text = get_secret_contents(
        pas_power_user_session,
        added_secret_id)
    description_updated = get_secret_details['Description']
    name_updated = get_secret_details['SecretName']
    assert 'MFAOnSecretUpdate' in name_updated,\
        f'Failed to update the name, API response result:{get_secret_success}'
    assert 'mfa_description' in description_updated,\
        f'Failed to update the description, API response result:{get_secret_success}'
    logger.info(f'Details of the secret updated: {get_secret_details}')

    # Deleting newly created secrets
    del_success, del_result = del_secret(pas_power_user_session, added_secret_id)
    assert del_success, f'Failed to delete the secret with pas user, API response result: {del_result}'
    logger.info(f'Secret deleted successfully with pas user:{del_result}')

    folders_list.append(child_folder_id)
    folders_list.append(charlie_id)
    folders_list.append(folder_beta_id)
    folders_list.append(alpha_folder_id)
    folders_list.append(parent_folder_id)
    logger.info(f'Added Folders are deleted successfully: {folders_list}')
    logger.info(f'Added Secrets deleted successfully: {secrets_list}')
