import pytest
import logging
from Shared.API.policy import PolicyManager
from Shared.API.secret import move_folder, update_folder, move_folder_by_using_mfa
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_remove_non_mfa_folder_and_mfa_parent_folder_apply(

        core_session,
        pas_general_secrets,
        create_secret_inside_folder,
        create_folder_inside_folder,
        cleanup_secrets_and_folders,
        clean_up_policy):

    """
         C284030: Remove MFA on folder and the MFA on parent folders should apply

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
    folder_id_list, folder_name, secret_list = create_secret_inside_folder
    parent_folder_info, nested_folder_info, nested_folder_id = create_folder_inside_folder
    folder_list = cleanup_secrets_and_folders[1]
    challenges1 = ["UP", ""]
    challenges2 = ["UP,SQ", ""]

    # creating First Authentication profile
    create_first_profile = PolicyManager.create_new_auth_profile(core_session, secrets_params['policy_name'] + guid(),
                                                                 challenges1, 0, 0)
    assert create_first_profile, f'Failed to create policy, API response result:{create_first_profile}'
    logger.info(f' Creating first policy:{create_first_profile}')
    clean_up_policy.append(create_first_profile)

    # creating second Authentication profile
    create_second_profile = PolicyManager.create_new_auth_profile(core_session, secrets_params['policy_name'] + guid(),
                                                                  challenges2, 0, 0)
    assert create_second_profile, f'Failed to create policy, API response result:{create_second_profile}'
    logger.info(f' Creating second policy:{create_second_profile}')
    clean_up_policy.append(create_second_profile)

    # Applying MFA on Folder
    result = update_folder(core_session, parent_folder_info['ID'],
                           parent_folder_info['Name'],
                           secrets_params['mfa_folder_name_update'] + guid(),
                           description=secrets_params['mfa_folder_description'],
                           policy_id=create_second_profile)
    assert result['success'], f'Not Able to apply MFA, API response result:: {result["Message"]} '
    logger.info(f'Applying MFA  for folder: {result}')

    # Applying MFA on another Folder
    result = update_folder(core_session, folder_id_list[1],
                           folder_name,
                           secrets_params['mfa_folder_name_update'] + guid(),
                           description=secrets_params['mfa_folder_description'],
                           policy_id=create_first_profile)
    assert result['success'], f'Not Able to apply MFA, API response result:: {result["Message"]} '
    logger.info(f'Applying MFA  for folder: {result}')

    # Move one mfa enabled folder to another mfa enabled folder.
    logger.info(f'Moving Folder {folder_name} into Folder:{parent_folder_info}')
    result_folder_result = move_folder(core_session, folder_id_list[1], nested_folder_id)

    # StartChallenge MFA Authentication
    session, mechanism = core_session.start_mfa_authentication(user_name, result_folder_result['Result']['ChallengeId'])
    assert mechanism, f'Not able to authenticate mfa challenges, API response result:{mechanism}'

    # AdvanceAuthentication MFA to Password
    advance_auth_result = core_session.advance_authentication(answer=core_session.user.user_input.password,
                                                              session_id=session, mechanism_id=mechanism)
    mfa_result = advance_auth_result.json()
    assert advance_auth_result, f'Password Authentication Failed, API response result:{mfa_result["success"]}'

    # After Authenticating of MFA move mfa enabled folder to the non mfa enabled folder.
    moved_success, moved_result = move_folder_by_using_mfa(core_session, folder_id_list[1],
                                                           target_folder_info=nested_folder_id,
                                                           ChallengeStateId=result_folder_result['Result'][
                                                               'ChallengeId'])
    assert moved_success, f'User: {user_name} Not Able to move mfa enabled folder' \
        f' to the other mfa enabled folder: {moved_result}'
    logger.info(f'User: {user_name} moved mfa enabled folder: successfully '
                f'to the other mfa enabled folder:')
    folder_list.insert(0, folder_list.pop(1))

    # Removing MFA on Folder
    result = update_folder(core_session, folder_id_list[0],
                           folder_name,
                           secrets_params['mfa_folder_name_update'] + guid(),
                           description=secrets_params['mfa_folder_description'])
    assert result['success'], f'Not Able to remove MFA, API response result: {result["Message"]} '
    logger.info(f'Applying MFA  for folder: {result}')

    # Move removed mfa folder that contains in mfa enabled folder to Parent.
    result_folder_result = move_folder(core_session, folder_id_list[0], "")

    # StartChallenge MFA Authentication
    session, mechanism = core_session.start_mfa_authentication(user_name, result_folder_result['Result']['ChallengeId'])
    assert mechanism, f'Not able to authenticate mfa challenges, API response result:{mechanism}'

    # AdvanceAuthentication MFA to Password
    advance_auth_result = core_session.advance_authentication(answer=core_session.user.user_input.password,
                                                              session_id=session, mechanism_id=mechanism)
    mfa_result = advance_auth_result.json()
    assert advance_auth_result, f'Password Authentication Failed, API response result:{mfa_result["success"]}'

    # After Authenticating of MFA move non mfa enabled folder to the outside or make it parent folder.
    moved_success, moved_result = move_folder_by_using_mfa(core_session, folder_id_list[0],
                                                           target_folder_info="",
                                                           ChallengeStateId=result_folder_result['Result'][
                                                               'ChallengeId'])
    assert moved_success, f'User: {user_name} Not Able to move non mfa enabled folder' \
        f' to the outside or make it parent folder: {moved_result}'
    logger.info(f'User: {user_name} moved non mfa enabled folder: successfully '
                f'to the outside or make it parent folder:')

    # Removing MFA on Folder
    result = update_folder(core_session, parent_folder_info['ID'],
                           parent_folder_info['Name'],
                           secrets_params['mfa_folder_name_update'] + guid(),
                           description=secrets_params['mfa_folder_description'])
    assert result['success'], f'Not Able to remove MFA, API response result: {result["success"]} '
    logger.info(f'Applying MFA  for folder: {result}')
