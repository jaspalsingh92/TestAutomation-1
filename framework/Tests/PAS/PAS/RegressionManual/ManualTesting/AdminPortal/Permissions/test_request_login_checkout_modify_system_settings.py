import datetime
import pytest
import logging
from Shared.API.infrastructure import ResourceManager
from Shared.API.redrock import RedrockController
from Shared.API.workflow import WorkflowManager


logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.bhavna
def test_ui_check_after_request_login_checkout(core_session, pas_setup, get_limited_user_function):
    """
    Test case: C2121
    :param core_session: Authenticated Centrify session
    :param pas_setup: fixture to create system with accounts
    :param users_and_roles: fixture to create user with specific right
    """
    system_id, account_id, sys_info = pas_setup

    limited_sesh, limited_user = get_limited_user_function
    username = limited_sesh.auth_details["User"]
    user_id = limited_sesh.auth_details['UserId']

    result, status = ResourceManager.assign_system_permissions(core_session, "View,Edit", username, user_id,
                                                               pvid=system_id)
    assert status, f'failed to assign "Edit" permission to user {username} for system {sys_info[0]}'
    logger.info(f'Edit permission assigned to user {username} for system {sys_info[0]}')

    # Assigning rights to cloud user, excluding checkout and Login right.
    rights = "View,Manage"
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

    req_request, req_success = WorkflowManager.request_checkout(limited_sesh, account_id,
                                                                starttime=None, endtime=None,
                                                                accesstype="Login", assignmenttype="perm")
    assert req_success, "Workflow Request Failed"
    logger.info(f'Workflow Request is success: {req_request}')
    logger.info(f'user: {username} successfully requested for Login in account: {sys_info[4]}')

    # Step: Request login for an Account
    timenow = datetime.datetime.utcnow()
    start_time = str(timenow)
    end_time = str(timenow + datetime.timedelta(hours=1))
    req_request, req_success = WorkflowManager.request_checkout(limited_sesh, account_id, start_time,
                                                                end_time, "Reason: Testing", "Checkout")
    assert req_success, "Workflow checkout Request Failed"
    logger.info(f'Workflow checkout Request is success: {req_request}')
    logger.info(f'user: {username} successfully requested for checkout of account: {sys_info[4]}')

    test_description = f"Test description by user: {username}"
    result, success = ResourceManager.update_system(core_session, system_id, sys_info[0], sys_info[1],
                                                    "Windows", description=test_description)

    assert success, f"Unable to add a description: {sys_info[0]}. API response result: {result}"
    logger.info(f'successfully updated the description of system: {sys_info[0]}')

    # Get computer details
    result = RedrockController.get_system(core_session, system_id)
    assert result[0]['Row']['Description'] == test_description, f'System description is mismatched'
    logger.info(f'successfully matched the description of system: {sys_info[0]}')
