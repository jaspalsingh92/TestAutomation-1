import pytest
import logging
from bs4 import BeautifulSoup
from Shared.endpoint_manager import EndPoints

pytestmark = [pytest.mark.api, pytest.mark.corebatapi]
logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.platform
@pytest.mark.pas
def get_redirect_url_and_form(content):
    soup = BeautifulSoup(content, 'html.parser')
    form = soup.find('form')
    url = form['action']
    logger.info(form['action'])

    inputs = soup.find_all('input')
    form_data = dict()
    for item in inputs:
        if item['type'].lower() != 'submit':
            form_data[item['name']] = item['value']
    return url, form_data


@pytest.mark.api
@pytest.mark.platform
@pytest.mark.pas
def test_launch_user_password_app(deploy_app_jira_server_user_password, core_session, application_cleaner):
    """
        Launch app, then make sure this website show up and logged in
    """
    app_key = deploy_app_jira_server_user_password
    result = core_session.get(EndPoints.LAUNCH_APP + "?appkey=" + app_key)
    content = result.content.decode()
    assert content.find('<input type="submit" value="Submit" />') > -1, f'Could not find submit input that is expected in handleAppClick if username and password is found correctly'
    url, form_data = get_redirect_url_and_form(content)
    response = core_session.session.request('POST', url, data=form_data, verify=False)
    logger.info(response.headers)
    assert 'log out' in str(response.content).lower(), 'Could not find log out after launch!'
    application_cleaner.append(app_key)


@pytest.mark.api
@pytest.mark.platform
@pytest.mark.pas
def test_launch_saml_app(deploy_app_confluence_server_saml, core_session, application_cleaner):
    """
        Launch app, then make sure this website show up and logged in
    """
    app_key = deploy_app_confluence_server_saml
    result = core_session.get(EndPoints.LAUNCH_APP + "?appkey=" + app_key)
    content = result.content.decode()
    assert content.find(
        'document.myform.submit();') > -1, f'Could not find submit input that is expected in handleAppClick if username and password is found correctly'
    url, form_data = get_redirect_url_and_form(content)
    response = core_session.session.request('POST', url, data=form_data, verify=False)
    assert 'log out' in str(response.content).lower(), 'Could not find log out after launch!'
    application_cleaner.append(app_key)
