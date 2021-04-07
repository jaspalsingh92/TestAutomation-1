import logging
import pytest
from Shared.API.policy import PolicyManager
from Shared.API.secret import update_folder, get_secret, update_secret
from Shared.UI.Centrify.SubSelectors.grids import GridRowByGuid
from Shared.UI.Centrify.SubSelectors.modals import NoTitleModal, Modal
from Shared.UI.Centrify.SubSelectors.navigation import ActiveMainContentArea
from Shared.UI.Centrify.routines.login import Login
from Shared.UI.Centrify.selectors import InputBoxValue
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.ui
def test_retrieve_mfa_policy_on_both_parent_folder_and_secret_verify_secret_mfa(
        core_session,
        core_admin_ui,
        pas_general_secrets,
        create_secret_inside_folder,
        clean_up_policy):

    """
           C2986: MFA policy on both Parent folder and Secret, verify secret MFA
         1) Set MFA on both MFAonSecret & MFAOnParent
         2) Right click "MFAonSecret" then Retrieve.
         3) Verify challenged with MFA should be from "MFAonSecret"
         4) Enter password & verify you can retrieve secret

    :param core_session: Authenticated Centrify Session
    :param core_admin_ui: Fixture to launch ui session for cloud admin
    :param pas_general_secrets: Fixture to read secret data from yaml file
    :param create_secret_inside_folder: Fixture to create secret "MFAOnSecret" inside folder "MFAOnParentFolder"
    :param clean_up_policy: Fixture to clean up the policy created
    """
    params = pas_general_secrets
    suffix = guid()
    folder_list, folder_name, secret_list = create_secret_inside_folder
    verify_text = params['secret_text']

    # Getting details of the secret replaced
    found_secret = get_secret(core_session, secret_list[0])
    assert found_secret['success'], \
        f'Failed to get the details of the secret updated, API response result:{found_secret["Message"]}'
    logger.info(f'Getting details of the secret: {found_secret}')
    secret_name = found_secret['Result']['SecretName']

    challenges_v2 = ["UP,EMAIL", ""]
    # Creating new policy with Password & Email
    policy_result_email = PolicyManager.create_new_auth_profile(core_session,
                                                                params['policy_name'] + "V2" + suffix,
                                                                challenges_v2, 0, 0)
    assert policy_result_email, f'Failed to create another policy, API response result:{policy_result_email}'
    logger.info(f' Creating new policy:{policy_result_email}')
    clean_up_policy.append(policy_result_email)
    challenges = ["UP", ""]

    # Creating another policy with password only
    policy_result = PolicyManager.create_new_auth_profile(core_session, params['policy_name'] + suffix,
                                                          challenges, 0, 0)
    assert policy_result, f'Failed to create policy, API response result:{policy_result}'
    logger.info(f' Creating another policy:{policy_result}')
    clean_up_policy.append(policy_result)

    # Applying MFA on Folder
    result = update_folder(core_session, folder_list[0],
                           folder_name,
                           folder_name,
                           policy_id=policy_result_email)
    assert result['success'], f'Not Able to apply MFA, API response result: {result["Message"]} '
    logger.info(f'Applying MFA  for folder: {result}')

    # Applying MFA on Secret
    result = update_secret(core_session,
                           secret_list[0], secret_name,
                           description=params['mfa_secret_description'],
                           policy_id=policy_result)
    assert result['success'], f'Not Able to apply MFA on the secret, API response result:{result["Message"]} '
    logger.info(f'MFA Applied on the secret: {result}')

    ui = core_admin_ui
    password = ui.get_user().get_password()
    login = Login(ui)
    ui.navigate('Resources', 'Secrets')
    ui.search(folder_name)
    ui.click_row(GridRowByGuid(folder_list[0]))
    ui.click_row(GridRowByGuid(secret_list[0]))
    ui.action('Retrieve')
    ui.switch_context(Modal(text=secret_name))
    ui.button('Show Text')
    ui.switch_context(NoTitleModal())
    login.click_next_on_auth()
    login.enter_login_password(password)
    login.click_next_on_auth()
    ui.switch_context(ActiveMainContentArea())
    ui.expect(InputBoxValue(verify_text), f'Expect to find {verify_text} in Retrieve but could not.')
    logger.info(f'Text Retrieved with MFA challenge(password only)i.e. MFAOnSecret successfully: {verify_text}')

    # Removing MFA on Folder
    result = update_folder(core_session, folder_list[0],
                           folder_name,
                           params['mfa_folder_name_update'] + suffix)
    assert result['success'], f'Not Able to remove MFA, API response result: {result["Message"]} '
    logger.info(f'MFA Removed for folder: {result}')

    # Removing MFA on Secret
    result = update_secret(core_session,
                           secret_list[0],
                           params['mfa_secret_name_update'] + suffix)
    assert result['success'], f'Not Able to remove MFA, API response result:{result["Message"]} '
    logger.info(f'MFA Removed on secret: {result}')
