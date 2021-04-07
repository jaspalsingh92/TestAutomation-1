import pytest
from Utils.guid import guid
from Shared.API.infrastructure import ResourceManager
import logging

logger = logging.getLogger("test")


@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_delete_accounts(core_session, pas_config, remote_users_qty1, cleanup_resources):
    """
    TC C283234: Delete accounts.
    :param cleanup_resources: cleanup for systems.
    :param core_session: Authenticates API session
    :param pas_config: returns yaml object
    :param remote_users_qty1: Creates account in target system.
    :param cleanup_resources:clean up system.
    """
    # Clean up system
    systems_list = cleanup_resources[0]

    # Getting system details.
    sys_name = f"{'Win-2012'}{guid()}"
    sys_details = pas_config
    sys_fqdn = sys_details['Windows_infrastructure_data']['FQDN']
    add_user_in_target_system = remote_users_qty1
    user_password = 'Hello123'

    # Adding system.
    add_sys_result, add_sys_success = ResourceManager.add_system(core_session, sys_name,
                                                                 sys_fqdn,
                                                                 'Windows',
                                                                 "Rdp")
    assert add_sys_success, f"failed to add system:API response result:{add_sys_result}"
    logger.info(f"Successfully added system:{add_sys_result}")
    systems_list.append(add_sys_result)

    # Adding account in portal.
    acc_result, acc_success = ResourceManager.add_account(core_session, add_user_in_target_system[0],
                                                          password=user_password, host=add_sys_result,
                                                          ismanaged=True)
    assert acc_success, f"Failed to add account in the portal: {acc_result}"
    logger.info(f"Successfully added account {add_user_in_target_system[0]} in the portal")

    # Delete Account.
    del_account_result, del_account_success = ResourceManager.del_account(core_session, acc_result)
    assert del_account_success, f'Failed to delete account:API response result:{del_account_result}'
    logger.info(f"Successfully deleted account:{del_account_result}")

    # Getting deletion activity.
    sys_activity = ResourceManager.get_system_activity(core_session, add_sys_result)
    assert f'{core_session.auth_details["User"]} deleted local account "{add_user_in_target_system[0]}" for' \
           f' "{sys_name}"({sys_fqdn}) with credential type Password' in \
           sys_activity[0]['Detail'], f"Failed to get the delete account activity:API response result:{sys_activity}"
    logger.info(f"Successfully found deletion activity in system activity:{sys_activity}")
