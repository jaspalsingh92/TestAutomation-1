import pytest
import logging
from Shared.UI.Centrify.selectors import Anchor, PageWithTitle, Label, Header

logger = logging.getLogger('test')


@pytest.mark.pas
@pytest.mark.ui
@pytest.mark.bhavna
def test_check_help_page_correctly(core_admin_ui):
    """ test case: C1664
        :param core_session: Centrify session
        :param core_admin_ui: Creates random user and login in browser.
    """
    ui = core_admin_ui
    ui.navigate("Settings", "Resources", "Password Profiles")

    # Clicking the 'Learn More' link in the Password profiles page.
    ui.expect(Anchor(button_text="Learn more"), "expecting a like named 'Learn more'", time_to_wait=20).try_click()
    logger.info("Clicked the Learn More link in the password profiles page")
    ui.switch_to_newest_tab()
    ui.expect(PageWithTitle("Configuring password profiles"), "Page with title 'Configuring password profiles'")
    logger.info("Verifying the page title appeared")
    ui.switch_to_main_window()

    # Clicking the 'Learn More' link in the Security Settings page.
    ui.navigate("Settings", "Resources", "Security", "Security Settings")
    ui.expect(Anchor(button_text="Learn more"), "expecting a link named 'Learn more'", time_to_wait=20).try_click(
        Label("SSH Gateway Banner"))
    logger.info("Clicked the Learn More link in the Security Settings page")
    ui.switch_to_newest_tab()
    ui.expect(PageWithTitle("Setting global security options"), "Page with title 'Setting global security options'")
    logger.info("Verifying the page title appeared")

    # Checking the password profile help page.
    ui.expect(Anchor(href="Password-profiles.htm"), "Expecting password profile page", time_to_wait=20).try_click(
        Header("Setting global security options"))
    logger.info("Clicking the password profile help page")
    ui.switch_to_newest_tab()
    ui.expect(PageWithTitle("Password profiles"), "Page with title 'Password profiles'")
    logger.info("Verifying the page title appeared")
