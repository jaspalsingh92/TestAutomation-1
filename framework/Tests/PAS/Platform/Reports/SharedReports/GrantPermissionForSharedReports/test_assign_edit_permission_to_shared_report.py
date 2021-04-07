import pytest
from Shared.API.reports import ReportsManager
from Shared.API.users import UserManager
from Shared.UI.Centrify.SubSelectors.grids import GridCell
from Shared.UI.Centrify.SubSelectors.navigation import TreeFolder
from Shared.UI.Centrify.SubSelectors.state import RestCallComplete
from Shared.UI.Centrify.selectors import DisabledButton, LoadingMask
import logging

logger = logging.getLogger("test")


@pytest.mark.ui
@pytest.mark.bhavna
@pytest.mark.pas_failed
def test_assign_edit_permission_to_shared_report(core_session, create_report, users_and_roles):
    """
    TCID: C6352 Assign 'Edit' permission to shared report
    :param core_session: Centrify Authentication session
    :param create_report: To create the report
    :param users_and_roles: To open an UI and assign specific right to user
    """
    my_report = create_report(core_session, "Select Name From Server", dir="/Reports")
    report_name = my_report['Name']
    grant_str = "0000000000000000000000000000000000000000000000000000000011101100"
    ui = users_and_roles.get_ui_as_user("MFA Unlock")
    user = ui.get_user()
    user_name = user.get_login_name()
    user_id = user.get_id()
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
    result, success, message = ReportsManager.update_report_permission(core_session, user_name,
                                                                       user_id, grant_str, report_name, ['ReadWrite'])
    assert success, f'Failed to assign Edit permission to MFA user:{message}'
    logger.info(f'Successfully assign the Edit permission to MFA user:{result}')
    ui.navigate("Reports", check_rendered_tab=False)
    ui.expect_disappear(LoadingMask(), "Report page did not load properly", 60)
    ui.expect(RestCallComplete(), "Expected rest call to complete.")
    ui.expect(TreeFolder("Shared Reports"), "Failed to find shared Reports Tab under Reports", time_to_wait=60)
    shared_reports_button = ui._searchAndExpect(TreeFolder("Shared Reports"),
                                                f'Expected find Shared Reports Folder in Tree', time_to_wait=60)
    shared_reports_button.try_click()
    ui.expect(GridCell(report_name),
              f'Can not see the shared report which assigned Edit permission to MFA user')
    ui.check_actions(["Copy", "Move", "Delete", "Modify", "Export Report", "Email Report"], report_name)
    ui.action("Modify", report_name)
    session = users_and_roles.get_session_for_user('MFA Unlock')
    query = "Select * From role"
    result, success, message = ReportsManager.modify_report(session, "/Reports", report_name, query)
    assert success, f'Script editor could not modified successfully:{message}'
    logger.info(f'Script editor could not modified successfully:{result}')
    ui.tab("Permissions")
    ui.expect(DisabledButton("Add"), "Add is not grey can edit the permission")
    logger.info(f"'Add' button is grey, and cannot modify the existing permission")
