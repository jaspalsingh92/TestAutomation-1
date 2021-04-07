import pytest
import logging
from Shared.API.policy import PolicyManager
from Shared.API.secret import move_folder, update_folder, get_secrets_and_folders_in_folders
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_move_no_mfa_enabled_folder_to_mfa_enabled_folder(

        core_session,
        pas_general_secrets,
        create_secret_inside_folder,
        create_folder_inside_folder,
        cleanup_secrets_and_folders,
        clean_up_policy):

    """
         C284027: test method to Move no mfa enabled folder to mfa enabled folder, verify challenged

    :param core_session:  Authenticated Centrify Session
    :param pas_general_secrets: Fixture to read secret data from yaml file
    :param create_secret_inside_folder: Fixture to create secret "MFAOnSecret" inside folder "MFAOnParentFolder"
    :param create_folder_inside_folder: Fixture to create nested Folder & yields folder & sub folder related details
    :param cleanup_secrets_and_folders: Fixture to cleanup the secrets & folders created.
    :param clean_up_policy: Fixture to clean up the policy created

    """
    secrets_params = pas_general_secrets
    suffix = guid()
    folder_id_list, folder_name, secret_list = create_secret_inside_folder
    parent_folder_info, nested_folder_info, nested_folder_id = create_folder_inside_folder
    folder_list = cleanup_secrets_and_folders[1]
    update_folder_name = secrets_params['mfa_folder_name_update'] + suffix
    challenges = ["UP", ""]
    policy_result = PolicyManager.create_new_auth_profile(core_session, secrets_params['policy_name'] + suffix,
                                                          challenges, 0, 0)
    assert policy_result, f'Failed to create policy, API response result:{policy_result}'
    logger.info(f' Creating new policy:{policy_result}')
    clean_up_policy.append(policy_result)

    # Applying MFA on Folder
    result = update_folder(core_session, parent_folder_info['ID'],
                           parent_folder_info['Name'],
                           update_folder_name,
                           description=secrets_params['mfa_folder_description'],
                           policy_id=policy_result)
    assert result['success'], f'Not Able to apply MFA, API response result:: {result["Message"]} '
    logger.info(f'Applying MFA  for folder: {result}')

    # Move no mfa enabled folder to mfa enabled folder.
    logger.info(f'Moving Folder {folder_name} into Folder:{parent_folder_info}')
    result_move = move_folder(core_session, folder_id_list[1], nested_folder_id)
    assert result_move['success'], \
        f'Not Able to move no mfa enabled folder to mfa enabled folder, API response result: {result_move["Result"]}'
    logger.info(f'Moved successfully non mfa enabled Folder {folder_id_list[1]} to'
                f'mfa enabled folder:{nested_folder_id}')
    folder_list.insert(0, folder_list.pop(1))

    # Verifying non mfa enabled folder moved successfully or not , inside mfa enabled folder.
    moved_folder = get_secrets_and_folders_in_folders(core_session, nested_folder_id)
    moved_folder_name = moved_folder["Result"]["Results"][0]["Row"]["Name"]
    assert moved_folder_name == folder_name, f'Failed to get the moved folder{moved_folder_name} ' \
        f'inside the folder'
    logger.info(f'Moved folder {moved_folder_name} get successfully inside the folder')

    # Removing MFA on Folder
    result = update_folder(core_session, parent_folder_info['ID'],
                           parent_folder_info['Name'],
                           secrets_params['mfa_folder_name_update'] + suffix,
                           description=secrets_params['mfa_folder_description'])
    assert result['success'], f'Not Able to remove MFA, API response result: {result["success"]} '
    logger.info(f'Applying MFA  for folder: {result}')
