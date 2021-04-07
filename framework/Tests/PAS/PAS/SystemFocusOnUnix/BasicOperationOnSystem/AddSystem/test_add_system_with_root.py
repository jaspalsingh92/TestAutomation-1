import pytest
import logging
from Shared.API.infrastructure import ResourceManager
from Shared.API.redrock import RedrockController
from Shared.util import Util

logger = logging.getLogger('test')


@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi
def test_add_system_with_root_with_managed_proxy_account(core_session, unix_machine_environment_config,
                                                         cleanup_resources_with_admin, cleanup_accounts,
                                                         create_unix_users, ssh_session_as_root):
    """
    Test case : C279340
    :param ssh_session_as_root: session to create a user_account in unix
    :param cleanup_accounts: to delete all accounts
    :param cleanup_resources_with_admin: to delete the all the systems from portal
    :param unix_machine_environment_config: to get the unix system details
   :param core_session: Centrify session manager
    :param create_unix_users: fixture that provide created unix system data
    """
    systems_list = cleanup_resources_with_admin
    accounts_list = cleanup_accounts[0]
    conf = unix_machine_environment_config
    hostname = conf['host'] + "_" + Util.random_string(5)
    # add users on target system
    users = create_unix_users(ssh_session_as_root, "manage-unix", 2)
    logger.info("Users created " + str(len(users)))
    proxy_user = users[0]
    accountuser = users[1]
    new_system_id, add_system_success = ResourceManager.add_system(
        core_session, hostname, conf["ipaddress"], "Unix", "Ssh", "Unix system")
    assert add_system_success, "Add System Failed"
    logger.info(f"Added system Id {new_system_id}")
    systems_list.append(new_system_id)
    # Update system with proxy user
    update_sys_success, update_sys_result = ResourceManager.update_system(core_session, new_system_id, hostname,
                                                                          conf["ipaddress"], 'Unix',
                                                                          proxyuser=proxy_user['Name'],
                                                                          proxyuserpassword=proxy_user['Password'],
                                                                          proxyuserismanaged=True)
    assert update_sys_success, f'Fail to update the system:API response result: {update_sys_result}'
    logger.info(f"Successfully update the system:{update_sys_result}")

    admin_account_id, add_account_success = ResourceManager.add_account(
        core_session, accountuser['Name'], accountuser['Password'], new_system_id)
    assert add_account_success, "Failed to create Account user: root"
    logger.info(f"Added root Account.  Id {admin_account_id}")
    accounts_list.append(admin_account_id)

    # Get computer details for update
    result = RedrockController.get_system(core_session, new_system_id)
    system = result[0]["Row"]
    is_managed = system['ProxyUserIsManaged']
    assert is_managed, f"Added account is not managed account"