import pytest
import logging
from Shared.util import Util
from Shared.API.redrock import RedrockController
from Shared.API.infrastructure import ResourceManager

logger = logging.getLogger('test')


@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi
def test_add_root_using_managed_password(core_session, unix_machine_environment_config, ssh_session_as_root,
                                         create_unix_users,
                                         cleanup_resources_with_admin, cleanup_accounts):
    """
    Test case C283102: Add system with root using managed proxy account
    :param core_session: Authorised centrify session.
    :param ssh_session_as_root: session to create a user_account in unix
    :param cleanup_accounts: cleanup  all accounts
    :param cleanup_resources_with_admin: to delete the all the systems from portal
    :param unix_machine_environment_config: to get the unix system details
    :param create_unix_users: add system with account and yield system ID, account ID, and system information
    """

    # Getting yaml data.
    systems_list = cleanup_resources_with_admin
    accounts_list = cleanup_accounts[0]
    conf = unix_machine_environment_config
    hostname = conf['host'] + "_" + Util.random_string(5)

    # add users on target system.
    users = create_unix_users(ssh_session_as_root, "manage-unix", 1)
    logger.info("Users created " + str(len(users)))
    proxy_user = users[0]

    # Adding system with managed proxy.
    new_system_id, add_system_success = ResourceManager.add_system(core_session, hostname,
                                                                   conf["ipaddress"],
                                                                   "Unix", "Ssh",
                                                                   "Unix system",
                                                                   proxyuserismanaged=True,
                                                                   proxyuser=proxy_user['Name'],
                                                                   proxyuserpassword=proxy_user['Password'])
    assert add_system_success, f"Failed to add system with managed proxy:API response result:{new_system_id}"
    logger.info(f"Successfully added with managed proxy: {new_system_id}")
    systems_list.append(new_system_id)

    # Adding local account to the system.
    admin_account_id, add_account_success = ResourceManager.add_account(
        core_session, 'root', conf['rootpassword'], new_system_id, ismanaged=False)
    assert add_account_success, f"Failed to add root user:API response result:{admin_account_id}"
    logger.info(f"Successfully added root account to the system: {admin_account_id}")
    accounts_list.append(admin_account_id)

    # checking added system in the system list.
    computer_lists = RedrockController.get_computers(core_session)
    for computer_detail in computer_lists:
        if computer_detail['ID'] == new_system_id:
            assert computer_detail['Name'] == hostname, f'Failed to found created system in the list:' \
                                                        f'API response result:{computer_lists}'
            logger.info(f"Successfully found created system in the list:{computer_lists}")
            break
