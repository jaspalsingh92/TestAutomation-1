import pytest
import logging
from Shared.UI.Centrify.SubSelectors.grids import GridRowByGuid
from Shared.UI.Centrify.SubSelectors.modals import ConfirmModal
from Shared.UI.Centrify.selectors import Span
from Utils.guid import guid

logger = logging.getLogger("test")


@pytest.mark.api_ui
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi_ui
def test_cancel_to_add_manage_proxy_account(core_session, pas_windows_setup, core_admin_ui):
    """
    TC:C2169 Cancel to add a managed proxy account.
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
    ui.check('undefined')
    proxy_user = f'test_proxy{guid()}'
    proxy_password = f'Pass@{guid()}'
    ui.input('ProxyUser', proxy_user)
    ui.input('ProxyUserPassword', proxy_password)
    ui.check('ProxyUserIsManaged')
    ui.button('Save')
    ui.expect(ConfirmModal(), 'Expect a error modal but could not found it.')
    logger.info('Successfully found error modal after save.')
    ui.expect(Span('x'), 'Expect to found the "x"  on error modal but could not found it.').try_click()
    logger.info('Successfully Cancel to add a managed proxy account.')
