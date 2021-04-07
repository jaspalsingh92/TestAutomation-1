from Shared.UI.Centrify.SubSelectors.grids import GridRowByGuid
from Shared.UI.Centrify.selectors import Label
import logging
import pytest

logger = logging.getLogger("test")


@pytest.mark.ui
@pytest.mark.bhavna
@pytest.mark.pas
def test_check_dialog(core_admin_ui, add_single_system):
    """
    Test Case ID: C2220
    Test Case Description: Check the dialog for Select User, Group, Role panel
    :param core_admin_ui: Authenticates Centrify UI session
    :param add_single_system: Creates a single system
    """
    ui = core_admin_ui
    ui.navigate('Resources', 'Systems')
    added_system_id, sys_info = add_single_system
    system_name = sys_info[0]
    ui.search(system_name)
    ui.click_row(GridRowByGuid(added_system_id))
    ui.tab('Permissions')
    ui.launch_modal('Add', modal_title='Select User, Group, or Role')

    # Checking Computer is not present in the List
    assert ui.check_exists(Label('Computers')) is False, 'Computers is present in the list of dialog'
    logger.info('Computers is not present in the list of dialog')
