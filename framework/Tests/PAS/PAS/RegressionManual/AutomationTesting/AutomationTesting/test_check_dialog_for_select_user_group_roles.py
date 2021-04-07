import pytest
import logging
from Shared.UI.Centrify.SubSelectors.grids import GridRowByGuid
from Shared.UI.Centrify.SubSelectors.navigation import RenderedTab

logger = logging.getLogger("test")


@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.ui
def test_check_dialog_select_user_group_role(core_session, core_admin_ui, pas_windows_setup):
    """
       TC:C2220 Check the dialog for Select User, Group, Role panel.
       :param:core_session: Returns Authenticated Centrify session.
       :param:core_admin_ui:Returns browser session.
       :param pas_windows_setup: Return a fixture.
    """

    # Creating a system and account.
    system_id, account_id, sys_info, connector_id, user_password = pas_windows_setup()

    # UI Launch
    ui = core_admin_ui
    ui.navigate('Resources', 'Systems')
    ui.search(sys_info[0])
    ui.click_row(GridRowByGuid(system_id))
    ui.tab('Permissions')
    ui.switch_context(RenderedTab('Permissions'))
    ui.launch_modal('Add', modal_title='Select User, Group, or Role')
    logger.info('Successfully could not find "computer" in "Select User, Group, or Role" dialog list.')
