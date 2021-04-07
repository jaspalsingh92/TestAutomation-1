import pytest
import logging
from Shared.UI.Centrify.SubSelectors.forms import FieldLabel
from Shared.UI.Centrify.SubSelectors.grids import GridRowCheckboxByGuid
from Shared.UI.Centrify.SubSelectors.modals import Modal
from Shared.UI.Centrify.SubSelectors.navigation import PageTitle
from Shared.UI.Centrify.selectors import Div
from Utils.guid import guid

logger = logging.getLogger("test")


@pytest.mark.ui
@pytest.mark.pas
@pytest.mark.bhavna
def test_system_action_button(pas_windows_setup, core_admin_ui):
    """
    TC:C2161 Check system's Actions button.
    :param core_admin_ui: Return a browser session.
    :param pas_windows_setup: Returns a fixture.
    :param core_session: Returns a API session.
    """

    # Creating a system and account.
    system_id, account_id, sys_info, connector_id, user_password = pas_windows_setup()

    # UI Launch.
    ui = core_admin_ui
    ui.navigate('Resources', 'Systems')
    ui.search(sys_info[0])
    ui.check_row_by_guid(system_id)
    ui.expect(GridRowCheckboxByGuid(system_id, checked=True),
              f'Expect to find system is checked but could not.')
    logger.info(f'System checkbox {sys_info[0]} is checked.')
    assert ui.button_exists("Actions"), "Action' is enabled and visible."
    logger.info(f"'Action' button is enabled on UI.")

    # Switching to other page and returning back to system page.
    ui.navigate('Resources', 'Accounts')
    ui.switch_context(PageTitle('Accounts'))
    ui.navigate('Resources', 'Systems')
    ui.expect(GridRowCheckboxByGuid(system_id, checked=False),
              f'Expect to find system is unchecked but could not.')
    logger.info(f'System checkbox {sys_info[0]} is unchecked ')
    assert ui.check_exists(Div('Actions')) is False, 'Actions is enabled and visible.'
    logger.info('Actions is disabled on UI.')


@pytest.mark.ui
@pytest.mark.bhavna
@pytest.mark.pas_skip("CC-77322")
def test_reselect_system_type_while_add_sys(core_admin_ui):
    """
    TC:C2163 Reselect system type while add system.
    :param core_admin_ui: Return a browser session.
    """

    # Launch UI.
    ui = core_admin_ui
    ui.navigate('Resources', 'Systems')
    ui.launch_modal('Add System')
    system_name = f'test_system{guid()}'
    ui.input('Name', system_name)
    ui.select_option('SystemProfileId', 'Check Point Gaia')
    fqdn = f'fqdn{guid()}'
    ui.input('FQDN', fqdn)
    ui.step('Next >')
    ui.step('Next >')

    # Validating the UI.
    ui.expect(Modal('Add System'), f'Expect to find modal title"Add System" but could not')
    logger.info(f'Successfully find modal title"Add System" on UI.')
    ui.expect(FieldLabel('Add expert mode account for this system'),
              f'Expect to find "Use a proxy account to manage this system." but could not')
    logger.info(f'Successfully find  find "Use a proxy account to manage this system." on UI.')
    assert ui.button_exists("Next >"), "Next button is not Enabled"
    logger.info('Successfully find "Next button" is enabled and visible')
    assert ui.button_exists("< Back"), "Back button is not Enabled"
    logger.info('Successfully find "Back button" is enabled and visible')
    ui.step('< Back')
    ui.step('< Back')

    # Changing the Computer Class to Unix.
    ui.select_option('SystemProfileId', 'Unix')
    ui.step('Next >')
    ui.step('Next >')

    # Validating the UI.
    assert ui.button_exists("Finish"), "finish button is not Enabled"
    logger.info('Successfully find "finish button" is enabled and visible')
    assert ui.button_exists("< Back"), "Back button is not Enabled"
    logger.info('Successfully find "back button" is enabled and visible')
    ui.expect(Modal('Add System'), f'Expect to find modal title"Add System" but could not')
    logger.info(f'Successfully find modal title"Add System" on UI.')
    ui.expect(FieldLabel('Verify System Settings'), f'Expect to find "Verify System Settings." but could not')
    logger.info(f'Successfully find  "Verify System Settings". on UI.')
