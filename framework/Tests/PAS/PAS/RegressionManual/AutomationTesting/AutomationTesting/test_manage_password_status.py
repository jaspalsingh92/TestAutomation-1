import pytest
import logging
from Utils.guid import guid
from Shared.UI.Centrify.selectors import InputDropdown

logger = logging.getLogger("test")


@pytest.mark.ui
@pytest.mark.pas
@pytest.mark.pasui
@pytest.mark.bhavna
def test_manage_password_status(core_admin_ui):
    """
    TC:C2182 Check "Manage this password" status.
    :param core_admin_ui: Return a browser session.
    """

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
    proxy_user = f"{'test_proxy_user'}{guid()}"
    proxy_password = f"{'pass@3qW'}{guid()}"
    ui.input("ProxyUser", proxy_user)
    ui.input("ProxyUserPassword", proxy_password)
    ui.check('ProxyUserIsManaged')
    is_managed_enabled = ui.check_exists(InputDropdown("ProxyUserIsManaged"))
    assert is_managed_enabled, "Managed password  is not Enabled"
    logger.info("Managed  password enabled successfully")
