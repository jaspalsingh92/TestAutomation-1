import pytest
import logging
from Shared.API.infrastructure import ResourceManager
from Shared.API.redrock import RedrockController
from Utils.guid import guid

logger = logging.getLogger("test")


@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
@pytest.mark.pas_pdst
def test_checkout_password(core_session, pas_config, cleanup_resources, cleanup_accounts, remote_users_qty1):
    """TC C2554 - Checkout password for a windows managed account from Accounts page
     trying to Checkout password for a windows managed account from Accounts page
        Steps:
           Pre: Create system with 1 manage account hand
              1. Try to Checkout password for an account
                  -Assert Failure
              2. Try to check my password checkouts in workspace
                  -Assert Failure
    """
    system_list = cleanup_resources[0]
    accounts_list = cleanup_accounts[0]
    # Getting system details.
    sys_name = f'{"Win-2012"}{guid()}'
    user_password = 'Hello123'
    sys_details = pas_config
    add_user_in_target_system = remote_users_qty1
    fdqn = sys_details['Windows_infrastructure_data']['FQDN']
    # Adding system.
    add_sys_result, add_sys_success = ResourceManager.add_system(core_session, sys_name,
                                                                 fdqn,
                                                                 'Windows',
                                                                 "Rdp")
    assert add_sys_success, f"failed to add system:API response result:{add_sys_result}"
    logger.info(f"Successfully added system:{add_sys_result}")
    system_list.append(add_sys_result)

    success, response = ResourceManager.update_system(core_session, add_sys_result, sys_name,
                                                      fdqn, 'Windows',
                                                      managementmode='RpcOverTcp')
    assert success, f"failed to change the management mode:API response result:{response}"
    logger.info(f"Successfully updated the system:{add_sys_result}")

    # Adding account in portal.
    acc_result, acc_success = ResourceManager.add_account(core_session, add_user_in_target_system[0],
                                                          password=user_password, host=add_sys_result,
                                                          ismanaged=True)
    assert acc_success, f"Failed to add account in the portal: {acc_result}"
    logger.info(f"Successfully added account {add_user_in_target_system[0]} in the portal")

    server_id = ResourceManager.wait_for_server_to_exist_return_id(core_session, sys_name)
    acc_id = ResourceManager.wait_for_account_to_exist_return_id(core_session, add_user_in_target_system[0])
    assert server_id == add_sys_result, "Server was not created"
    assert acc_id == acc_result, "Account was not created"

    res, success = ResourceManager.rotate_password(core_session, acc_result)
    assert success, f"Failed to add account in the portal: {res}"

    password_checkout_result, password_checkout_success = \
        ResourceManager.check_out_password(core_session, 1, accountid=acc_result)
    assert password_checkout_result['Password'] != user_password, \
        f"expected password equal to actual password: {password_checkout_result}"
    logger.info(f"password successfully checkout Account password: {password_checkout_result}")
    my_password_checkout = RedrockController.get_total_checkouts(core_session)
    created_date_json = str(my_password_checkout[0]['LoanDate'])
    ResourceManager.get_date(created_date_json)
    check_out_details = []
    for i in my_password_checkout:
        if i['Summary'] in f'{add_user_in_target_system[0]} ({sys_name})':
            check_out_details.append(i['Summary'])
    assert check_out_details[0] == f'{add_user_in_target_system[0]} ({sys_name})',\
        "fail to checkout password from workspace"
    logger.info(f"password successfully checkout Account password::{my_password_checkout}")
    accounts_list.append(acc_result)
    password_check_in_result, password_check_in_success = ResourceManager.check_in_password(
        core_session, coid=password_checkout_result['COID'])
    assert password_check_in_success, f"password check-in Failed. API response result: {password_check_in_result}"
    logger.info(f"password successfully check in for account: {add_user_in_target_system[0]}")


@pytest.mark.pas
@pytest.mark.api
def test_check_in_password(core_session, pas_config, cleanup_resources, cleanup_accounts,
                           remote_users_qty1):
    """TC C2555 Checkin password for the managed account from Accounts page
      trying to Checkin password for the managed account from Accounts page
         Steps:
           Pre: Create system with 1 manage account hand
              1. Try to Checkout password for an account
                  -Assert Failure
              2. Try to check my password check-ins in workspace
                  -Assert Failure
      """
    system_list = cleanup_resources[0]
    accounts_list = cleanup_accounts[0]
    # Getting system details.
    sys_name = f'{"Win-2012"}{guid()}'
    user_password = 'Hello123'
    sys_details = pas_config
    add_user_in_target_system = remote_users_qty1
    fdqn = sys_details['Windows_infrastructure_data']['FQDN']
    # Adding system.
    add_sys_result, add_sys_success = ResourceManager.add_system(core_session, sys_name,
                                                                 fdqn,
                                                                 'Windows',
                                                                 "Rdp")
    assert add_sys_success, f"failed to add system:API response result:{add_sys_result}"
    logger.info(f"Successfully added system:{add_sys_result}")
    system_list.append(add_sys_result)

    success, response = ResourceManager.update_system(core_session, add_sys_result, sys_name,
                                                      fdqn, 'Windows',
                                                      managementmode='RpcOverTcp')
    assert success, f"failed to change the management mode:API response result:{response}"
    logger.info(f"Successfully updated the system:{add_sys_result}")

    # Adding account in portal.
    acc_result, acc_success = ResourceManager.add_account(core_session, add_user_in_target_system[0],
                                                          password=user_password, host=add_sys_result,
                                                          ismanaged=True)
    assert acc_success, f"Failed to add account in the portal: {acc_result}"
    logger.info(f"Successfully added account {add_user_in_target_system[0]} in the portal")

    server_id = ResourceManager.wait_for_server_to_exist_return_id(core_session, sys_name)
    acc_id = ResourceManager.wait_for_account_to_exist_return_id(core_session, add_user_in_target_system[0])
    assert server_id == add_sys_result, "Server was not created"
    assert acc_id == acc_result, "Account was not created"

    password_checkout_result, password_checkout_success = \
        ResourceManager.check_out_password(core_session, 1, accountid=acc_result)
    assert password_checkout_success, \
        f"expected password equal to actual password: {password_checkout_result}"
    logger.info(f"password successfully checkout Account password: {password_checkout_result}")
    my_password_checkout = RedrockController.get_total_checkouts(core_session)
    created_date_json = str(my_password_checkout[0]['LoanDate'])
    ResourceManager.get_date(created_date_json)

    check_in_details = []
    for i in my_password_checkout:
        if i['Summary'] in f'{add_user_in_target_system[0]} ({sys_name})':
            check_in_details.append(i['Summary'])
    assert check_in_details[0] == f'{add_user_in_target_system[0]} ({sys_name})', \
        "fail to checkout password from workspace"
    logger.info(f"password successfully checkout Account password::{my_password_checkout}")
    password_check_in_result, password_check_in_success = ResourceManager.check_in_password(
        core_session, coid=password_checkout_result['COID'])
    assert password_check_in_success, f"password check-in Failed. API response result: {password_check_in_result}"
    logger.info(f"password successfully check in for account: {add_user_in_target_system[0]}")

    username = core_session.get_user().get_login_name()
    row = ResourceManager.get_system_activity(core_session, add_sys_result)
    created_date_json = str(row[0]['When'])
    ResourceManager.get_date(created_date_json)
    check_in_details = []
    for i in row:
        if i['Detail'].__contains__("checked in local account"):
            check_in_details.append(i['Detail'])

    assert f'{username} checked in local account "{add_user_in_target_system[0]}" ' \
           f'password for system "{sys_name}"({fdqn})' in \
           check_in_details[0], "fail to check in password "
    logger.info(f"account activity list:{row}")
    my_password_checkout = RedrockController.get_total_checkouts(core_session)
    assert len(my_password_checkout) == 0, "Check in my password in workspace is not getting updated"
    logger.info(f"password successfully check in for account: {my_password_checkout}")
    accounts_list.append(acc_result)
