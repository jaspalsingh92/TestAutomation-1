import pytest
from Shared.API.infrastructure import ResourceManager
import logging

logger = logging.getLogger("test")


@pytest.mark.bhavna
@pytest.mark.pasapi
@pytest.mark.pas_broken
def test_add_managed_account_without_password_when_policy_is_not_enabled(core_session, ad_session,
                                                                         domain_config_data,
                                                                         set_domain_administrative_account,
                                                                         cleanup_accounts):
    """
    TC ID: C1332
    Add a managed account without password when automatic maintenance policy is not enabled
    :param core_session: Centrify authentication session
    :param set_domain_administrative_account: Fixture to set administrative account
    """
    session, api_user = ad_session
    account_list = cleanup_accounts[0]
    directory_service_Name, directory_service_Admin_ID, directory_service_ID = set_domain_administrative_account

    account_id, success_status = ResourceManager.add_account(core_session, api_user.user_input.name, password='',
                                                             ismanaged=True, domainid=directory_service_ID)
    assert success_status is False, f'failed to add account{account_id}'
    account_list.append(account_id)
    logger.info(f'Cannot add managed account or update account from un managed to managed without '
                f'password as automatic account maintenance is not enabled:{account_id}')
