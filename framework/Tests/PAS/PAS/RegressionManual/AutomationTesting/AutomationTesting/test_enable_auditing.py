import logging
import pytest
from Shared.UI.Centrify.selectors import Line

logger = logging.getLogger("test")


@pytest.mark.ui
@pytest.mark.pas_failed
def test_enable_auditing(core_admin_ui):
    """
    Test Case ID: C2195
    Test Case Description: Enable Auditing with installation name is less more sign? or &#
    :param core_admin_ui: Authenticates Centrify UI session
    """
    ui = core_admin_ui
    ui.navigate('Settings', 'Resources', 'Other', 'Auditing Service')
    ui.check('DaAuditEnabled')
    invalid_text = '&#'
    ui.input('DaAuditName', invalid_text)
    ui.save_warning()
    error_message = "Field cannot contain leading or trailing spaces, '&#' and input after '<' is not allowed"
    ui.expect(Line(error_message), expectation_message='Failed to find pop up warning icon with message for entering '
                                                       'invalid inputs.')
    logger.info('Tooltip present after entering invalid input in Installation text field')
