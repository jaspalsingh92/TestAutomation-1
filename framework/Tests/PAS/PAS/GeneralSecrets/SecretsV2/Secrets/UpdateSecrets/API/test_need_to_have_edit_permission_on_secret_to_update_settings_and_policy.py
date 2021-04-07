import pytest
import logging
from Shared.API.policy import PolicyManager
from Shared.API.secret import set_users_effective_permissions, update_secret
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_need_to_have_edit_permission_on_secret_to_update_settings_and_policy(core_session, users_and_roles,
                                                                              added_secrets_file,
                                                                              added_secrets,
                                                                              pas_general_secrets, clean_up_policy):
    """
    test method to set permissions on secrets(with Edit/Without Edit) to update the settings & policy.

    :param core_session:  Authenticated Centrify Session
    :param users_and_roles: Fixture to create New user with PAS Power Rights
    :param added_secrets_file: Fixture to create file type secret & yield secret id
    :param added_secrets: Fixture to create text type secret & yield secret id, secret_name
    :param pas_general_secrets: Fixture to read secret data from yaml file
    :param clean_up_policy: Fixture to clean up the policy created

    """
    added_file_secret_id = added_secrets_file
    added_text_secret_id, added_text_secret_name = added_secrets
    secrets_params = pas_general_secrets
    secret_prefix = guid()
    pas_power_user = users_and_roles.get_user('Privileged Access Service Power User')
    user_name = pas_power_user.get_login_name()
    user_id = pas_power_user.get_id()

    # API to set user permissions (Edit)for file_type_secret"""
    file_type_secret_result, file_type_secret_success = set_users_effective_permissions(core_session,
                                                                                        user_name,
                                                                                        'View,Grant,Edit',
                                                                                        user_id,
                                                                                        added_file_secret_id)
    assert file_type_secret_success, f'setting permissions for file type secret failed: {file_type_secret_result}'
    logger.info(f'Setting permissions for file type secret: {file_type_secret_success}')

    # API to set user permissions (without Edit)for text_type_secret"""
    text_type_secret_result, text_type_secret_success = set_users_effective_permissions(core_session,
                                                                                        user_name,
                                                                                        'View,Grant',
                                                                                        user_id,
                                                                                        added_text_secret_id[0])
    assert text_type_secret_success, f'setting permissions for text type secret failed:{text_type_secret_result}'
    logger.info(f'Setting permissions for text type secret: : {text_type_secret_success}')

    # API to get new session for User A"""
    pas_power_user_session = users_and_roles.get_session_for_user('Privileged Access Service Power User')
    assert pas_power_user_session.auth_details, 'Failed to Login with PAS Power User'
    logger.info(f'User with PAS Power User Rights login successfully :user_Name: {user_name}'
                f' & Password: {pas_power_user.get_password()} ')

    # Api to update the name of the secret(file_type)
    result = update_secret(pas_power_user_session,
                           added_file_secret_id,
                           secret_prefix + secrets_params['updated_secret_name'])
    assert result['success'], f'Not Able to update the settings  {result["Result"]} '
    logger.info(f'Updating the settings for secret:  {result["success"]} & {result["Exception"]}')

    # Api to create new policy
    policy_result = PolicyManager.create_new_auth_profile(core_session,
                                                          secret_prefix + secrets_params['policy_name'],
                                                          ["UP",
                                                           None],
                                                          None,
                                                          "30")
    assert policy_result is not None, f'Failed to create policy:{policy_result}'
    logger.info(f' Creating new policy:{policy_result}')
    clean_up_policy.append(policy_result)

    # Api to assign policy to file type secret
    policy_assigned = update_secret(pas_power_user_session,
                                    added_file_secret_id,
                                    added_text_secret_name,
                                    policy_id=policy_result)
    assert policy_assigned['success'], f'Failed to assign policy to secret: {policy_assigned["Result"]["ID"]}'
    logger.info(f' Policy assigned to secret: {policy_assigned}')

    # Api to update settings for text type secret
    result = update_secret(pas_power_user_session, added_text_secret_id[0],
                           secret_prefix + secrets_params['updated_secret_name'])
    assert result['success'] is False, f'Able to update the settings: {result["Message"]} '
    logger.info(f'Not able to Update settings for secret: {result}')

    # Api to assign policy for text type secret
    policy_assigned = update_secret(pas_power_user_session,
                                    added_text_secret_id[0],
                                    added_text_secret_name,
                                    policy_id=policy_result)
    assert policy_assigned['success'] is False, f'Able to assign policy to secret: {policy_assigned["Message"]}'
    logger.info(f' Not able to assign Policy to text type secret: {policy_assigned}')

    # Api to Remove policy for file type secret
    policy_removed = update_secret(pas_power_user_session,
                                   added_file_secret_id,
                                   added_text_secret_name)
    assert policy_removed['success'], f'Failed to remove policy to secret: {policy_removed["Message"]}'
    logger.info(f'Successfully removed Policy to text type secret: {policy_removed}')
