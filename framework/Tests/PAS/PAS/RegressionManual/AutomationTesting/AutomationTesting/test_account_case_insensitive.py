import pytest
import logging
from Shared.UI.Centrify.SubSelectors.grids import GridRowByGuid
from Shared.UI.Centrify.SubSelectors.modals import ErrorModal
from Shared.UI.Centrify.SubSelectors.navigation import RenderedTab
from Utils.guid import guid

logger = logging.getLogger("test")


@pytest.mark.api_ui
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi_ui
def test_account_case_insensitive(core_session, pas_windows_setup, core_admin_ui):
    """
    TC:C2191 Account should be case insensitive for Windows.
    :param core_session: Returns a API session.
    :param pas_windows_setup: Returns a fixture.
    :param core_admin_ui: Return a browser session.
    """
    # Adding a system with account.
    system_id, account_id, sys_info, connector_id, user_password = pas_windows_setup()

    # Launch UI.
    ui = core_admin_ui
    ui.navigate('Resources', 'Systems')
    ui.search(sys_info[0])
    ui.click_row(GridRowByGuid(system_id))
    ui.switch_context(RenderedTab("Accounts"))
    ui.launch_modal("Add", modal_title="Add Account")
    ui.input('User', sys_info[4].upper())
    password = f'Password@123{guid()}'
    ui.input('Password', password)
    ui.button("Add")
    assert ui.check_exists(ErrorModal()), 'Failed to found Error Modal'
    logger.info('Successfully Found Error Modal')
