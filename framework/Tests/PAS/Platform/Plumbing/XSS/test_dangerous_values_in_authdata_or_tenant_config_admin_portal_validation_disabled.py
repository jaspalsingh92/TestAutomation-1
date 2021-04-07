import pytest
import logging
import time
import json

from copy import deepcopy

from Shared.endpoint_manager import EndPoints

logger = logging.getLogger("test")

lock_tenant = True


@pytest.fixture(scope="function")
def setup_ui_settings_attack_no_validation(core_blessed_session, core_session, core_tenant, reset_portal_config):

    existing_settings = core_blessed_session.post(EndPoints.GET_CUSTOMER_CONFIG, {}).json()

    old_user_settings = existing_settings['Result']['UserSettings']

    logger.info(f'Old user settings {old_user_settings}')

    turnOffValidation = {
        # 'tenantId': core_tenant['id'],
        'key': 'OldSanitizationPaths',
        'value': json.dumps(['/TenantConfig/SetUISettings', '/TenantConfig/Foo'])
    }

    logger.info('Turning new validation logic off for TenantConfig/SetUISettings')
    response = core_blessed_session.post(
        EndPoints.SET_CONFIG_GLOBAL, turnOffValidation).json()
    assert response['success'] is True, f'Failed to set global configuration for turning off validation logic {response}'

    new_ui_settings = deepcopy(old_user_settings)
    if new_ui_settings is None:
        new_ui_settings = {}
    new_ui_settings['uisection'] = {}
    new_ui_settings['uisection']['AttackProperty'] = ['</script><script>alert(\'foo\')</script>']
    result = core_session.post(EndPoints.SET_UI_SETTINGS, new_ui_settings).json()
    assert result['success'] is True, f'Should be allowed to set dangerous UI setting since request validation is off {result}'

    result = core_blessed_session.post(EndPoints.NUKE_MEMCACHE, {}).json()
    assert result['success'] is True, f'Unable to clear out cached version of ServerConfig/TenantConfig which tests need to be accurate. {result}'

    yield

    result = core_session.post(EndPoints.SET_UI_SETTINGS, old_user_settings).json()
    assert result['success'] is True, f'Failed to reset ui settings {result}'

    logger.info('Turning validation back on for TenantConfig/SetUISettings')
    turnOffValidation['value'] = None
    response = core_blessed_session.post(
        EndPoints.DEL_CONFIG_GLOBAL, turnOffValidation).json()
    assert response['success'] is True, f'Failed to display login banner {response}'

    result = core_blessed_session.post(EndPoints.NUKE_MEMCACHE, {}).json()
    assert result['success'] is True, f'Unable to clear out cached version of ServerConfig/TenantConfig which tests need to be accurate. {result}'


@pytest.mark.xss
@pytest.mark.security
@pytest.mark.embedded_json
def test_ui_settings_attack_no_input_validation(setup_ui_settings_attack_no_validation, core_admin_ui):
    """
    UI will throw unexpected alert Exception and test will fail if attack was successful
    """
    assert True