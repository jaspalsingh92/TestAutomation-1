import pytest
import logging
from Shared.API.infrastructure import ResourceManager
from Shared.UI.Centrify.selectors import GridCell


logger = logging.getLogger('test')


@pytest.mark.api_ui
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi_ui
def test_check_my_password_checkout_field_after_checkout_account(core_session, pas_setup, core_admin_ui):
    """
    Test case: C14837
    :param core_session: Centrify session
    :param pas_setup: fixture to create system with account
    :param core_admin_ui: UI session
    """
    system_id, account_id, system_info = pas_setup

    result, status = ResourceManager.check_out_password(core_session, 1, account_id, 'test checkout account')
    assert status, f'failed to checkout password for account {system_info[4]}, returned result is: {result}'

    ui = core_admin_ui
    ui.navigate(('Workspace', 'My Password Checkouts'))
    ui.expect(GridCell(f'{system_info[4]} ({system_info[0]})'), f'expected to find checkout details for account '
                                                                f'{system_info[4]} but did not')
