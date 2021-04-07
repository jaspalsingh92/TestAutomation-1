import pytest
import logging
from Shared.API.policy import PolicyManager
from Shared.API.secret import update_folder, move_secret, move_secret_by_using_mfa
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_move_mfa_on_parent_folder(
        core_session,
        pas_general_secrets,
        create_secret_inside_folder,
        cleanup_secrets_and_folders,
        clean_up_policy):
    """
            C283936: MFA policy on Parent folder, verify challenged
    :param core_session:  Authenticated Centrify Session
    :param pas_general_secrets: Fixture to read secret data from yaml file
    :param create_secret_inside_folder: Fixture to create secret inside folder & yields folder & secret details
    :param cleanup_secrets_and_folders: Fixture to cleanup the secrets & folders created.
    :param clean_up_policy: Fixture to clean up the policy created
    """
    user_detail = core_session.__dict__
    user_name = user_detail['auth_details']['User']
    secrets_params = pas_general_secrets
    suffix = guid()
    folder_list, folder_name, secret_list = create_secret_inside_folder
    challenges = ["UP", ""]

    # creating a new Authentication profile
    policy_result = PolicyManager.create_new_auth_profile(core_session, secrets_params['policy_name'] + suffix,
                                                          challenges, 0, 0)
    assert policy_result, f'Failed to create policy, API response result:{policy_result}'
    logger.info(f' Creating new policy:{policy_result}')
    clean_up_policy.append(policy_result)

    # Applying MFA on Folder
    result = update_folder(core_session, folder_list[0],
                           folder_name,
                           folder_name,
                           description=secrets_params['mfa_folder_description'],
                           policy_id=policy_result)
    assert result['success'], f'Failed to apply MFA, API response result:: {result["Message"]} '
    logger.info(f'Applying MFA for folder: {result}')

    # Move Secret with Mfa Authentication
    result_secret = move_secret(core_session, secret_list[0])

    # StartChallenge MFA Authentication
    session, mechanism = core_session.start_mfa_authentication(user_name, result_secret['Result']['ChallengeId'])

    # AdvanceAuthentication MFA to Password
    advance_auth_result = core_session.advance_authentication(answer=core_session.user.user_input.password,
                                                              session_id=session, mechanism_id=mechanism)
    mfa_result = advance_auth_result.json()
    assert advance_auth_result, f'Password Authentication Failed, API response result:{mfa_result["success"]}'

    # After Authenticating of move secret with mfa on parent folder
    moved_success, moved_result = move_secret_by_using_mfa(core_session, secret_list[0],
                                                           ChallengeStateId=result_secret['Result']['ChallengeId'])
    assert moved_success, f'Moving secret not challenged by mfa:{moved_result}'
    logger.info(f'Moving secret challenged by mfa on parent successfully:{moved_result} {moved_success}')

    # Removing MFA on Folder
    result = update_folder(core_session, folder_list[0],
                           folder_name,
                           folder_name,
                           description=secrets_params['mfa_folder_description'])
    assert result['success'], f'Failed to remove MFA, API response result:: {result["Message"]} '
    logger.info(f'Successfully removed MFA on folder: {result}')
