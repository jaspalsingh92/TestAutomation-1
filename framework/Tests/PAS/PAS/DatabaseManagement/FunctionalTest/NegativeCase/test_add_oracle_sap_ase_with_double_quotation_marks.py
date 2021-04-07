import pytest
import logging
from Shared.API.infrastructure import ResourceManager

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.bhavna
def test_add_oracle_sap_ase_account_with_double_quotation_mark(core_session, database_config,
                                                               add_database_with_account):
    """
    Test case: C1148
    :param core_session: Centrify authenticated session
    :param add_database_with_account: fixture to create database with account as optional
    :param core_admin_ui: Centrify authenticated ui session
    """

    # Create a oracle DB with account.
    db_name, db_id, db_account_id, db_data, database_cleaner_list, account_cleaner_list = \
        add_database_with_account(db_class='oracle', add_account=False)
    logger.info(f"Successfully created oracle Database: {db_name}")

    # Create a SAP DB with account.
    sap_db_name, sap_db_id, db_account_id, sap_db_data, database_cleaner_list, account_cleaner_list = \
        add_database_with_account(db_class='sapase', add_account=False)
    logger.info(f"Successfully created sap Database: {sap_db_name}")

    ora_account = f'"{db_data["db_account"]}"'
    sp_account = f'"{sap_db_data["db_account"]}"'

    # trying to add Oracle db account with using of double quote string
    db_account_id, status = ResourceManager.add_account(core_session, user=ora_account, password=db_data['password'],
                                                        ismanaged=db_data['is_managed'],
                                                        description=db_data['account_desc'], databaseid=db_id)
    assert status is False, f'able to add account in database {db_data["db_name"]}, returned status is {status} ' \
                            f'and id is: {db_account_id}'
    logger.info(f"Failed to add account in oracle Database: {db_name}")

    # trying to add sap db account with using of double quote string
    db_account_id, status = ResourceManager.add_account(core_session, user=sp_account, password=sap_db_data['password'],
                                                        ismanaged=sap_db_data['is_managed'],
                                                        description=sap_db_data['account_desc'], databaseid=sap_db_id)
    assert status is False, \
        f'failed to add account in database {sap_db_name}, ' \
        f'returned status is {status} and id is {sap_db_id}'
    logger.info(f"Failed to add account in sap Database: {sap_db_name}")
