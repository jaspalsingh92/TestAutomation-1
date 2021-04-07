import logging
import pytest
from Shared.API.policy import PolicyManager
from Shared.API.secret import give_user_permissions_to_folder, update_folder, get_folder
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_edit_folder_permission_to_update_settings_and_policy(core_session,
                                                              create_secret_folder,
                                                              pas_general_secrets,
                                                              users_and_roles,
                                                              cleanup_secrets_and_folders,
                                                              clean_up_policy):
    """
        C3032:test method to login with cloud admin
        1) Enable Edit folder permission for UserA,
        2) Login with User A
        3) Update the Settings and Policy on the folder and
        4) Verify that you can edit settings and policy
    :param core_session: Authenticated Centrify session
    :param create_secret_folder: Fixture to create secret inside folder & yields secret & folder details
    :param pas_general_secrets: Fixture to read secrets related data from yaml file
    :param users_and_roles: Fixture to create random user with PAS Power Rights
    :param cleanup_secrets_and_folders: Fixture to cleanup the secrets & folders created
    :param clean_up_policy: Fixture to cleanup the policy created
    """
    secret_folder_details = create_secret_folder
    folder_id = secret_folder_details['ID']
    folder_name = secret_folder_details['Name']
    folder_prefix = guid()
    folder_params = pas_general_secrets

    # API to get new session for User A
    pas_power_user_session = users_and_roles.get_session_for_user('Privileged Access Service Power User')
    assert pas_power_user_session.auth_details is not None, 'Failed to Login with PAS Power User'
    user_name = pas_power_user_session.auth_details['User']
    user_id = pas_power_user_session.auth_details['UserId']
    logger.info(f'User with PAS Power User Rights login successfully: user_Name: {user_name}')

    # Api to create new policy
    policy_result = PolicyManager.create_new_auth_profile(core_session,
                                                          folder_prefix + folder_params['policy_name_new'],
                                                          ["UP", None],
                                                          None,
                                                          "30")
    assert policy_result is not None, f'Failed to create policy:{policy_result}'
    logger.info(f' Creating new policy:{policy_result}')
    clean_up_policy.append(policy_result)

    # Api to give user permissions to folder(EDIT Enabled)
    user_permissions_result = give_user_permissions_to_folder(core_session, user_name, user_id, folder_id,
                                                              'View,Edit')
    assert user_permissions_result, f'Not Able to set user permissions to folder{user_permissions_result}'
    logger.info(f'User Permissions to folder: {user_permissions_result}')

    # Updating settings & policy of the folder created
    result = update_folder(pas_power_user_session, folder_id,
                           folder_name,
                           folder_params['mfa_folder_name_update']+folder_prefix,
                           description=folder_params['mfa_folder_description'],
                           policy_id=policy_result)
    assert result['success'], f'Updating settings & policy Failed: {result["Message"]} '
    logger.info(f'Updating settings & policy: {result["success"]} {result}')

    # Getting details of the Folder updated
    result_folder = get_folder(core_session, folder_id)
    logger.info(f'Updated Folder details: {result_folder}')
    description_updated = result_folder["Result"]["Results"][0]["Row"]["Description"]
    name_updated = result_folder["Result"]["Results"][0]["Row"]["Name"]
    assert 'MFAOnParentFolderUpdate' in name_updated, \
        f'Failed to update the name{result_folder["Result"]["Results"][0]["Row"]["Name"]}'
    assert 'mfa_description' in description_updated, \
        f'Failed to update the description{result_folder["Result"]["Results"][0]["Row"]["Description"]}'

    # Removing policy of the folder
    result = update_folder(pas_power_user_session, folder_id,
                           folder_name,
                           folder_params['mfa_folder_name_update'] + folder_prefix,
                           description=folder_params['mfa_folder_description'])
    assert result['success'], f'Updating settings & policy Failed: {result["Message"]}'
    logger.info(f'Updating settings & policy: {result["success"]} {result}')
