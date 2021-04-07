import pytest
from Shared.API.infrastructure import ResourceManager
import logging

logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.bhavna
@pytest.mark.pas_broken
def test_add_managed_account_without_password(core_session, domain_config_data,
                                              update_administrative_account_permission_to_pas_admin, cleanup_accounts):
    """
    TCID: C1328 Add a managed account without password when administrative account is not defined
    :param core_session: Centrify Authentication Session
    :param domain_config_data: To take data from config file
    :param update_administrative_account_permission_to_pas_admin: To create the session for Privileged Access Service Administrator
    """
    session, directory_service_Name, directory_service_Admin_ID, \
        directory_service_ID = update_administrative_account_permission_to_pas_admin
    result, success, response = ResourceManager.set_administrative_account(core_session, [directory_service_Name])
    account_list = cleanup_accounts[0]
    assert success, f'Failed to clear the administrative account:{result}'
    logger.info(f'Successfully clear the administrative account:{response}')
    conf = domain_config_data
    data = conf['pas_scenario1_new_accounts'][0]
    managed_account = data['Managed_account']
    account_id, success_status = ResourceManager.add_account(session,
                                                             managed_account,
                                                             password='',
                                                             ismanaged=True,
                                                             domainid=directory_service_ID)
    assert success_status is False, f"Successfully add the managed password {account_id}"
    account_list.append(account_id)
    logger.info(f'Cannot add managed account or update '
                f'account from unmanaged to managed without password '
                f'as administrative account is not defined:{account_id}')
