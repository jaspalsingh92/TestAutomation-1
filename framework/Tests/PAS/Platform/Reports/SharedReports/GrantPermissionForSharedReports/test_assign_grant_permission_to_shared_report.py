import pytest
from Shared.API.reports import ReportsManager
from Shared.API.users import UserManager
from Shared.UI.Centrify.SubSelectors.grids import GridCell
from Shared.UI.Centrify.SubSelectors.navigation import TreeFolder
from Shared.UI.Centrify.selectors import Div, LoadingMask
import logging

logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.bhavna
@pytest.mark.pas_failed
def test_assign_grant_permission_to_shared_reports(core_session, create_report, users_and_roles):
    """
    TCID: C6353 Assign 'Grant' permission to shared report
    :param core_session: Centrify Authentication Session
    """
    my_report = create_report(core_session, "Select Name From Server", dir="/Reports")
    report_name = my_report['Name']
    session_user = core_session.get_user()
    session_user_name = session_user.get_login_name()
    session_user_id = session_user.get_id()
    grant_str = "0000000000000000000000000000000000000000000000000000000011101101"
    ui = users_and_roles.get_ui_as_user("Federation Management")
    user_details = ui.get_user()
    user_name = user_details.get_login_name()
    user_id = user_details.get_id()
    role = UserManager.get_user_role_rights(core_session, user_id)
    assign_result = ReportsManager.assign_directory_rights_to_role(core_session, "/Reports",
                                                                   [{"Role": role['Result']['Results'][0]['Entities'][0][
                                                                             'Key'],
                                                                     "Rights": ["Read"]},
                                                                    {"Role": "Everybody",
                                                                     "Rights": ["Read"]
                                                                                }])
    assert assign_result, f'Failed to give the read the permission to Shared Folder'
    result, success, message = ReportsManager.update_report_permission(core_session, user_name, user_id, grant_str,
                                                                       report_name, ['Owner'])
    assert success, f'Failed to assign grant permission to Federation user:{message}'
    logger.info(f'Successfully assign the grant permission to federation user:{result}')
    ui.navigate("Reports", check_rendered_tab=False)
    ui.expect_disappear(LoadingMask(), 'Report page did not load properly')
    ui.expect(TreeFolder("My Reports"), "Failed to find Shared Reports Tab under Reports", time_to_wait=30)
    ui.expect(TreeFolder("Shared Reports"), f'Expected find Shared Reports Folder in Tree', time_to_wait=30).try_click()
    ui.expect(GridCell(report_name),
              f'Can not see the shared report which assigned grant permission to federation user')
    ui.check_actions(["Copy", "Move", "Delete", "Modify", "Export Report", "Email Report"], report_name)
    ui.action("Modify", report_name)
    ui.expect(Div("Report Builder"), f'Failed to enter report detail page')
    session = users_and_roles.get_session_for_user('Federation Management')
    result, success, message = ReportsManager.update_report_permission(session,
                                                                       session_user_name, session_user_id,
                                                                       grant_str, report_name, ['Owner'])
    assert success, f'Failed to save permission, API response: {message}'
    logger.info(f'Permission saved successfully:{result}')
