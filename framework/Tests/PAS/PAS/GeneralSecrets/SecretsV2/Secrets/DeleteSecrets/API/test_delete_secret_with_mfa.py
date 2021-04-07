import logging
import pytest
from Shared.API.policy import PolicyManager
from Shared.API.secret import update_secret, get_secret, give_user_permissions_to_folder, \
    set_member_permissions_to_folder, del_secret, del_secret_mfa, del_folder, create_folder, \
    create_text_secret_within_folder
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_delete_mfa_policy_on_secret(
        core_session,
        pas_general_secrets,
        clean_up_policy,
        users_and_roles):
    """
        C283962: MFA policy on Secret, verify challenged
    :param core_session: Authenticated Centrify session
    :param pas_general_secrets: Fixture to read secrets data from yaml file
    :param clean_up_policy: Fixture to cleanup the policy created
    :param users_and_roles: Fixture to create new user with restricted rights
    """
    secrets_params = pas_general_secrets
    suffix = guid()

    # Create a folder A
    secret_folder_success, secret_folder_parameters, secret_folder_id = create_folder(
        core_session,
        secrets_params['mfa_folder_name'] + suffix,
        secrets_params['description'])
    assert secret_folder_success, f'Failed to create a folder {secret_folder_id}'
    logger.info(f' Folder created successfully: {secret_folder_success} ')
    secret_folder_parameters['ID'] = secret_folder_id

    # Create a secret under A folder
    added_secret_success, added_secret_id = create_text_secret_within_folder(core_session,
                                                                             secrets_params['mfa_secret_name'] + suffix,
                                                                             secrets_params['secret_text'],
                                                                             secrets_params['secret_description'],
                                                                             secret_folder_id)
    assert added_secret_success, f"Added Secret Failed {added_secret_id}"
    logger.info(f'Added secrets info {added_secret_success, added_secret_id}')

    # Getting details of the secret
    found_secret = get_secret(core_session, added_secret_id)
    assert found_secret['success'], \
        f'Failed to get the details of the secret , API response result:{found_secret["Message"]}'
    logger.info(f'Getting details of the secret: {found_secret}')
    secret_name = found_secret['Result']['SecretName']

    challenges = ["UP", ""]
    # Creating new policy
    policy_result = PolicyManager.create_new_auth_profile(core_session, secrets_params['policy_name'] + suffix,
                                                          challenges, 0, 0)
    assert policy_result, f'Failed to create policy, API response result:{policy_result}'
    logger.info(f' Creating new policy:{policy_result}')
    clean_up_policy.append(policy_result)

    # Applying MFA on Secret
    result = update_secret(core_session,
                           added_secret_id, secret_name,
                           description=secrets_params['mfa_secret_description'],
                           policy_id=policy_result)
    assert result['success'], f' Failed to apply MFA on the secret, API response result:{result["Message"]} '
    logger.info(f'MFA Applied on the secret: {result}')

    # Getting new session for User
    pas_power_user_session = users_and_roles.get_session_for_user('Privileged Access Service Power User')
    assert pas_power_user_session.auth_details, 'Failed to Login with PAS Power User'
    user_name = pas_power_user_session.auth_details['User']
    user_id = pas_power_user_session.auth_details['UserId']
    logger.info(f'User with PAS Power User Rights login successfully: user_Name: {user_name}')

    # Api to give user permissions to folder
    user_permissions_result = give_user_permissions_to_folder(core_session,
                                                              user_name,
                                                              user_id,
                                                              secret_folder_id,
                                                              'Grant,View,Delete')
    assert user_permissions_result, f'Failed to set user permissions to folder{user_permissions_result}'
    logger.info(f'User Permissions to folder: {user_permissions_result}')

    # Api to set DELETE permissions to folder
    member_perm_result, member_perm_success = set_member_permissions_to_folder(core_session,
                                                                               user_name,
                                                                               'Grant,View,Delete,Retrieve',
                                                                               user_id,
                                                                               secret_folder_id)
    assert member_perm_success, f'Failed to set member permissions to Folder{member_perm_result["Result"]}'
    logger.info(f'Member permissions to folder:{member_perm_result}')

    # Delete secret with Mfa Authentication
    del_success, del_result = del_secret(pas_power_user_session, added_secret_id)

    # StartChallenge MFA Authentication
    session, mechanism = pas_power_user_session.start_mfa_authentication(user_name, del_result['ChallengeId'])

    # AdvanceAuthentication MFA to Password
    result = pas_power_user_session.advance_authentication(answer=pas_power_user_session.user.user_input.password,
                                                           session_id=session, mechanism_id=mechanism)
    assert result, "Password Authentication Failed"
    logger.info(f'Advance authentication: {result}')

    # After Authentication of MFA delete the secret under folder
    del_secret_success, del_secret_result = del_secret_mfa(
        pas_power_user_session, added_secret_id, ChallengeStateId=del_result['ChallengeId'])
    assert del_secret_success, f'User: {user_name} failed to delete secret from this folder: {secret_folder_id}'
    logger.info(f'User: {user_name} deleted secret: '
                f'{added_secret_id} successfully from this folder: {secret_folder_id}')

    # Delete folder
    del_folder_res = del_folder(core_session, secret_folder_id)
    assert del_folder_res, f'User: {user_name} failed to delete folder: {secret_folder_id}'
    logger.info(f'User: {user_name} successfully deleted folder: {secret_folder_id}')
