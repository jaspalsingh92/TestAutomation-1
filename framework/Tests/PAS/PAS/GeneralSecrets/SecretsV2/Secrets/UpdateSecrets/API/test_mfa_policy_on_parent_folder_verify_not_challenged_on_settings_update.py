import logging
import pytest
from Shared.API.policy import PolicyManager
from Shared.API.secret import update_folder, get_folder
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_mfa_policy_on_parent_folder_verify_not_challenged_on_settings_update(core_session,
                                                                              pas_general_secrets,
                                                                              create_secret_inside_folder,
                                                                              clean_up_policy):
    """
    test method to verify that mfa does not exist on updating the settings & policy for an existing
    parent folder "MFAOnParentFolder" with already assigned mfa for that folder

    :param core_session:  Authenticated Centrify Session
    :param pas_general_secrets: Fixture to read secret data from yaml file
    :param create_secret_inside_folder: Fixture to create secret "MFAOnSecret" inside folder "MFAOnParentFolder"
    :param clean_up_policy: Fixture to clean up the policy created
    """
    secrets_params = pas_general_secrets
    prefix = guid()
    folder_list, folder_name, secret_list = create_secret_inside_folder

    # creating new policy
    policy_result = PolicyManager.create_new_auth_profile(core_session,
                                                          prefix + secrets_params['policy_name'],
                                                          ["UP", None],
                                                          None,
                                                          "30")
    assert policy_result is not None, f'Failed to create policy:{policy_result}'
    logger.info(f' Creating new policy:{policy_result}')
    clean_up_policy.append(policy_result)

    # updating settings & policy for Folder
    result = update_folder(core_session, folder_list[0],
                           folder_name,
                           secrets_params['mfa_folder_name_update'] + prefix,
                           description=secrets_params['mfa_folder_description'],
                           policy_id=policy_result)
    assert result['success'], f'Not Able to update the settings: {result["Message"]} '
    logger.info(f'Update settings for secret: {result}')

    # Getting details of the Folder updated
    result_folder = get_folder(core_session, folder_list[0])
    description_updated = result_folder["Result"]["Results"][0]["Row"]["Description"]
    name_updated = result_folder["Result"]["Results"][0]["Row"]["Name"]
    assert 'MFAOnParentFolderUpdate' in name_updated,\
        f'Failed to update the name{result_folder["Result"]["Results"][0]["Row"]["Name"]}'
    assert 'mfa_description' in description_updated, \
        f'Failed to update the description{result_folder["Result"]["Results"][0]["Row"]["Description"]}'

    # Removing MFA for Folder
    result = update_folder(core_session, folder_list[0],
                           folder_name,
                           secrets_params['mfa_folder_name_update'] + prefix,
                           description=secrets_params['mfa_folder_description'])
    assert result['success'], f'Not Able to update the settings: {result["Message"]} '
    logger.info(f'Update settings for secret: {result}')
