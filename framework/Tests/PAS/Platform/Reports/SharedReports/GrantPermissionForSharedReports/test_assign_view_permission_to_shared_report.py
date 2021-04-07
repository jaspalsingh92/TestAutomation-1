import pytest
from Shared.API.reports import ReportsManager
from Shared.API.users import UserManager
from Shared.UI.Centrify.SubSelectors.grids import GridCell
from Shared.UI.Centrify.SubSelectors.navigation import TreeFolder
from Shared.UI.Centrify.SubSelectors.state import RestCallComplete
from Shared.UI.Centrify.selectors import LoadingMask
import logging

logger = logging.getLogger("test")


@pytest.mark.ui
@pytest.mark.bhavna
@pytest.mark.pas_failed
def test_assign_view_permission_to_shared_report(core_session, create_report, users_and_roles):
    """
    TCID: C6351 Assign 'View' permission to shared report
    :param core_session: Centrify Authentication session
    :param create_report: To create the report
    :param users_and_roles: To open an UI and assign specific right to user
    """
    my_report = create_report(core_session, "Select Name From Server", dir="/Reports")
    report_name = my_report['Name']
    grant_str = "0000000000000000000000000000000000000000000000000000000010000100"
    ui = users_and_roles.get_ui_as_user("Application Management")
    user_details = ui.get_user()
    user_name = user_details.get_login_name()
    user_id = user_details.get_id()
    role = UserManager.get_user_role_rights(core_session, user_id)
    assign_result = ReportsManager.assign_directory_rights_to_role(core_session, "/Reports",
                                                                   [{"Role":
                                                                         role['Result']['Results'][0]['Entities'][0][
                                                                             'Key'],
                                                                     "Rights": ["Read"]},
                                                                    {"Role": "Everybody",
                                                                     "Rights": ["Read"]
                                                                     }])
    assert assign_result, f'Failed to give the read the permission to Shared Folder'
    result, success, message = ReportsManager.update_report_permission(core_session,
                                                                       user_name, user_id, grant_str, report_name, ['Read'])
    assert success, f'Failed to assign View permission to Application Management user:{message}'
    logger.info(f'Successfully assign the View permission to Application Management user:{result}')
    ui.navigate("Reports", check_rendered_tab=False)
    ui.expect_disappear(LoadingMask(), "Reports page did not loaded properly")
    ui.expect(RestCallComplete(), "Expected rest call to complete.")
    ui.expect(TreeFolder("Shared Reports"), "Failed to find shared Reports Tab under Reports", time_to_wait=60)
    shared_reports_button = ui._searchAndExpect(TreeFolder("Shared Reports"),
                                                f'Expected find Shared Reports Folder in Tree', time_to_wait=60)
    shared_reports_button.try_click()
    ui.expect(GridCell(report_name),
              f'Can not see the shared report which assigned View permission to federation user')
    ui.check_actions(["Copy", "Details", "Export Report", "Email Report"], report_name)
    ui.action("Details", report_name)
    session = users_and_roles.get_session_for_user('Application Management')
    query = "Select * from role"
    result, success, message = ReportsManager.modify_report(session, "/Reports", report_name, query)
    assert success is False, f'Report modified:{result}'
    logger.info(f'Report can not modified, API response: {message}')
