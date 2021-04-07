import pytest
import logging
from Utils.guid import guid
from Shared.API.infrastructure import ResourceManager

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi
def test_add_system_with_unmanaged_account(core_session, network_config, cleanup_accounts, cleanup_resources):
    """
    C2605 - Add system with unmanaged account
    :param core_session: Authenticated Centrify session.
    :param network_config: Returns network device configuration from environment configuration file.
    :param cleanup_accounts: Deletes created account during tear-down.
    :param cleanup_resources: Deletes created system during tear-down.
    """
    system_list = cleanup_resources[0]
    account_list = cleanup_accounts[0]
    device_data = network_config['f5bigip']
    system_name = f"{device_data['system_name']}{guid()}"

    # Adding the network device/ system
    system_id, system_success = ResourceManager.add_system(core_session, system_name, device_data['FQDN'],
                                                           device_data['system_class'], device_data['session_type'],
                                                           device_data['description'])
    assert system_success, f"System addition failed with API response result {system_id}"
    logger.info(f'System: {system_name} successfully added to CPS portal.')
    system_list.append(system_id)

    # Adding unmanaged account to the system
    account_id, success = ResourceManager.add_account(core_session, device_data['account_name'],
                                                      device_data['password'], system_id, device_data['is_managed'])
    assert success, f"Account addition failed with API response result {account_id}"
    logger.info(f"An unmanaged account {device_data['account_name']} successfully added to {system_name}")
    account_list.append(account_id)
