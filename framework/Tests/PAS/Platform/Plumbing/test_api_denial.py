import pytest
import logging
from Shared.endpoint_manager import EndPoints

logger = logging.getLogger("test")

lock_tenant = True


@pytest.fixture(scope="function")
def api_denial_fixture(core_session, core_blessed_session, core_tenant, is_blessed):

    # Set global config Core.DenialCheck.GlobalSwitch => "True"
    globalConfigArguments = {
        'tenantId': 'centrify',
        'key': 'Core.DenialCheck.GlobalSwitch',
        'value': 'True'
    }

    # Set tenant config
    tenantConfigArguments = {
        'tenantId': core_tenant['id'],
        'key': 'Core.DenialCheck.sysinfocontroller.version',
        'value': 'True'
    }

    logger.info(f'Setting api denail on {core_tenant["id"]}')

    logger.info('Setting up for denial test')
    response = core_session.get("/sysinfo/version")
    assert response.status_code == 200, f'Cannot invoke sysinfo/version even before fixture sets up configs'

    logger.info('Enabling global feature')
    response = core_blessed_session.post(
        EndPoints.SET_CONFIG_GLOBAL, globalConfigArguments).json()
    assert response['success'] is True, f'Failed to set global config {response}'

    logger.info('Denying at tenant level')
    response = core_blessed_session.post(
        EndPoints.SET_CONFIG_GLOBAL, tenantConfigArguments).json()
    assert response['success'] is True, f'Failed to set tenant config {response}'

    yield True

    # Cleanup
    logger.info('Removing feature flags')
    response = core_blessed_session.post(
        EndPoints.DEL_CONFIG_GLOBAL, globalConfigArguments).json()
    assert response['success'] is True, f'Failed to delete global config {response}'
    response = core_blessed_session.post(
        EndPoints.DEL_CONFIG_GLOBAL, tenantConfigArguments).json()
    assert response['success'] is True, f'Failed to delete tenant config {response}'


@pytest.mark.api
@pytest.mark.platform
@pytest.mark.pas
@pytest.mark.plumbing
@pytest.mark.daily
def test_api_denial(api_denial_fixture, core_session, core_tenant):
    logger.info('Executing /sysinfo/version denial test')

    response = core_session.get("/sysinfo/version")
    assert response.status_code == 503, f'Expected sysinfo/version to fail after setting configs but it succeeded or return an unexpected status code.'
