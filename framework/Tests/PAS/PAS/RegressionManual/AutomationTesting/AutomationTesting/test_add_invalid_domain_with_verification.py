import pytest
import logging
from Shared.UI.Centrify.SubSelectors.modals import WaitModal
from Shared.UI.Centrify.selectors import Div
from Utils.guid import guid

logger = logging.getLogger("test")


@pytest.mark.ui
@pytest.mark.pas
@pytest.mark.bhavna
def test_add_invalid_domain_with_verification(core_admin_ui):
    """
    TC:C2202 Add invalid domain with verification.
    :param core_admin_ui: Return a browser session.
    """
    # UI Launch.
    ui = core_admin_ui
    ui.navigate("Resources", "Domains", check_rendered_tab=False)
    ui.launch_modal("Add Domain", "Domain Settings")
    domain_name = f'{"R1C1"}{guid()}'
    ui.input('Name', domain_name)
    ui.button('Add', WaitModal())
    ui.switch_context(WaitModal())
    warning_pop_message = 'Verification failed. The domain could not be reached.'
    ui.expect(Div(warning_pop_message), f'Warning modal did not contain correct text')
    logger.info("Warning modal did contain correct text")
