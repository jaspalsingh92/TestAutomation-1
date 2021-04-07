import pytest
import logging

from Shared.API.redrock import RedrockController
from Shared.UI.Centrify.SubSelectors.forms import ComboboxWithNameStartsWith
from Shared.UI.Centrify.SubSelectors.grids import EmptyGrid, GridCell
from Shared.UI.Centrify.SubSelectors.modals import ErrorModal, Modal
from Shared.UI.Centrify.selectors import Div, LoadingMask
from Utils.guid import guid

logger = logging.getLogger("test")


@pytest.mark.pas
@pytest.mark.pasui
@pytest.mark.bhavna
def test_check_ui_system_login_dialog(core_session, core_admin_ui, pas_setup):
    """
    TC : C2072 Check UI on system login dialog
    param:core_admin_ui: Returns browser Session
    param: core_session: Returns Api session.
    param: pas_setup: Return fixture
    """
    # Launch UI.
    ui = core_admin_ui
    created_system_id, created_account_id, system_details = pas_setup
    system_name = system_details[0]
    ui.navigate('Resources', 'Systems')
    ui.search(system_name)
    ui.right_click_action(GridCell(system_name), 'Select/Request Account')
    ui.expect_disappear(LoadingMask(), 'Expected to find account but it did not', 30)
    ui.switch_context(Modal(system_name + ' Login'))
    logger.info("Successfully show loading before all account display")


@pytest.mark.api_ui
@pytest.mark.pas
@pytest.mark.pasui
@pytest.mark.bhavna
def test_search_specify_string_in_search_field(core_admin_ui):
    """
    TC : C2073 Search specify string( &  # ) in search field
    param:core_admin_ui: Returns browser Session
    """

    # Launch UI.
    ui = core_admin_ui
    ui.navigate('Resources', 'Systems')
    ui.search("&#")
    ui.switch_context(ErrorModal())
    error_text = "A potentially dangerous string is included in the request body."
    ui.check_exists(Div(error_text), f"Expected to find {error_text} message but it did not. ")
    logger.info(f"Successfully shows the error text {error_text}.")
    ui.close_modal('Close')
    ui.navigate('Resources', 'Domains')
    ui.search("&#")
    assert ui.check_exists(ErrorModal()) is False, f"Error modal appears"
    logger.info("No error text shown on Domain search field")


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.bhavna
def test_search_system_not_by_name(core_session, pas_setup):
    """
    TC : C2074 Search system not by name
    param:core_admin_ui: Returns browser Session
    param:pas_setup: created a system
    """
    # Created a system along with one account
    created_system_id, created_account_id, sys_info = pas_setup

    # Search valid system name in 'DNS Name/IP Address'
    result = RedrockController.search_server_by_filter(core_session, sys_info[0])
    assert [] == result, f'able to fetch the system: {result}'
    logger.info(" There is no system on the search list")
    # Search invalid system IP in 'DNS Name/IP Address'
    server_fdqn = f"{guid()}%"
    result = RedrockController.search_server_by_filter(core_session, server_fdqn)
    assert [] == result, f'able to fetch the system: {result}'
    logger.info(" There is no system on the search list")
