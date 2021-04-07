import pytest
import logging
from Shared.API.policy import PolicyManager
from Shared.API.secret import move_folder, update_folder, move_folder_by_using_mfa
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_both_source_and_destination_have_mfa(
        core_session,
        pas_general_secrets,
        create_secret_inside_folder,
        create_secret_folder,
        clean_up_policy):
    """
         C284028: Both source and destination have MFA
    :param core_session: Authenticated Centrify Session
    :param pas_general_secrets: Fixture to read secret data from yaml file
    :param create_secret_inside_folder: Fixture to create secret "MFAOnSecret" inside folder "MFAOnParentFolder"
    :param create_secret_folder: Fixture to create Folder & yields folder related details
    :param clean_up_policy: Fixture to clean up the policy created
    """
    user_detail = core_session.__dict__
    user_name = user_detail['auth_details']['User']
    secrets_params = pas_general_secrets
    suffix = guid()
    folder_id_source, folder_name_source, secret_list = create_secret_inside_folder
    secret_folder_details = create_secret_folder
    folder_id_destination = secret_folder_details['ID']
    folder_name_destination = secret_folder_details['Name']
    challenges = ["UP", ""]
    challenges_v2 = ["SQ", ""]

    # creating a new Authentication profile
    policy_result = PolicyManager.create_new_auth_profile(core_session, secrets_params['policy_name'] + suffix,
                                                          challenges, 0, 0)
    assert policy_result, f'Failed to create policy, API response result:{policy_result}'
    logger.info(f' Creating new policy:{policy_result}')
    clean_up_policy.append(policy_result)

    # creating a new Authentication profile
    policy_result_v2 = PolicyManager.create_new_auth_profile(core_session,
                                                             secrets_params['policy_name'] + "v2" + suffix,
                                                             challenges_v2, 0, 0)
    assert policy_result_v2, f'Failed to create policy, API response result:{policy_result_v2}'
    logger.info(f' Creating new policy:{policy_result_v2}')
    clean_up_policy.append(policy_result_v2)

    # Applying MFA on Folder
    result = update_folder(core_session, folder_id_source[0],
                           folder_name_source,
                           folder_name_source,
                           description=secrets_params['mfa_folder_description'],
                           policy_id=policy_result)
    assert result['success'], f'Not Able to apply MFA, API response result:: {result["Message"]} '
    logger.info(f'Applying MFA  for folder: {result}')

    # Applying MFA on Folder
    result = update_folder(core_session, folder_id_destination,
                           folder_name_destination,
                           folder_name_destination,
                           description=secrets_params['mfa_folder_description'],
                           policy_id=policy_result_v2)
    assert result['success'], f'Not Able to apply MFA, API response result:: {result["Message"]} '
    logger.info(f'Applying MFA  for folder: {result}')

    # Move Folder with Mfa Authentication
    result_folder_result = move_folder(core_session, folder_id_source[0], folder_id_destination)

    # StartChallenge MFA Authentication
    session, mechanism = core_session.start_mfa_authentication(user_name, result_folder_result['Result']['ChallengeId'])

    # AdvanceAuthentication MFA to Password
    advance_auth_result = core_session.advance_authentication(answer=core_session.user.user_input.password,
                                                              session_id=session, mechanism_id=mechanism)
    mfa_result = advance_auth_result.json()
    assert advance_auth_result, f'Password Authentication Failed, API response result:{mfa_result["success"]}'

    # After Authenticating of MFA move source folder with mfa to destination folder with mfa.
    moved_success, moved_result = move_folder_by_using_mfa(core_session, folder_id_source[0],
            target_folder_info=folder_id_destination, ChallengeStateId=result_folder_result['Result']['ChallengeId'])
    assert moved_success, f'Failed to verify Mfa challenged by source folder, API response result:{mfa_result} '
    logger.info(f'Successfully verified Mfa challenged by source folder: {moved_result}')

    # Removing MFA on Folder
    result = update_folder(core_session, folder_id_source[0],
                           folder_name_source,
                           folder_name_source,
                           description=secrets_params['mfa_folder_description'])
    assert result['success'], f'Failed to  remove  MFA, API response result: {result["Message"]} '
    logger.info(f'Successfully removed MFA for folder: {result}')

    # Removing MFA on Folder
    result = update_folder(core_session, folder_id_destination,
                           folder_name_destination,
                           folder_name_destination,
                           description=secrets_params['mfa_folder_description'])
    assert result['success'], f'Failed to  remove  MFA, API response result: {result["Message"]} '
    logger.info(f'Successfully removed MFA for folder: {result}')
