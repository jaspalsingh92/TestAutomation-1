import pytest
import logging
from Shared.API.policy import PolicyManager
from Shared.API.secret import move_folder, update_folder, get_secrets_and_folders_in_folders, move_folder_by_using_mfa
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_move_mfa_enabled_folder_to_non_mfa_enabled_folder(

        core_session,
        pas_general_secrets,
        create_secret_inside_folder,
        create_folder_inside_folder,
        cleanup_secrets_and_folders,
        clean_up_policy):

    """
         C284026: test method to move Source parent has MFA, destination no MFA, verify challenged

    :param core_session:  Authenticated Centrify Session
    :param pas_general_secrets: Fixture to read secret data from yaml file
    :param create_secret_inside_folder: Fixture to create secret "MFAOnSecret" inside folder "MFAOnParentFolder"
    :param create_folder_inside_folder: Fixture to create nested Folder & yields folder & sub folder related details
    :param cleanup_secrets_and_folders: Fixture to cleanup the secrets & folders created.
    :param clean_up_policy: Fixture to clean up the policy created

    """
    user_detail = core_session.__dict__
    user_name = user_detail['auth_details']['User']
    secrets_params = pas_general_secrets
    suffix = guid()
    folder_id_list, folder_name, secret_list = create_secret_inside_folder
    parent_folder_info, nested_folder_info, nested_folder_id = create_folder_inside_folder
    folder_list = cleanup_secrets_and_folders[1]
    update_folder_name = secrets_params['mfa_folder_name_update'] + suffix
    challenges = ["UP", ""]

    # creating a new Authentication profile
    policy_result = PolicyManager.create_new_auth_profile(core_session, secrets_params['policy_name'] + suffix,
                                                          challenges, 0, 0)
    assert policy_result, f'Failed to create policy, API response result:{policy_result}'
    logger.info(f' Creating new policy:{policy_result}')
    clean_up_policy.append(policy_result)

    # Applying MFA on Folder
    result = update_folder(core_session, folder_id_list[1],
                           folder_name,
                           update_folder_name,
                           description=secrets_params['mfa_folder_description'],
                           policy_id=policy_result)
    assert result['success'], f'Not Able to apply MFA, API response result:: {result["Message"]} '
    logger.info(f'Applying MFA  for folder: {result}')

    # Move Folder with Mfa Authentication
    result_folder_result = move_folder(core_session, folder_id_list[1], nested_folder_id)

    # StartChallenge MFA Authentication
    session, mechanism = core_session.start_mfa_authentication(user_name, result_folder_result['Result']['ChallengeId'])

    # AdvanceAuthentication MFA to Password
    advance_auth_result = core_session.advance_authentication(answer=core_session.user.user_input.password,
                                                              session_id=session, mechanism_id=mechanism)
    mfa_result = advance_auth_result.json()
    assert advance_auth_result, f'Password Authentication Failed, API response result:{mfa_result["success"]}'

    # After Authenticating of MFA move mfa enabled folder to the non mfa enabled folder.
    moved_success, moved_result = move_folder_by_using_mfa(core_session, folder_id_list[1], target_folder_info=nested_folder_id,
                                              ChallengeStateId=result_folder_result['Result']['ChallengeId'])
    assert moved_success, f'User: {user_name} Not Able to move mfa enabled folder' \
        f' to the non mfa enabled folder: {moved_result}'
    logger.info(f'User: {user_name} moved mfa enabled folder: {update_folder_name} successfully '
                f'to the non mfa enabled folder:')
    folder_list.insert(0, folder_list.pop(1))

    # Verifying mfa enabled folder moved successfully or not, inside non mfa enabled folder.
    moved_folder = get_secrets_and_folders_in_folders(core_session, nested_folder_id)
    moved_folder_name = moved_folder["Result"]["Results"][0]["Row"]["Name"]
    assert moved_folder_name == update_folder_name, f'Failed to get the moved folder{moved_folder_name} ' \
        f'inside the folder'
    logger.info(f'Moved folder {moved_folder_name} get successfully inside the folder')

    # Removing MFA on Folder
    result = update_folder(core_session, folder_id_list[0],
                           update_folder_name,
                           secrets_params['mfa_folder_name_update'] + suffix,
                           description=secrets_params['mfa_folder_description'])
    assert result['success'], f'Not Able to remove MFA, API response result: {result["Message"]} '
    logger.info(f'Applying MFA  for folder: {result}')
