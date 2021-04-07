import pytest
import logging
from Shared.API.infrastructure import ResourceManager

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi
def test_delete_system_without_account(core_session, add_single_system):
    """
        Test case: C279344
        :param core_session: CENTRIFY session
        :param pas_setup: fixture to add system and account
        :return:
        """
    system_id, sys_info = add_single_system
    result, status = ResourceManager.del_system(core_session, system_id)
    assert status, f"failed to delete system returned status {status} and result {result}"
