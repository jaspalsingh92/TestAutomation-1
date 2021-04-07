import pytest
import logging

from Shared.API.infrastructure import ResourceManager

logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_check_result_after_removing_related_permission(core_session, get_admin_user_function, pas_setup):
    """
    :param core_session: Authenticated Centrify session.
    :param get_admin_user_function: core_session, Authenticated Centrify Session.
    :param pas_setup: Returning a fixture.

    Steps for this scenario using API:
            1) Create a normal cloud user by using get_admin_user_function fixture
            2) Assign grant permission to the normal cloud user under system
            3) Assign grant and edit permission to the normal cloud user under system account
            4) Remove grant permission of the account under system by calling assign_system_permissions API
            5) Remove grant permission of the system by calling assign_system_permissions API

    """
    # Creating a normal user
    limited_sesh, limited_user = get_admin_user_function
    created_system_id, created_account_id, sys_info = pas_setup

    result, success = ResourceManager.assign_system_permissions(core_session, "Grant",
                                                                limited_user.get_login_name(),
                                                                limited_user.get_id(),
                                                                pvid=created_system_id)
    assert success, f"Failed to assign the system permission:{success}"
    logger.info(f"Successfully set the Grant permission for the system:{result}")

    # Assign grant and edit permission to the normal cloud user under system account
    result, success = ResourceManager.assign_account_permissions(core_session, "Owner,Manage",
                                                                 limited_user.get_login_name(),
                                                                 limited_user.get_id(),
                                                                 pvid=created_account_id)
    assert success, f"Failed to set the system account permission:{success}"
    logger.info(f"Successfully set the system account permission:{result}")

    # Remove grant permission of the account
    result, success = ResourceManager.assign_account_permissions(limited_sesh, "Manage",
                                                                 limited_user.get_login_name(),
                                                                 limited_user.get_id(),
                                                                 pvid=created_account_id)
    assert success, f"Failed to set the account permission: {result}"
    logger.info(f"Successfully remove the  grant member aacont Permission: {success}")

    # Remove grant permission of the system
    result, success = ResourceManager.assign_system_permissions(limited_sesh, "View",
                                                                limited_user.get_login_name(),
                                                                limited_user.get_id(),
                                                                pvid=created_system_id)
    assert success, f"Failed to remove the Grant member permission of the system: {result}"
    logger.info(f"Successfully remove the grant member Permission: {success}")
