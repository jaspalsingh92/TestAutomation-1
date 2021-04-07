import logging
import pytest
from Shared.API.discovery import Discovery
from Shared.API.infrastructure import ResourceManager
from Shared.API.redrock import RedrockController

logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.pas_failed
@pytest.mark.bhavna
def test_check_service_for_window_system(core_session, ad_discovery_profile, pas_modify_discovery_config,
                                         pas_ad_discovery_config, clean_up_collections, delete_discovered_system):
    """
    TC - Check Services sub-page shows under windows system (C2546)
    :param core_session: Centrify Authentication Session
    :param ad_discovery_profile: Fixture to create AD discovery profile
    :param pas_modify_discovery_config:
    :param pas_ad_discovery_config: Fixture to read yaml file to create AD discovery profile
    :param clean_up_collections:
    :param delete_discovered_system: Fixture run before and after discovery
    """
    config_profile = pas_ad_discovery_config
    domain_details = config_profile['domains']
    domain_name = []
    domain_id_list = []
    for domains in domain_details:
        domain_name.append(domains['Name'])
    for domain in domain_name:
        domain_id = RedrockController.get_id_from_name(core_session, domain, 'VaultDomain')
        domain_id_list.append(domain_id)
    profile_data = config_profile['ad_profile_data'][0]
    profile_list, profile_name, profile_id, account_list, account_id = ad_discovery_profile(domain_name,
                                                                                            profile_data[
                                                                                                'account_in_domain'])
    delete_discovered_system(profile_data['discovered_system'], domain_id_list)

    # Run Discovery Profile to discover system
    result_run, success, response = Discovery.run_discovery_profile(core_session, profile_id, wait_for_run=True)
    assert success, f"Failed to run discovery profile: {response}"

    # Check the Discovered system
    system_list = RedrockController.get_computers(core_session)
    discovered_system = []
    for system in system_list:
        if system['DiscoveredTime'] is not None:
            discovered_system.append(system['ID'])
    assert len(discovered_system) != 0, f"Failed to discover system {discovered_system}"
    logger.info(f"Discovered system is: {discovered_system}")
    system_name_list = []
    for system in discovered_system:
        system_name = RedrockController.get_computer_with_ID(core_session, system)
        system_name_list.append(system_name['Name'])

        # System to be discovered should be in System List
    assert profile_data['discovered_system'] in system_name_list, \
        f"Failed to discovered system {profile_data['discovered_system']}"
    logger.info(f"Discovered system is: {profile_data['discovered_system']}")

    # Check discovered services
    service_list = RedrockController.get_services(core_session)
    discovered_service = []
    discovered_service_name = []
    for service in service_list:
        if service['DiscoveredTime'] is not None:
            discovered_service.append(service['ID'])
            discovered_service_name.append(service['Service'])
    assert len(discovered_service) != 0, f"Failed to discover services {discovered_service}"
    assert profile_data['discovered_service'] in discovered_service_name, \
        f"Failed to discovered system{profile_data['discovered_service']}"
    logger.info(f"Discovered Service(s): {discovered_service_name}")

    # check the Discovered Account
    account_list = RedrockController.get_accounts(core_session)
    discovered_account = []
    discovered_account_name = []
    for account in account_list:
        if account['AccountDiscoveredTime'] is not None:
            discovered_account.append(account['ID'])
            discovered_account_name.append(account['User'])
    assert len(discovered_account) != 0, f"Failed to discover account {discovered_account}"
    system_id = RedrockController.get_id_from_name(core_session, profile_data['discovered_system'], 'Server')
    flag = 0
    for account in discovered_account:
        if flag < len(discovered_account):
            account_host_local = \
                ResourceManager.get_account_information(core_session, account)[0]['VaultAccount']['Row']['Host']
            account_host_domain = \
                ResourceManager.get_account_information(core_session, account)[0]['VaultAccount']['Row'][
                    'DomainID']
            flag += 1
            if account_host_local == system_id:
                local_account_name_list = []
                local_account_name = ResourceManager.get_account_information(core_session,
                                                                             account)[0]['VaultAccount']['Row'][
                    'User']
                local_account_name_list.append(local_account_name)
                assert profile_data['local_discovered_account_name'] in local_account_name_list,\
                    f"Failed to discover desired account {profile_data['local_discovered_account_name']}"
                logger.info(f"Local Discovered Account is: {local_account_name_list}")
            if account_host_domain in domain_id_list:
                domain_account_name_list = []
                domain_account_name = ResourceManager.get_account_information(core_session,
                                                                              account)[0]['VaultAccount']['Row'][
                    'User']
                domain_account_name_list.append(domain_account_name)
                assert profile_data['domain_discovered_account_name'] in domain_account_name_list, \
                    f"Failed to discover desired account {profile_data['domain_discovered_account_name']}"
                logger.info(f"Domain Discovered Account is: {domain_account_name_list}")
                break
        else:
            assert False
    delete_discovered_system(profile_data['discovered_system'], domain_id_list)
