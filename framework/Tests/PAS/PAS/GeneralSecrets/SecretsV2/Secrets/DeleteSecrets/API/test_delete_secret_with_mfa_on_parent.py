import logging
import pytest
from Shared.API.policy import PolicyManager
from Shared.API.secret import give_user_permissions_to_folder, set_member_permissions_to_folder, \
    del_secret, del_secret_mfa, update_folder
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_delete_secret_with_mfa_on_parent(
        core_session,
        pas_general_secrets,
        clean_up_policy,
        users_and_roles,
        create_secret_inside_folder,
        cleanup_secrets_and_folders):
    """
         C283963: MFA policy on Parent folder, verify challenged
    :param core_session: Authenticated Centrify Session
    :param pas_general_secrets: fixture to read secrets related data from yaml file
    :param clean_up_policy: Fixture to cleanup the policy created
    :param users_and_roles: Fixture to create new user with restricted rights
    :param create_secret_inside_folder: Fixture to create secrets inside folder & yields secrets & folders data
    :param cleanup_secrets_and_folders: Fixture to cleanup the secrets & folders created
    """
    secrets_params = pas_general_secrets
    suffix = guid()
    folder_id_list, folder_name, secret_id_list = create_secret_inside_folder
    secrets_list = cleanup_secrets_and_folders[0]

    challenges = ["UP", ""]
    # Creating new policy
    policy_result = PolicyManager.create_new_auth_profile(core_session, secrets_params['policy_name'] + suffix,
                                                          challenges, 0, 0)
    assert policy_result, f'Failed to create policy, API response result:{policy_result}'
    logger.info(f' Creating new policy:{policy_result}')
    clean_up_policy.append(policy_result)

    # Updating the Folder(Applying MFA)
    result = update_folder(core_session,
                           folder_id_list[0],
                           folder_name,
                           folder_name,
                           description=secrets_params['mfa_folder_description'],
                           policy_id=policy_result)
    assert result['success'], f' Failed to apply MFA on folder, API response result: {result["Message"]} '
    logger.info(f'MFA Applied on Folder: {result}')

    # Getting new session for User A
    pas_power_user_session = users_and_roles.get_session_for_user('Privileged Access Service Power User')
    assert pas_power_user_session.auth_details, 'Failed to Login with PAS Power User'
    user_name = pas_power_user_session.auth_details['User']
    user_id = pas_power_user_session.auth_details['UserId']
    logger.info(f'User with PAS Power User Rights login successfully: user_Name: {user_name}')

    # Api to give user permissions to folder
    user_permissions_result = give_user_permissions_to_folder(core_session,
                                                              user_name,
                                                              user_id,
                                                              folder_id_list[0],
                                                              'View')
    assert user_permissions_result, f'Failed to set user permissions to folder{user_permissions_result}'
    logger.info(f'User Permissions to folder: {user_permissions_result}')

    # Api to set DELETE permissions folder
    member_perm_result, member_perm_success = set_member_permissions_to_folder(core_session,
                                                                               user_name,
                                                                               'Grant,View,Delete,Retrieve',
                                                                               user_id,
                                                                               folder_id_list[0])
    assert member_perm_success, f'Failed to set member permissions to Folder{member_perm_result["Result"]}'
    logger.info(f'Member permissions to folder:{member_perm_result}')

    # Delete secret with Mfa Authentication
    del_success, del_result = del_secret(pas_power_user_session, secret_id_list[0])

    # StartChallenge MFA Authentication
    session, mechanism = pas_power_user_session.start_mfa_authentication(user_name, del_result['ChallengeId'])

    # AdvanceAuthentication MFA to Password
    result = pas_power_user_session.advance_authentication(answer=pas_power_user_session.user.user_input.password,
                                                           session_id=session, mechanism_id=mechanism)
    assert result, "Password Authentication Failed"

    # After Authentication of MFA delete the secret under folder
    del_secret_success, del_secret_result = del_secret_mfa(pas_power_user_session, secret_id_list[0],
                                                           ChallengeStateId=del_result['ChallengeId'])
    assert del_secret_success, f'Failed to delete secret with MFA {del_secret_result} with User: {user_name}'
    logger.info(f'Successfully deleted secret with MFA {del_secret_result} for User: {user_name} ')
    secrets_list.remove(secret_id_list[0])

    # Updating the Folder(Removing MFA)
    result = update_folder(core_session,
                           folder_id_list[0],
                           folder_name,
                           folder_name,
                           description=secrets_params['mfa_folder_description'])
    assert result['success'], f'Failed to remove MFA on folder, API response result: {result["Message"]} '
    logger.info(f'Successfully Removed MFA on Folder: {result}')
