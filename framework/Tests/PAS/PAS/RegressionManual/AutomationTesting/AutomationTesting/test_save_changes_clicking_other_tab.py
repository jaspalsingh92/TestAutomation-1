import pytest
import logging
from Shared.API.redrock import RedrockController
from Shared.UI.Centrify.SubSelectors.grids import GridRowByGuid
from Utils.guid import guid

logger = logging.getLogger("test")


@pytest.mark.api_ui
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi_ui
def test_save_changes_clicking_other_tab(core_session, setup_pas_system_for_unix, core_admin_ui):
    """
    TC:C2186 Save the changes after clicking other tabs.
    :param core_ui: Return a browser session.
    :param core_session: Return API session.
    :param: pas_setup: Returning a fixture.
    """
    # Adding a system with account.
    created_system_id, created_account_id, sys_info = setup_pas_system_for_unix
    system_name = sys_info[0]

    # Launch UI.
    ui = core_admin_ui
    ui.navigate('Resources', 'Systems')
    ui.search(system_name)
    ui.click_row(GridRowByGuid(created_system_id))
    ui.tab('Settings')
    modified_system_name = f'UnixServer{guid()}'
    ui.input('Name', modified_system_name)
    ui.save()
    # Validating that system name is modified.
    system_rows = RedrockController.get_computer_with_ID(core_session, created_system_id)
    assert system_rows['Name'] == modified_system_name, f'Failed to modify system name:{system_rows}'
    logger.info('Successfully modified system name.')
