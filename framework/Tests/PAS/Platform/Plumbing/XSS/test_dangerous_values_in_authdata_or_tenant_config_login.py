import pytest
import logging

from copy import deepcopy

from Shared.endpoint_manager import EndPoints
from Shared.UI.Centrify.selectors import Selector, Anchor
from selenium.webdriver.common.by import By

from Utils.xss_vectors import xss_attack_for_urls

logger = logging.getLogger("test")


@pytest.fixture(scope="function")
def setup_login_strings(core_session, core_blessed_session, core_tenant, is_blessed, reset_portal_config):

    enableTenant = {
        'tenantId': core_tenant['id'],
        'key': 'Cloud.EnableCustomLink.StandaloneLogin',
        'value': 'True'
    }

    enableLoginBanner = {
        'tenantId': core_tenant['id'],
        'key': 'DisplayLoginBanner',
        'value': 'True'
    }

    displayLoginBanner = {
        'tenantId': core_tenant['id'],
        'key': 'EnableLoginBannerFeature',
        'value': 'True'
    }

    logger.info('Get existing customer config')
    result = core_session.post(EndPoints.GET_CUSTOMER_CONFIG, {}).json()
    assert result['success'] is True, f'Failed to get customer config {result}'

    old_customer_config = result['Result']

    # injection_string = xss_attack['attack']
    # server_will_reject = xss_attack['server_validation_rejects']

    logger.info('Enable custom login link')
    response = core_blessed_session.post(
        EndPoints.SET_CONFIG_GLOBAL, enableTenant).json()
    assert response['success'] is True, f'Failed to set custom login link {response}'

    logger.info('Enable login banner')
    response = core_blessed_session.post(
        EndPoints.SET_CONFIG_GLOBAL, enableLoginBanner).json()
    assert response['success'] is True, f'Failed to enable login banner {response}'

    logger.info('Display login banner')
    response = core_blessed_session.post(
        EndPoints.SET_CONFIG_GLOBAL, displayLoginBanner).json()
    assert response['success'] is True, f'Failed to display login banner {response}'

    new_customer_config = deepcopy(old_customer_config)
    new_customer_config['CustomLinkTitle1'] = 'foo "'
    new_customer_config['CustomLinkUrl1'] = 'https://google.com/foo'
    new_customer_config['CustomLinkTitle2'] = 'bar "'
    new_customer_config['CustomLinkUrl2'] = 'https://google.com/foo'
    new_customer_config['LoginSampleText'] = 'Sample login text >'
    new_customer_config['TermsOfUseLink'] = xss_attack_for_urls
    new_customer_config['PrivacyPolicyLink'] = xss_attack_for_urls

    # Make the custom login banner message show up
    new_customer_config['DisplayLoginBanner'] = True
    new_customer_config['LoginBannerMessageL10nEnabled'] = False
    new_customer_config['LoginBannerMessage'] = 'Custom login banner >'

    logger.info('Set customer config with XSS attack')
    result = core_session.post(EndPoints.SET_CUSTOMER_CONFIG, new_customer_config).json()
    assert result['success'] is True, f'Server unexpectedly disallowed custom login links {result}'

    result = core_blessed_session.post(EndPoints.NUKE_MEMCACHE, {}).json()
    assert result['success'] is True, f'Unable to clear out cached version of ServerConfig/TenantConfig which tests need to be accurate. {result}'

    # Allow the test to run now
    yield new_customer_config['CustomLinkTitle1'], new_customer_config['CustomLinkTitle2'], new_customer_config['LoginSampleText'], new_customer_config['LoginBannerMessage']

    enableTenant['value'] = 'False'
    enableLoginBanner['value'] = 'False'
    displayLoginBanner['value'] = 'False'

    logger.info('Turning custom login links off for tenant')
    response = core_blessed_session.post(
        EndPoints.DEL_CONFIG_GLOBAL, enableTenant).json()
    assert response['success'] is True,  f'Failed to delete global config {response}'

    logger.info('Turning off login banner enable')
    response = core_blessed_session.post(
        EndPoints.DEL_CONFIG_GLOBAL, enableLoginBanner).json()
    assert response['success'] is True, f'Failed to enable login banner {response}'

    logger.info('Turning off login banner display')
    response = core_blessed_session.post(
        EndPoints.DEL_CONFIG_GLOBAL, displayLoginBanner).json()
    assert response['success'] is True, f'Failed to display login banner {response}'

    logger.info('Restore old customer config')
    result = core_session.post(EndPoints.SET_CUSTOMER_CONFIG, old_customer_config).json()
    assert result['success'] is True, f'Failed to restore old customer config with XSS {result}'

    result = core_blessed_session.post(EndPoints.NUKE_MEMCACHE, {}).json()
    assert result['success'] is True, f'Unable to clear out cached version of ServerConfig/TenantConfig which tests need to be accurate. {result}'



@pytest.mark.xss
@pytest.mark.security
@pytest.mark.embedded_json
def test_login_ui_protected_from_xss(setup_login_strings, core_session_unauthorized, core_tenant, login_ui):
    document_contents = core_session_unauthorized.get('/login').text
    logger.info(document_contents)
    custom_link_title_1, custom_link_title_2, login_sample_text, login_banner_message = setup_login_strings

    # Checks embedded authdata/serverconfig encoding as well as the eventual dom rendering.
    # JSON encoding should be \" and html encoding should be &quot;
    assert document_contents.find(custom_link_title_1) == -1, f'Found un-encoded custom link title which can lead to a login attack.'
    assert document_contents.find(custom_link_title_2) == -1, f'Found un-encoded custom link title which can lead to a login attack.'

    json_encoded_title_1 = custom_link_title_1.replace('"', '\\"')
    json_encoded_title_2 = custom_link_title_1.replace('"', '\\"')
    assert document_contents.find(json_encoded_title_1) > -1, f'Could not find properly json encoded custom link title which can lead to a login attack.'
    assert document_contents.find(json_encoded_title_2) > -1, f'Could not find properly json encoded custom link title which can lead to a login attack.'

    # one would think the xpath should have the html encoded entity but apparently not - the browser and Selenium conspire to make that not work,
    # even though the JavaScript is actually embedding an html entity properly
    login_ui.expect(Selector(By.XPATH, f"//a[text()='{custom_link_title_1}']"), f'Could not find properly html encoded custom link 1 title')
    login_ui.expect(Selector(By.XPATH, f"//a[text()='{custom_link_title_2}']"), f'Could not find properly html encoded custom link 2 title')

    login_ui.expect(Selector(By.XPATH, f"//label[text()='{login_banner_message}']"), f'Could not find login banner message')

    login_name_field = Selector(By.XPATH, f"//input[contains(@placeholder , '{login_sample_text}')]")
    continue_button = login_ui.expect(Selector(By.XPATH, f"//button[text()='Continue']"), 'Could not find continue button')
    continue_button.try_click(login_name_field)

    terms_of_use_link = login_ui.expect(Anchor(text="Terms of Use"), f'Could not find terms of use link')
    terms_of_use_link.try_click()
    fixed_xss_attack = xss_attack_for_urls.replace('JavascripT:', '')
    fixed_xss_url = f'https://{core_tenant["fqdn"]}/{fixed_xss_attack}'
    logger.info(f'Expecting de-fanged xss url to be {fixed_xss_url}')
    login_ui.wait_for_tab_with_url(fixed_xss_url)
    login_ui.browser.close()
    login_ui.switch_first_tab()

    privacy_policy_link = login_ui.expect(Anchor(text="Privacy Policy"), f'Could not find terms of use link')
    privacy_policy_link.try_click()
    login_ui.wait_for_tab_with_url(fixed_xss_url)
