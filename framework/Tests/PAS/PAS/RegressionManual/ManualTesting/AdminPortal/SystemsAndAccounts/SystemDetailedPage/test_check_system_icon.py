from Shared.UI.Centrify.SubSelectors.grids import GridRowByGuid
from Shared.UI.Centrify.SubSelectors.modals import Modal
from Shared.UI.Centrify.SubSelectors.navigation import ActiveMainContentArea
from Shared.UI.Centrify.selectors import UnixIconAlert
import logging
import pytest

logger = logging.getLogger("test")


@pytest.mark.ui
@pytest.mark.pasapi_ui
@pytest.mark.bhavna
@pytest.mark.pas
def test_check_system_icon(setup_pas_system_for_unix, core_admin_ui):
    """
    Test Case ID: C2091
    Test Case Description: Check system icon on system Settings page
    :param setup_pas_system_for_unix: Creates Unix System and Account
    :param core_admin_ui: Authenticates Centrify UI session
    """
    system_id, account_id, sys_info = setup_pas_system_for_unix
    system_name = sys_info[0]
    account_name = sys_info[4]
    ui = core_admin_ui
    ui.navigate('Resources', 'Systems')
    ui.search(system_name)
    ui.switch_context(ActiveMainContentArea())
    ui.click_row(GridRowByGuid(system_id))
    ui.right_click_action(GridRowByGuid(account_id), 'Checkout')
    ui.switch_context(Modal(text=account_name))
    ui.button('Show Password')
    assert ui.check_exists(UnixIconAlert()) is False, 'Alert Icon ! is present'
    logger.info("System icon shows correctly without alert icon i.e. '!'.")
    ui.close_modal('Close')
    assert ui.check_exists(UnixIconAlert()) is False, 'Alert Icon ! is present'
    logger.info("System icon shows correctly without alert icon i.e. '!' after closing the modal.")
