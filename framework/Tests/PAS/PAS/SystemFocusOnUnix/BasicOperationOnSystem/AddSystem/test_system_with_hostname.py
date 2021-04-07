import pytest
import logging
from Shared.API.infrastructure import ResourceManager
from Shared.API.redrock import RedrockController

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi
def test_add_system_with_hostname_without_account(core_session, add_single_system):
    """
    Test case : C279338
    :param core_session: Centrify session manager
    :param add_single_system: add system and provide it's ID and system basic information
    :return:
    """
    system_id, system_info = add_single_system
    system_rows = RedrockController.get_computer_with_ID(core_session, system_id)
    assert system_rows['Name'] == system_info[0], f"failed to find system {system_info[0]} in portal, returned row is {system_rows} "
    logger.info(f"system found {system_rows}")
