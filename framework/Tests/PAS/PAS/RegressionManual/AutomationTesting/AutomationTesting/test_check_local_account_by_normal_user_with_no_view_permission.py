import pytest
import logging

from Shared.API.infrastructure import ResourceManager
from Shared.UI.Centrify.SubSelectors.grids import EmptyGrid

logger = logging.getLogger("test")


@pytest.mark.pas
@pytest.mark.ui
@pytest.mark.bhavna
def test_check_local_account_by_normal_user_with_no_view_permission(core_session, users_and_roles, pas_setup):
    """
    Test case ID: C2205  Check local account in User Portal using a normal user with Privilege Service User right
    :param users_and_roles: Returns Authenticated Centrify UI session  with limited rights.
    :param core_session: Authenticated Centrify Session.
    :param pas_setup: Returning a fixture.

    """
    created_system_id, created_account_id, sys_info = pas_setup

    # Getting the limited user session with limited rights " Privilege Service User right."
    ui = users_and_roles.get_ui_as_user("Privileged Access Service User")
    limited_user = ui.get_user()

    # Assigning permission to the system account
    account_set_result, account_set_success = ResourceManager.assign_account_permissions(core_session, "View,Login",
                                                                                         limited_user.get_login_name(),
                                                                                         limited_user.get_id(),
                                                                                         pvid=created_account_id)
    assert account_set_success, f"Failed to assign 'view' and 'login' permissions to user for system's account: {account_set_success}"
    logger.info(f"Successfully granted permission to the system account:{account_set_result}")

    # Assigning permission to the system
    system_set_success, system_set_result = ResourceManager.assign_system_permissions(core_session, "Edit",
                                                                                      limited_user.get_login_name(),
                                                                                      limited_user.get_id(),
                                                                                      pvid=created_system_id)
    assert system_set_result, f"Failed to assign permission to user for system: {system_set_success}"
    logger.info(f"Successfully set the permission to other system: {system_set_result}")

    # UI Launch.
    ui.navigate('Resources', 'Systems')
    empty_grid = ui.check_exists(EmptyGrid("No Systems listed "))
    assert empty_grid, f"System found in the list"
    ui.navigate('Resources', 'Accounts')
    empty_grid = ui.check_exists(EmptyGrid("No Accounts listed "))
    assert empty_grid, "Account found in the list"
