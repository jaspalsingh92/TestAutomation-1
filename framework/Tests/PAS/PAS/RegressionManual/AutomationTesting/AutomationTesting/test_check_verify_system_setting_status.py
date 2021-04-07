import pytest
import logging
from Shared.UI.Centrify.SubSelectors.forms import CheckedCheckbox
from Utils.guid import guid

logger = logging.getLogger("test")


@pytest.mark.ui
@pytest.mark.pas
@pytest.mark.pas_ui
@pytest.mark.bhavna
def test_check_verify_system_setting_status(core_admin_ui):
    """
    TC : C2164 Check Verify System Settings status
    param:core_admin_ui: Returns browser Session
    """

    # Launch UI.
    ui = core_admin_ui
    sys_name = "test_ui_sys_creation_name" + guid()
    sys_fqdn = "fqdn" + guid()
    user_name = "test_user_name" + guid()
    password = "test_pass" + guid()
    ui.navigate('Resources', 'Systems')
    ui.launch_modal('Add System')
    ui.input("Name", sys_name)
    ui.input("FQDN", sys_fqdn)
    ui.step('Next >')
    ui.input("User", user_name)
    ui.input("Password", password)
    ui.step('Next >')
    ui.check('SetupProxyAccount')
    ui.check('ProxyUserIsManaged')
    ui.uncheck('SetupProxyAccount')
    ui.step('Next >')
    assert ui.expect(CheckedCheckbox("verify_server_and_account"), f'Check box Element "verify_server_and_account" is disabled')
    logger.info("Successfully Verified, The system setting page is enabled.")
