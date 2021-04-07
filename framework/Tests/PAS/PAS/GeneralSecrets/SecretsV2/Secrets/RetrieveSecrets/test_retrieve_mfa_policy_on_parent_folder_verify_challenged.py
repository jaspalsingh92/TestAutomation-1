import logging
import pytest
from Shared.API.policy import PolicyManager
from Shared.API.secret import update_folder, get_secret
from Shared.UI.Centrify.SubSelectors.grids import GridRowByGuid
from Shared.UI.Centrify.SubSelectors.modals import NoTitleModal, Modal
from Shared.UI.Centrify.SubSelectors.navigation import ActiveMainContentArea
from Shared.UI.Centrify.routines.login import Login
from Shared.UI.Centrify.selectors import InputBoxValue
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi_ui
@pytest.mark.bhavna
def test_retrieve_mfa_policy_on_parent_folder_verify_challenged(
        core_session,
        core_admin_ui,
        pas_general_secrets,
        create_secret_inside_folder,
        clean_up_policy):

    """
             C2985: MFA policy on Parent folder, verify challenged
         1) Set MFA on MFAonParent
         2) Right click "MFAonSecret" then Retrieve.
         3) Verify challenged with MFA popups,
         4) Enter password & verify you can retrieve secret

    :param core_session: Authenticated Centrify Session
    :param core_admin_ui: Fixture to launch ui session for cloud admin
    :param pas_general_secrets: Fixture to read secret data from yaml file
    :param create_secret_inside_folder: Fixture to create secret "MFAOnSecret" inside folder "MFAOnParentFolder"
    :param clean_up_policy: Fixture to clean up the policy created
    """
    secrets_params = pas_general_secrets
    suffix = guid()
    folder_list, folder_name, secret_list = create_secret_inside_folder
    verify_text = secrets_params['secret_text']

    # Getting details of the secret replaced
    found_secret = get_secret(core_session, secret_list[0])
    assert found_secret['success'], \
        f'Failed to get the details of the secret updated, API response result:{found_secret["Message"]}'
    logger.info(f'Getting details of the secret: {found_secret}')
    secret_name = found_secret['Result']['SecretName']

    challenges = ["UP", ""]
    # Creating new policy
    policy_result = PolicyManager.create_new_auth_profile(core_session, secrets_params['policy_name'] + suffix,
                                                          challenges, 0, 0)
    assert policy_result, f'Failed to create policy, API response result:{policy_result}'
    logger.info(f' Creating new policy:{policy_result}')
    clean_up_policy.append(policy_result)

    # Applying MFA on Folder
    result = update_folder(core_session, folder_list[0],
                           folder_name,
                           folder_name,
                           policy_id=policy_result)
    assert result['success'], f'Not Able to apply MFA, API response result: {result["Message"]} '
    logger.info(f'Applying MFA  for folder: {result}')

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
    logger.info(f'Text Retrieved with MFA challenge(password only)i.e. MFAonParent successfully: {verify_text}')

    # Removing MFA on Folder
    result = update_folder(core_session, folder_list[0],
                           folder_name,
                           secrets_params['mfa_folder_name_update'] + suffix,
                           description=secrets_params['mfa_folder_description'])
    assert result['success'], f'Not Able to apply MFA, API response result: {result["Message"]} '
    logger.info(f'Applying MFA  for folder: {result}')
