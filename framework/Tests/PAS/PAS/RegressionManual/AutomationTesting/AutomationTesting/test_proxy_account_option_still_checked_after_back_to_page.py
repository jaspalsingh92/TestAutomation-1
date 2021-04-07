import pytest
import logging

from Shared.UI.Centrify.SubSelectors.forms import CheckedCheckbox
from Utils.guid import guid

logger = logging.getLogger("test")


@pytest.mark.ui
@pytest.mark.pas
@pytest.mark.pasui
@pytest.mark.bhavna
def test_proxy_account_option_still_checked_after_back_to_page(core_ui):
    """
       TCID: C2162  Basic UI Test that runs through the creation of system
        Steps:
            1. Go to Systems Tab And Click Add System
            2. Fill in Add Sys Info Page 1 (Name, Descript, SysType, DNS/IP)
            3. Input Proxy Account
            4. Test Going Back and Forth
            5. Check Proxy account is still checked or not
            """
    ui = core_ui
    sys_name = "test_ui_sys_creation_name" + guid()
    sys_fqdn = "fqdn" + guid()

    ui.navigate('Resources', 'Systems')
    ui.launch_modal('Add System')

    ui.input("Name", sys_name)
    ui.input("FQDN", sys_fqdn)
    ui.step('Next >')

    # Skip Associated Account
    ui.step('Next >') 

    # Add system Third page (Proxy Account Information)
    ui.check('SetupProxyAccount')
    ui.input("ProxyUser", "test_proxy_user")
    ui.input("ProxyUserPassword", "pass_proxy_1234")
    ui.step('Next >')

    # Test Going back
    ui.step('< Back')
    ui._searchAndExpect(CheckedCheckbox("SetupProxyAccount"), f'The check box is not already checked')
    logger.info("Proxy account to manage this system is still checked after 'back' to the page")
