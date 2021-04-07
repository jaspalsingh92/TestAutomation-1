import pytest
import logging
from Shared.API.redrock import RedrockController
from Shared.UI.Centrify.SubSelectors.forms import TextField
from Shared.UI.Centrify.SubSelectors.grids import GridRowByGuid

logger = logging.getLogger('test')


@pytest.mark.api_ui
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi_ui
def test_system_default_management_port(core_session, network_device_setup, core_admin_ui):
    """
    TC: C2607 - System default management port
    :param core_session: Authenticated Centrify session.
    :param network_device_setup: Adds a network with account and returns UUID of both.
    :param core_admin_ui: Authenticated Centrify browser session.
    """

    system_id, account_id, device_data, system_list, account_list = network_device_setup('paloalto')
    system_info = RedrockController.get_computer_with_ID(core_session, system_id)
    ui = core_admin_ui
    ui.navigate('Resources', 'Systems')
    ui.search(system_info['Name'])
    ui.click_row(GridRowByGuid(system_id))
    ui.tab('Settings')
    ui.input("ManagementPort", "1")
    ui.save()
    ui.expect(TextField('ManagementPort'), "Unable to locate management port input").clear()
    ui.save()
    management_port = RedrockController.get_computer_with_ID(core_session, system_id)['ManagementPort']
    assert management_port is None, "Management port value isn't 443 i.e. default."
    logger.info(f'Management port value retrieved via API is {management_port} i.e. placeholder 443 in UI.')
