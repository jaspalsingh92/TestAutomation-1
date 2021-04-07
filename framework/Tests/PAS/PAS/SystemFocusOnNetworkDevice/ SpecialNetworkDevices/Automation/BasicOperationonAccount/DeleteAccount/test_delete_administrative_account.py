import pytest
import logging
from Shared.API.redrock import RedrockController
from Shared.API.infrastructure import ResourceManager

logger = logging.getLogger('test')


@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi
def test_delete_administrative_account(core_session, network_device_setup):
    """
    TC: C2623 - Delete administrative account
    :param core_session: Authenticated Centrify session.
    :param network_device_setup: Adds a network with account and returns UUID of both.
    """
    system_id, account_id, device_data, system_list, account_list = network_device_setup('checkpoint')
    system_info = RedrockController.get_computer_with_ID(core_session, system_id)

    # setting up Admin account for system
    result, success, message = ResourceManager.set_system_administrative_account(core_session, system_id, account_id)
    assert success, f"Failed to update Administrative account for system {system_info['Name']}"
    logger.info(f"Successfully added an administrative account for system {system_info['Name']}")

    # deleting administrative account
    del_result, del_success = ResourceManager.del_account(core_session, account_id)
    assert del_success is False, f"Admin account deleted successfully, unexpected behaviour as Admin account " \
                                 f"should not be deleted. API response result: {del_success}"
    logger.info(f'Admin account could not be deleted as expected, API response result: {del_success}')

    # finding all systems for cleanup:
    acc_script = "@/lib/server/get_accounts.js(mode:'AllAccounts', newcode:true, localOnly:true, colmemberfilter:" \
                 "'Select ID from VaultAccount WHERE Host IS NOT NULL')"
    acc = RedrockController.redrock_query(core_session, acc_script)
    for account in acc:
        if account['Row']['FQDN'] == "Check.Point":
            # Removing Admin Account for successful cleanup of system and account
            result, success, message = ResourceManager.set_administrative_account(core_session,
                                                                                  systems=[account['Row']['Host']])
            assert success, f"Failed to update Administrative account for system {account['Row']['Name']}"

            # Removing Admin Account for successful cleanup of system and account
            ResourceManager.update_system(core_session,
                                          account['Row']['Host'],
                                          account['Row']['Name'],
                                          account['Row']['FQDN'],
                                          'CheckPointGaia',
                                          sessiontype=account['Row']['SessionType'])

            # deleting administrative account from this system
            ResourceManager.del_account(core_session, account['Row']['ID'])

            # Removing Admin Account for successful cleanup of system and account
            result, success, message = ResourceManager.set_administrative_account(core_session,
                                                                                  systems=[account['Row']['Host']])
            assert success, f"Failed to update Administrative account for system {account['Row']['Name']}"
