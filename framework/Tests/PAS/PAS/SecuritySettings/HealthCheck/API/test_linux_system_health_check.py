import pytest
import logging
from Shared.API.redrock import RedrockController
from Shared.API.infrastructure import ResourceManager

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_linux_system_health_check(core_session, setup_pas_system_for_unix):
    """
    C1556 : Linux system health check
    :param core_session: Authenticated Centrify Session.
    :param setup_pas_system_for_unix: create one system and return details associated to it.
    """
    system_info = setup_pas_system_for_unix
    system_details = RedrockController.get_computer_with_ID(core_session, system_info[0])
    ResourceManager.get_date(system_details['LastHealthCheck'])
    assert system_details['HealthStatus'] == 'OK', "Remote System is not reachable either system is down or system " \
                                                   "could not configured properly. "
    logger.info(f"Remote System is reachable successfully: {system_details}")
