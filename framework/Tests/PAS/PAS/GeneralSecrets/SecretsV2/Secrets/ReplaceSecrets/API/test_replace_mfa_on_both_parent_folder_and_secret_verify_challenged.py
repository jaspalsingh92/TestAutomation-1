import logging
import pytest
from Shared.API.policy import PolicyManager
from Shared.API.secret import update_secret, update_folder, get_secret
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_replace_mfa_on_both_parent_folder_and_secret_verify_challenged(
        core_session,
        pas_general_secrets,
        create_secret_inside_folder,
        core_session_unauthorized,
        clean_up_policy):
    """
         C2981: test method to MFA policy on both Parent folder and Secret, verify secret MFA
         1) Set MFA on MFAonSecret & MFAOnParentFolder
         2) Right click "MFAonSecret" then Replace.
         3) Verify challenged with MFA popups,
         4) Enter password & verify you can replace secret

    :param core_session:  Authenticated Centrify Session
    :param pas_general_secrets: Fixture to read secret data from yaml file
    :param create_secret_inside_folder: Fixture to create secret "MFAOnSecret" inside folder "MFAOnParentFolder"
    :param core_session_unauthorized: Fixture to start authentication MFA
    :param clean_up_policy: Fixture to clean up the policy created
    """
    secrets_params = pas_general_secrets
    prefix = guid()
    folder_list, folder_name, secret_list = create_secret_inside_folder

    challenges = ["UP", ""]
    policy_result = PolicyManager.create_new_auth_profile(core_session, prefix + secrets_params['policy_name'],
                                                          challenges, 0, 0)
    assert policy_result, f'Failed to create policy, API response result:{policy_result}'
    logger.info(f' Creating new policy:{policy_result}')
    clean_up_policy.append(policy_result)

    # Applying MFA on Secret
    result = update_secret(core_session,
                           secret_list[0], prefix + secrets_params['mfa_secret_name_update'],
                           description=secrets_params['mfa_secret_description'],
                           policy_id=policy_result)
    assert result['success'], f'Not Able to apply MFA on the secret, API response result:{result["Message"]} '
    logger.info(f'MFA Applied on the secret: {result}')

    # Applying MFA on Folder
    result = update_folder(core_session, folder_list[0],
                           folder_name,
                           folder_name,
                           description=secrets_params['mfa_folder_description'],
                           policy_id=policy_result)
    assert result['success'], f'Not Able to apply MFA on folder, API response result: {result["Message"]} '
    logger.info(f'MFA Applied on Folder: {result}')

    user = core_session.get_user()
    user_name = user.get_login_name()
    password = user.get_password()

    # MFA Authentication starts on the secret to be replaced
    mfa_authentication = core_session_unauthorized.start_authentication(user_name)
    result = mfa_authentication.json()['Result']
    success = mfa_authentication.json()['success']
    assert success, f'Failed to start MFA Authentication on the secret to be replaced, API response result:{result}'
    challenge_value = result['Challenges'][0]['Mechanisms'][0]['Name']
    assert challenge_value == 'UP', f'Challenge "Password" is not set, API response result:{result}'
    logger.info(f'MFA Authentication starts on the secret to be replaced:{mfa_authentication.json()}')

    # Advance MFA Authentication starts on the secret to be replaced
    up_result = core_session_unauthorized.advance_authentication(password, challenge_index=0, mechanism_name='UP')
    mfa_result = up_result.json()
    assert mfa_result['success'], f'Failed to respond to challenge, API response result:{mfa_result["Result"]}'
    logger.info(f'MFA popups before secret gets replaced:{mfa_result}')

    # Replacing the text of the secret
    result = update_secret(core_session,
                           secret_list[0],
                           secrets_params['mfa_secret_name_update'] + prefix,
                           secret_text=secrets_params['secret_text_replaced'],
                           policy_id=policy_result)
    assert result['success'], f'Not Able to replace the text of the secret, API response result:{result["Message"]} '
    logger.info(f'Secret gets replaced: {result}')

    # Removing MFA
    result = update_secret(core_session,
                           secret_list[0],
                           secrets_params['mfa_secret_name_update'] + prefix,
                           secret_text=secrets_params['secret_text_replaced'])
    assert result['success'], f'Not Able to replace the text of the secret, API response result:{result["Message"]} '
    logger.info(f'Secret gets replaced: {result}')

    # Removing MFA from folder
    result = update_folder(core_session, folder_list[0],
                           folder_name,
                           folder_name,
                           description=secrets_params['mfa_folder_description'])
    assert result['success'], f'Not Able to update the folder, API response result:: {result["Message"]} '
    logger.info(f'Updating the folder: {result}')

    # Getting details of the secret replaced
    found_secret = get_secret(core_session, secret_list[0])
    assert found_secret['success'], \
        f'Failed to get the details of the secret updated, API response result:{found_secret["Message"]}'
    logger.info(f'Getting details of the secret: {found_secret}')
    secret_name = found_secret['Result']['SecretName']
    assert 'MFAOnSecretUpdate' in secret_name, \
        f'Failed to update the secret, API response result:{found_secret["success"]}'
