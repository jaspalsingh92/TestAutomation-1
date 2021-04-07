import pytest

from Shared.API.infrastructure import ResourceManager
import logging

logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.bhavna
@pytest.mark.pasapi
@pytest.mark.pas
def test_add_permission_for_account(core_session, pas_setup):
    """
    TCID: C2204  Add permission for account
    :param core_session: To create the session
    :param pas_setup: Add system and its account
    """
    system_id, account_id, sys_info = pas_setup
    user_detail = core_session.__dict__
    rights = "View"
    user_name = user_detail['auth_details']['User']
    principalid = user_detail['auth_details']['UserId']
    result_permission, success_permission = ResourceManager.assign_account_permissions(
                                            core_session, rights, user_name, principalid, pvid=account_id)
    assert success_permission, f'Failed to add the user permission:{result_permission}'
    logger.info(f'Add user permission successfully:{result_permission}')
