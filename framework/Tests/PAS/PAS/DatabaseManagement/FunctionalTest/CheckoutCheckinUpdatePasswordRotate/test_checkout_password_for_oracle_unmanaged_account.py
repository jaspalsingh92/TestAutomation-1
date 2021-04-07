import pytest
import logging
from Shared.API.infrastructure import ResourceManager
from Shared.API.redrock import RedrockController

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_checkout_password_for_oracle_unmanaged_account(core_session, add_database_with_account):
    """
    Test case: C1102
    :param core_session: Authenticated centrify session
    """
    db_name, db_id, db_account_id, db_data, database_cleaner_list, sql_account_cleaner_list = \
        add_database_with_account(db_class='oracle', add_account=True)

    result, status = ResourceManager.check_out_password(core_session, lifetime=15, accountid=db_account_id)
    assert status, f'failed to checkout account {db_data["db_account"]} password.'
    assert result['Password'] == db_data['password'], "Checked out password dose'nt match the actual password"
    logger.info(f'{db_data["db_account"]} password check out successfully.')

    acc_activity = RedrockController.get_account_activity(core_session, db_account_id)
    assert f'{core_session.auth_details["User"]} checked out database account "{db_data["db_account"]}" password for ' \
           f'database "{db_name}"' in \
           acc_activity[0]['Detail'], f"no activity of checkout found for account {db_data['db_account']}"
    logger.info(f"There is a checkout record for the account {db_data['db_account']} in activity")
