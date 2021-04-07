import logging
import pytest
from Shared.UI.Centrify.SubSelectors.navigation import ActiveMainContentArea

logger = logging.getLogger("test")


@pytest.mark.ui
@pytest.mark.pas_failed
def test_migrate_password_with_invalid_email(core_admin_ui):
    """
    Test Case ID: C2196
    Test Case Description: Migrate Password with invalid email address
    :param core_admin_ui: Authenticates Centrify UI session
    """
    ui = core_admin_ui
    ui.navigate('Settings', 'Resources', 'General', 'Password Storage', check_rendered_tab=False)
    ui.switch_context(ActiveMainContentArea())
    ui.launch_modal('Migrate Passwords')
    invalid_text = 'aa'
    ui.input('emailAddresses', invalid_text)
    tooltip = ui.check_tooltip_error('This field should be an e-mail address in the format '
                                     '"user@example.com"')
    assert tooltip, 'Failed to find the tool tip error message'
    logger.info('Tooltip present after entering invalid input in migrated password.')
    assert ui.button_exists('Yes', disable=True), "'Yes' button is enabled even after entering invalid email address"
    logger.info("'Yes' button is disabled after entering invalid email address")
