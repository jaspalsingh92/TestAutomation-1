import logging
import pytest
from Shared.API.infrastructure import ResourceManager
from Shared.API.redrock import RedrockController

logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_system_health_check(core_session, pas_windows_setup):
    """
    C1553 : Add System
    :param core_session: Authenticated Centrify Session.
    :param pas_windows_setup: Creates system with account
    """
    sys_info = pas_windows_setup()
    system_details = RedrockController.get_computer_with_ID(core_session, sys_info[0])
    ResourceManager.get_date(system_details['LastHealthCheck'])
    assert system_details['HealthStatus'] == 'OK', "Remote System is not reachable either system is down or system " \
                                                   "could not configured properly. "
    logger.info(f"System is reachable successfully: {system_details}")


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_import_system_and_health_check(core_session, pas_windows_setup):
    """
    C1554 : Import system and check health
    :param core_session: Authenticated Centrify Session.
    :param pas_windows_setup:
    """
    system_id, account_id, sys_info, connector_id, user_password = pas_windows_setup()
    system_details = RedrockController.get_computer_with_ID(core_session, system_id)

    system_counter = 1
    while system_counter < 60:
        if system_details['HealthStatus'] == 'OK' and system_details['LastHealthCheck']:
            break
        system_counter += 1
    ResourceManager.get_date(system_details['LastHealthCheck'])
    assert system_details['HealthStatus'] == 'OK', "System not reachable because connector is not up."
    logger.info(f"System is reachable successfully: {system_details}")

    account_counter = 1
    account_details = None
    while account_counter < 60:
        account_details = ResourceManager.get_account_information(core_session, account_id)
        if account_details[0]['VaultAccount']['Row']['Healthy'] == 'OK' and \
                account_details[0]['VaultAccount']['Row']['LastHealthCheck']:
            break
        account_counter += 1
    ResourceManager.get_date(account_details[0]['VaultAccount']['Row']['LastHealthCheck'])
    assert account_details[0]['VaultAccount']['Row']['Healthy'] == 'OK', \
        "System not reachable because connector is not up."
    logger.info(f"Account is reachable successfully: {account_details}")
