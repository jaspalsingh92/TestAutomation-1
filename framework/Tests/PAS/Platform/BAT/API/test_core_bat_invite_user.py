import pytest
import requests
import logging

from Shared.API.tenantconfig import TenantConfigManager
from Shared.API.users import UserManager

pytestmark = [pytest.mark.api, pytest.mark.corebatapi]
logger = logging.getLogger('test')
# Testing these requires a tenant inactive default policy to prevent apply to test policies
# Locking the tenant to prevent corruption of other tests.
lock_tenant = True


@pytest.mark.api
@pytest.mark.platform
@pytest.mark.pas
def test_user_login_from_invited_email(create_user_with_policy_enable_auth_email,
                                       core_session, get_email_authentication_link):
    """
    Login Portal using invited email link with user
    """
    user = create_user_with_policy_enable_auth_email
    is_invite = UserManager.invite_users_by_action(core_session, [user.get_login_name()])
    assert is_invite

    # to get the user email link
    urls = get_email_authentication_link(user.get_login_name().lower())

    # Access the Link for authentication
    session = requests.session()
    response = session.request("POST", urls)
    assert user.get_login_name().lower() in str(response.content).lower(), f"User {user.get_login_name()} " \
                                                                           f"MFA Login Failed"


@pytest.mark.api
@pytest.mark.platform
@pytest.mark.pas_broken
def test_reset_password_on_login_page(core_session, create_user_with_policy_enable_self_service_reset_pwd,
                                      core_session_unauthorized):
    """
        Reset User Password on Login page via forgot password
    """
    all_sq = TenantConfigManager.get_admin_security_questions(core_session)
    logger.info(all_sq)
    for admin_sq in all_sq:
        TenantConfigManager.delete_admin_security_question(core_session, admin_sq['Uuid'])

    user = create_user_with_policy_enable_self_service_reset_pwd
    core_session_unauthorized.start_authentication(user.get_login_name())
    r = core_session_unauthorized.advance_authentication(action='ForgotPassword')
    result = r.json()['Result']
    assert 'Challenges' in result, f'This user does not have MFA challenges!'

    # Security question
    res = core_session_unauthorized.advance_authentication(
        mechanism_id=result['Challenges'][0]['Mechanisms'][0]['MechanismId'], answer="basketball", action="Answer")
    logger.info(f"StartOOB result {r.json()}")
    assert res.ok, "Response is OK"

    # Check Advance email MFA for login.
    temp_password = "Password@123"
    resp = core_session_unauthorized.advance_authentication(
        mechanism_id=result['Challenges'][1]['Mechanisms'][0]['MechanismId'], answer=temp_password, action="Answer")
    assert resp.json()['success'], 'Password change failed'

    # login up and set security question
    result = core_session_unauthorized.start_authentication(user.get_login_name())
    res = core_session_unauthorized.advance_authentication(
        mechanism_id=result.json()['Result']['Challenges'][0]['Mechanisms'][0]['MechanismId'], answer=temp_password,
        action="Answer")
    logger.info(f"StartOOB result {r.json()}")
    assert res.ok, "Login Failed"
