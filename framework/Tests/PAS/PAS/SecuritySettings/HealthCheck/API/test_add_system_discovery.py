import logging
import pytest
from Shared.API.discovery import Discovery
from Shared.API.redrock import RedrockController
from Shared.API.server import ServerManager

logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.pas_failed
@pytest.mark.bhavna
def test_add_system_discovery(core_session, ad_discovery_profile, pas_ad_discovery_config, core_value,
                              delete_discovered_system):
    """
    Test Case: Add System (C1555)
    :param core_session: Authenticated Centrify Session
    :param ad_discovery_profile: Fixture to create AD profile for system discovery
    :param pas_ad_discovery_config: fixture to read yaml file to create profile
    :param core_value: fixture to read core.yaml
    :param delete_discovered_system: fixture for cleanup before and after discovery
    """
    config_profile = pas_ad_discovery_config
    profile_data = config_profile['ad_profile_data'][0]
    domain_details = config_profile['domains']
    domain_name = []
    domain_id_list = []
    for domains in domain_details:
        domain_name.append(domains['Name'])
    for domain in domain_name:
        domain_id = RedrockController.get_id_from_name(core_session, domain, 'VaultDomain')
        domain_id_list.append(domain_id)

    # Delete System and account before discovery
    delete_discovered_system(profile_data['discovered_system'], domain_id_list)
    profile_list, profile_name, profile_id, account_list, account_id = ad_discovery_profile(domain_name,
                                                                                            profile_data['account_in_domain'])
    # Run Discovery to discover window system
    result_run, success, response = Discovery.run_discovery_profile(core_session, profile_id, wait_for_run=True)
    assert success, f"Failed to run discovery profile: {response}"
    logger.info(f"Discovery ran successfully, API response: {result_run} ")

    # Check Last Verify and Last Verify Result for Account
    last_verify = None
    last_verify_result = None
    account_list = RedrockController.get_accounts(core_session)
    discovered_account = []
    for account in account_list:
        if account['AccountDiscoveredTime'] is not None:
            discovered_account.append(account['ID'])
            last_verify = account['Status']
            last_verify_result = account['LastHealthCheck']
    assert len(discovered_account) != 0, f"Failed to discover system, account and services {discovered_account}"
    logger.info(f"Discovered Account is: {discovered_account}")
    assert last_verify_result is not None, "Failed to test account"
    assert last_verify == "Missing Password", "Failed to test account"
    logger.info(f"Last Test:{last_verify} and Last Test Result: {last_verify_result}")

    # Check Last Test Result and Last Test for Domain
    result = ServerManager.get_all_domains(core_session)
    for domain in result:
        if domain['Name'] in domain_name:
            last_test = domain['LastHealthCheck']
            last_test_result = domain['HealthCheckInterval']
            assert last_test is not None, "Failed to test Domain"
            assert last_test_result is None, "Failed to test Domain"
            logger.info(f"Domain Name: {domain['Name']}, Last Test:{last_test} and Last Test Result: {last_test_result}")

    # Check Last Test Result and Last Test for Discovered System
    result = RedrockController.get_computers(core_session)
    last_test = None
    last_test_result = None
    discovered_system = []
    for system in result:
        if system['DiscoveredTime'] is not None:
            discovered_system.append(system['ID'])
            last_test = system['LastHealthCheck']
            last_test_result = system['HealthCheckInterval']
    assert last_test is not None, "Failed to test system"
    assert last_test_result is None, "Failed to test system"
    logger.info(f"Last Test:{last_test} and Last Test Result: {last_test_result}")

    # Cleanup after discovery
    delete_discovered_system(profile_data['discovered_system'], domain_id_list)
