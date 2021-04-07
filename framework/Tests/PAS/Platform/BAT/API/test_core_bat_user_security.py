import pytest
import logging
from Shared.API.users import UserManager

pytestmark = [pytest.mark.api, pytest.mark.corebatapi]
logger = logging.getLogger('test')
# Testing these requires a tenant inactive default policy to prevent apply to test policies
# Locking the tenant to prevent corruption of other tests.
lock_tenant = True


@pytest.mark.api
@pytest.mark.platform
@pytest.mark.pas_broken
def test_unlock_user_account(create_user_with_policy_enable_self_service_unlock_account, core_session_unauthorized,
                             core_session):
    """
        Lock user via enter wrong password, then unlock User Account
    """
    user = create_user_with_policy_enable_self_service_unlock_account
    i = 0
    # Do fail to login 3 times, then the user be locked automatically
    while i < 3:
        i = i + 1
        r = core_session_unauthorized.start_authentication(user.get_login_name())
        result = r.json()['Result']
        assert 'Challenges' in result, f'This user does not have MFA challenges!'
        mechanisms1 = result['Challenges'][0]['Mechanisms']
        mechanisms2 = result['Challenges'][1]['Mechanisms']
        sq_mech_id = None
        for mechanism in mechanisms1:
            if mechanism['Name'] == 'SQ':
                sq_mech_id = mechanism['MechanismId']
                sq_mechanism = mechanism
                break
        assert sq_mech_id is not None, 'Security question MechanismId does not exist!'
        security_questions = user.get_security_questions()

        core_session_unauthorized.sq_advance_authentication(security_questions, sq_mechanism, sq_mech_id)

        up_mech_id = None
        for mechanism in mechanisms2:
            if mechanism['Name'] == 'UP':
                up_mech_id = mechanism['MechanismId']
                break
        assert up_mech_id is not None, 'Password MechanismId does not exist!'
        # use wrong password to login
        r = core_session_unauthorized.advance_authentication(answer=user.get_password() + ",", mechanism_id=up_mech_id)
        assert r.json()['success'] is False, 'Authentication passed!'

    # Check user was locked
    uid = UserManager.get_user_id(core_session, user.get_login_name())
    user_attr = UserManager.get_user(core_session, uid)
    assert user_attr['DisplayName'] in user.get_login_name(), 'Get locked user name is wrong!'
    assert user_attr['State'] == "Locked", 'Get user state is not be Locked!'

    # unlock user
    r = UserManager.set_user_state(core_session, uid, False)
    assert r, "set user state fail"

    # Check user was unlocked
    user_attr = UserManager.get_user(core_session, uid)
    assert user_attr['DisplayName'] in user.get_login_name(), 'Get locked user name is wrong!'
    assert user_attr['State'] == "None", 'Get user state is not None!'
