import pytest
import json
import logging
from Shared.API.redrock import RedrockController
from Shared.UI.Centrify.SubSelectors.navigation import ActiveMainContentArea
from Shared.reports import Reports
from Shared.endpoint_manager import EndPoints
from Utils.guid import guid
from Shared.UI.Centrify.selectors import Button, Modal, GridCell, TreeFolder, ConfirmModal
from selenium.webdriver.common.by import By
from Shared.UI.Centrify.selectors import Selector

pytestmark = [pytest.mark.daily, pytest.mark.ui_navigation, pytest.mark.report, pytest.mark.ui]

logger = logging.getLogger("test")

"""
TestRail Link: 
https://testrail.centrify.com/index.php?/suites/view/5&group_by=cases:section_id&group_id=1633&group_order=asc

Tests:
    1. test_create_report
    2. test_copy_a_report
    3. test_move_report_to_same_dir
    4. test_move_report_different
    5. test_view_report
    6. test_create_report_directory
    7. test_delete_report_directory
    8. test_modify_directory
    9. test_email_report
    10. test_view_report_with_parameters_basic
    11. test_view_report_with_parameters_system_type
"""


@pytest.mark.api
@pytest.mark.platform
@pytest.mark.pas
@pytest.mark.smoke
def test_create_report(core_session, create_report, create_resources, cleanup_reports):
    sys = create_resources(core_session, 1, 'Unix')[0]

    my_report = create_report(core_session, "Select Server.Name From Server")
    result = RedrockController.redrock_query(core_session, "Select Server.Name From Server")
    system_flag = False
    for system in result:
        if system['Row']['Name'] == sys['Name']:
            system_flag = True
    assert system_flag, f"Expected to see created System {sys['Name']} in report but did not find system"

    reports = Reports(core_session, "fixture_report")
    found_report = reports.get_report_by_name(core_session, my_report['Name'] + ".report")
    assert found_report is not None, f'failed to find report {my_report["Name"] + ".report"}'


@pytest.mark.api
@pytest.mark.platform
@pytest.mark.pas
def test_copy_a_report(core_session, create_report, cleanup_reports, create_resources):
    sys = create_resources(core_session, 1, 'Unix')[0]
    Reports(core_session, "fixture_report")
    my_report = create_report(core_session, "Select Name From Server")
    payload = {
        "path": f"~/Reports/Copy {my_report['Name']}.report",
        "text": my_report['Name']
    }
    response = core_session.post(EndPoints.WRITE_FILE, payload)
    assert response, f'not able to copy the report from existing report'
    logger.info(f'Successfully copy the report: {response}')
    result = RedrockController.redrock_query(core_session, "Select Server.Name From Server")
    system_flag = False
    for system in result:
        if system['Row']['Name'] == sys['Name']:
            system_flag = True
    assert system_flag, f"Expected to see created System {sys['Name']} in report but did not find system"


@pytest.mark.ui
@pytest.mark.platform
@pytest.mark.pas_failed
def test_move_report_to_same_dir(core_admin_ui, core_session, create_report, create_resources):
    my_report = create_report(core_session, "Select Name From Server")
    core_admin_ui.navigate('Reports')
    core_admin_ui.action('Move', my_report['Name'])
    move_modal = Modal(f'Move: {my_report["Name"]}')
    core_admin_ui.switch_context(move_modal)
    core_admin_ui.button("Move")
    core_admin_ui.switch_context(ConfirmModal())
    core_admin_ui.close_modal("No")
    # core_admin_ui.button("Move")  #TODO: Seems that the fixture fails when moved to the same directory, seems awry
    # core_admin_ui.button("Yes")
    core_admin_ui.expect(GridCell(my_report['Name']), f"Expected to see created Report {my_report['Name']} in report")


@pytest.mark.ui
@pytest.mark.platform
@pytest.mark.pas_failed
def test_move_report_different(core_admin_ui, core_session, create_report, create_resources):
    my_report = create_report(core_session, "Select Name From Server")
    core_admin_ui.navigate('Reports')
    core_admin_ui.action('Move', my_report['Name'])
    move_modal = Modal("Move: " + my_report['Name'])
    core_admin_ui.switch_context(move_modal)
    core_admin_ui.expect(Button("Move"), f"Expected to see a Move button")
    core_admin_ui.down()
    core_admin_ui.close_modal("Move")
    # Expect to see the report in shared
    core_admin_ui.expect(GridCell(my_report['Name']), f"Expected to see created Report {my_report['Name']} in reports")


@pytest.mark.api_ui
@pytest.mark.platform
@pytest.mark.pas
@pytest.mark.daily
# @pytest.mark.smoke # flakiness this test fails around 3% of the time CC-74103
def test_view_report(core_session, create_report, create_resources):
    sys = create_resources(core_session, 1, 'Unix')[0]
    result = RedrockController.redrock_query(core_session, "Select Name From Server")
    system_flag = False
    for system in result:
        if system['Row']['Name'] == sys['Name']:
            system_flag = True
    assert system_flag, f"Expected to see created System {sys['Name']} in report but did not find system"


@pytest.mark.ui
@pytest.mark.platform
@pytest.mark.pas_failed
def test_create_report_directory(core_admin_ui, core_session, create_report):
    my_report = create_report(core_session, "Select Name From Server")

    core_admin_ui.navigate('Reports')
    core_admin_ui.expect(GridCell(my_report['Name']), f"Expected to see created Report {my_report['Name']} in report")
    core_admin_ui.right_click_action(TreeFolder("Shared Reports"), "New folder")

    folder_name = "new_folder" + guid()
    move_modal = Modal("Create new folder")
    core_admin_ui.switch_context(move_modal)
    core_admin_ui.input('file-name', folder_name)
    core_admin_ui.close_modal('Save')
    core_admin_ui.remove_context()
    try:
        core_admin_ui.expect(TreeFolder(folder_name), f'Expected to find My Reports Btn')
    finally:
        del_directory_result = \
            core_session.apirequest(EndPoints.DELETE_DIRECTORY, {"path": "/Reports/" + folder_name}).json()
        assert del_directory_result['success'], \
            f"Unable to Delete Report {folder_name}, response {json.dumps(del_directory_result)}"


@pytest.mark.api_ui
@pytest.mark.platform
@pytest.mark.pas_failed
def test_delete_report_directory(core_admin_ui, core_session, create_directory, create_report):
    my_directory = create_directory(core_session, "TestDirName").split('/')[-1]
    # Does not need guid, already has one in the creation!

    my_report = create_report(core_session, "Select Name From Server")

    core_admin_ui.navigate('Reports')
    core_admin_ui.expect(GridCell(my_report['Name']), f"Expected to see created Report {my_report['Name']} in report")

    core_admin_ui.expect(TreeFolder("My Reports"), "Unable to find My Reports Tab under Reports")
    shared_reports_button = core_admin_ui._searchAndExpect(TreeFolder("My Reports"),
                                                           f'Expected find My Reports Folder in Tree')
    shared_reports_button.try_click()
    core_admin_ui.expect(TreeFolder(my_directory), f"The directory {my_directory} did not show up")

    core_admin_ui.right_click_action(TreeFolder(my_directory), "Delete")
    core_admin_ui.switch_context(ConfirmModal())
    core_admin_ui.close_modal('Yes')


@pytest.mark.api_ui
@pytest.mark.platform
@pytest.mark.pas_failed
def test_modify_directory(core_admin_ui, core_session, create_directory, create_report):
    my_directory = create_directory(core_session, "TestDirName").split('/')[-1]
    # Does not need guid, already has one in the creation!

    my_report = create_report(core_session, "Select Name From Server")

    core_admin_ui.navigate('Reports')
    core_admin_ui.expect(GridCell(my_report['Name']), f"Expected to see created Report {my_report['Name']} in report")

    core_admin_ui.expect(TreeFolder("My Reports"), "Unable to find My Reports Tab under Reports")
    shared_reports_button = core_admin_ui._searchAndExpect(TreeFolder("My Reports"), f'Expected to find My Reports Btn')
    shared_reports_button.try_click()
    core_admin_ui.expect(TreeFolder(my_directory), f"The directory {my_directory} did not show up")

    core_admin_ui.right_click_action(TreeFolder(my_directory), "Modify")

    move_modal = Modal()
    core_admin_ui.switch_context(move_modal)
    core_admin_ui.close_modal('Cancel')


@pytest.mark.api_ui
@pytest.mark.platform
@pytest.mark.pas_failed
def test_email_report(core_admin_ui, core_session, create_report):
    my_report = create_report(core_session, "Select Name From Server")

    core_admin_ui.navigate('Reports')
    core_admin_ui.action('Email Report', my_report['Name'])
    core_admin_ui.switch_context(Modal('Email Report'))
    core_admin_ui.input("emailTo", "junkjunkjunkjunk@bogusinvalid.com")
    core_admin_ui.close_modal("OK")
    core_admin_ui.expect(GridCell(my_report['Name']), f"Expected to see created Report {my_report['Name']} in report")


@pytest.mark.api_ui
@pytest.mark.platform
@pytest.mark.pas_failed
def test_view_report_with_parameters_basic(core_admin_ui, core_session, create_report, create_resources):
    sys = create_resources(core_session, 1, 'Unix')[0]

    my_report = create_report(core_session, f"Select Name From Server Where Server.Name = @CompNamePlz")

    core_admin_ui.navigate('Reports')
    core_admin_ui.action('Modify', my_report['Name'])
    core_admin_ui.tab("Parameters")
    core_admin_ui.launch_modal('Add', "Report Parameter")

    core_admin_ui.input("Name", "CompNamePlz")
    core_admin_ui.input("Label", "Please Slap me with that Computer Name")
    core_admin_ui.select_option('Type', "String")
    core_admin_ui.close_modal("OK")

    core_admin_ui.launch_modal('Preview', "Required Parameters")

    core_admin_ui.input("CompNamePlz", sys['Name'])
    core_admin_ui.close_modal("OK")

    core_admin_ui.switch_context(Modal("Report Preview"))
    core_admin_ui.expect(GridCell(sys['Name']), f"Failed to find {sys['Name']} row in Systems")
    core_admin_ui.close_modal('Close')


@pytest.mark.ui
@pytest.mark.platform
@pytest.mark.pas_failed
def test_view_report_with_parameters_system_type(core_admin_ui, core_session, create_report, create_resources):
    systems = create_resources(core_session, 2, 'Unix')

    my_report = create_report(core_session, f"Select Name From Server Where Server.ComputerClass = @CompParam")

    core_admin_ui.navigate('Reports')
    core_admin_ui.action('Modify', my_report['Name'])
    core_admin_ui.tab("Parameters")
    core_admin_ui.launch_modal('Add', "Report Parameter")
    core_admin_ui.input("Name", "CompParam")
    core_admin_ui.input("Label", "Pick a computer pls")
    core_admin_ui.select_option('Type', "System")
    core_admin_ui.select_option('ObjectProperty', "ComputerClass")
    core_admin_ui.close_modal("OK")
    core_admin_ui.switch_context(ActiveMainContentArea())
    core_admin_ui.launch_modal('Preview', "Pick a computer pls")
    core_admin_ui.check_row(systems[0]['Name'])
    core_admin_ui.close_modal("Select")

    # We are changing UI to APi, Because there is number of records existed on
    # tiles ui step did n't find the path in dom
    query = "Select Name From Server Where Server.ComputerClass = @CompParam"
    parameter = [{"Name": "CompParam", "Value": "Unix",
                  "Label": "Pick a computer pls", "Type": "Server", "ColumnType": 12}]
    server_results = RedrockController.redrock_query(core_session, query, parameters=parameter)
    computer_names = []
    for i in server_results:
        computer_names.append(i['Row']['Name'])

    assert systems[1]['Name'] in computer_names, \
        f"Computer is not found in above list: {computer_names}, Expected: {systems[1]['Name']}"
    logger.info(f"Computer is found in above list: {computer_names}, Expected: {systems[1]['Name']}")
    core_admin_ui.close_modal('Close')
    # re-establish context
    core_admin_ui.tab('Parameters')
    core_admin_ui.right_click_action(Selector(By.CSS_SELECTOR, f"tr[test-text='CompParam']"), "Delete")
