import pytest
import logging
from Shared.API.infrastructure import ResourceManager
from Shared.API.redrock import RedrockController
from Shared.winrm_commands import update_user_password
from Utils.guid import guid

logger = logging.getLogger("test")


@pytest.mark.pas
@pytest.mark.api
def test_update_un_managed_account(pas_windows_setup, core_session):
    """
    :param pas_windows_setup:    Fixture for adding a system and an account associated with it.
    :param core_session: Authenticated Centrify Session.
    TC: C2548 - Update un managed account
    trying to Update un managed account password
      Steps:
           Pre: Create system with 1 un manage account hand
            1. Try to update valid password
                -Assert Failure
            2. Try to get activity of updated password
                -Assert Failure
            3. Try to check password history
    """
    user_name = core_session.get_user().get_login_name()
    system_id, account_id, sys_info, connector_id, user_password = pas_windows_setup()
    logger.info(f"System: {sys_info[0]} successfully added with UUID: {system_id} and account: {sys_info[4]} "
                f"with UUID: {account_id} associated with it.")
    Result, success = ResourceManager.update_password(core_session, account_id, guid())
    assert success, f"Did not update password, API Response: {Result}"
    logger.info(f'user not able to update password, API Response::{Result}')
    row = ResourceManager.get_system_activity(core_session, system_id)
    assert f'{user_name} updated local account "{sys_info[4]}" password for "{sys_info[0]}"' in row[0]['Detail'], \
        "user not able to update un managed account password"
    logger.info(f'account activity logs for un manage account API response:{row}')
    result, success = ResourceManager.check_out_password(core_session, 1, account_id)
    assert success, f"Did not retrieve password API response: {result}"
    logger.info(f'user not able to retrieve password API response:{result}')
    query = f"select EntityId, State, StateUpdatedBy, StateUpdatedTime from PasswordHistory where EntityId=" \
            f"'{account_id}' and StateUpdatedBy='{user_name}' and State='Retired'"
    password_history = RedrockController.get_result_rows(RedrockController.redrock_query(core_session, query))[0]
    assert len(password_history) > 0, f"Password history table did not update {password_history}"
    logger.info(f'Password history table API response:{password_history}')


@pytest.mark.pas
@pytest.mark.api
def test_update_manage_proxy_account(pas_config, core_session, winrm_engine,
                                     remote_users_qty3, test_proxy, cleanup_accounts, cleanup_resources):
    """
    TC: C2549 - Update managed account with using proxy account
    trying to Update managed account with using proxy account
     Steps:
          Pre: Create system with 1 proxy and manage account hand
          1. Try to update invalid password for proxy account
              -Assert Failure
          2. Try to update valid password for proxy account
              -Assert Failure
          3.  Try to check activity log's
              -Assert Failure
          4. Try to check password history
    """

    system_list = cleanup_resources[0]
    accounts_list = cleanup_accounts[0]
    # Getting system details.
    sys_name = f'{"Win-2012"}{guid()}'
    sys_details = pas_config
    add_user_in_target_system = remote_users_qty3
    user_password = 'Hello123'
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

    # Update system with proxy user password.
    update_sys_success, update_sys_result = ResourceManager.update_system(core_session, add_sys_result, sys_name,
                                                                          fdqn, 'Windows',
                                                                          proxyuser=add_user_in_target_system[1],
                                                                          proxyuserpassword=guid(),
                                                                          proxyuserismanaged=True)
    assert update_sys_result is False, f'Fail to update the system:API response result: {update_sys_result}'
    logger.info(f"Successfully update the system:{update_sys_result}")

    # Adding account in portal.
    acc_result, acc_success = ResourceManager.add_account(core_session, add_user_in_target_system[0],
                                                          password=user_password, host=add_sys_result,
                                                          ismanaged=True)
    assert acc_success, f"Failed to add account in the portal: {acc_result}"
    logger.info(f"Successfully added account {add_user_in_target_system[0]} in the portal")
    accounts_list.append(acc_result)
    # set a different password for the user
    update_user_password(winrm_engine, add_user_in_target_system[1],
                         user_password)

    user_name = core_session.get_user().get_login_name()

    # rotate password for manage account
    result, success = ResourceManager.rotate_password(core_session, acc_result)
    assert success, f"Did not Rotate Password {result}"
    logger.info(f'account activity logs for un manage account API response:{result}')
    result, success = ResourceManager.check_out_password(core_session, 1, acc_result)
    assert success, f"Did not retrieve password {result}"
    logger.info(f'account activity logs for un manage account API response:{result}')
    row = ResourceManager.get_system_activity(core_session, add_sys_result)
    assert f'{user_name} checked out local account "{add_user_in_target_system[0]}" ' \
           f'password for system "{sys_name}"({fdqn})' in \
           row[0]['Detail'], "user not able to update un managed account password"
    logger.info(f'account activity logs for un manage account API response:{row}')
    query = f"select EntityId, State, StateUpdatedBy, StateUpdatedTime from PasswordHistory where EntityId=" \
            f"'{acc_result}' and StateUpdatedBy='{user_name}' and State='Retired'"
    password_history = RedrockController.get_result_rows(RedrockController.redrock_query(core_session, query))[0]
    assert len(password_history) > 0, f"Password history table did not update {password_history}"
    logger.info(f'Password history table API response:{password_history}')


@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi
def test_update_manage_account_win_rm(pas_config, winrm_engine, core_session, remote_users_qty1,
                                      cleanup_accounts, test_proxy, cleanup_resources):
    """
    :param pas_config: to get the data from yaml files.
    :param remote_users_qty1: to create a manage account in windows system
    :param cleanup_resources: cleanup the system from portal
    :param cleanup_accounts: cleanup the accounts from portal
    :param winrm_engine:  session to update manage account
    :param core_session: Authenticated Centrify Session.
    TC: C2551 - Update managed account password with winRM https configured
    trying to Update managed account password with winRM https configured
     Steps:
          Pre: Create system with 1 proxy and manage account hand
          1. Try to update invalid password for manage account
              -Assert Failure
    """
    sys_details = pas_config
    system_data_values = sys_details['Windows_infrastructure_data']
    add_user_in_target_system = remote_users_qty1

    password = "Pass@123"
    # set a different password for the user
    update_user_password(winrm_engine, add_user_in_target_system[0],
                         password)

    system_list = cleanup_resources[0]
    accounts_list = cleanup_accounts[0]
    # Getting system details.
    sys_name = f'{"Win-2012"}{guid()}'

    # Adding system.
    add_sys_result, add_sys_success = ResourceManager.add_system(core_session, sys_name,
                                                                 system_data_values['FQDN'],
                                                                 'Windows',
                                                                 "Rdp")
    assert add_sys_success, f"failed to add system:API response result:{add_sys_result}"
    logger.info(f"Successfully added system:{add_sys_result}")
    system_list.append(add_sys_result)
    # Update system with management mode 'WinRMOverHttp'.
    update_sys_success, update_sys_result = ResourceManager.update_system(core_session, add_sys_result, sys_name,
                                                                          system_data_values['FQDN'],
                                                                          'Windows',
                                                                          managementmode='WinRMOverHttps')
    assert update_sys_success, f'Fail to update the system:API response result: {update_sys_result}'
    logger.info(f"Successfully update the system:{update_sys_result}")

    # Adding account in portal.
    acc_result, acc_success = ResourceManager.add_account(core_session, add_user_in_target_system[0],
                                                          password=password,
                                                          host=add_sys_result,
                                                          ismanaged=True)
    assert acc_success, f"Failed to add account in the portal: {acc_result}"
    logger.info(f"Successfully added account {add_user_in_target_system[0]} in the portal")
    accounts_list.append(acc_result)
    managementMode = RedrockController.get_computer_with_ID(core_session, add_sys_result)
    assert managementMode['ManagementMode'] == "WinRMOverHttps", \
        f"management mode is failed because of system doesnt have proxy account. API response result: {managementMode}"
    logger.info(f"Fetch management mode successfully: {managementMode['ManagementMode']}")
    Result, success = ResourceManager.update_password(core_session, acc_result, guid())
    assert success is False, f"Did not update password {Result}"
    logger.info(f"user not able to update password API response: {Result}")
