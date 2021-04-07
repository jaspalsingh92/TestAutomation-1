import pytest
from Shared.API.infrastructure import ResourceManager
from Utils.guid import guid
import logging

logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.bhavna
@pytest.mark.pas_broken
def test_update_unmanaged_account(core_session, set_domain_administrative_account, cleanup_accounts):
    """
        TC ID: C1333, Update an unmanaged account without password to managed when automatic maintenance policy is set as
        :param set_domain_administrative_account: To open a browser and login with the admin account
        :param core_session: To create a session
    """
    directory_service_Name, directory_service_Admin_ID, directory_service_ID = set_domain_administrative_account
    accounts_list = cleanup_accounts[0]
    unmanaged_account = f'user{guid()}'
    account_id, success_status = ResourceManager.add_account(core_session,
                                                             unmanaged_account,
                                                             password='',
                                                             domainid=directory_service_ID)
    assert success_status, f'failed to add account{account_id}'
    logger.info(f'Successfully add the account{account_id}')

    result, success = ResourceManager.update_account(core_session, account_id,
                                                     unmanaged_account, domainid=directory_service_ID,
                                                     ismanaged=True)
    assert success is False, f'Successfully update the account:{result}'
    logger.info(f'Cannot add managed account or update account from unmanaged to managed '
                f'without password as automatic account maintenance is not enabled:{result}')
    accounts_list.append(account_id)
