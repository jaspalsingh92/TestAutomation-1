import pytest
import logging
import requests
from bs4 import BeautifulSoup


pytestmark = [pytest.mark.corebatapi, pytest.mark.loginbatapi]
logger = logging.getLogger('test')
# Testing these requires a tenant inactive default policy to prevent apply to test policies
# Locking the tenant to prevent corruption of other tests.
lock_tenant = True


@pytest.mark.api
@pytest.mark.platform
@pytest.mark.pas
def test_login_using_upn_with_factors_pwd_email_code(create_user_with_policy_enable_auth_email,
                                                     core_session_unauthorized, get_email_authentication_code,
                                                     delete_mail):
    """
        Login Portal using UPN with user
        Select Challenge1: Password
        Select Challenge2: Email code
    """

    # Create a user along with role, policies and profile.
    user = create_user_with_policy_enable_auth_email
    logger.info(user)

    # Check Start MFA for login.
    r = core_session_unauthorized.start_authentication(user.get_login_name())
    result = r.json()['Result']
    assert 'Challenges' in result, f'This user does not need MFA challenges!'
    assert len(result['Challenges']) == 1, f'This user has 1 MFA challenges!'

    # Check Advance MFA for login.
    r = core_session_unauthorized.advance_authentication(
        mechanism_id=result['Challenges'][0]['Mechanisms'][0]['MechanismId'], action="StartOOB")
    logger.info(f"StartOOB result {r.json()}")
    assert r.ok, "Response is OK"

    # To get the Authentication code.
    session = requests.session()
    urls = get_email_authentication_code("Authentication Needed")
    response = session.request("POST", urls)
    soup = BeautifulSoup(response.content, 'html.parser')
    assert "Authentication Successful" in str(soup.find_all()[0].find('span')), 'User cannot login via code as a link! '

    # To delete all the mails
    delete_mail


@pytest.mark.api
@pytest.mark.platform
@pytest.mark.pas
def test_login_using_upn_with_factors_pwd_email_link(create_user_with_policy_enable_auth_all_factors,
                                                     core_session_unauthorized, get_email_authentication_link,
                                                     delete_mail):
    """
        Login Portal using UPN with user
            Select Challenge1: Password
            Select Challenge2: Email link
    """
    user = create_user_with_policy_enable_auth_all_factors
    logger.info(user)
    user_name = user.get_login_name()
    logger.info(f'User {user_name} start to login')
    r = core_session_unauthorized.start_authentication(user_name)
    result = r.json()['Result']
    assert 'Challenges' in result, f'This user does not need MFA challenges!'
    assert len(result['Challenges']) == 1, 'This user has 2 MFA challenges!'

    # to get the user email link
    urls = get_email_authentication_link(user.get_login_name().lower())

    # Access the Link for authentication
    session = requests.session()
    response = session.request("POST", urls)
    assert user.get_login_name().lower() in str(response.content).lower(), f"User {user_name} MFA Login Failed"
    # To delete all the mails
    delete_mail


@pytest.mark.api
@pytest.mark.platform
@pytest.mark.pas_broken
def test_login_using_samaccountname_when_inside_ip_range(create_user_with_policy_2sq,
                                                         set_inside_ip_range, core_session_with_suffix_unauthorized):
    """
     3. Change IP range in Settings, make current machine is inside IP range
     4. Login Portal again, needn't do MFA and login successfully
    """
    assert set_inside_ip_range, "Failed to set current machine to outside IP range"
    user = create_user_with_policy_2sq
    logger.info(user)
    centrify_session = core_session_with_suffix_unauthorized
    r = centrify_session.start_authentication(user.get_login_name())
    result = r.json()['Result']
    assert 'Challenges' in result, f'This user does not need MFA challenges!'
    assert len(result['Challenges']) == 1, f'This user has 1 MFA challenge!'
    up_result = centrify_session.advance_authentication(
        mechanism_id=result['Challenges'][0]['Mechanisms'][0]['MechanismId'], answer='basketball')
    assert up_result.json()['success'], "Password Authentication Failed"
    assert up_result.json()['Result']['Summary'] == 'LoginSuccess'
    logger.info(up_result.json())



