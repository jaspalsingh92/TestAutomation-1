import pytest
import logging
from Shared.API.infrastructure import ResourceManager
from Shared.endpoint_manager import EndPoints

logger = logging.getLogger('test')


@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi
def test_check_permission_name_on_portal(core_session, pas_setup, users_and_roles):
    """
    Test case: C2118
    :param core_session: Authenticated Centrify session
    :param pas_setup: Fixture to create system with account in portal
    :param users_and_roles: fixture to create user with role in portal
    """

    system_id, account_id, sys_info = pas_setup

    # API session for cloud user
    cloud_user_session = users_and_roles.get_session_for_user('Privileged Access Service Power User')

    cloud_user_data = cloud_user_session.get_user()
    username = cloud_user_data.get_login_name()
    user_id = cloud_user_data.get_id()

    # Assigning cloud user "Grant" permission for system
    result, status = ResourceManager.assign_system_permissions(core_session, "Grant,View", username, user_id,
                                                               pvid=system_id)
    assert status, f'failed to assign Grant permission to user {username} for system {sys_info[0]} returned result is ' \
                   f'{result}'
    logger.info(f'successfully assigned Grant permission to user {username} for system {sys_info[0]}')

    # Assigning "Grant", "Edit" permission to user for account
    result, status = ResourceManager.assign_account_permissions(core_session, "Owner,View,Manage", username,
                                                                user_id, pvid=account_id)
    assert status, f'failed to assign "Grant", "Edit" permission to user {username} for account {sys_info[4]} ' \
                   f'of system {sys_info[0]}'
    logger.info(f'successfully assigned "Grant", "Edit" permission to user {username} for account {sys_info[4]}')

    # cloud user remove its own "Grant" permission for account
    result, status = ResourceManager.assign_account_permissions(cloud_user_session, "View,Manage", username, user_id,
                                                                pvid=account_id)
    assert status, f'user {username} failed to remove Grant permission'
    logger.info('grant permission removed successfully')

    # cloud remove its own "Grant" permission for system
    result, status = ResourceManager.assign_system_permissions(core_session, "View", username, user_id,
                                                               pvid=system_id)
    assert status, f'user {username} failed to remove Grant permission'
    logger.info(f'grant permission removed successfully')

    args = {"Args": {"Caching": -1}, "RowKey": system_id, "Table": "Server"}
    aces_result = cloud_user_session.post(EndPoints.GET_ROW_ACES, args).json()
    user_permission = []
    for i in aces_result['Result']:
        if i['PrincipalName'] == username:
            user_permission.append(i['PrincipalName'])
    assert user_permission[0] == username, 'expected to find user {username} row in permissions table but did not'
    logger.info(f'UI for system permission for cloud user {username} '
                f'shown normally after removing "Grant" permission of system.')

    args = {"Args": {"Caching": -1}, "RowKey": account_id, "Table": "VaultAccount"}
    aces_result = cloud_user_session.post(EndPoints.GET_ROW_ACES, args).json()
    user_permission = []
    for i in aces_result['Result']:
        if i['PrincipalName'] == username:
            user_permission.append(i['PrincipalName'])
    assert user_permission[0] == username, 'expected to find user {username} row in permissions table but did not'
    logger.info(f'UI for Account permission for cloud user {username} shown normally after removing "Grant" permission '
                f'of system.')