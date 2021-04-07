import pytest
import logging
import time

from Shared.UI.Centrify.SubSelectors.grids import GridCell, GridRow
from Shared.UI.Centrify.SubSelectors.forms import DisabledCheckbox, DisabledCombobox
from Shared.UI.Centrify.SubSelectors.modals import Modal
from Shared.UI.Centrify.selectors import DisabledButton, Button, Component
from Shared.UI.Centrify.SubSelectors.navigation import ActiveMainContentArea
from Shared.API.sets import SetsManager
from Shared.API.workflow import WorkflowManager
from Shared.API.infrastructure import ResourceManager

logger = logging.getLogger("test")

"""
Tests to ensure critical functionality for privilege elevation workflow UI

1) Make sure a user with permission to enabled priv elevation workflow can enable it, and can also approve and reject
2) Make sure a user without permission, like a Power User, sees disabled inputs on the workflow tab for a system


"""
@pytest.mark.ui
@pytest.mark.privilege_elevation
@pytest.mark.workflow
@pytest.mark.parametrize('user_rights', ['System Administrator'], indirect=True)
def test_privilege_elevation_workflow_can_be_enabled_by_sys_admin(test_agent, cds_ui, cds_session, core_session):
    ui, ui_user = cds_ui
    session, user = cds_session
    main_admin_session = core_session
    main_admin_user = main_admin_session.get_user()

    server_id = test_agent.computerUuid

    permission_string = 'Grant,View,Edit,Delete,ManageSession,AgentAuth,RequestZoneRole,AddAccount,UnlockAccount'
    result, success = ResourceManager.assign_system_permissions(main_admin_session, permission_string,
                                                                ui_user.get_login_name(),
                                                                ui_user.get_id(), "User", server_id)

    # Create an assignment at collection scope
    ui.navigate('Resources', 'Systems')
    ui.click_row_by_guid(server_id)
    ui.tab('Workflow')
    ui.select_option('PrivilegeElevationWorkflowEnabled', 'Yes')
    ui.switch_context(Component('privilegeElevationApproverGrid'))
    ui.button('Add')
    ui.select_option('Type', 'Specified User or Role')
    ui.launch_modal(Button('Add', 'inlineAddButton'), 'Select User or Role')
    ui.search(user.get_login_name())
    ui.check_row(user.get_login_name())
    ui.close_modal('Add')
    ui.save()

    time.sleep(20)

    request_settings = {
        'assignment_type': 'Temporary',
        'start_grant_value': '10',
        'end_grant_value': '50',
        'start_time_interval': 'hours',
        'start_time_interval_value': 60,
        'end_time_interval': 'hours',
        'end_time_interval_value': 60,
        'ticket': '1'
    }

    # Request twice so we can approve/reject
    _request_pe_permission(ui, request_settings, server_id)
    _request_pe_permission(ui, request_settings, server_id)

    jobs, is_get = WorkflowManager.get_my_jobs(session)
    request_jobs = []
    options = None
    for i in jobs:
        if i['Row']['Context']['Scope'] == server_id:
            job = i['Row']
            request_jobs.append(job)
            options = job['Context']['RequestedOptions']
            assert options['StartGrantValue'] == int(request_settings['start_grant_value']), f'StartGrantValue is not correct in job context compared to ui entry'
            assert options['EndGrantValue'] == int(request_settings['end_grant_value']), f'EndGrantValue is not correct in job context compared to ui entry'
            assert options['StartTimeInterval'] == request_settings['start_time_interval_value'], f'StartTimeInterval is not correct in job context compared to ui entry'
            assert options['EndTimeInterval'] == request_settings['end_time_interval_value'], f'EndTimeInterval is not correct in job context compared to ui entry'

    approve_job = request_jobs[0]
    ui.navigate('Access', 'Requests')
    ui.click_row_by_guid(approve_job['ID'])
    ui.launch_modal('Approve', 'Approve Privilege Elevation Request')
    time.sleep(20)
    ui.button('Submit', expectations={
        'click_element_should_dissapear': True,
        'seconds_to_wait': 60 #because Azure
    })

    job = WorkflowManager.get_my_job(session, approve_job['ID'])
    assert job['TargetPrincipalAction'] == 'Approved', f'PE workflow request should have been approved after UI interaction but it is not'

    reject_job = request_jobs[1]
    ui.navigate('Access', 'Requests')
    ui.click_row_by_guid(reject_job['ID'])
    ui.launch_modal('Reject', 'Reject Privilege Elevation Request')
    ui.input('Reason', 'Not today')
    time.sleep(20)
    ui.button('Submit', expectations={
        'click_element_should_dissapear': True,
        'seconds_to_wait': 60 #because Azure
    })

    job = WorkflowManager.get_my_job(session, reject_job['ID'])
    assert job['TargetPrincipalAction'] == 'Rejected', f'PE workflow request should have been approved after UI interaction but it is not'

    system_direct_selector = GridRow(user.get_login_name())

    # Look at the server directly, make sure the system assignment via workflow is there.
    ui.navigate('Resources', 'Systems')
    ui.click_row_by_guid(server_id)
    ui.tab('Privilege Elevation')
    ui.expect(system_direct_selector, 'Command assignment directly on system not present even though we just created it.')
    time.sleep(20)


@pytest.mark.ui
@pytest.mark.privilege_elevation
@pytest.mark.workflow
@pytest.mark.parametrize('user_rights', ['Privileged Access Service Power User'], indirect=True)
def test_privilege_elevation_workflow_read_only(test_agent, cds_ui):
    ui, user = cds_ui

    server_id = test_agent.computerUuid

    ui.navigate('Resources', 'Systems')
    ui.click_row_by_guid(server_id)
    ui.tab('Workflow')
    ui.expect(DisabledCombobox('PrivilegeElevationWorkflowEnabled'), 'Enable workflow button should be disabled when user does not have Edit rights')


def _request_pe_permission(ui, request_settings, server_id):
    reason = f'I need to run commands on system {server_id}'
    ui.switch_context(ActiveMainContentArea())
    request_modal = Modal('Request Privilege Elevation Permission')
    ui.action('Request Privilege Elevation', expected_selector=request_modal)
    ui.switch_context(request_modal)
    ui.input('Reason', reason)
    ui.select_option('AssignmentType', request_settings['assignment_type'])
    ui.input('StartGrantValue', request_settings['start_grant_value'])
    ui.input('EndGrantValue', request_settings['end_grant_value'])
    ui.select_option('StartTimeInterval', request_settings['start_time_interval'])
    ui.select_option('EndTimeInterval', request_settings['end_time_interval'])
    ui.input('Ticket', request_settings['ticket'])
    ui.button('Submit', expectations={
        'click_element_should_dissapear': True,
        'seconds_to_wait': 60 #because Azure
    })