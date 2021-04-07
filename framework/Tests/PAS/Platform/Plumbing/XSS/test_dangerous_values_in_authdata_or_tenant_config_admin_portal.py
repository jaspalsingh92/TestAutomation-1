import pytest
import logging
import time

from Shared.endpoint_manager import EndPoints
from copy import deepcopy
from Utils.xss_vectors import xss_attack_expectations, xss_attack_for_urls
from Utils.guid import guid

from Shared.UI.Centrify.SubSelectors.forms import TextField


logger = logging.getLogger("test")

lock_tenant = True

# https://owasp.org/www-community/xss-filter-evasion-cheatsheet


@pytest.fixture(scope="function")
def xss_attack(request):
    yield request.param


@pytest.fixture(params=[
    True,
    False
])
def in_enumerable(request):
    yield request.param


@pytest.fixture(scope="function")
def inject_xss_attacks_in_server_config(core_session, core_blessed_session, xss_attack, in_enumerable, reset_portal_config):
    logger.info('Get existing customer config')
    result = core_session.post(EndPoints.GET_CUSTOMER_CONFIG, {}).json()
    assert result['success'] is True, f'Failed to get customer config {result}'

    old_customer_config = result['Result']

    injection_string = xss_attack['attack']
    server_will_reject = xss_attack['server_validation_rejects']

    new_customer_config = deepcopy(old_customer_config)
    if in_enumerable:
        new_customer_config['AllowCors'] = [injection_string]
    else:
        new_customer_config['WelcomeMessage'] = injection_string

    logger.info(f'Set customer config with XSS attack {injection_string}')
    result = core_session.post(EndPoints.SET_CUSTOMER_CONFIG, new_customer_config).json()
    assert result['success'] is not server_will_reject and result['MessageID'] != '_I18N_System.NullReferenceException', \
        f'The server did not react to the attack in the expected manner. Reject: {server_will_reject}. Attack: {injection_string} {result}'

    result = core_blessed_session.post(EndPoints.NUKE_MEMCACHE, {}).json()
    assert result['success'] is True, f'Unable to clear out cached version of ServerConfig/TenantConfig which tests need to be accurate. {result}'

    yield True

    logger.info('Restore old customer config')
    result = core_session.post(EndPoints.SET_CUSTOMER_CONFIG, old_customer_config).json()
    assert result['success'] is True, f'Failed to restore old customer config with XSS {result}'

    result = core_blessed_session.post(EndPoints.NUKE_MEMCACHE, {}).json()
    assert result['success'] is True, f'Unable to clear out cached version of ServerConfig/TenantConfig which tests need to be accurate. {result}'


@pytest.fixture(scope="function")
def inject_privacy_tos_attack_in_server_config(core_blessed_session, core_session, reset_portal_config):
    logger.info('Get existing customer config')
    result = core_session.post(EndPoints.GET_CUSTOMER_CONFIG, {}).json()
    assert result['success'] is True, f'Failed to get customer config {result}'

    old_customer_config = result['Result']

    new_customer_config = deepcopy(old_customer_config)
    new_customer_config['TermsOfUseLink'] = xss_attack_for_urls
    new_customer_config['PrivacyPolicyLink'] = xss_attack_for_urls

    logger.info(f'Set customer config with XSS attack {xss_attack_for_urls} in TOS/privacy links')
    result = core_session.post(EndPoints.SET_CUSTOMER_CONFIG, new_customer_config).json()
    assert result['success'] is True, 'Server rejected xss attack in urls we expected it to accept'

    result = core_blessed_session.post(EndPoints.NUKE_MEMCACHE, {}).json()
    assert result['success'] is True, f'Unable to clear out cached version of ServerConfig/TenantConfig which tests need to be accurate. {result}'

    yield True

    logger.info('Restore old customer config')
    result = core_session.post(EndPoints.SET_CUSTOMER_CONFIG, old_customer_config).json()
    assert result['success'] is True, f'Failed to restore old customer config with XSS {result}'

    result = core_blessed_session.post(EndPoints.NUKE_MEMCACHE, {}).json()
    assert result['success'] is True, f'Unable to clear out cached version of ServerConfig/TenantConfig which tests need to be accurate. {result}'


@pytest.fixture(scope="function")
def setup_google_key_attack(core_session, core_blessed_session):

    result = core_session.post(EndPoints.SET_GOOGLE_KEY, {
        'googleKey': '<script>alert(\'foo\')</script>',
        'GoogleKeyEnabled': True
    }).json()

    assert result['success'] is False, f'Allowed to set dangerous google API key {result}'

    result = core_blessed_session.post(EndPoints.NUKE_MEMCACHE, {}).json()
    assert result['success'] is True, f'Unable to clear out cached version of ServerConfig/TenantConfig which tests need to be accurate. {result}'

    yield

    result = core_session.post(EndPoints.SET_GOOGLE_KEY, {
        'googleKey': '',
        'GoogleKeyEnabled': False
    }).json()

    assert result['success'] is True, f'Failed to reset google key status {result}'

    result = core_blessed_session.post(EndPoints.NUKE_MEMCACHE, {}).json()
    assert result['success'] is True, f'Unable to clear out cached version of ServerConfig/TenantConfig which tests need to be accurate. {result}'


@pytest.fixture(scope="function")
def setup_ui_settings_attack(core_blessed_session):

    existing_settings = core_blessed_session.post(EndPoints.GET_CUSTOMER_CONFIG, {}).json()

    old_user_settings = existing_settings['Result']['UserSettings']

    logger.info(f'Old user settings {old_user_settings}')

    new_ui_settings = deepcopy(old_user_settings)
    if new_ui_settings is None:
        new_ui_settings = {}
    new_ui_settings['AttackProperty'] = '<script>alert(\'foo\')</script>'

    result = core_blessed_session.post(EndPoints.SET_UI_SETTINGS, new_ui_settings).json()

    assert result['success'] is False, f'Allowed to set dangerous UI setting {result}'

    result = core_blessed_session.post(EndPoints.NUKE_MEMCACHE, {}).json()
    assert result['success'] is True, f'Unable to clear out cached version of ServerConfig/TenantConfig which tests need to be accurate. {result}'

    yield

    result = core_blessed_session.post(EndPoints.SET_UI_SETTINGS, old_user_settings).json()

    assert result['success'] is True, f'Failed to reset ui settings {result}'

    result = core_blessed_session.post(EndPoints.NUKE_MEMCACHE, {}).json()
    assert result['success'] is True, f'Unable to clear out cached version of ServerConfig/TenantConfig which tests need to be accurate. {result}'


@pytest.mark.parametrize('xss_attack', xss_attack_expectations, indirect=True)
def test_xss_injection_via_customer_config(inject_xss_attacks_in_server_config):
    """
    Note that at the time of writing this, our use of ASP.NET RequestValidation on json properties in the payload
    seems to prevent any dangerous payloads from being stored. Namely payloads that contain a <script> tag which will
    break the browser out of its current json block. There was a bug where a specific property, "AllowCors" did not go
    through ASP.NET RequestValidation (likely because it is an array) so that property was able to contain a <script> tag
    """
    # This test will fail automatically if there is an XSS attack because the fixture checks to make sure the API request
    # to save the dangerous value fails.
    assert True


@pytest.mark.xss
@pytest.mark.security
@pytest.mark.embedded_json
def test_google_key_api_is_safe(setup_google_key_attack):
    """
    Checking to make sure dangerous string are not allowed in google api.
    """
    assert True


@pytest.mark.xss
@pytest.mark.security
@pytest.mark.embedded_json
def test_setting_ui_settings_is_safe(setup_ui_settings_attack):
    """
    Checking to make sure dangerous string are not allowed in google api.
    """
    assert True


@pytest.mark.xss
@pytest.mark.security
@pytest.mark.embedded_json
def test_privacy_tos_links(inject_privacy_tos_attack_in_server_config, core_admin_ui):
    """
    Injecting an unsafe xss attack into privacy policy / tos links and making sure the
    alert is not shown in the admin ui
    """
    core_admin_ui.navigate('Settings', 'General', 'Account Customization')
    tosInput = core_admin_ui.expect(TextField('TermsOfUseLink'), 'Could not find terms of use link input to test clicking for xss')
    tosInput.try_click()


@pytest.mark.xss
@pytest.mark.security
@pytest.mark.embedded_json
def test_giving_current_user_unsafe_name(users_and_roles):
    """
    Checking that a user's name is properly escaped.
    """
    user_guid = guid()
    username = f'"-{user_guid}'
    json_encoded_username = f'\"-{user_guid}'

    user = users_and_roles.get_user(rights=['System Administrator'], user_properties={
        'Username': username,
        'Password': 'testTEST1234'
    })

    session = users_and_roles.get_session_for_specific_user(user)

    document_contents = session.get('/home').text

    assert document_contents.find(username) == -1, f'Found un-encoded username which is dangerous and allows xss attack.'

    assert document_contents.find(json_encoded_username) == -1, f'Could not find json encoded username which would prevent xss attack'