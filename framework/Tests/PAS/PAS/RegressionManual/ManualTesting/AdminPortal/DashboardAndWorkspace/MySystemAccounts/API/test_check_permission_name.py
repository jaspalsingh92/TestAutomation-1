import pytest
import logging
from Shared.API.infrastructure import ResourceManager
from Shared.API.sets import SetsManager
from Shared.API.redrock import RedrockController
from Utils.guid import guid

logger = logging.getLogger('test')
lock_tenant = True


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.bhavna
def test_check_permission_name_on_portal(core_session, pas_setup, clean_up_collections):
    """
    Test case: C2059
    :param core_session: Authenticated Centrify Session
    :param pas_setup: fixture to create system with accounts in portal
    :param core_admin_ui: Authenticated Centrify ui session
    """
    system_id, account_id, sys_info = pas_setup

    # Getting the Id of the user.
    user_details = core_session.__dict__
    user_id = user_details['auth_details']['UserId']
    User_name = user_details['auth_details']['User']

    # Assigning 'UserPortalLogin' permission to user for account.
    account_result, account_success = ResourceManager.assign_account_permissions(core_session, 'UserPortalLogin',
                                                                                 User_name,
                                                                                 user_id, 'User',
                                                                                 account_id)
    assert account_success, f"Failed to give 'UserPortalLogin' permission to user: {User_name} for " \
                            f"Account: {account_id}. API response 'Result': {account_result}"
    logger.info(f"'UserPortalLogin' permission given to user: {User_name} for Account:{account_id}.")

    # Fetching account information to validate desired account is un managed
    result, status = ResourceManager.get_account_information(core_session, account_id)
    assert status, f"failed to retrieve account information, returned result is {result}"

    set_name = f"test_setname{guid()}"
    status, set_result = SetsManager.create_manual_collection(core_session, set_name, "VaultAccount",
                                                              object_ids=[account_id])
    assert status, f"failed to create set {set_name}, returned result is {set_result}"
    logger.info(f"set {set_name} created for account {sys_info[4]} of system {sys_info[0]}")
    clean_up_collections.append(set_result)  # Set cleanup list

    # "Workspace Login" rather than "Portal Login" in granted permission activity
    result, success = ResourceManager.assign_account_permissions(core_session, "UserPortalLogin",
                                                                 User_name, user_id,
                                                                 pvid=account_id)
    assert success, f'failed to assign permissions "UserPortalLogin" to ' \
                    f'{User_name} for account {sys_info[4]} ' \
                    f'for system {sys_info[0]}'

    activity = RedrockController.get_account_activity(core_session, account_id)
    assert activity[0]['Detail'] == f'{User_name} granted User "{User_name}" to have "Workspace Login" permissions ' \
                                    f'on local account "{sys_info[4]}" for "{sys_info[0]}"({sys_info[1]})' \
                                    f' with credential type Password ', 'No Workspace Login keyword found in ' \
                                                                        'retrieved permission activity '
    logger.info(f'Displayed "Workspace Login" rather than "Portal Login" in granted permission activity for '
                f'account {sys_info[4]}')

    status, result, SetsManager.set_collection_member_permission(core_session, User_name,
                                                                 user_id,
                                                                 "UserPortalLogin", set_result)
    assert status, f'failed to assign workspace login permission to ' \
                   f'user {User_name} for set {set_name}'
    logger.info(f'successfully assigned work space login permission to user {User_name}.')

    # "Workspace Login" in set activity
    set_activity_rows = ResourceManager.get_activity_for_collection(core_session, set_result)
    assert set_activity_rows[0]['Detail'] == f'{User_name} granted User ' \
                                             f'"{User_name}" to have ' \
                                             f'"Workspace Login" permissions on the account set "{set_name}"', \
        f'failed to get {set_name} activity for permissions'
    logger.info(f'displayed "Workspace Login" in activity in set {set_name} activity')

    # displayed "Workspace Login" in user profile activity
    user_profile_activity = RedrockController.get_user_activity_profile(core_session, user_id)
    counter = 0
    while counter < 10:
        user_profile_activity = RedrockController.get_user_activity_profile(core_session, user_id)
        if user_profile_activity[0]['EventMessage'].__contains__(sys_info[0]):
            break
    counter += 1
    assert user_profile_activity[0]['EventMessage'] == f'{User_name} ' \
                                                       f'granted User "{User_name}" to have "Workspace Login" ' \
                                                       f'permissions on local account "{sys_info[4]}" ' \
                                                       f'for "{sys_info[0]}"({sys_info[1]}) with credential type ' \
                                                       f'Password ', \
        f'No Workspace Login keyword found in retrieved permission activity '
    logger.info('displayed "Workspace Login" in user profile activity')
