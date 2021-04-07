import pytest
import logging
from Shared.API.infrastructure import ResourceManager
from Shared.util import Util

pytestmark = [pytest.mark.pasapi, pytest.mark.bhavna]

logger = logging.getLogger('test')


@pytest.mark.pas
def test_add_managed_proxy_account_on_system_setting_page(core_session, unix_machine_environment_config,
                                                          ssh_session_as_root, create_unix_users,
                                                          cleanup_resources_with_admin):
    """
    :param core_session: Authenticated Centrify session.
    :param create_unix_users: add unix users
    Note: previously two test cases exist here
      1. add manage proxy account in unix system
      2. un manage proxy account in unix system now only one test cases doing two things.
    """
    systems_list = cleanup_resources_with_admin
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

    # Add manage proxy account
    result, success = ResourceManager.update_system(core_session, new_system_id, hostname, conf["ipaddress"],
                                                    "Unix", proxyuser=accountuser['Name'],
                                                    proxyuserpassword=accountuser['Password'],
                                                    proxyuserismanaged=True)

    assert success, f"Unable to add a managed proxy user for {hostname}. API response result: {result}"
    logger.info(f"Managed proxy account {accountuser['Name']} added to Unix system: {hostname}")

    # Changing managed proxy account to un managed
    unmanaged_result, unmanaged_success = ResourceManager.update_system(core_session, new_system_id, hostname,
                                                                        conf["ipaddress"],
                                                                        "Unix", proxyuser=accountuser['Name'],
                                                                        proxyuserpassword=accountuser['Password'],
                                                                        proxyuserismanaged=False)

    assert unmanaged_success, f"Unable to changed managed proxy user to un managed for Unix: {hostname}. API " \
                              f"response result: {result}"
    logger.info(f"Managed proxy account {accountuser['Name']} changed to 'Un managed' for {hostname}")
