from Shared.API.infrastructure import ResourceManager
import logging
import pytest

logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.pasapi
@pytest.mark.bhavna
@pytest.mark.pas
def test_check_systems_checkouts(core_session, pas_setup):
    """
    Test Case ID: C2209
    Test Case Description: Check Top System Checkouts on Dashboards after checking out
    :param core_session: Authenticates API session
    :param pas_setup: Creates a windows system and account
    """

    system_id, account_id, sys_info = pas_setup
    system_name = sys_info[0]
    result, success = ResourceManager.check_out_password(core_session, lifetime=2, accountid=account_id)
    assert success, f'Failed to checkout password due to result: {result}'
    logger.info('Successfully checkout account')
    get_system_checkouts = ResourceManager.get_top_system_checkouts(core_session)
    list_to_store_checkout = []
    for name in get_system_checkouts:
        if name['Row']['Name'] == system_name:
            list_to_store_checkout.append(name['Row']['Name'])
    assert list_to_store_checkout, f'{system_name} is not present in Top Systems Checkouts'
    logger.info(f'{system_name} is present in Top system checkouts.')
