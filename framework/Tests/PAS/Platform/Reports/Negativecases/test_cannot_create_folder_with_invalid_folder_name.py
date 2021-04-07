import pytest

from Shared.UI.Centrify.SubSelectors.forms import InvalidInputAlert
from Shared.UI.Centrify.SubSelectors.modals import Modal, WarningModal
from Shared.UI.Centrify.SubSelectors.navigation import TreeFolder
from Shared.UI.Centrify.selectors import Anchor, LoadingMask
import logging

logger = logging.getLogger("test")


@pytest.mark.ui
@pytest.mark.bhavna
@pytest.mark.pas_failed
def test_cannot_create_folder_with_invalid_name(core_admin_ui):
    """
    TCID: #C6364 Cannot create folder with invalid folder name
    :param core_admin_ui: To open the browser
    """
    ui = core_admin_ui
    ui.navigate("Reports")
    ui.expect_disappear(LoadingMask(), 'Reports page did not load properly')
    ui.expect(TreeFolder("My Reports"), "Unable to find My Reports Tab under Reports")
    ui.right_click_action(TreeFolder("My Reports"), "New folder")

    # 1st Case
    folder_name = "<new_folder>"
    ui.switch_context(Modal("Create new folder"))
    ui.input('file-name', folder_name)
    ui.expect(Anchor(button_text="Save"), "Folder Name is created").try_click()
    alert_text = "The report name can include alpha numeric and special characters "
    ui.expect(InvalidInputAlert(alert_text), "Invalid Input alert tooltip appears")
    logger.info(f'Invalid file name')

    # 2nd Case
    folder_name = ' '
    ui.input('file-name', folder_name)
    ui.expect(Anchor(button_text="Save"), "Failed to find the save button").try_click()
    ui.expect(WarningModal(), "Folder is created with space")
    logger.info(f'Invalid file name')
    ui.switch_context(WarningModal())
    ui.button("Close")
    ui.remove_context()

    # 3rd Case
    folder_name = "  name"
    ui.input('file-name', folder_name)
    ui.expect(Anchor(button_text="Save"), "Failed to find the save button").try_click()
    ui.expect(WarningModal(), "Folder is created space with name")
    logger.info(f'Invalid file name')
    ui.switch_context(WarningModal())
    ui.button("Close")
    ui.remove_context()
    ui.close_modal("Cancel")
