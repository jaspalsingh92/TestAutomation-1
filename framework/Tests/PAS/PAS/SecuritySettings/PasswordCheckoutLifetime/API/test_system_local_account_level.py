import logging
import pytest
from Utils.guid import guid
from Shared.API.server import ServerManager
from Shared.API.redrock import RedrockController
from Shared.API.infrastructure import ResourceManager

logger = logging.getLogger("test")


@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_system_local_account_level(core_session, pas_config, remote_users_qty1, cleanup_accounts, cleanup_resources):
    """
    TC C282671: System Local Account Level.
    :param cleanup_resources: cleanup for systems.
    :param core_session: Authenticates API session
    :param pas_config: returns yaml object
    :param remote_users_qty1: Creates account in target system.
    :param cleanup_accounts: cleanup for account.
    """
    systems_list = cleanup_resources[0]
    accounts_list = cleanup_accounts[0]

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
    accounts_list.append(acc_result)

    # Setting the lifetime checkout for account to 15 min.
    default_checkout_lifetime = 15
    updated_account_result, update_account_success = \
        ResourceManager.update_account(core_session,
                                       acc_result,
                                       add_user_in_target_system[0],
                                       host=add_sys_result,
                                       default_checkout_time=default_checkout_lifetime)
    assert update_account_success, f"Failed to add default checkout time: API response result:{updated_account_result}"
    logger.info(f'Successfully added default checkout time: {updated_account_result}"')

    # Setting the lifetime checkout for system to 60 min.
    updated_sys_result, update_sys_success = ResourceManager.update_system(core_session, add_sys_result,
                                                                           sys_name,
                                                                           sys_fqdn,
                                                                           'Windows',
                                                                           defaultcheckouttime=60)
    assert update_sys_success, f"Failed to add default checkout time: API response result:{updated_account_result}"
    logger.info(f'Successfully added default checkout time: {updated_sys_result}"')

    # Checking the default account password set to default ie 60 min.
    default_account_password_chk_lifetime = 60
    results, success = ServerManager.get_server_settings(core_session, key='policy')
    assert results['DefaultCheckoutTime'] == default_account_password_chk_lifetime, \
        f"account password  checkout lifetime is not {default_account_password_chk_lifetime} "

    # Checkout account.
    checkout_result, checkout_success = ResourceManager.check_out_password(core_session, 15, acc_result)
    assert checkout_success, f"Fail to checkout account : {acc_result} : API response " \
                             f"result: {checkout_result}"
    logger.info(f"Successfully checked account : {checkout_result}")

    # Checking the checkout in the workspace and validating the checkout lifetime.
    checkout_remaining_time = str(default_checkout_lifetime - 1)
    checkout_accounts = RedrockController.get_password_checkout_from_workspace(core_session,
                                                                               core_session.auth_details['UserId'])
    for checkout_account in checkout_accounts:
        if checkout_account['ID'] == checkout_result['COID']:
            assert checkout_account['Remaining'].split()[0] == checkout_remaining_time,\
                f"Fail to find the remaining  checkout time equal to {checkout_remaining_time} "
            logger.info(" Successfully found the checkout activity in workspace.")

    # Trying to checkout once again,expecting a null checkout ID.
    failed_checkout_result, failed_checkout_success = ResourceManager.check_out_password(core_session, 15, acc_result)
    assert failed_checkout_result['COID'] is None, f"checkout account ID generated for : " \
                                                   f"{add_user_in_target_system[0]}:" \
                                                   f"API response result: {failed_checkout_result}"
    logger.info(f"Check in option is action enable : {failed_checkout_result}")

    # Checking out checkout activity.
    acc_activity = RedrockController.get_account_activity(core_session, acc_result)
    assert f'{core_session.auth_details["User"]} checked out local account "{add_user_in_target_system[0]}" password ' \
           f'for system "{sys_name}"({sys_fqdn})' in \
           acc_activity[0]['Detail'], f"no activity of checkout found for account {add_user_in_target_system[0]}"
    logger.info(f"There is a checkout record for the account {add_user_in_target_system[0]} in activity")
