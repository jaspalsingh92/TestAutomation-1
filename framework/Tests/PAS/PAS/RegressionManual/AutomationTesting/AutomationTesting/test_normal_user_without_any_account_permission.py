import pytest
import logging
from Shared.UI.Centrify.SubSelectors.grids import GridRowByGuid

logger = logging.getLogger("test")


@pytest.mark.ui
@pytest.mark.bhavna
@pytest.mark.pasui
@pytest.mark.pas
def test_update_account_permission_without_any_account_permission(pas_setup, users_and_roles):
    """
    TCID: C2201  Normal user without any account's permission
    :param pas_setup:
    :param users_and_roles: To login with Previous Admin service power user
    """
    system_id, account_id, sys_info = pas_setup
    ui = users_and_roles.get_ui_as_user("Privileged Access Service Power User")

    # To navigate accounts page and click on added system
    ui.navigate("Resources", "Accounts")
    system_name = sys_info[0]
    ui.search(system_name)
    ui.click_row(GridRowByGuid(account_id))
    ui.check_actions(['Add To Set', 'Verify Credential'])
    logger.info(f"Update Password is not in the Account's action list")
