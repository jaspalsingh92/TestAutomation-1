import pytest
import logging
from Shared.API.infrastructure import ResourceManager
from Shared.util import Util

logger = logging.getLogger('test')


@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi
def test_add_managed_account(core_session, unix_machine_environment_config, ssh_session_as_root, create_unix_users,
                             cleanup_resources_with_admin, cleanup_accounts):
    """
    Test case: C279345
    :param core_session: Centrify session
    :param ssh_session_as_root: session to create a user_account in unix
    :param cleanup_accounts: to delete all accounts
    :param cleanup_resources_with_admin: to delete the all the systems from portal
    :param unix_machine_environment_config: to get the unix system details
    :param create_unix_users: add system with account and yeild system ID, account ID, and system information
    """
    systems_list = cleanup_resources_with_admin
    accounts_list = cleanup_accounts[0]
    conf = unix_machine_environment_config
    hostname = conf['host'] + "_" + Util.random_string(5)
    # add users on target system
    users = create_unix_users(ssh_session_as_root, "manage-unix", 1)
    logger.info("Users created " + str(len(users)))
    accountuser = users[0]
    new_system_id, add_system_success = ResourceManager.add_system(
        core_session, hostname, conf["ipaddress"], "Unix", "Ssh", "Unix system")
    assert add_system_success, "Add System Failed"
    logger.info(f"Added system Id {new_system_id}")
    systems_list.append(new_system_id)

    admin_account_id, add_account_success = ResourceManager.add_account(
        core_session, accountuser['Name'], accountuser['Password'], new_system_id, ismanaged=True)
    assert add_account_success, "Failed to create Account user: root"
    logger.info(f"Added root Account.  Id {admin_account_id}")
    accounts_list.append(admin_account_id)

    # Fetching account information to validate desired account is managed or not
    result, status = ResourceManager.get_account_information(core_session, admin_account_id)
    assert status, f"failed to retrieve account information, returned result is {result}"

    is_managed = result['VaultAccount']['Row']['IsManaged']
    assert is_managed, "Added account is not managed account"
