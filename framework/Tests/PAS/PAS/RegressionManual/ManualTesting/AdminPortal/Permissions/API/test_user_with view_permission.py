import pytest
import logging
from Shared.API.infrastructure import ResourceManager
from Shared.API.redrock import RedrockController
from Shared.API.secret import create_text_secret, set_users_effective_permissions, get_secret_activity
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi_ui
def test_privilege_service_user_with_view_permission(core_session, pas_setup, get_limited_user_module):
    """
    Test case: C286564 :- Privilege Service User with view permission should can see the related activity
    :param core_session: Authenticated Centrify session
    :param pas_setup: fixture to create system with account
    :param get_limited_user_module: creating cloud user with "Privileged Access Service Power User" right
    """
    system_id, account_id, sys_info = pas_setup

    cloud_user_session, cloud_user = get_limited_user_module
    username = cloud_user.get_login_name()
    user_id = cloud_user.get_id()

    # "View" permission to cloud user for system
    result, success = ResourceManager.assign_system_permissions(core_session, "View", username, user_id, pvid=system_id)
    assert success, f'failed to assign view permission to user {username} for system {sys_info[0]}'
    logger.info(f'view permission for system {sys_info[0]} assigned to user {username}')

    # Activity validation of system by cloud user
    rows = ResourceManager.get_system_activity(cloud_user_session, system_id)
    assert rows[0][
               'Detail'] == f'{core_session.auth_details["User"]} granted User "{username}" to have "View" permissions on system ' \
                            f'"{sys_info[0]}"({sys_info[1]})', 'No activity related to view permission found '
    logger.info(f'cloud user {username} can see all the activities of system {sys_info[0]}')

    # "View" permission to cloud user for account
    result, success = ResourceManager.assign_account_permissions(core_session, "View", username,
                                                                 user_id,
                                                                 pvid=account_id)
    assert success, f'failed to assign permissions "View" to {username} for account {sys_info[4]} ' \
                    f'for system {sys_info[0]}'
    logger.info(f'View permission for account {sys_info[4]} of system {sys_info[0]} to user {username}')

    # Activity validation of account by cloud user
    activity = RedrockController.get_account_activity(cloud_user_session, account_id)
    assert activity[0][
               'Detail'] == f'{core_session.auth_details["User"]} granted User "{username}" to have "View" permissions on local account' \
                            f' "{sys_info[4]}" for "{sys_info[0]}"({sys_info[1]}) with credential ' \
                            f'type Password ', 'No activity related to view permission found '
    logger.info(f'cloud user {username} can see all the activities of account {sys_info[4]} of system {sys_info[0]}')

    # Created secret
    secret_name = f"test_secret{guid()}"
    status, parameters, secret_result = create_text_secret(core_session, secret_name, "test_secret_text")
    assert status, f'failed to create secret with returned result: {result}'
    logger.info(f'secret created successfully {result}, returned parameters are {parameters}')

    # Assigning view permission to secret to cloud user
    result, success = set_users_effective_permissions(core_session, username, "View", user_id, secret_result)
    assert success, f'failed to set permissions of secret for user {username}'
    logger.info(f'successfully granted "View" permission for secret to {secret_name} to user {username}')

    # Activity validation of secret by cloud user
    secret_activity = get_secret_activity(cloud_user_session, secret_result)
    assert f'{core_session.auth_details["User"]} granted User "{username}" to have "View" permissions on the ' \
           f'secret "{secret_name}"' in secret_activity[0]['Detail'], 'No activity related to view permission found '
    logger.info(f'cloud user {username} can see all the activities of secret of {secret_name}')
