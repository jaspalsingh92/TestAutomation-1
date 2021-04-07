import pytest
import logging
from Shared.API.infrastructure import ResourceManager
from Shared.API.redrock import RedrockController
from Shared.API.sets import SetsManager
from Utils.guid import guid

logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_accounts_removed_my_sys_account_view_permission(core_session, users_and_roles, pas_windows_setup):
    """
    TC:C2061 Account will removed from "My System Account" after delete "View" permission for user.
    :param:core_session:  Returns a API session.
    :param:users_and_roles:Fixture to manage roles and user.
    :param pas_windows_setup:Returns a fixture.
    """

    # Creating a system and account.
    system_id, account_id, sys_info, connector_id, user_password = pas_windows_setup()

    # Cloud user session with "Privileged Access Service User".
    cloud_user_session = users_and_roles.get_session_for_user('Privileged Access Service User')
    user_name = cloud_user_session.auth_details['User']
    user_id = cloud_user_session.auth_details['UserId']

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

    # Assigning "Workspace Login" permission for account to limited user.
    rights = "View,Login,UserPortalLogin"
    assign_account_perm_res, assign_account_perm_success = \
        ResourceManager.assign_account_permissions(core_session, rights, user_name, user_id, 'User', account_id)

    assert assign_account_perm_success, f'Failed to assign "Workspace Login" permission:' \
                                        f'API response result:{assign_account_perm_res}'
    logger.info(f'Successfully  "Workspace Login" of account permission to user"{assign_account_perm_res}"')

    # Getting the details from "My System Accounts" in workspace and validating  account in "My System Accounts" list.
    workspace_account_list = []
    workspace_result_detail, workspace_success = ResourceManager.\
        get_my_system_accounts_from_workspace(cloud_user_session)
    for workspace_result in workspace_result_detail:
        if workspace_result['Name'] == sys_info[0]:
            workspace_account_list.append(workspace_result['User'])
    assert sys_info[4] in workspace_account_list, f'Failed to get the account {sys_info[4]} on workspace.'
    logger.info(f"Could  display on Account {sys_info[4]} on workspace")

    # Deleting the "Workspace Login permission for account to limited user.
    assign_account_perm_res, assign_account_perm_success = \
        ResourceManager.assign_account_permissions(core_session, "View", user_name, user_id, 'User', account_id)

    assert assign_account_perm_success, f"Failed to delete the workspace account permission:" \
                                        f" API response result: {assign_account_perm_res}"
    logger.info(f"Successfully assign account new permission to user'{assign_account_perm_res}'")

    # Getting the details from "My System Accounts" in workspace and validating  account not in "My System Accounts"
    # list.
    workspace_result, workspace_success = ResourceManager.get_my_system_accounts_from_workspace(cloud_user_session)
    assert sys_info[4] not in workspace_result, f'Could find the account {sys_info[4]} on workspace.'
    logger.info(f"Could not display on Account {sys_info[4]} on workspace")


@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_accounts_removed_my_sys_account_delete_workspace_permission(core_session, users_and_roles,
                                                                     pas_windows_setup):
    """
    TC:C2060 Account will removed from "My System Account" after delete "Workspace Login" permission.
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

    # Not Assigning "Workspace_login account permission to user.
    assign_account_perm_res, assign_account_perm_success = \
        ResourceManager.assign_account_permissions(core_session, "View", user_name, user_id, 'User', account_id)

    assert assign_account_perm_success, f" Workspace account permission is assigned: " \
                                        f"API response result:{assign_account_perm_res}"
    logger.info(f"Successfully not assign account Workspace permission to user'{assign_account_perm_res}'")

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

    # Getting the details from "My System Accounts" in workspace and validating  account not in "My System Accounts"
    # list.
    workspace_result, workspace_success = ResourceManager.get_my_system_accounts_from_workspace(cloud_user_session)
    assert sys_info[4] not in workspace_result, f'Could find the account {sys_info[4]} on workspace.'
    logger.info("Could not display Account on workspace")

    # Assigning "Workspace Login" permission for account to limited user.
    rights = "View,Login,UserPortalLogin"
    assign_account_perm_res, assign_account_perm_success = \
        ResourceManager.assign_account_permissions(core_session, rights, user_name, user_id, 'User', account_id)

    assert assign_account_perm_success, f'Failed to assign "Workspace Login" permission:' \
                                        f'API response result:{assign_account_perm_res}'
    logger.info(f'Successfully  "Workspace Login" of account permission to user"{assign_account_perm_res}"')

    # Getting the details from "My System Accounts" in workspace and validating  account in "My System Accounts" list.
    workspace_account_list = []
    workspace_result_detail, workspace_success = ResourceManager.\
        get_my_system_accounts_from_workspace(cloud_user_session)
    for workspace_result in workspace_result_detail:
        if workspace_result['Name'] == sys_info[0]:
            workspace_account_list.append(workspace_result['User'])
    assert sys_info[4] in workspace_account_list, f'failed to get the account {sys_info[4]} on workspace.'
    logger.info(f"Successfully display account {sys_info[4]} on workspace")

    # Not Assigning "Workspace_login account permission to user.
    assign_account_perm_res, assign_account_perm_success = \
        ResourceManager.assign_account_permissions(core_session, "View", user_name, user_id, 'User', account_id)

    assert assign_account_perm_success, f" Workspace account permission is assigned: " \
                                        f"API response result:{assign_account_perm_res}"
    logger.info(f"Successfully not assign account Workspace permission to user'{assign_account_perm_res}'")

    # Getting the details from "My System Accounts" in workspace and validating  account not in "My System Accounts"
    # list.
    workspace_result, workspace_success = ResourceManager.get_my_system_accounts_from_workspace(cloud_user_session)
    assert sys_info[4] not in workspace_result, f'Could find the account {sys_info[4]} on workspace.'
    logger.info(f"Failed to display on Account {sys_info[4]} on workspace")


@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_accounts_set_my_system_accounts(core_session, pas_windows_setup, users_and_roles, clean_up_collections):
    """
    TC:C2067 Add account to set on "My System Accounts".
    :param:core_session:  Returns a API session.
    :param:users_and_roles:Fixture to manage roles and user.
    :param pas_windows_setup:Returns a fixture.
    :param:clean_up_collections: Cleans up Set.
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

    # Getting the details from "My System Accounts" in workspace and validating  account not in "My System Accounts"
    # list.
    workspace_result, workspace_success = ResourceManager.get_my_system_accounts_from_workspace(cloud_user_session)
    assert sys_info[4] not in workspace_result, f'Could find the account:API response result:{workspace_result}'
    logger.info("Failed to display on Account on workspace")

    # Creating a set and adding a account to set.
    account_set_name = f'Set_test{guid()}'
    success, account_set_result = SetsManager.create_manual_collection(core_session, account_set_name,
                                                                       'VaultAccount',
                                                                       object_ids=[account_id])
    assert success, f"Failed to create system set {account_set_result}"
    logger.info(f'Successfully created set:{account_set_result}')

    # Getting the details of created_account_set in Accounts page and validating account is in created set.
    account_set_details = RedrockController.get_set_account_details(core_session, account_id=account_id,
                                                                    set_id=account_set_result)

    assert account_set_details[0]['User'] == sys_info[4], f'Fail to find the account{sys_info[4]}'
    logger.info(f'Successfully find "{account_set_details[0]["User"]}" in created set" {account_set_name}".')

    # Cleanup the created set.
    clean_up_collections.append(RedrockController.get_id_from_name(core_session, account_set_name, "Sets"))
    logger.info(f'Successfully deleted created set" {account_set_name}".')
