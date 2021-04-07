import pytest
import logging
import datetime
from Shared.API.infrastructure import ResourceManager
from Shared.API.workflow import WorkflowManager

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.bhavna
def test_check_ui(core_session, pas_setup, users_and_roles):
    """
    Test case: C2120
    :param core_session: Authenticated centrify session
    :param pas_setup: fixture to create system with accounts
    :param users_and_roles: fixture to create cloud user ui session
    """
    system_id, account_id, sys_info = pas_setup

    # Getting user with PAS Power User rights
    pas_user_session = users_and_roles.get_session_for_user('Privileged Access Service Power User')
    assert pas_user_session.auth_details, 'Failed to Login with PAS Power User'
    username = pas_user_session.auth_details['User']
    user_id = pas_user_session.auth_details['UserId']
    logger.info(f'User with PAS Power User Rights login successfully: user_Name:{username}')

    result, status = ResourceManager.assign_account_permissions(core_session, "View,Manage", username, user_id,
                                                                pvid=account_id)
    assert status, f'failed to assign Edit permission to user: {username} for account {sys_info[4]}'
    logger.info(f'Edit permission provided for account {sys_info[4]} to user {username}')

    # enabling account workflow
    result, status = ResourceManager.update_account_with_approver(core_session, account_id, sys_info[4], system_id,
                                                                  core_session.get_user().get_id(),
                                                                  core_session.get_user().get_login_name())
    assert status, f'failed to enable account workflow for account {sys_info[4]} of system {sys_info[0]}'
    logger.info(f'workflow enabled for account {sys_info[4]} of system {sys_info[0]}.')

    # Request login for an Account
    start_time = str(datetime.datetime.utcnow())
    end_time = str(datetime.datetime.utcnow() + datetime.timedelta(hours=1))
    request_reason = 'I want to Login'
    login_request, login_success = WorkflowManager.request_checkout(pas_user_session, account_id, start_time, end_time,
                                                                    reason=request_reason, accesstype='Login')
    assert login_success, f"Login Request Failed:{login_request}"
    logger.info(f'Login Request success: {login_request}')