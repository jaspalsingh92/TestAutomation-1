import pytest
import logging
from Shared.UI.Centrify.SubSelectors.grids import GridRow
from Shared.UI.Centrify.SubSelectors.modals import Modal
from Shared.UI.Centrify.selectors import Div
from Utils.guid import guid

logger = logging.getLogger("test")


@pytest.mark.api_ui
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi_ui
def test_cancel_update_password(core_session, pas_windows_setup, core_admin_ui):
    """
    TC:C2203 Cancel to update password
    :param core_admin_ui: Return a browser session.
    :param core_session: Return API session.
    :param:pas_windows_setup: Returning a fixture.
    """

    # Creating a system and account.
    system_id, account_id, sys_info, connector_id, user_password = pas_windows_setup()

    # UI Launch.
    ui = core_admin_ui
    ui.navigate('Resources', 'Accounts')
    ui.search(sys_info[0])
    ui.right_click_action(GridRow(sys_info[0]), "Update Password")
    ui.switch_context(Modal())
    update_password = f'{"test1@"}{guid()}'
    ui.input("Password", update_password)
    ui.button('Cancel')
    result = ui.check_exists(Div('An unknown error occurred'))
    assert result is False, f'Error message popups appears.'
    logger.info("Successfully cancel without pop error message")
