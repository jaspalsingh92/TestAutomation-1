import pytest
from Shared.UI.Centrify.SubSelectors.modals import Modal
from Shared.UI.Centrify.SubSelectors.navigation import TreeFolder
from Shared.UI.Centrify.selectors import Div, DisabledButton, Button, LoadingMask
from Shared.reports import Reports
import logging

logger = logging.getLogger("test")


@pytest.mark.ui
@pytest.mark.bhavna
@pytest.mark.pas_failed
def test_cannot_edit_reports_permissions_under_my_reports(core_session, create_report,
                                                          core_admin_ui, cleanup_reports):
    """
    TCID: C6337 Cannot edit report's permissions under My reports
    :param core_session: Centrify Authentication session
    :param create_report: To create a report
    :param core_admin_ui: To open the browser
    :param cleanup_reports: To clean the shared report
    """
    my_report = create_report(core_session, "Select Name From Server")
    report_name = my_report['Name']
    logger.info(f'Successfully created reports:{my_report}')

    ui = core_admin_ui
    ui.navigate("Reports")
    ui.check_actions(["Copy", "Move", "Delete",
                      "Modify", "Export Report", "Email Report"], report_name)
    ui.navigate("Reports")
    ui.action("Modify", report_name)
    ui.tab("Permissions")
    expected_msg = "The current report must be moved out of the home " \
                   "directory before permissions can be set for other users and roles."
    ui.expect(Div(expected_msg), f'Failed to get the expected message:{expected_msg}')
    logger.info(f'Expectation message is:{expected_msg}')
    ui.expect(DisabledButton("Add"), f'Add button is enable and can edit the permission')
    ui.navigate("Reports")
    ui.action("Copy", report_name)
    copy_modal = f'Copy : Copy {report_name}'
    ui.switch_context(Modal(copy_modal))
    ui.expect(Button("Save File"), f"Expected to see a Save File button but could not")

    # Down method is used select the Shared Reports folder
    ui.down()
    ui.close_modal("Save File")
    ui.navigate("Reports")
    ui.expect_disappear(LoadingMask(), f'Report page did not load properly')
    ui.expect(TreeFolder("Shared Reports"), f'Expected to see the Shared Reports but could not')
    shared_reports_button = ui._searchAndExpect(TreeFolder("Shared Reports"),
                                                f'Expected find shared Folder but could not')
    shared_reports_button.try_click()
    logger.info(f'Successfully copy report to shared reports folder "Copy {report_name}"')
    ui.action("Modify", "Copy " + report_name)
    ui.tab("Permissions")
    ui.expect(Button("Add"), f'Add button is disable, Report permissions can not be edited under "Shared Reports" folder')
    reports = Reports(core_session, f"Copy {report_name}.report")
    found_report = reports.get_report_by_name(core_session, f"Copy {report_name}.report", dir="/Reports/")
    cleanup_reports.append(found_report['Path'])
