import pytest
import logging
from Shared.API.policy import PolicyManager
from Shared.API.secret import move_secret_by_using_mfa, move_secret, update_secret
from Utils.guid import guid


logger = logging.getLogger("test")


@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_move_mfa_on_secrets_should_apply(
        core_session,
        pas_general_secrets,
        create_secret_folder,
        added_secrets,
        clean_up_policy):

    """
         C283939: MFA on secret should still apply once moved to another folder
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

    # Applying MFA to secret
    result = update_secret(core_session,
                           secret_id[0],
                           secret_name,
                           description=secrets_params['mfa_secret_description'],
                           policy_id=policy_result)
    assert result['success'], f'Failed to apply mfa to secret, API response result: {result["Message"]} '
    logger.info(f'Successfully applied MFA to Secret: {result}')

    # Move Secret with Mfa Authentication
    result_secret = move_secret(core_session, secret_id[0], folder_info=folder_id)

    # StartChallenge MFA Authentication
    session, mechanism = core_session.start_mfa_authentication(user_name, result_secret['Result']['ChallengeId'])

    # AdvanceAuthentication MFA to Password
    advance_auth_result = core_session.advance_authentication(answer=core_session.user.user_input.password,
                                                              session_id=session, mechanism_id=mechanism)
    mfa_result = advance_auth_result.json()
    assert advance_auth_result, f'Password Authentication Failed, API response result:{mfa_result["success"]}'
    logger.info(f'successfully applied password authentication: {mfa_result}')

    # After Authenticating of MFA move secret with challenge password
    moved_success, moved_result = move_secret_by_using_mfa(core_session, secret_id[0], target_folder_info=folder_id,
                                                           ChallengeStateId=result_secret['Result']['ChallengeId'])
    assert moved_success, f'User: {user_name} Failed to move secret to another folder: {moved_result}'
    logger.info(f'User: {user_name} successfully moved secret to another folder: {moved_result}')

    # Move Secret with Mfa Authentication
    result_secret = move_secret(core_session, secret_id[0])
    assert result_secret['success'] is False, \
        f'Failed to preserve MFA Policy,API Response result:{result_secret["Message"]}'
    logger.info(f'MFA Policy is preserved successfully: {result_secret}')

    # Removing mfa from secret
    result = update_secret(core_session,
                           secret_id[0],
                           secret_name,
                           description=secrets_params['mfa_secret_description'])
    assert result['success'], f'Failed to remove mfa from secret, API response result: {result["Message"]} '
    logger.info(f'Successfully removed mfa from secret: {result}')
