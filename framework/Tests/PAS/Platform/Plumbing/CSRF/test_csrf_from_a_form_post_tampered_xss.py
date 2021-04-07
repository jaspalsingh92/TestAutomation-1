import pytest
import logging
import time

from urllib.parse import quote
from Shared.endpoint_manager import EndPoints

from selenium.webdriver.common.by import By

logger = logging.getLogger('test')

lock_tenant = True


@pytest.mark.ui
@pytest.mark.csrf
@pytest.mark.security
def test_csrf_from_a_form_post_tampered_xss(external_site, cds_ui, cds_session, core_tenant, reset_portal_config):
    ui, user = cds_ui
    session, user = cds_session
    attack_endpoint = EndPoints.SET_CUSTOMER_CONFIG
    # Give the browser a moment to finish all xhr requests which will then let us get the "freshest" antixss value
    time.sleep(5)
    anti_xss = ui.browser.wait_for_cookie('antixss')['value']

    # Set one of the anti-xss tokens to an invalid value
    all_tokens = anti_xss.split('-')
    tampered_xss_token = 'foo'
    all_tokens[0] = tampered_xss_token
    tampered_tokens = '-'.join(all_tokens)
    attack_url_with_antixss = f'https://{core_tenant["fqdn"]}{attack_endpoint}?antixss={quote(tampered_xss_token)}'
    ui.browser.set_cookie('antixss', tampered_tokens)

    # See if the attack will work with a tampered xss token
    external_site_url = f'{external_site}/form?attackUrl={quote(attack_url_with_antixss)}'
    ui.browser.navigate(external_site_url)
    ui.input('NavigationColor', '#333333')
    submit_button = ui.expect((By.CSS_SELECTOR, 'input[type="submit"]'), 'Could not find submit input.')
    submit_button.try_click()

    # Expected to fail because origin header set by the browser will get rejected.
    ui.browser.wait_for_document_ready()

    result = session.post(EndPoints.GET_CUSTOMER_CONFIG, {}).json()

    assert result['Result']['NavigationColor'] != '#333333', '!!!Security hole!!! Form post CSRF was successful.'
