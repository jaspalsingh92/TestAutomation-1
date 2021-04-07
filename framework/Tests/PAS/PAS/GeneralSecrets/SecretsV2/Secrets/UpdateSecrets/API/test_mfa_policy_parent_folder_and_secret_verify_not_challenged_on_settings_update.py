import logging
import pytest
from Shared.API.policy import PolicyManager
from Shared.API.secret import update_secret, get_secret_contents, set_users_effective_permissions, update_folder, \
    get_folder
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_mfa_policy_parent_folder_and_secret_verify_not_challenged_on_settings_update(
        core_session,
        pas_general_secrets,
        users_and_roles,
        create_secret_inside_folder,
        clean_up_policy):
    """
    test method to verify that mfa does not exist on updating the settings & policy for an existing
    parent folder "MFAOnParentFolder" & secret "MFAOnSecrets" with already assigned
    mfa for that folder & secret

    :param core_session:  Authenticated Centrify Session
    :param pas_general_secrets: Fixture to read secret data from yaml file
    :param create_secret_inside_folder: Fixture to create secret "MFAOnSecret" inside folder "MFAOnParentFolder"
    :param users_and_roles: Fixture to create New user with PAS Power Rights
    :param clean_up_policy: Fixture to clean up the policy created
    """
    secrets_params = pas_general_secrets
    prefix = guid()
    folder_list, folder_name, secret_list = create_secret_inside_folder
    pas_power_user = users_and_roles.get_user('Privileged Access Service Power User')
    user_name = pas_power_user.get_login_name()
    user_id = pas_power_user.get_id()

    text_type_secret_result, text_type_secret_success = set_users_effective_permissions(core_session,
                                                                                        user_name,
                                                                                        'View,Edit',
                                                                                        user_id,
                                                                                        secret_list[0])
    assert text_type_secret_success, f'setting permissions for text type secret:{text_type_secret_result}'
    logger.info(f'setting permissions for text type secret: : {text_type_secret_success}')

    # Api to create new policy
    policy_result_sq = PolicyManager.create_new_auth_profile(core_session,
                                                             prefix + secrets_params['policy_name'],
                                                             ["SQ",
                                                              None],
                                                             None,
                                                             "30")
    assert policy_result_sq is not None, f'Failed to create policy:{policy_result_sq}'
    logger.info(f' Creating new policy:{policy_result_sq}')
    clean_up_policy.append(policy_result_sq)

    # Api to create new policy
    policy_result = PolicyManager.create_new_auth_profile(core_session,
                                                          prefix + secrets_params['policy_name_new'],
                                                          ["UP", None],
                                                          None,
                                                          "30")
    assert policy_result is not None, f'Failed to create policy:{policy_result}'
    logger.info(f' Creating new policy:{policy_result}')
    clean_up_policy.append(policy_result)

    # Update settings & policy for Folder
    result = update_folder(core_session,
                           folder_list[0],
                           folder_name,
                           secrets_params['mfa_folder_name_update'] + prefix,
                           description=secrets_params['mfa_folder_description'],
                           policy_id=policy_result_sq)

    assert result['success'], f'Not Able to update the settings: {result["Message"]} '
    logger.info(f'Update settings for secret: {result}')

    # Update settings for secret
    result = update_secret(core_session,
                           secret_list[0],
                           prefix + secrets_params['mfa_secret_name_update'],
                           description=secrets_params['mfa_secret_description'],
                           policy_id=policy_result)
    assert result['success'], f'Not Able to update the settings: {result["Message"]} '
    logger.info(f'Update settings for secret: {result}')

    # Removing policy for Folder
    result = update_folder(core_session,
                           folder_list[0],
                           folder_name,
                           secrets_params['mfa_folder_name_update'] + prefix,
                           description=secrets_params['mfa_folder_description'])
    assert result['success'], f'Not Able to update the settings: {result["Message"]} '
    logger.info(f'Update settings for secret: {result}')

    # Removing policy for secret
    result = update_secret(core_session,
                           secret_list[0],
                           prefix + secrets_params['mfa_secret_name_update'],
                           description=secrets_params['mfa_secret_description'])
    assert result['success'], f'Not Able to update the settings: {result["Message"]} '
    logger.info(f'Update settings for secret: {result}')

    # Getting details of the Folder updated
    result_folder = get_folder(core_session, folder_list[0])
    logger.info(f'Updated Folder details: {result_folder}')
    description_updated = result_folder["Result"]["Results"][0]["Row"]["Description"]
    name_updated = result_folder["Result"]["Results"][0]["Row"]["Name"]
    assert 'MFAOnParentFolderUpdate' in name_updated, \
        f'Failed to update the name{result_folder["Result"]["Results"][0]["Row"]["Name"]}'
    assert 'mfa_description' in description_updated, \
        f'Failed to update the description{result_folder["Result"]["Results"][0]["Row"]["Description"]}'

    # Getting details of the Secret updated
    get_secret_details, get_secret_success, get_secret_created_date, get_secret_text = get_secret_contents(
        core_session,
        secret_list[0])
    description_updated = get_secret_details['Description']
    name_updated = get_secret_details['SecretName']

    assert 'MFAOnSecretUpdate' in name_updated, f'Failed to update the name{get_secret_success}'
    assert 'mfa_description' in description_updated, f'Failed to update the description{get_secret_success}'
    logger.info(f'Details of the secret updated: {get_secret_details}')
