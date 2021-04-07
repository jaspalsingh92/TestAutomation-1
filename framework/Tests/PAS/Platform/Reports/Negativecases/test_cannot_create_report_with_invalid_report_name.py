import pytest

from Shared.UI.Centrify.SubSelectors.modals import ConfirmModal, WarningModal
from Shared.UI.Centrify.selectors import HeaderNameInput, Anchor
import logging

logger = logging.getLogger("test")

lock_tenant = True


@pytest.mark.ui
@pytest.mark.bhavna
@pytest.mark.pas_failed
def test_cannot_create_report_with_invalid_name(core_admin_ui):
    """
    TCID: C6363 Cannot create report with invalid report name
    :param core_admin_ui: To open the browser
    """
    core_admin_ui.navigate("Reports")
    core_admin_ui.launch_add("New Report", HeaderNameInput())
    core_admin_ui.launch_modal("Edit Script", modal_selector=ConfirmModal())
    core_admin_ui._waitUntilSettled()
    core_admin_ui.close_modal('Yes')

    report_name = "<>"
    core_admin_ui.input("header-edit-input", report_name)
    core_admin_ui.write_to_codemirror("Select Server.Name From Server")
    core_admin_ui.expect(Anchor(button_text="Save"), "Failed to find the save button").try_click()
    core_admin_ui.expect(WarningModal(), f'Report got saved')
    logger.info(f'Invalid file name')
    core_admin_ui.switch_context(WarningModal())
    core_admin_ui.button("Close")
    core_admin_ui.remove_context()

    report_name = " "
    core_admin_ui.input("header-edit-input", report_name)
    core_admin_ui.expect(Anchor(button_text="Save"), "Failed to find the save button").try_click()
    core_admin_ui.expect(WarningModal(), f'Report got saved')
    logger.info(f'Invalid file name')
    core_admin_ui.switch_context(WarningModal())
    core_admin_ui.button("Close")
    core_admin_ui.remove_context()

    report_name = "  name"
    core_admin_ui.input("header-edit-input", report_name)
    core_admin_ui.expect(Anchor(button_text="Save"), "Failed to find the save button").try_click()
    core_admin_ui.expect(WarningModal(), f'Report got saved')
    logger.info(f'Invalid file name')
    core_admin_ui.switch_context(WarningModal())
    core_admin_ui.button("Close")
    core_admin_ui.remove_context()
