import pytest
import logging

from Shared.UI.Centrify.SubSelectors.forms import CheckedCheckbox, Checkbox
from Shared.UI.Centrify.SubSelectors.grids import GridRowByGuid

logger = logging.getLogger('test')


@pytest.mark.api_ui
@pytest.mark.pas
@pytest.mark.pasui
@pytest.mark.bhavna
def test_check_use_proxy_account_option(setup_pas_system_for_unix, core_admin_ui, pas_config):
    """
        Test case: C2185 Check Use proxy account option
        :param core_admin_ui: Authenticated Centrify Session.
        :param setup_pas_system_for_unix: Add Unix System and Account associated with it
        :param  pas_config: Config file to get data from the yaml.
        """
    created_system_id, created_account_id, sys_info = setup_pas_system_for_unix
    logger.info(f"System added successfully : {created_system_id}")
    ui = core_admin_ui
    ui.navigate('Resources', 'Systems')
    ui.search(sys_info[0])
    ui.click_row(GridRowByGuid(created_system_id))
    ui.tab('Settings')
    ui.check('undefined')
    ui.input("ProxyUser", "test_proxy_user")
    ui.input("ProxyUserPassword", "pass_proxy_1234")
    ui.save()
    ui.tab('Accounts')
    ui.launch_modal('Add', modal_title='Add Account')
    ui.expect(Checkbox("UseWheel"), "Use proxy account option is not shown in add account wizard")
    logger.info(f"Use proxy account option check box exist.")
    ui.expect(CheckedCheckbox("UseWheel"), f'Use proxy account option is not checked on add account wizard')
    logger.info(f"Use proxy account option check box is checked on add account wizard ")
