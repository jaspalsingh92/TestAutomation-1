import pytest
import logging
import time
from Shared.endpoint_manager import EndPoints

lock_tenant = True

logger = logging.getLogger("test")


@pytest.fixture(scope="function")
def api_ratelimit_fixture(core_session, core_blessed_session, core_tenant, is_blessed):
    logger.info('Setting up for rate limit test')

    enableGlobal = {
        'tenantId': 'centrify',
        'key': 'Core.TokenBuckets.GlobalSwitch',
        'value': 'True'
    }

    enableTenant = {
        'tenantId': core_tenant['id'],
        'key': 'Core.TokenBuckets.TenantSwitch',
        'value': 'True'
    }

    limitSysinfo = {
        'tenantId': core_tenant['id'],
        'key': 'Core.TokenBuckets.RestCall.Limit.sysinfocontroller.version',
        'value': '1'
    }

    # Verify we can call /sysinfo/version without issue to start
    response = core_session.get("/sysinfo/version")
    assert response.status_code == 200

    logger.info('Setting up for rate limiting sysinfo/version')
    response = core_blessed_session.post(
        EndPoints.SET_CONFIG_GLOBAL, limitSysinfo).json()
    assert response['success'] is True, f'Failed to set global config {response}'
    response = core_blessed_session.post(
        EndPoints.SET_CONFIG_GLOBAL, enableTenant).json()
    assert response['success'] is True, f'Failed to set global config {response}'
    response = core_blessed_session.post(
        EndPoints.SET_CONFIG_GLOBAL, enableGlobal).json()
    assert response['success'] is True, f'Failed to set global config {response}'

    # Allow the test to run now
    yield True

    # Cleanup
    logger.info('Removing feature flags and disabling rate limiting')
    response = core_blessed_session.post(
        EndPoints.DEL_CONFIG_GLOBAL, enableGlobal).json()
    assert response['success'] is True, f'Failed to delete global config {response}'
    response = core_blessed_session.post(
        EndPoints.DEL_CONFIG_GLOBAL, enableTenant).json()
    assert response['success'] is True,  f'Failed to delete global config {response}'
    response = core_blessed_session.post(
        EndPoints.DEL_CONFIG_GLOBAL, limitSysinfo).json()
    assert response['success'] is True,  f'Failed to delete global config {response}'


@pytest.mark.api
@pytest.mark.platform
@pytest.mark.pas
@pytest.mark.plumbing
@pytest.mark.daily
@pytest.mark.smoke
def test_api_ratelimit(api_ratelimit_fixture, core_session):
    logger.info('Executing /sysinfo/version denial test')

    response = core_session.get("/sysinfo/version")
    assert response.status_code == 200

    # Wait at least >1 second, should be able to get another one
    time.sleep(2)

    response = core_session.get("/sysinfo/version")
    assert response.status_code == 200

    # Now call rapidly in a loop until we've gotten 10 successful 200 results
    # Counting all 200s and 429s, it should take ~10 seconds to run this (fudging for timing)
    logger.info("starting rapid request loop")
    start_time = time.time()
    expected_count = 10
    success_count = 0
    limited_count = 0
    while success_count < expected_count:
        response = core_session.get("/sysinfo/version")
        if response.status_code == 200:
            success_count = success_count + 1
        elif response.status_code == 429:
            limited_count = limited_count + 1
        else:
            logger.error(
                "Unexpected result from rest api was neither 200 or 429")
            assert False, f'Unexpected result from rest API was neither 200 or 429 {response.status_code}'

    finish_time = time.time()
    elapsed_time = (finish_time - start_time)
    logger.info("done rapid request loop - success: {} limited: {} took (seconds): {}".format(
        success_count, limited_count, elapsed_time))
    # Verify that time it took was within spitting distance (dont want to be too pedantic here to avoid other timing problems causing failure)
    assert abs(expected_count - elapsed_time) <= expected_count, f'Rate limiting not properly limiting each rest call to the right duration'
