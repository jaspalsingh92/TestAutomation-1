import pytest
import logging
import datetime
from Shared.API.infrastructure import ResourceManager
from Shared.API.workflow import WorkflowManager

logger = logging.getLogger('test')


@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi
def test_check_account_settings_page(core_session, pas_setup, get_limited_user_function):
    """
    Test case: C2119
    :param core_session: Authenticated centrify session
    :param pas_setup: fixture to create system with account
    :param get_limited_user_function: Centrify ui session for user with right "Privileged Access Service Administrator"
    """

    system_id, account_id, sys_info = pas_setup

    limited_sesh, limited_user = get_limited_user_function

    user_details = core_session.__dict__['auth_details']
    username = user_details['User']
    user_id = user_details['UserId']

    # Assigning rights to cloud user, excluding checkout and Login right.
    rights = "Owner,View,Manage,Delete,UpdatePassword,RotatePassword,FileTransfer"
    result, success = ResourceManager.assign_account_permissions(core_session, rights, username, user_id,
                                                                 pvid=account_id)
    assert success, f'failed to assign rights: {rights} to cloud user {username} for account {sys_info[4]} ' \
                    f'of {sys_info[0]}.'
    logger.info(f'rights {rights} successfully assigned to to cloud user {username} for account {sys_info[4]} '
                f'of {sys_info[0]}.')

    # enabling account workflow
    result, status = ResourceManager.update_account_with_approver(core_session, account_id, sys_info[4], system_id,
                                                                  core_session.get_user().get_id(),
                                                                  core_session.get_user().get_login_name())
    assert status, f'failed to enable account workflow for account {sys_info[4]} of system {sys_info[0]}'
    logger.info(f'workflow enabled for account {sys_info[4]} of system {sys_info[0]}.')

    # Step: Request login for an Account
    timenow = datetime.datetime.utcnow()
    start_time = str(timenow)
    end_time = str(timenow + datetime.timedelta(hours=1))
    req_request, req_success = WorkflowManager.request_checkout(limited_sesh, account_id, start_time, end_time,
                                                                reason=None, accesstype="Login")
    assert req_success, "Workflow Request Failed"
    logger.info(f'Workflow Request is success: {req_request}')

    # # Step: Request Checkout for an Account
    req_request, req_success = WorkflowManager.request_checkout(limited_sesh, account_id, start_time, end_time)
    assert req_success, "Workflow Request Failed"
    logger.info(f'Workflow Request is success: {req_request}')
