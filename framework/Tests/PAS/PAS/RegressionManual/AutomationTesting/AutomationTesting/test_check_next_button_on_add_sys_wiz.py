import pytest
import logging
from Utils.guid import guid
from Shared.UI.Centrify.selectors import Anchor

logger = logging.getLogger("test")


@pytest.mark.ui
@pytest.mark.pas
@pytest.mark.pasui
@pytest.mark.bhavna
def test_check_next_button_on_add_system_wizard(core_admin_ui):
    """
    TC:C2181 Check Next button on Add system wizard.
    :param core_admin_ui: Return a browser session.
    """
    # UI Launch.
    ui = core_admin_ui
    ui.navigate('Resources', 'Systems')
    sys_name = "test_ui_sys_creation_name" + guid()
    sys_fqdn = "fqdn" + guid()
    ui.navigate('Resources', 'Systems')
    ui.launch_modal('Add System')
    ui.input("Name", sys_name)
    ui.input("FQDN", sys_fqdn)
    ui.step('Next >')
    ui.step('Next >')
    ui.check('SetupProxyAccount')
    proxy_user = "test_proxy_user" + guid()
    proxy_password = "pass_proxy_1234" + guid()
    ui.input("ProxyUser", proxy_user)
    ui.input("ProxyUserPassword", proxy_password)
    next_button_enabled = ui.check_exists(Anchor(button_text="Next >"))
    assert next_button_enabled, "Next button is not Enabled"
    logger.info("Next button enabled successfully")
