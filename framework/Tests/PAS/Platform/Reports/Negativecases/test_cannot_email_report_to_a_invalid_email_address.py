import pytest

from Shared.UI.Centrify.SubSelectors.modals import Modal, WarningModal
from Shared.UI.Centrify.selectors import Anchor
import logging

logger = logging.getLogger("test")


@pytest.mark.ui
@pytest.mark.bhavna
@pytest.mark.pas_failed
def test_cannot_export_report_with_invalid_name(core_session, create_report, core_admin_ui):
    """
    TCID: C6367 Cannot email report to a invalid email address
    :param core_session: Centrify Session
    :param create_report: To create the report
    :param core_admin_ui: To open the browser
    """
    my_report = create_report(core_session, "Select Name From Server")
    report_name = my_report['Name']

    ui = core_admin_ui
    ui.navigate("Reports")
    ui.check_row(report_name)
    ui.action("Email Report")

    modal = "Email Report"
    ui.switch_context(Modal(modal))
    ui.input("emailTo", "<123#")
    ui.expect(Anchor(button_text="OK"), "Button is not present").try_click()
    ui.expect(WarningModal(), "Failed to get any warning message (Modal)")
    logger.info(f'Email is Invalid')
