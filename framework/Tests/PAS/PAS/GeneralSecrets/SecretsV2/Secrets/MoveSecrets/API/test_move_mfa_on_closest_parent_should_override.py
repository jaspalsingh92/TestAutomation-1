import pytest
import logging
from Shared.API.policy import PolicyManager
from Shared.API.secret import update_folder, create_text_secret_within_folder, move_secret_by_using_mfa, \
    give_user_permissions_to_folder, set_member_permissions_to_folder, move_secret
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.pas_broken
@pytest.mark.api
@pytest.mark.bhavna
def test_move_mfa_on_closest_parent_should_override(
        core_session,
        pas_general_secrets,
        create_folder_inside_folder,
        cleanup_secrets_and_folders,
        clean_up_policy,
        users_and_roles):
    """
         C283938: MFA on closest parent should override MFA on higher levels
    :param core_session:  Authenticated Centrify Session
    :param pas_general_secrets: Fixture to read secret data from yaml file
    :param create_folder_inside_folder: Fixture to create nested Folder & yields folder & sub folder related details
    :param cleanup_secrets_and_folders: Fixture to cleanup the secrets & folders created.
    :param clean_up_policy: Fixture to clean up the policy created
    :param users_and_roles: Fixture to create New user with PAS Power Rights
    """
    secrets_params = pas_general_secrets
    suffix = guid()
    parent_folder_info, nested_folder_info, nested_folder_id = create_folder_inside_folder
    parent_folder_id = parent_folder_info['ID']
    parent_folder_name = parent_folder_info['Name']
    secret_list = cleanup_secrets_and_folders[0]
    challenges1 = ["UP", ""]
    challenges2 = ["SQ", ""]

    # Api to create secret within folder
    added_text_secret_success, secret_id = create_text_secret_within_folder(core_session,
                                                                            secrets_params['secret_name'] + suffix,
                                                                            secrets_params['secret_text'],
                                                                            secrets_params['secret_description'],
                                                                            nested_folder_id)
    assert added_text_secret_success, f'Unable to create secret {secret_id}'
    logger.info(f'Secret Created successfully: {added_text_secret_success}')
    secret_list.append(secret_id)

    # creating a new Authentication profile for nested folder
    policy_result = PolicyManager.create_new_auth_profile(core_session, secrets_params['policy_name'] + suffix,
                                                          challenges1, 0, 0)
    assert policy_result, f'Failed to create policy, API response result:{policy_result}'
    logger.info(f' Creating new policy:{policy_result}')
    clean_up_policy.append(policy_result)

    # creating another Authentication profile for parent folder
    policy_result_v1 = PolicyManager.create_new_auth_profile(core_session,
                                                             secrets_params['policy_name'] + "V1" + suffix,
                                                             challenges2, 0, 0)
    assert policy_result_v1, f'Failed to create policy, API response result:{policy_result_v1}'
    logger.info(f' Creating new policy:{policy_result_v1}')
    clean_up_policy.append(policy_result_v1)

    # Applying MFA on Nested Folder
    result = update_folder(core_session, nested_folder_id,
                           nested_folder_info['Name'],
                           nested_folder_info['Name'],
                           description=secrets_params['mfa_folder_description'],
                           policy_id=policy_result)
    assert result['success'], f'Not Able to apply MFA, API response result:: {result["Message"]} '
    logger.info(f'Applying MFA  for folder: {result}')

    # Applying MFA on Parent Folder
    result = update_folder(core_session, parent_folder_id,
                           parent_folder_name,
                           parent_folder_name,
                           description=secrets_params['mfa_folder_description'],
                           policy_id=policy_result_v1)
    assert result['success'], f'Not Able to apply MFA, API response result:: {result["Message"]} '
    logger.info(f'Applying MFA  for folder: {result}')

    # Getting User with PAS Power User rights
    pas_user_session = users_and_roles.get_session_for_user('Privileged Access Service Power User')
    assert pas_user_session.auth_details, 'Failed to Login with PAS Power User'
    user_name = pas_user_session.auth_details['User']
    user_id = pas_user_session.auth_details['UserId']
    logger.info(f'User with PAS Power User Rights login successfully: user_Name:{user_name}')

    # Api to give user permissions to folder
    user_permissions_result = give_user_permissions_to_folder(core_session,
                                                              user_name, user_id, parent_folder_id, 'View')
    assert user_permissions_result, f'Not Able to set user permissions to folder{user_permissions_result}'
    logger.info(f'User Permissions to folder: {user_permissions_result}')

    # Api to give member permissions to folder
    member_perm_result, member_perm_success = set_member_permissions_to_folder(core_session,
                                                                               user_name,
                                                                               'View, Edit',
                                                                               user_id,
                                                                               parent_folder_id)
    assert member_perm_success, f'Not Able to set member permissions to Folder{member_perm_result["Result"]}'
    logger.info(f'Member permissions to folder:{member_perm_result}')

    # Move Secret with Mfa Authentication
    result_secret = move_secret(pas_user_session, secret_id)

    # StartChallenge MFA Authentication
    session, mechanism = pas_user_session.start_mfa_authentication(user_name, result_secret['Result']['ChallengeId'])

    # AdvanceAuthentication MFA to Password
    advance_auth_result = pas_user_session.advance_authentication(answer=pas_user_session.user.user_input.password,
                                                                  session_id=session, mechanism_id=mechanism)
    mfa_result = advance_auth_result.json()
    assert advance_auth_result, f'Password Authentication Failed, API response result:{mfa_result["success"]}'
    logger.info(f'successfully applied password authentication: {mfa_result}')

    # After Authenticating of MFA move secret with challenge password
    moved_success, moved_result = move_secret_by_using_mfa(pas_user_session, secret_id,
                                                           ChallengeStateId=result_secret['Result']['ChallengeId'])
    assert moved_success, f'User: {user_name} Failed to move secret with closest parent challenge: {moved_result}'
    logger.info(f'User: {user_name} successfully moved secret with closest parent challenge: {moved_result}')

    # Removing MFA on Nested Folder
    result = update_folder(core_session, nested_folder_id,
                           nested_folder_info['Name'],
                           nested_folder_info['Name'],
                           description=secrets_params['mfa_folder_description'])
    assert result['success'], f'Failed to remove MFA, API response result: {result["Message"]} '
    logger.info(f'Removing MFA for Nested folder: {result}')

    # Removing MFA on Parent Folder
    result = update_folder(core_session, parent_folder_id,
                           parent_folder_name,
                           parent_folder_name,
                           description=secrets_params['mfa_folder_description'])
    assert result['success'], f'Failed to remove MFA, API response result: {result["Message"]} '
    logger.info(f'Removing MFA for Parent folder: {result}')
