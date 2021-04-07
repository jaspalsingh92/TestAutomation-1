import pytest
import logging
from Shared.API.policy import PolicyManager
from Shared.API.secret import update_secret, get_secret_contents, set_users_effective_permissions
from Utils.guid import guid
from Shared.API.users import UserManager

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_update_retrieve_replace_activity_logged(core_session,
                                                 added_secrets,
                                                 pas_general_secrets,
                                                 users_and_roles,
                                                 clean_up_policy):
    """
            C3071: Update, retrieve, replace activity logged
    :param core_session:  Authenticated Centrify Session
    :param added_secrets: Fixture to create text type secret & yield secret id, secret_name
    :param pas_general_secrets: Fixture to read secret data from yaml file
    :param users_and_roles: Fixture to create New user with PAS Power Rights
    :param clean_up_policy: Fixture to clean up the policy created
    """
    secret_suffix = guid()
    added_text_secret_id, added_text_secret_name = added_secrets
    secrets_params = pas_general_secrets

    # API to get new session for User A
    pas_power_user_session = users_and_roles.get_session_for_user('Privileged Access Service User')
    assert pas_power_user_session.auth_details, 'Failed to Login with PAS User'
    user_name = pas_power_user_session.auth_details['User']
    user_id = pas_power_user_session.auth_details['UserId']
    logger.info(f'User with PAS User Rights login successfully: user_Name:{user_name}')

    # Api to give user permissions to secrets
    set_permission_result, set_permission_success = set_users_effective_permissions(core_session,
                                                                                    user_name,
                                                                                    'View,Grant',
                                                                                    user_id,
                                                                                    added_text_secret_id[0])
    assert set_permission_success, f'Failed to set permission: {set_permission_result}'
    logger.info(f'Setting permission:{set_permission_result}{set_permission_success}')

    # Retrieving details(text) of the secret
    get_secret_details, get_secret_success, get_secret_created_date, get_secret_text = get_secret_contents(
        core_session,
        added_text_secret_id[0])
    assert get_secret_success, f'Failed to retrieve the secret:{get_secret_text}'
    logger.info(f' Retrieved secret details: {get_secret_details} ')

    # Api to create new policy
    policy_result = PolicyManager.create_new_auth_profile(core_session,
                                                          secrets_params['policy_name'] + secret_suffix,
                                                          ["UP", None],
                                                          None,
                                                          "30")
    assert policy_result is not None, f'Failed to create policy:{policy_result}'
    logger.info(f' Creating new policy:{policy_result}')
    clean_up_policy.append(policy_result)

    # Api to update secret(assign policy & update name)
    policy_assigned = update_secret(core_session,
                                    added_text_secret_id[0],
                                    secrets_params['updated_secret_name'] + secret_suffix,
                                    policy_id=policy_result)
    assert policy_assigned['success'], f'Failed to assign policy to secret: {policy_assigned["Result"]["ID"]}'
    logger.info(f' Policy assigned to text type secret: {policy_assigned}')

    # Api to retrieve the activity of the secret
    rows_result = UserManager.get_secret_activity(core_session, added_text_secret_id[0])
    assert rows_result, f'Failed to fetch Secret updated details & activity fetched:{rows_result}'
    logger.info(f'Activity list:{rows_result}')

    assert 'updated the secret' in rows_result[0]["Detail"], f'Failed to update the secret:{rows_result[0]["Detail"]}'
    assert 'viewed the secret' in rows_result[1]["Detail"], f'Failed to retrieve the secret :{rows_result[1]["Detail"]}'
    added_secret_status = False
    added_permissions_status = False
    for rows in rows_result:
        if 'added a secret' in rows['Detail']:
            added_secret_status = True
    assert added_secret_status, f'Failed to add secret: {added_secret_status}'
    for rows in rows_result:
        if 'granted User' in rows['Detail']:
            added_permissions_status = True
    assert added_permissions_status, f'Failed to add permissions: {added_permissions_status}'

    # Api to remove policy from the secret
    policy_assigned = update_secret(core_session,
                                    added_text_secret_id[0],
                                    added_text_secret_name)
    assert policy_assigned['success'], f'Failed to remove policy from secret: {policy_assigned["Result"]["ID"]}'
    logger.info(f' Policy removed from secret: {policy_assigned}')
