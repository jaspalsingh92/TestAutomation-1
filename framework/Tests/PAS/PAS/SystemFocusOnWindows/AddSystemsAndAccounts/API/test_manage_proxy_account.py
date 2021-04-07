import logging
import pytest
from Shared.API.infrastructure import ResourceManager
from Shared.API.redrock import RedrockController

logger = logging.getLogger("test")

pytestmark = [pytest.mark.api, pytest.mark.pas, pytest.mark.bhavna]


@pytest.mark.pas_failed
def test_add_managed_proxy_account(core_session, pas_windows_setup):
    """
    :param core_session: Authenticated Centrify Session.
    :param pas_windows_setup: Fixture for adding a system and an account associated with it.
    TC: C2537 - Add system with managed account and Proxy account with WinRM https settings
     trying to Add system with managed account and Proxy account with WinRM https settings
            Steps:
                Pre: Create system with 1 manage and proxy account
                1. Try to fetch the management mode in setting page
                    -Assert Failure
                2. Try to check out password from account
                    -Assert Failure
    """
    system_id, account_id, sys_info, connector_id, user_password = pas_windows_setup(True, True)
    logger.info(f"System: {sys_info[0]} successfully added with UUID: {system_id} and account: {sys_info[4]} "
                f"with UUID: {account_id} associated with it.")
    managementmode = RedrockController.get_computer_with_ID(core_session, system_id)
    assert managementmode['ManagementMode'] == "WinRMOverHttps", \
        f"management mode is failed because of system doesnt have proxy account. API response result: {managementmode}"
    logger.info(f"Fetch management mode successfully: {managementmode['ManagementMode']}")
    password_checkout_result, password_checkout_success = ResourceManager.check_out_password(core_session, 1,
                                                                                             accountid=account_id)
    assert password_checkout_result['Password'] is not user_password, \
        f"password checkout Failed. API response result: {password_checkout_result}"
    logger.info(f"password successfully checkout Account password: {password_checkout_result['COID']}")


def test_add_windows_activity(core_session, add_single_system):
    """
    :param core_session: Authenticated Centrify Session.
    TC: C2532 - Add Windows system without account
    """
    user_name = core_session.get_user().get_login_name()

    added_system_id, sys_info = add_single_system
    logger.info(f"System {sys_info[0]}, with fqdn {sys_info[1]} created successfully with Uuid {added_system_id}")

    result, success = ResourceManager.get_system_health(core_session, added_system_id)
    assert success and result == 'OK', 'failed to test connection with system'
    result, success = ResourceManager.get_system_health(core_session, added_system_id)
    assert result != 'Unreachable', f"system {added_system_id} is unreachable, API response result : {result}"
    logger.info(f"System health check was successful and API response result is: {result}")

    system_activity = ResourceManager.get_system_activity(core_session, added_system_id)
    assert f"{user_name} added system" in system_activity[0]['Detail'], f"no system activity found, API response " \
                                                                        f"result {system_activity}"
    logger.info(f"System Activity successfully retrieved: {system_activity[0]['Detail']}")


def test_add_un_manage_account_activity(core_session, pas_setup):
    """
     :param core_session: Authenticated Centrify Session.
    :param pas_setup: Fixture for adding a system and an account associated with it.
    TC: C2534 - Add Windows system with un managed account
    trying to validate the add un manage Account Activity log's
                Steps:
                1. Try to add a system with un managed account
                    -Assert Failure
                2. Try to check in the activity of system
                    -Assert Failure
    """
    user_name = core_session.get_user().get_login_name()
    sys_id, acc_id, sys_info = pas_setup
    logger.info(f"System: {sys_info[0]} successfully added with UUID: {sys_id} and account: {sys_info[4]} "
                f"with UUID: {acc_id} associated with it.")
    checkflag = True
    counter = 0
    row = None
    while checkflag is True:
        if counter != 5:
            row = ResourceManager.get_system_activity(core_session, sys_id)
            if row is not None:
                break
        checkflag = False
        counter += 1
    reports = []
    for system_activity in row:
        if system_activity['Detail'].__contains__("added local"):
            reports.append(system_activity["Detail"])
    created_date_json = str(row[0]['When'])
    ResourceManager.get_date(created_date_json)
    assert f'{user_name} added local account "{sys_info[4]}" for "{sys_info[0]}"({sys_info[1]}) ' \
        f'with credential type Password ' in reports[0], "Account Not Added"
    logger.info(f"account activity list:{row}")


def test_add_system_invalid_proxy_account_activity(core_session, pas_setup):
    """
     :param core_session: Authenticated Centrify Session.
    :param pas_setup: Fixture for adding a system and an account associated with it.
    TC: C1822 - Add Windows resource after clearing valid managed account and invalid proxy account
    trying to validate the invalid proxy account activity log's
                Steps:
                1. Try to add a system with managed account
                    -Assert Failure
                2. Try to check manage account updated to un manage account
                    -Assert Failure
    """
    user_name = core_session.get_user().get_login_name()
    sys_id, acc_id, sys_info = pas_setup
    logger.info(f"System: {sys_info[0]} successfully added with UUID: {sys_id} and account: {sys_info[4]} "
                f"with UUID: {acc_id} associated with it.")
    row = None
    counter = 0
    while counter <= 10:
        row = ResourceManager.get_system_activity(core_session, sys_id)
        if row is not None:
            break
        counter += 1
    reports = []
    for system_activity in row:
        if system_activity['Detail'].__contains__("added local"):
            reports.append(system_activity["Detail"])
    # ResourceManager.get_date(created_date_json)
    assert f'{user_name} added local account "{sys_info[4]}" for "{sys_info[0]}"({sys_info[1]}) ' \
           f'with credential type Password ' in reports[0], "Account Not Added"
    logger.info(f"account activity list:{row}")


def test_add_account_activity(core_session, pas_setup):
    """
    :param core_session: Authenticated Centrify Session.
    :param pas_setup: Fixture for adding a system and an account associated with it.
    TC: C2533-Add managed account to existing system
    trying to validate the added Account Activity log's
            Steps:
                1. Try to add a system along with an account
                    -Assert Failure
                2. Try to check in the activity of system
                    -Assert Failure

    """
    user_name = core_session.get_user().get_login_name()
    sys_id, acc_id, sys_info = pas_setup
    logger.info(f"System: {sys_info[0]} successfully added with UUID: {sys_id} and account: {sys_info[4]} "
                f"with UUID: {acc_id} associated with it.")
    checkflag = True
    counter = 0
    row = None
    while checkflag is True:
        if counter != 5:
            row = ResourceManager.get_system_activity(core_session, sys_id)
            if row is not None:
                break
        checkflag = False
        counter += 1
    reports = []
    for system_activity in row:
        if system_activity['Detail'].__contains__("added local"):
            reports.append(system_activity["Detail"])
    created_date_json = str(row[0]['When'])
    ResourceManager.get_date(created_date_json)
    assert f'{user_name} added local account "{sys_info[4]}" for "{sys_info[0]}"({sys_info[1]}) ' \
           f'with credential type Password ' in reports[0], "Account Not Added"
    logger.info(f"account activity list:{row}")


def test_add_manage_proxy_account(core_session, pas_setup):
    """
    :param core_session: Authenticated Centrify Session.
    :param pas_setup: Fixture for adding a system and an account associated with it.
    TC: C2535 - Add Windows system with managed account and proxy account
    trying to validate the added managed proxy Account Activity log's
            Steps:
                1. Try to add a system along with manage proxy account
                    -Assert Failure
                2. Try to check in the activity of system
                    -Assert Failure
    """
    user_name = core_session.get_user().get_login_name()
    sys_id, acc_id, sys_info = pas_setup
    logger.info(f"System: {sys_info[0]} successfully added with UUID: {sys_id} and account: {sys_info[4]} "
                f"with UUID: {acc_id} associated with it.")
    checkflag = True
    counter = 0
    row = None
    while checkflag is True:
        if counter != 5:
            row = ResourceManager.get_system_activity(core_session, sys_id)
            if row is not None:
                break
        checkflag = False
        counter += 1
    reports = []
    for system_activity in row:
        if system_activity['Detail'].__contains__("added local"):
            reports.append(system_activity["Detail"])
    created_date_json = str(row[0]['When'])
    ResourceManager.get_date(created_date_json)
    assert f'{user_name} added local account "{sys_info[4]}" for "{sys_info[0]}"({sys_info[1]}) ' \
           f'with credential type Password ' in reports[0], "Account Not Added"
    logger.info(f"account activity list:{row}")


def test_add_un_manage_account_with_dns_name(core_session, add_single_system):
    """
    :param core_session: Authenticated Centrify Session.
    TC: C1819 - Add a windows system with un managed account which hostname as DNS Name
    trying to validating the added un manged account with dns name System Activity log
            Steps:
                1. Try to add a system with dns name
                    -Assert Failure
                2. Try to check in the activity of system
                    -Assert Failure
    """
    user_name = core_session.get_user().get_login_name()
    added_system_id, sys_info = add_single_system
    logger.info(
        f"System {sys_info[0]}, with fqdn {sys_info[1]} created successfully with Uuid {added_system_id}")
    row = ResourceManager.get_system_activity(core_session, added_system_id)
    assert f'{user_name} added system "{sys_info[0]}"({sys_info[1]})' in row[0]['Detail'], "No system activity data"
    logger.info(f"account activity list:{row}")


def test_add_account_join_domain(core_session, pas_setup):
    """
     :param core_session: Authenticated Centrify Session.
    :param pas_setup: Fixture for adding a system and an account associated with it.
    TC: C2538 - Add a managed account for a Windows System which have joined domain
    trying to validate the added Account Activity log's
                Steps:
                1. Try to add a system with managed account
                    -Assert Failure
                2. Try to check in the activity of system
                    -Assert Failure
    """
    user_name = core_session.get_user().get_login_name()
    sys_id, acc_id, sys_info = pas_setup
    logger.info(f"System: {sys_info[0]} successfully added with UUID: {sys_id} and account: {sys_info[4]} "
                f"with UUID: {acc_id} associated with it.")
    checkflag = True
    counter = 0
    row = None
    while checkflag is True:
        if counter != 5:
            row = ResourceManager.get_system_activity(core_session, sys_id)
            if row is not None:
                break
        checkflag = False
        counter += 1
    reports = []
    for system_activity in row:
        if system_activity['Detail'].__contains__("added local"):
            reports.append(system_activity["Detail"])
    created_date_json = str(row[0]['When'])
    ResourceManager.get_date(created_date_json)
    assert f'{user_name} added local account "{sys_info[4]}" for "{sys_info[0]}"({sys_info[1]}) ' \
           f'with credential type Password ' in reports[0], "Account Not Added"
    logger.info(f"account activity list:{row}")


def test_manage_to_un_managed(core_session, pas_setup):
    """
     :param core_session: Authenticated Centrify Session.
    :param pas_setup: Fixture for adding a system and an account associated with it.
    TC: C2545 Change managed account to un managed account
    trying to Validate account activity log's
                Steps:
                1. Try to add a system with managed account
                    -Assert Failure
                2. Try to check manage account updated to un manage account
                    -Assert Failure
    """
    user_name = core_session.get_user().get_login_name()
    sys_id, acc_id, sys_info = pas_setup
    logger.info(f"System: {sys_info[0]} successfully added with UUID: {sys_id} and account: {sys_info[4]} "
                f"with UUID: {acc_id} associated with it.")
    success, response = ResourceManager.update_account(core_session, acc_id, sys_info[4], host=sys_id,
                                                       ismanaged=False)
    assert success, f'Updating account failed. API response: {response}'
    logger.info(f'account updated successfully: {response}')
    checkflag = True
    counter = 0
    row = None
    while checkflag is True:
        if counter != 5:
            row = ResourceManager.get_system_activity(core_session, sys_id)
            if row is not None:
                break
        checkflag = False
        counter += 1
    reports = []
    for system_activity in row:
        if system_activity['Detail'].__contains__("updated local"):
            reports.append(system_activity["Detail"])
    created_date_json = str(row[0]['When'])
    ResourceManager.get_date(created_date_json)
    assert f'{user_name} updated local account "{sys_info[4]}" for "{sys_info[0]}"({sys_info[1]}) ' \
           f'with credential type Password ' in reports[0], "Account Not Added"
    logger.info(f"account activity list:{row}")
