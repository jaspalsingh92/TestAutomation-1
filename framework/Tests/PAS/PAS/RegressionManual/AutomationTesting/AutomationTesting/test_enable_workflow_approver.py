import pytest
import logging
from Shared.UI.Centrify.SubSelectors.grids import GridRowByGuid
from Shared.UI.Centrify.SubSelectors.modals import WarningModal, Modal
from Shared.UI.Centrify.SubSelectors.navigation import RenderedTab, ActiveMainContentArea, TreeFolder
from Shared.UI.Centrify.selectors import Div

logger = logging.getLogger("test")


@pytest.mark.ui
@pytest.mark.pas
@pytest.mark.workflow
def test_enable_workflow_without_approve(core_session, pas_windows_setup, core_admin_ui):
    """
    TC:C2192 Enable workflow without approver.
    :param core_session: Returns a API session.
    :param pas_windows_setup: Returns a fixture.
    :param core_admin_ui: Return a browser session.

    """
    # Creating a system and account.
    system_id, account_id, sys_info, connector_id, user_password = pas_windows_setup()

    # Launch UI.
    ui = core_admin_ui
    ui.navigate('Resources', 'Systems')
    ui.search(sys_info[0])
    ui.click_row(GridRowByGuid(system_id))
    ui.click_row(GridRowByGuid(account_id))
    ui.tab('Workflow')
    ui.select_option('WorkflowEnabled', 'Yes')
    ui.switch_context(ActiveMainContentArea())
    ui.expect(TreeFolder('Permissions'), 'Expect to permission tab but failed to find it.').try_click(Modal())
    ui.switch_context(WarningModal())
    warning_message = "Please correct the errors before leaving the page."
    ui.check_exists(Div(warning_message))
    logger.info('Successfully found warning modal when try to navigate to another page.')
    ui.close_modal('Close')
    ui.switch_context(RenderedTab('Workflow'))
    ui.button('Save')
    ui.switch_context(WarningModal())
    save_warning_message = "Please correct the errors in your form before submitting."
    ui.check_exists(Div(save_warning_message))
    logger.info('Successfully found warning modal containing "Please correct the errors in your form before '
                'submitting".')
