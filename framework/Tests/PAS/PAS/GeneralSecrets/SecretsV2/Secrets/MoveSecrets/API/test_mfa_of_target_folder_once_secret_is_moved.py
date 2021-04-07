import pytest
import logging
from Shared.API.policy import PolicyManager
from Shared.API.secret import move_secret_by_using_mfa, move_secret, update_folder
from Utils.guid import guid

logger = logging.getLogger("test")


@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_mfa_of_target_folder_once_secret_is_moved(
        core_session,
        pas_general_secrets,
        create_secret_folder,
        added_secrets,
        clean_up_policy):
    """
        C283940: MFA of the target folder will apply once secret is moved to it
    :param core_session:  Authenticated Centrify Session
    :param pas_general_secrets: Fixture to read secret data from yaml file
    :param create_secret_folder: Fixture to create secret folder & yields folder related details
    :param added_secrets: Fixture to create text type secrets & yields secrets details
    :param clean_up_policy: Fixture to clean up the policy created
    """
    secrets_params = pas_general_secrets
    suffix = guid()
    secret_folder_details = create_secret_folder
    folder_id = secret_folder_details['ID']
    secret_id, secret_name = added_secrets
    challenges1 = ["UP", ""]
    user_name = core_session.auth_details['User']

    # creating a new Authentication profile for nested folder
    policy_result = PolicyManager.create_new_auth_profile(core_session, secrets_params['policy_name'] + suffix,
                                                          challenges1, 0, 0)
    assert policy_result, f'Failed to create policy, API response result:{policy_result}'
    logger.info(f' Creating new policy:{policy_result}')
    clean_up_policy.append(policy_result)

    # Applying MFA on Folder
    result = update_folder(core_session, folder_id,
                           secret_folder_details['Name'],
                           secret_folder_details['Name'],
                           description=secrets_params['mfa_folder_description'],
                           policy_id=policy_result)
    assert result['success'], f'Not Able to apply MFA, API response result:: {result["Message"]} '
    logger.info(f'Applying MFA  for folder: {result}')

    # Move Secret with Mfa Authentication
    result_secret = move_secret(core_session, secret_id[0], folder_info=folder_id)
    assert result_secret['success'], f'Failed to move secret into folder,API Response Result: {result_secret["Result"]}'

    # Moving Secret with new parent inherited policies
    secret_new_permissions = move_secret(core_session, secret_id[0])

    # StartChallenge MFA Authentication
    session, mechanism = core_session.start_mfa_authentication(user_name,
                                                               secret_new_permissions['Result']['ChallengeId'])

    # AdvanceAuthentication MFA to Password
    advance_auth_result = core_session.advance_authentication(answer=core_session.user.user_input.password,
                                                              session_id=session, mechanism_id=mechanism)
    mfa_result = advance_auth_result.json()
    assert advance_auth_result, f'Password Authentication Failed, API response result:{mfa_result["success"]}'
    logger.info(f'successfully applied password authentication: {mfa_result}')

    # After Authenticating of MFA move secret with challenge password
    moved_success, moved_result = move_secret_by_using_mfa(
        core_session, secret_id[0], ChallengeStateId=secret_new_permissions['Result']['ChallengeId'])
    assert moved_success, f'Failed to move secret with new parent inherited policies: {moved_result}'
    logger.info(f'User: {user_name} successfully moved secret with new parent inherited policies: {moved_result}')

    # Applying MFA on Folder
    result = update_folder(core_session, folder_id,
                           secret_folder_details['Name'],
                           secret_folder_details['Name'])
    assert result['success'], f'Not Able to apply MFA, API response result:: {result["Message"]} '
    logger.info(f'Applying MFA  for folder: {result}')
