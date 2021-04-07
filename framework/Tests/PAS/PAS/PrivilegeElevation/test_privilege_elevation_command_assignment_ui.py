import pytest
import logging
import time

from Shared.UI.Centrify.SubSelectors.grids import GridCell, GridRow
from Shared.UI.Centrify.selectors import DisabledButton
from Shared.API.sets import SetsManager

logger = logging.getLogger("test")

"""
Tests to ensure critical functionality for privilege elevation UI

1) Make sure a user with pas admin / agent management rights can assign global, system level and collection level command assignments
2) Make sure all three privilege elevation grids (system/collection/global) are read only when the user does not have agent management rights

Note that test_navigation_tabs_are_correct_for_user_with_single_admin_right covers testing whether the privilege elevation tabs show up appropriately
based on the administrative rights the user has.

"""
# Lock the tenant because the global privilege elevation assignments will affect any other test using the same tenant.
lock_tenant = True

@pytest.mark.ui
@pytest.mark.privilege_elevation
@pytest.mark.parametrize('user_rights', ['System Administrator'], indirect=True)
def test_privilege_elevation_command_assignment_works_at_all_three_scopes(test_agent, pe_global_command_assignment_cleaner_by_user, create_manual_set, cds_ui, cds_session, core_session):
    ui, user = cds_ui
    session, _ = cds_session
    main_admin_session = core_session
    main_admin_user = main_admin_session.get_user()

    # Make sure the users global assignments will be cleaned up
    pe_global_command_assignment_cleaner_by_user.append(user.get_id())

    server_id = test_agent.computerUuid

    logger.info(f'Server guid for vritual agent {server_id}')
    permission_string = 'Grant,View,Edit,Delete,ManageSession,AgentAuth,RequestZoneRole,AddAccount,UnlockAccount,' \
                        'ManagePrivilegeElevationAssignment'

    agent_server_set = create_manual_set(session, 'Server', object_ids=[server_id])
    # Give all permissions to the admin

    result = SetsManager.set_collection_resource_permissions(session, permission_string,
                                                             user.get_login_name(), user.get_id(), agent_server_set["ID"],
                                                             "User")

    assert result['success'], "setting admin collection permissions failed: " + result
    set_name = agent_server_set['Name']

    # Create an assignment at global scope
    ui.navigate('Settings', 'Resources', 'Security', 'Global Privilege Elevation')
    ui.launch_modal('Add', 'Select User, Group, or Role')
    ui.search(user.get_login_name())
    ui.check_row(user.get_login_name())
    ui.close_modal('Add')
    ui.save()

    global_assignment_selector = GridCell('Global').inside(GridRow(user.get_login_name()))

    # Create an assignment at collection scope
    ui.navigate('Resources', 'Systems')
    ui.set_action(set_name, "Modify")
    ui.tab('Member Privilege Elevation')
    ui.expect(global_assignment_selector, 'Inherited command from global is not present even though we just created it.')
    ui.launch_modal('Add', 'Select User, Group, or Role')
    ui.search(user.get_login_name())
    ui.check_row(user.get_login_name())
    ui.close_modal('Add')
    ui.save()

    collection_assignment_selector = GridCell(f'{set_name}').inside(GridRow(user.get_login_name()))

    # Look at the PE tab on the server, make sure inherited assignments are there and add another.
    ui.navigate('Resources', 'Systems')
    ui.click_row_by_guid(server_id)
    ui.tab('Privilege Elevation')
    ui.expect(global_assignment_selector, 'Inherited command from global is not present even though we just created it.')
    ui.expect(collection_assignment_selector, 'Inherited command from collection is not present even though we just created it.')
    ui.launch_modal('Add', 'Select User, Group, or Role')
    ui.search(main_admin_user.get_login_name())
    ui.check_row(main_admin_user.get_login_name())
    ui.close_modal('Add')
    ui.save()

    system_direct_selector = GridRow(main_admin_user.get_login_name())

    # Look at the server directly, make sure all assignments still there.
    ui.navigate('Resources', 'Systems')
    ui.click_row_by_guid(server_id)
    ui.tab('Privilege Elevation')
    ui.expect(global_assignment_selector, 'Inherited command from global is not present even though we just created it.')
    ui.expect(collection_assignment_selector, 'Inherited command from collection is not present even though we just created it.')
    ui.expect(system_direct_selector, 'Command assignment directly on system not present even though we just created it.')


@pytest.mark.ui
@pytest.mark.privilege_elevation
def test_privilege_elevation_command_assignment_read_only(test_agent, cds_ui):
    ui, user = cds_ui

    server_id = test_agent.computerUuid

    ui.navigate('Settings', 'Resources', 'Security', 'Global Privilege Elevation')
    ui.expect(DisabledButton('Add'), 'Add button should be disabled when user does not have agent management rights')

    ui.navigate('Resources', 'Systems')
    ui.click_row_by_guid(server_id)
    ui.tab('Privilege Elevation')
    ui.expect(DisabledButton('Add'), 'Add button should be disabled when user does not have agent management rights')