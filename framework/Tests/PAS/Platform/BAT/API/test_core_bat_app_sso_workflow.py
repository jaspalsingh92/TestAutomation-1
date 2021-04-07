from Shared.API.applications import ApplicationManager
from Shared.API.workflow import WorkflowManager
import pytest
import logging

pytestmark = [pytest.mark.api, pytest.mark.corebatapi]
logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.platform
@pytest.mark.pas
def test_workflow_approve(deploy_app_jira_server_user_password_with_workflow, core_session, core_tenant,
                          core_session_unauthorized, application_cleaner):
    """
        1. Request user login
        2. Request launch app
        3. Cloudadmin Approve request
        4. Role2 Approve request
        5. Manager Approve request
        6. Request success, then user login to launch app
    """
    users, roles, app_key = deploy_app_jira_server_user_password_with_workflow
    logger.info('User login and request one app')
    user0 = users[0]
    core_session_unauthorized.security_login(core_tenant['id'], user0.get_login_name(), user0.get_password())
    assert core_session_unauthorized.auth_details is not None, "Login Failed"
    job_id, is_success = WorkflowManager.request_launch(core_session_unauthorized, app_key, reason='I want to use this app.')
    logger.info(f'Request job id: {job_id}')
    assert is_success, f'Request launch app failed!'
    core_session_unauthorized.logout()

    jobs, is_get = WorkflowManager.get_my_jobs(core_session)
    assert is_get, f'Get jobs failed!'
    for i in jobs:
        if i['Row']['ID'] == job_id:
            assert i['Row']['InitiatorNotes'] == 'I want to use this app.', f'The job request reason is wrong'
            assert i['Row']['TotalStepNum'] == 3, f'The job approver step is wrong'
            assert i['Row']['StepNum'] == 1, f'The job current step is not the first'
            assert i['Row']['TargetPrincipalName'] == core_tenant["admin_user"], f'The current job approver is not admin!'
            assert i['Row']['State'] == 'Ask', f'The job state is wrong'
            break

    logger.info('Approver 1st time: admin login and approve')
    r_job, is_approve = WorkflowManager.approve_request(core_session, job_id, None, None, assignmenttype='perm')
    logger.info(f'Admin approve request: {r_job}')
    assert job_id == r_job['_RowKey'], f'Wrong job was approved by the admin.'
    assert is_approve, f'The request approve failed!'
    assert r_job['StepNum'] == 2, f'The job current step is not the second'
    assert r_job['TargetPrincipalName'] == roles[1]['Name'], f'The next approver is not role'
    assert r_job['TargetPrincipalType'] == 'Role', f'The next approver\'s type is not role'
    assert r_job['State'] == 'Ask', f'The job state is wrong'

    logger.info('Approver 2nd time: user in role login and approve')
    user1 = users[1]
    core_session_unauthorized.security_login(core_tenant['id'], user1.get_login_name(), user1.get_password())
    assert core_session_unauthorized.auth_details is not None, "Login Failed"

    r_job, is_approve = WorkflowManager.approve_request(core_session_unauthorized, job_id, None, None, assignmenttype='perm')
    logger.info(f'User in role approve request: {r_job}')
    assert job_id == r_job['_RowKey'], f'Wrong job was approved by role member.'
    assert is_approve, f'The request approve failed!'
    assert r_job['StepNum'] == 3, f'The job current step is not the 3rd'
    user2 = users[2]
    assert user2.get_login_name() in r_job['TargetPrincipalName']
    assert r_job['State'] == 'Ask', f'The job state is wrong'
    core_session_unauthorized.logout()

    logger.info('Approver 3rd time: cbcu2 login and approve')
    core_session_unauthorized.security_login(core_tenant['id'], user2.get_login_name(), user2.get_password())
    assert core_session_unauthorized.auth_details is not None, "Login Failed"
    r_job, is_approve = WorkflowManager.approve_request(core_session_unauthorized, job_id, None, None, assignmenttype='perm')
    logger.info(f'User manager approve request: {r_job}')
    assert is_approve, f'The request approve failed!'
    assert r_job['TargetPrincipalAction'] == 'Approved', f'The request is not be approved'
    assert r_job['State'] == 'Complete', f'The request is not complete'
    core_session_unauthorized.logout()

    logger.info('User login and check whether get the launch permission')
    core_session_unauthorized.security_login(core_tenant['id'], user0.get_login_name(), user0.get_password())
    assert core_session_unauthorized.auth_details is not None, "Login Failed"

    permissions = ApplicationManager.get_application_permissions(core_session_unauthorized, app_key, user0)
    assert user0.get_login_name().lower() in str(permissions)
    for perm in permissions:
        if perm['name'].lower() == user0.get_login_name().lower():
            assert 'View' in perm['right'], f"The user doesn't have View permission for this app"
            assert 'Run' in perm['right'], f"The user doesn't have Run permission for this app"
    application_cleaner.append(app_key)


@pytest.mark.api
@pytest.mark.platform
@pytest.mark.pas
def test_workflow_reject(deploy_app_confluence_server_saml_with_workflow, core_session, core_tenant, core_session_unauthorized, application_cleaner):
    """
        1. User Request launch app
        2. cloudadmin reject the request
        3. User login and check
    """
    logger.info('User login and request one app')
    user, role, app_key = deploy_app_confluence_server_saml_with_workflow
    core_session_unauthorized.security_login(core_tenant['id'], user.get_login_name(), user.get_password())
    assert core_session_unauthorized.auth_details is not None, "Login Failed"
    job_id, is_success = WorkflowManager.request_launch(core_session_unauthorized, app_key, reason='I want to use this app.')
    logger.info(f'Request job id: {job_id}')
    assert is_success, f'The request failed!'

    jobs, is_get = WorkflowManager.get_my_jobs(core_session)
    assert is_get, f'Get my job failed!'
    for i in jobs:
        if i['Row']['ID'] == job_id:
            assert i['Row']['InitiatorNotes'] == 'I want to use this app.', f'The job request reason is wrong'
            assert i['Row']['TotalStepNum'] == 2, f'The job approver step is wrong'
            assert i['Row']['StepNum'] == 2, f'The job current step is not the second'
            assert i['Row']['TargetPrincipalName'] == core_tenant["admin_user"], f'The current job approver is not admin!'
            assert i['Row']['State'] == 'Ask', f'The job state is wrong'
            break

    logger.info('Approver 1st time: admin login and reject')
    r_job, is_approve = WorkflowManager.approve_request(core_session, job_id, None, None, event='reject')
    logger.info(f'Admin re request: {r_job}')
    assert job_id == r_job['_RowKey'], f'Wrong job was approved by the admin.'
    assert is_approve, f'The request approve failed!'
    assert r_job['State'] == 'Complete', f'The request is not complete'
    assert r_job['TargetPrincipalAction'] == 'Rejected', f'The request is not be Rejected'

    permissions_list = ApplicationManager.get_application_permissions(core_session, app_key, user)
    logger.info(f'Application permissions: {permissions_list}')
    assert user.get_login_name() not in str(permissions_list).lower()

    jobs, is_get = WorkflowManager.get_my_jobs(core_session_unauthorized)
    logger.info(f'My jobs: {jobs}')
    assert is_get, f'Get all jobs failed!'
    for i in jobs:
        if i['Row']['ID'] == job_id:
            assert i['Row']['TotalStepNum'] == 2, f'The job approver step is wrong'
            assert i['Row']['TargetPrincipalAction'] == 'Rejected'
            assert i['Row']['State'] == 'Complete', f'The request is not complete'
            break

    job, is_get = WorkflowManager.get_job(core_session_unauthorized, job_id)
    logger.info(f'This job detail: {job}')
    assert is_get, f'Get job failed!'
    assert job['TargetPrincipalAction'] == 'Rejected', f'The request is not be Rejected'
    assert job['State'] == 'Complete', f'The request is not complete'
    application_cleaner.append(app_key)
