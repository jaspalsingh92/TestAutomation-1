import pytest
import logging
from Shared.API.infrastructure import ResourceManager
from Shared.API.redrock import RedrockController
from Shared.API.users import UserManager

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_add_oracle_db_with_unmanaged_account(core_session, add_database_with_account):
    """
    Test case: C286608
    :param core_session: Authenticated Centrify session
    :param add_database_with_account: fixture to create database with account
    """
    db_name, db_id, db_account_id, db_data, database_cleaner_list, account_cleaner_list = \
        add_database_with_account(db_class='oracle', add_account=True)

    result = UserManager.security_refresh_token(core_session)
    assert result['success'], 'failed to refresh Centrify session.'

    db_row = RedrockController.get_database(core_session, db_id=db_id)
    assert db_name == db_row['Name'], f'"{db_name}" not found in Centrify portal.'
    logger.info(f'Database {db_name} found in Centrify portal with details {db_row}')

    result, status = ResourceManager.check_account_health(core_session, db_account_id)
    assert status, f"failed to verify DB account {db_data['db_account']} health"
    logger.info(f"database account {db_data['db_account']} verified successfully")
