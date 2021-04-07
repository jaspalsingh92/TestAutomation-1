import pytest
import logging
from Shared.UI.Centrify.SubSelectors.grids import GridRowByGuid
from Shared.UI.Centrify.SubSelectors.modals import WarningModal
from Shared.UI.Centrify.SubSelectors.navigation import RenderedTab
from Shared.UI.Centrify.selectors import Div

logger = logging.getLogger("test")

lock_tenant = True

pytestmark = [pytest.mark.ui, pytest.mark.pas, pytest.mark.bhavna, pytest.mark.rdp]


@pytest.mark.pas_failed
def test_access_system_not_allow_from_public_network(core_session, pas_windows_setup, core_admin_ui,
                                                     update_tenant_remote):
    """
    C1573 : 20180720-02:31:59 system Level
    :param core_session: Authenticated Centrify Session
    :param pas_windows_setup: Added Windows system with Account associated to it.
    :param core_admin_ui: Authenticated Centrify Browser Session
    """
    system_id, account_id, sys_info, connector_id, user_password = pas_windows_setup()
    ui = core_admin_ui

    # Disable 'Allow access from a public network' policy on Global Security Setting page
    result, success = update_tenant_remote(core_session, False)
    assert success, f"Not able to disable 'Allow access from a public network' policy on Global Security Setting " \
                    f"page. API response result: {result}. "
    logger.info(f"'Allow access from a public network' policy disabled on Global Security Setting page")

    # Navigating Resources - System page
    ui.navigate("Resources", "Systems")
    ui.search(sys_info[0])
    ui.click_row(GridRowByGuid(system_id))
    ui.check_row_by_guid(account_id)
    ui.switch_context(RenderedTab("Accounts"))

    # Login to Account using RDP session
    ui.action('Login')
    ui.wait_for_tab_with_name(f"Login session {sys_info[0]}")
    expected_alert_message = "Remote access not allowed. Please enable the 'Allow access from a public network' " \
                             "policy if web login from a public network is required."
    core_admin_ui.switch_context(WarningModal())
    assert core_admin_ui.check_exists((Div(
        expected_alert_message))), f"pop up warning message for Remote access is not same as : {expected_alert_message}"
    logger.info(f"Correct pop up warning message displayed for Remote access.")
