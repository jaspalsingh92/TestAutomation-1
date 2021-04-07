import pytest
import logging
from Shared.API.infrastructure import ResourceManager


logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.bhavna
def test_add_unmanaged_account_for_database(core_session, add_database_with_account, cleanup_accounts):
    """
    Test case: C1092 - Add an un manage account for Database
    :param core_session: Centrify authenticated session
    :param add_database_with_account: fixture to create database in portal with account if required
    :param core_admin_ui: Centrify authenticated ui session
    """
    accounts_list = cleanup_accounts[0]
    db_name, db_id, db_account_id, db_data, database_cleaner_list, account_cleaner_list = \
        add_database_with_account(db_class='oracle', add_account=True)

    sql_db_name, sql_db_id, sql_db_account_id, sql_db_data, sql_database_cleaner_list, sql_account_cleaner_list = \
        add_database_with_account(db_class='sql', add_account=True)

    db_account1, db_account2 = 'TEST_ACCOUNT1', 'test_account1'

    # Creates a account on an existing database. (Connector required)
    database_account_id, database_account_success = ResourceManager.add_account(
        core_session,
        user=db_account1,
        password='TESTtest1234',
        ismanaged=False,
        databaseid=db_id)
    assert database_account_success, f"Adding database account failed with API response Result:" \
                                     f"{database_account_id}"
    logger.info(f"Managed database account added successfully with API response result : {database_account_id}")
    accounts_list.append(database_account_id)

    # try to add Duplicate account
    database_account_id, database_account_success = ResourceManager.add_account(
        core_session,
        user=db_account2,
        password='TESTtest1234',
        ismanaged=False,
        databaseid=db_id)
    assert database_account_success is False, f"Adding database account with API response Result:" \
                                              f"{database_account_id}"
    logger.info(f"Managed database account not added successfully with API response result : {database_account_id}")

    # Creates a account on an existing database. (Connector required)
    database_account_id, database_account_success = ResourceManager.add_account(
        core_session,
        user=db_account1,
        password='TESTtest1234',
        ismanaged=False,
        databaseid=sql_db_id)
    assert database_account_success, f"Adding database account failed with API response Result:" \
                                     f"{database_account_id}"
    logger.info(f"Managed database account added successfully with API response result : {database_account_id}")
    accounts_list.append(database_account_id)

    # try to add Duplicate account
    database_account_id, database_account_success = ResourceManager.add_account(
        core_session,
        user=db_account2,
        password='TESTtest1234',
        ismanaged=False,
        databaseid=sql_db_id)
    assert database_account_success is False, f"Adding database account with API response Result:" \
                                              f"{database_account_id}"
    logger.info(f"database account not added with API response result : {database_account_id}")
