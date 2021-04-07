import pytest
import logging
from Shared.API.infrastructure import ResourceManager
from Utils.config_loader import Configs

logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi
def test_update_un_managed_using_managed_proxy_account_check_password_history(core_session,
                                                                              pas_windows_setup,
                                                                              test_proxy,
                                                                              pas_config):
    """
    TC: C2550 Update un managed account with using proxy account.
    :param core_session: Returns a API session.
    :param pas_windows_setup: Fixture for adding a system and an account associated with it.
    :param pas_config: fixture reading data from resource_data.yaml file.

    """
    # Creating a system with un managed account using un managed proxy account.
    system_id, account_id, sys_info, connector_id, user_password = pas_windows_setup()

    # Updating the proxy user password.
    payload_data = pas_config['Windows_infrastructure_data']
    update_proxy_result, update_proxy_success = ResourceManager.update_system(core_session,
                                                                              system_id,
                                                                              sys_info[0],
                                                                              sys_info[1],
                                                                              sys_info[2],
                                                                              proxyuser=payload_data['proxy_username'],
                                                                              proxyuserpassword=payload_data[
                                                                                  'proxy_password'],
                                                                              proxyuserismanaged=False)
    assert update_proxy_success, f"Failed to update proxy user password:API response result:{update_proxy_result}."
    logger.info(f"Successfully able to update the proxy user password without error {update_proxy_result}.")

    # Updating the un managed account with invalid password.
    invalid_data = Configs.get_test_node('invalid_resources_data', 'automation_main')
    invalid_payload_data = invalid_data['System_infrastructure_data']
    invalid_acc_password = invalid_payload_data['invalid_password']
    result_update_account, result_update_success = ResourceManager.update_password(core_session,
                                                                                   account_id,
                                                                                   invalid_acc_password)

    assert result_update_success, f"Failed to update account with invalid password:" \
                                  f"API response result:{result_update_account}"
    logger.info(f"Successfully able to update the un managed "
                f"account with invalid password:{result_update_account}.")

    # Getting the Account information and validating the status.
    status = 'BadCredentials'
    get_account_info, get_account_status = ResourceManager.get_accounts_from_resource(core_session, system_id)
    assert get_account_info[0]['Healthy'] == status, f'Status does not change to Unknown: {status}'
    logger.info(f"Successfully able to change status to Unknown {get_account_info}.")

    # Updating the un managed account with correct password.
    updated_account_correct_result, updated_account_correct_success = ResourceManager.update_password(core_session,
                                                                                                      account_id,
                                                                                                      payload_data[
                                                                                                          'password'])
    assert updated_account_correct_result, f"Failed to update account with correct password:{payload_data['password']}"
    logger.info(
        f"Successfully able to update the un managed account with correct password: {updated_account_correct_result}.")

    # Getting the system activity and validating update local account password is done or not.
    username = core_session.get_user().get_login_name()
    result_activity = ResourceManager.get_system_activity(core_session, system_id)
    assert f'{username} updated local account "{sys_info[4]}" password for "{sys_info[0]}"' \
           f'({sys_info[1]})' in result_activity[0]['Detail'], \
        f"fail to update local account password :{sys_info[4]} "
    logger.info(f"Successfully update un managed password : {result_activity}")
