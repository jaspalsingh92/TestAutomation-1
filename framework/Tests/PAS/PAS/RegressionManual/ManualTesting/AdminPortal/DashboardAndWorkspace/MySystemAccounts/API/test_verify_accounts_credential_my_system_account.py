import pytest
import logging
from Shared.API.infrastructure import ResourceManager

logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_verify_accounts_credential_my_system_accounts(core_session, pas_windows_setup, users_and_roles):
    """
    TC:C2068 Verify account's credential on "My System Accounts".
    :param:core_session:  Returns a API session.
    :param:users_and_roles:Fixture to manage roles and user.
    :param pas_windows_setup:Returns a fixture.
    """
    # Creating a system and account.
    system_id, account_id, sys_info, connector_id, user_password = pas_windows_setup()

    # Cloud user session with "Privileged Access Service Administrator".
    cloud_user_session = users_and_roles.get_session_for_user('Privileged Access Service Administrator')
    user_name = cloud_user_session.auth_details['User']
    user_id = cloud_user_session.auth_details['UserId']

    # Assigning "Workspace Login" permission for account to limited user.
    rights = "View,Login,UserPortalLogin"
    assign_account_perm_res, assign_account_perm_success = \
        ResourceManager.assign_account_permissions(core_session, rights, user_name, user_id, 'User', account_id)

    assert assign_account_perm_success, f'Failed to assign "Workspace Login" permission:' \
                                        f'API response result:{assign_account_perm_res}'
    logger.info(f'Successfully  "Workspace Login" of account permission to user"{assign_account_perm_res}"')

    # Assigning "View" permission for system to limited user.
    assign_system_perm_res, assign_system_perm_success = ResourceManager.assign_system_permissions(core_session,
                                                                                                   "View",
                                                                                                   user_name,
                                                                                                   user_id,
                                                                                                   'User',
                                                                                                   system_id)

    assert assign_system_perm_success, f'Failed to assign "View" permissions: ' \
                                       f'API response result {assign_system_perm_res}.'
    logger.info(f"Successfully assign system permission to user'{assign_system_perm_res}'")

    # Getting the details from "My System Accounts" in workspace and validating  account in "My System Accounts" list.
    workspace_account_list = []
    workspace_result_detail, workspace_success = ResourceManager.\
        get_my_system_accounts_from_workspace(cloud_user_session)
    for workspace_result in workspace_result_detail:
        if workspace_result['Name'] == sys_info[0]:
            workspace_account_list.append(workspace_result['User'])
    assert sys_info[4] in workspace_account_list, f'failed to get the account {sys_info[4]} on workspace.'
    logger.info(f"Could display on Account{sys_info[4]} on workspace")

    # validating Account health.
    verify_pass_result, verify_pass_success = ResourceManager.check_account_health(core_session, account_id)
    assert verify_pass_success, f"Failed to verify account health:API response result:{verify_pass_result}. "
    logger.info(f"Successfully account verified:{verify_pass_result}")
