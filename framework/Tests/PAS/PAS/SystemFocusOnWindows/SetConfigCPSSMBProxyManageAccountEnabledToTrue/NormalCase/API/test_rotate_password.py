import logging
import pytest
from Shared.API.infrastructure import ResourceManager
from Utils.guid import guid

logger = logging.getLogger("test")


@pytest.mark.pas
@pytest.mark.api
def test_rotate_password(core_session, pas_config, remote_users_qty3, test_proxy,
                         cleanup_resources, cleanup_accounts):
    """
    TC: C2577 - Rotate Password for managed account
     trying to Rotate Password for managed account
            Steps:
                Pre: Create system with 1 proxy and manage account hand
                1. Try to rotate password
                    -Assert Failure
                2. Try to check activity of manage account
                    -Assert Failure
    """
    system_list = cleanup_resources[0]
    accounts_list = cleanup_accounts[0]
    user_name = core_session.get_user().get_login_name()

    sys_name = f'{"Win-2012"}{guid()}'
    user_password = 'Hello123'
    sys_details = pas_config
    add_user_in_target_system = remote_users_qty3
    fdqn = sys_details['Windows_infrastructure_data']['FQDN']
    # Adding system.
    add_sys_result, add_sys_success = ResourceManager.add_system(core_session, sys_name,
                                                                 fdqn,
                                                                 'Windows',
                                                                 "Rdp")
    assert add_sys_success, f"failed to add system:API response result:{add_sys_result}"
    logger.info(f"Successfully added system:{add_sys_result}")
    system_list.append(add_sys_result)

    # Update system with proxy user
    update_sys_success, update_sys_result = ResourceManager.update_system(core_session, add_sys_result, sys_name,
                                                                          fdqn, 'Windows',
                                                                          proxyuser=add_user_in_target_system[1],
                                                                          proxyuserpassword=user_password,
                                                                          proxyuserismanaged=True)
    assert update_sys_success, f'Fail to update the system:API response result: {update_sys_result}'
    logger.info(f"Successfully update the system:{update_sys_result}")

    # Adding account in portal.
    acc_result, acc_success = ResourceManager.add_account(core_session, add_user_in_target_system[0],
                                                          password=user_password, host=add_sys_result,
                                                          ismanaged=True)
    assert acc_success, f"Failed to add account in the portal: {acc_result}"
    logger.info(f"Successfully added account {add_user_in_target_system[0]} in the portal")

    # Update system with management mode 'Smb'.
    update_sys_success, update_sys_result = ResourceManager.update_system(core_session, add_sys_result, sys_name,
                                                                          fdqn,
                                                                          'Windows',
                                                                          managementmode='Smb')
    assert update_sys_success, f'Fail to update the system:API response result: {update_sys_result}'
    logger.info(f"Successfully update the system:{update_sys_result}")

    result, success = ResourceManager.rotate_password(core_session, acc_result)
    assert success, f"Did not rotate password, API response: {result}"
    logger.info(f"User able to rotate the password: {result}")
    row = ResourceManager.get_system_activity(core_session, add_sys_result)
    assert f'{user_name} rotated local account "{add_user_in_target_system[0]}" credential for "{sys_name}"({fdqn})' \
           in row[0]['Detail'], "Did not retrieve the activity of rotate password"
    logger.info(f"User able to get the activity: {row[0]['Detail']}")
    accounts_list.append(acc_result)


@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_add_account_existing_system(core_session, pas_config, remote_users_qty1, test_proxy, cleanup_resources,
                                     cleanup_accounts):
    """
    TC: C2575 - Add managed account to existing system
     trying to Add managed account to existing system
            Steps:
                Pre: Create system with 1 proxy and manage account hand
                1. Try to checkout password
                    -Assert Failure
                2. Try to check activity of manage account
                    -Assert Failure
    """
    user_details = core_session.__dict__['auth_details']
    user_name = core_session.get_user().get_login_name()
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

    # Adding account in portal.
    acc_result, acc_success = ResourceManager.add_account(core_session, add_user_in_target_system[0],
                                                          password=user_password, host=add_sys_result,
                                                          ismanaged=True)
    assert acc_success, f"Failed to add account in the portal: {acc_result}"
    logger.info(f"Successfully added account {add_user_in_target_system[0]} in the portal")

    rights = "Owner,View,Manage,Delete,Login,Naked,RotatePassword,FileTransfer"
    result, success = ResourceManager.assign_account_permissions(core_session, rights, user_details['User'],
                                                                 user_details['UserId'], pvid=acc_result)
    assert success, f"Did not rotate password, API response: {result}"

    # Update system with management mode 'Smb'.
    update_sys_success, update_sys_result = ResourceManager.update_system(core_session, add_sys_result, sys_name,
                                                                          fdqn,
                                                                          'Windows',
                                                                          managementmode='Smb')
    assert update_sys_success, f'Fail to update the system:API response result: {update_sys_result}'
    logger.info(f"Successfully update the system:{update_sys_result}")

    res, success = ResourceManager.rotate_password(core_session, acc_result)
    assert success, f"Failed to add account in the portal: {res}"

    result, success = ResourceManager.check_out_password(core_session, 1, acc_result)
    assert result['Password'] != "Hello123", \
        f"password checkout Failed. API response result: {result}"
    logger.info(f"password successfully checkout Account password: {result['COID']}")
    row = ResourceManager.get_system_activity(core_session, add_sys_result)
    assert f'{user_name} checked out local account "{add_user_in_target_system[0]}" ' \
           f'password for system "{sys_name}"({fdqn})' in row[0]['Detail'], \
        "Did not retrieve the activity of rotate password"
    logger.info(f"User able to get the activity logs: {row[0]['Detail']}")
    accounts_list.append(acc_result)


@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_add_manage_account_with_proxy_account(core_session, pas_config, remote_users_qty3,
                                               cleanup_resources, cleanup_accounts, test_proxy):
    """
    TC: C2574 - Add system with managed account using proxy account
     trying to Add system with managed account using proxy account
            Steps:
                Pre: Create system with 1 proxy and manage account hand
                1. Try to checkout password
                    -Assert Failure
                2. Try to check activity of manage account
                    -Assert Failure
    """
    user_name = core_session.get_user().get_login_name()
    logger.info(f'core sessoin user {core_session.get_user()}')
    system_list = cleanup_resources[0]
    accounts_list = cleanup_accounts[0]
    # Getting system details.
    sys_name = f'{"Win-2012"}{guid()}'
    user_password = 'Hello123'
    sys_details = pas_config
    add_user_in_target_system = remote_users_qty3
    fdqn = sys_details['Windows_infrastructure_data']['FQDN']
    # Adding system.
    add_sys_result, add_sys_success = ResourceManager.add_system(core_session, sys_name,
                                                                 fdqn,
                                                                 'Windows',
                                                                 "Rdp")
    assert add_sys_success, f"failed to add system:API response result:{add_sys_result}"
    logger.info(f"Successfully added system:{add_sys_result}")
    system_list.append(add_sys_result)

    # Update system with proxy user
    update_sys_success, update_sys_result = ResourceManager.update_system(core_session, add_sys_result, sys_name,
                                                                          fdqn, 'Windows',
                                                                          proxyuser=add_user_in_target_system[1],
                                                                          proxyuserpassword=user_password,
                                                                          proxyuserismanaged=True)
    assert update_sys_success, f'Fail to update the system:API response result: {update_sys_result}'
    logger.info(f"Successfully update the system:{update_sys_result}")

    # Update system with management mode 'Smb'.
    update_sys_success, update_sys_result = ResourceManager.update_system(core_session, add_sys_result, sys_name,
                                                                          fdqn,
                                                                          'Windows',
                                                                          managementmode='Smb')
    assert update_sys_success, f'Fail to update the system:API response result: {update_sys_result}'
    logger.info(f"Successfully update the system:{update_sys_result}")

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

    result, success = ResourceManager.check_out_password(core_session, 1, acc_result)
    assert result['Password'] != "Hello123", \
        f"password checkout Failed. API response result: {result}"
    logger.info(f"password successfully checkout Account password: {result['COID']}")
    row = ResourceManager.get_system_activity(core_session, add_sys_result)
    assert f'{user_name} checked out local account "{add_user_in_target_system[0]}" ' \
           f'password for system "{sys_name}"({fdqn})' in row[0]['Detail'], \
        "Did not retrieve the activity of rotate password"
    logger.info(f"User able to get the activity logs: {row[0]['Detail']}")
    accounts_list.append(acc_result)
