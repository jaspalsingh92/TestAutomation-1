import pytest
from Shared.UI.Centrify.SubSelectors.forms import InvalidInputAlert
from Shared.UI.Centrify.SubSelectors.modals import Modal, WarningModal
from Shared.UI.Centrify.selectors import Anchor
import logging

logger = logging.getLogger("test")


@pytest.mark.ui
@pytest.mark.bhavna
@pytest.mark.pas_failed
def test_cannot_copy_report_to_invalid_report_name(core_session, create_report,
                                                   core_admin_ui,
                                                   cleanup_reports):
    """
    TCID C6365: Cannot copy report to a invalid report name
    :param core_session: Centrify Authentication Session
    :param create_report: Fixture to create the report
    :param core_admin_ui: To Open the browser
    :param cleanup_reports: Fixture to clean the reports
    """
    # As per the test case: Need 2 reports
    my_report = []
    for i in range(2):
        my_report.append(create_report(core_session,
                                       "Select Name From Server"))
    report_1 = my_report[0]['Name']
    report_2 = my_report[1]['Name']
    logger.info(f'Successfully created reports are:{my_report}')

    ui = core_admin_ui
    ui.navigate("Reports")
    ui.check_row(report_1)
    ui.check_row(report_2)
    ui.check_actions(['Delete'])
    logger.info("No copy action in list (cannot copy two reports one time)")
    ui.navigate("Reports")
    ui.check_row(report_1)
    ui.action("Copy")
    modal = "Copy : Copy"+' '+report_1
    move_modal = Modal(modal)
    ui.switch_context(move_modal)
    ui.input("file-name", "<>")
    ui.expect(Anchor(button_text="Save File"),
              "Failed to find the Save File button").try_click()
    alert_text = "The report name can " \
                 "include alpha numeric and special characters "
    ui.expect(InvalidInputAlert(alert_text),
              "Did not display warning icon").mouse_hover()
    ui.expect(WarningModal(), f'Did not populate the warning modal')
    logger.info("Display warning icon")
    for i in range(len(my_report)):
        cleanup_reports.append(my_report[i]['Path'])
