import logging
import pytest
from Shared.API.policy import PolicyManager
from Shared.API.secret import update_secret, update_folder, give_user_permissions_to_folder, \
    set_member_permissions_to_folder, get_secret_contents
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_replace_mfa_policy_on_parent_folder_verify_challenged(

        core_session,
        pas_general_secrets,
        create_secret_inside_folder,
        core_session_unauthorized,
        clean_up_policy,
        users_and_roles):

    """
         C2980: test method to MFA policy on Parent folder, verify challenged

    :param core_session:  Authenticated Centrify Session
    :param pas_general_secrets: Fixture to read secret data from yaml file
    :param create_secret_inside_folder: Fixture to create secret "MFAOnSecret" inside folder "MFAOnParentFolder"
    :param core_session_unauthorized: Fixture to start authentication MFA
    :param clean_up_policy: Fixture to clean up the policy created
    :param users_and_roles: Fixture to create random user with pas user rights

    """
    secrets_params = pas_general_secrets
    suffix = guid()
    folder_list, folder_name, secret_list = create_secret_inside_folder

    challenges = ["UP", ""]
    policy_result = PolicyManager.create_new_auth_profile(core_session, secrets_params['policy_name'] + suffix,
                                                          challenges, 0, 0)
    assert policy_result, f'Failed to create policy, API response result:{policy_result}'
    logger.info(f' Creating new policy:{policy_result}')
    clean_up_policy.append(policy_result)

    # Applying MFA on Folder
    result = update_folder(core_session, folder_list[0],
                           folder_name,
                           secrets_params['mfa_folder_name_update'] + suffix,
                           description=secrets_params['mfa_folder_description'],
                           policy_id=policy_result)
    assert result['success'], f'Not Able to apply MFA, API response result:: {result["Message"]} '
    logger.info(f'Applying MFA  for folder: {result}')

    # API to get new session for User A
    pas_power_user_session = users_and_roles.get_session_for_user('Privileged Access Service User')
    assert pas_power_user_session.auth_details, 'Failed to Login with PAS User'
    user_name = pas_power_user_session.auth_details['User']
    user_id = pas_power_user_session.auth_details['UserId']
    logger.info(f'{pas_power_user_session.auth_details}')
    logger.info(f'User with PAS User Rights login successfully: user_Name:{user_name}')

    # Getting password for MFA
    password = users_and_roles.get_default_user_password()

    # Api to give user permissions to folder
    user_permissions_alpha = give_user_permissions_to_folder(core_session, user_name, user_id, folder_list[0], 'View')
    assert user_permissions_alpha['success'], \
        f'Not Able to set user permissions to folder{user_permissions_alpha["Result"]}'
    logger.info(f'User Permissions to folder: {user_permissions_alpha}')

    # Api to give member permissions to folder
    member_perm_result, member_perm_success = set_member_permissions_to_folder(core_session,
                                                                               user_name,
                                                                               'View, Edit',
                                                                               user_id,
                                                                               folder_list[0])
    assert member_perm_success, f'Not Able to set member permissions to Folder: {member_perm_result}'
    logger.info(f'Member permissions to folder:{member_perm_result}')

    # MFA Authentication starts on the secret to be replaced
    mfa_authentication = pas_power_user_session.start_authentication(user_name)
    result = mfa_authentication.json()['Result']
    success = mfa_authentication.json()['success']
    assert success, f'Failed to start MFA Authentication on the secret to be replaced, API response result:{result}'
    challenge_value = result['Challenges'][0]['Mechanisms'][0]['Name']
    assert challenge_value == 'UP', f'Challenge "Password" is not set, API response result:{result}'
    logger.info(f'MFA Authentication with "Password" starts on the secret to be replaced:{mfa_authentication.json()}')

    # Advance MFA Authentication starts on the secret to be replaced
    up_result = pas_power_user_session.advance_authentication(password, challenge_index=0, mechanism_name='UP')
    mfa_result = up_result.json()
    assert mfa_result['success'], f'Failed to respond to challenge, API response result:{mfa_result["Result"]}'
    logger.info(f'MFA popups before secret gets replaced:{mfa_result}')

    # Replacing the text of the secret
    result = update_secret(pas_power_user_session,
                           secret_list[0],
                           secrets_params['mfa_secret_name_update'] + suffix,
                           secret_text=secrets_params['secret_text_replaced'],
                           policy_id=policy_result)
    assert result['success'], f'Not Able to replace the text of the secret, API response result:{result["Message"]} '
    logger.info(f'Secret gets replaced: {result}')

    # Removing MFA from secret
    result = update_secret(pas_power_user_session,
                           secret_list[0],
                           secrets_params['mfa_secret_name_update'] + suffix,
                           secret_text=secrets_params['secret_text_replaced']
                           )
    assert result['success'], f'Not Able to  remove MFA, API response result:{result["Message"]} '
    logger.info(f'Removing MFA from secret: {result}')

    # Removing MFA from folder
    result = update_folder(core_session, folder_list[0],
                           folder_name,
                           secrets_params['mfa_folder_name_update'] + suffix
                           )
    assert result['success'], f'Not Able to remove MFA, API response result:: {result["Message"]} '
    logger.info(f'Removing MFA from folder: {result}')

    # Getting details of the Secret Replaced
    get_secret_details, get_secret_success, get_secret_created_date, get_secret_text = get_secret_contents(
        core_session,
        secret_list[0])
    assert get_secret_text == secrets_params['secret_text_replaced'], \
        f'Failed to replace the secret, API response result: {get_secret_success}'
    logger.info(f'Details of the secret Replaced: {get_secret_details}')
