import pytest
import logging
from Shared.UI.Centrify.SubSelectors.grids import GridRowByGuid
from Shared.UI.Centrify.selectors import Div
from Utils.guid import guid

logger = logging.getLogger("test")


@pytest.mark.api_ui
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi_ui
def test_update_system_settings(core_session, pas_windows_setup, core_admin_ui):
    """
    TC:C2166 Update system Settings.
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
    ui.tab('Settings')

    # Updating the system with new system name and validating that "Accounts" page shows normally.
    new_system_name = f'test_system{guid()}'
    ui.input('Name', new_system_name)
    ui.save()
    ui.tab('Policy')
    ui.tab('Accounts')
    ui.expect(Div('Accounts'), 'Expect to find the title "Accounts" in the Account Page but could not.')
    logger.info('Successfully find the title "Accounts" in the Account Page.')
    assert ui.button_exists("Add", time_to_wait=3), "Add button is not Enabled."
    logger.info('Successfully find "Add button" is enabled and visible.')
    ui.expect(GridRowByGuid(account_id), f"Expect to find account {sys_info[4]} in the Accounts page but "
                                         f"could not.")
    logger.info(f'Successfully find account {sys_info[4]} in the Accounts page.')
