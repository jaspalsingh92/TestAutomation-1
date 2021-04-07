import pytest
import logging
from Shared.API.infrastructure import ResourceManager

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi
@pytest.mark.smoke
def test_add_unmanaged_account(core_session, pas_setup):
    """
    Test case: C279346

    :param core_session: Centrify session
    :param pas_setup: add system with account and yeild system ID, account ID, and system information
    """
    system_id, account_id, system_info = pas_setup

    # Fetching account information to validate desired account is unmanaged
    result, status = ResourceManager.get_account_information(core_session, account_id)
    assert status, f"failed to retrieve account information, returned result is {result}"

    is_managed = result['VaultAccount']['Row']['IsManaged']
    assert is_managed is False, "Added account is not unmanaged account"
