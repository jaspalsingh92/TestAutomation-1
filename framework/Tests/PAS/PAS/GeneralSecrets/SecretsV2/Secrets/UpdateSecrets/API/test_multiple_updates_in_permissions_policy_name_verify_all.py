import pytest
import logging
from Shared.API.policy import PolicyManager
from Shared.API.secret import set_users_effective_permissions, update_secret
from Utils.guid import guid
from Shared.API.users import UserManager

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_multiple_updates_in_permissions_policy_name_verify_all_2(core_session,
                                                                  added_secrets,
                                                                  pas_general_secrets,
                                                                  users_and_roles,
                                                                  clean_up_policy):
    """
    test method to verify multiple updates like (permissions, policy, name ..) for a secret
    :param core_session:  Authenticated Centrify Session
    :param added_secrets: Fixture to create text type secret & yield secret id, secret_name
    :param pas_general_secrets: Fixture to read secret data from yaml file
    :param users_and_roles: Fixture to create New user with PAS Power Rights
    :param clean_up_policy: Fixture to clean up the policy created
    """
    secret_prefix = guid()
    added_text_secret_id, added_text_secret_name = added_secrets

    secrets_params = pas_general_secrets
    application_management_user = users_and_roles.get_user('Privileged Access Service Power User')
    user_name = application_management_user.get_login_name()
    user_id = application_management_user.get_id()

    # API to set user permissions for text_type_secret
    set_permissions_result, set_permissions_success = set_users_effective_permissions(core_session,
                                                                                      user_name,
                                                                                      'View,Grant,Edit',
                                                                                      user_id,
                                                                                      added_text_secret_id[0])
    assert set_permissions_success, f'setting permissions for file type secret failed: {set_permissions_result}'
    logger.info(f'setting permissions for text type secret: {set_permissions_success} {set_permissions_result}')

    # Api to create new policy
    policy_result = PolicyManager.create_new_auth_profile(core_session,
                                                          secret_prefix + secrets_params['policy_name'],
                                                          ["UP", None],
                                                          None,
                                                          "30")
    assert policy_result is not None, f'Failed to create policy:{policy_result}'
    logger.info(f' Creating new policy:{policy_result}')
    clean_up_policy.append(policy_result)

    # Api to assign policy to the secret
    policy_assigned = update_secret(core_session,
                                    added_text_secret_id[0],
                                    added_text_secret_name,
                                    policy_id=policy_result)
    assert policy_assigned['success'], f'Failed to assign policy to secret: {policy_assigned["Result"]["ID"]}'
    logger.info(f' Policy assigned to text type secret: {policy_assigned}')

    # Api to update settings(secret_name) of the secret
    result = update_secret(core_session, added_text_secret_id[0],
                           secret_prefix + secrets_params['updated_secret_name'])
    assert result['success'], f'Not Able to update the settings  {result["Result"]} '
    logger.info(f'Updating the settings for secret:  {result["success"]} & {result["Exception"]}')

    # Api to retrieve the activity of the secret
    rows_result = UserManager.get_secret_activity(core_session, added_text_secret_id[0])
    assert rows_result is not None, f'Unable to fetch Secret updated details & activity fetched:{rows_result}'
    logger.info(f'activity list:{rows_result}')

    verify_name = 'update_secret1'
    verify_permissions = 'View , Grant , Edit'
    permissions_updated = False
    assert verify_name in rows_result[0]["Detail"], f'Unable to update the name:{rows_result[0]["Detail"]}'
    logger.info(f'Secret Updated details: {rows_result[0]["Detail"]}')
    for x in rows_result:
        if verify_permissions in x['Detail']:
            permissions_updated = True
    assert permissions_updated, f'Unable to update the permissions: {permissions_updated}'
