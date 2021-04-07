import pytest
import logging
from Shared.API.policy import PolicyManager
from Shared.API.secret import give_user_permissions_to_folder, get_folder_activity, update_folder
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_set_update_policy_verify_displayed_on_activity(core_session,
                                                        create_secret_folder,
                                                        users_and_roles,
                                                        pas_general_secrets,
                                                        clean_up_policy):
    """
            C3069: test method to Set/Update policy verify it’s displayed on Activity

    :param core_session: Authenticated Centrify Session
    :param create_secret_folder: Fixture to create secret folder & yields folder details
    :param users_and_roles: Fixture to create a random user with PAS Power rights
    :param pas_general_secrets: Fixture to read secrets related data from yaml
    :param clean_up_policy: Fixture to cleanup the policy created

    """
    secrets_params = pas_general_secrets
    suffix = guid()
    secret_folder_details = create_secret_folder
    folder_id = secret_folder_details['ID']
    folder_name = secret_folder_details['Name']

    challenges = ["UP", ""]
    policy_result = PolicyManager.create_new_auth_profile(core_session, secrets_params['policy_name'] + suffix,
                                                          challenges, 0, 0)
    assert policy_result, f'Failed to create policy, API response result:{policy_result}'
    logger.info(f' Creating new policy:{policy_result}')
    clean_up_policy.append(policy_result)

    # Updating the Folder(Applying MFA)
    result = update_folder(core_session,
                           folder_id,
                           folder_name,
                           folder_name,
                           description=secrets_params['mfa_folder_description'],
                           policy_id=policy_result)
    assert result['success'], f'Not Able to apply MFA on folder, API response result: {result["Message"]} '
    logger.info(f'MFA Applied on Folder: {result}')

    # API to get new session for User A
    pas_user_session = users_and_roles.get_session_for_user('Privileged Access Service User')
    assert pas_user_session.auth_details, 'Failed to Login with PAS User'
    user_name_user = pas_user_session.auth_details['User']
    user_id_user = pas_user_session.auth_details['UserId']
    logger.info(f'User with PAS User Rights login successfully: user_Name:{user_name_user}')

    # Api to give user permissions to folder
    permissions_user = give_user_permissions_to_folder(core_session,
                                                       user_name_user,
                                                       user_id_user,
                                                       folder_id,
                                                       'View')
    assert permissions_user['success'], \
        f'Not Able to set user permissions to folder, API response result:{permissions_user["Result"]}'
    logger.info(f'User Permissions to folder: {permissions_user}')

    # API to get new session for User A
    pas_admin_session = users_and_roles.get_session_for_user('Privileged Access Service Administrator')
    assert pas_admin_session.auth_details, 'Failed to Login with PAS Admin'
    user_name_admin = pas_admin_session.auth_details['User']
    user_id_admin = pas_admin_session.auth_details['UserId']
    logger.info(f'User with PAS Admin Rights login successfully: user_Name:{user_name_admin}')

    # Api to give user permissions to folder
    permissions_admin = give_user_permissions_to_folder(core_session,
                                                        user_name_admin,
                                                        user_id_admin,
                                                        folder_id,
                                                        'View')
    assert permissions_admin['success'], \
        f'Not Able to set user permissions to folder, API response result:{permissions_admin["Result"]}'
    logger.info(f'User Permissions to folder: {permissions_admin}')

    # API to get new session for User A
    pas_power_user_session = users_and_roles.get_session_for_user('Privileged Access Service Power User')
    assert pas_power_user_session.auth_details, 'Failed to Login with PAS Power User'
    user_name_power_user = pas_power_user_session.auth_details['User']
    user_id_power_user = pas_power_user_session.auth_details['UserId']
    logger.info(f'User with PAS Power User Rights login successfully: user_Name:{user_name_power_user}')

    # Api to give user permissions to folder
    permissions_admin = give_user_permissions_to_folder(core_session,
                                                        user_name_power_user,
                                                        user_id_power_user,
                                                        folder_id,
                                                        'View')
    assert permissions_admin['success'], \
        f'Not Able to set user permissions to folder, API response result:{permissions_admin["Result"]}'
    logger.info(f'User Permissions to folder: {permissions_admin}')

    # Updating the Folder(Removing MFA)
    result = update_folder(core_session,
                           folder_id,
                           folder_name,
                           folder_name
                           )
    assert result['success'], f'Not Able to apply MFA on folder, API response result: {result["Message"]} '
    logger.info(f'MFA Applied on Folder: {result}')

    # Getting activity of the folder(updating folder permissions multiple times)
    activity_rows = get_folder_activity(core_session, folder_id)
    verify_folder_update = 'updated the folder'
    verify_folder_permissions_user = f'granted User "{user_name_user}" to have "View" permissions on'
    verify_folder_permissions_power_user = f'granted User "{user_name_power_user}" to have "View" permissions on'
    verify_folder_permissions_admin = f'granted User "{user_name_admin}" to have "View" permissions on'
    assert verify_folder_permissions_user in activity_rows[3]['Detail'], \
        f'Failed to verify the activity, API response result::{activity_rows}'
    assert verify_folder_permissions_power_user in activity_rows[1]['Detail'], \
        f'Failed to verify the activity:{activity_rows}'
    assert verify_folder_permissions_admin in activity_rows[2]['Detail'], \
        f'Failed to verify the activity, API response result::{activity_rows}'
    assert verify_folder_update in activity_rows[0]['Detail'], \
        f'Failed to verify the activity, API response result::{activity_rows}'
    logger.info(f'Replace activity found for secret, API response result: {activity_rows}')
