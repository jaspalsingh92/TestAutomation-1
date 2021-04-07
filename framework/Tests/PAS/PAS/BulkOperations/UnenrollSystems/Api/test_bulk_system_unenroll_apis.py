import logging

import pytest
from pytest import skip

from Shared.API.infrastructure import ResourceManager
from Shared.API.redrock import RedrockController
from Shared.API.sets import SetsManager
from Shared.util import Util
from Shared.endpoint_manager import EndPoints
from Utils.guid import guid

pytestmark = [pytest.mark.api, pytest.mark.cps, pytest.mark.bulk_system_unenroll, pytest.mark.pas]

logger = logging.getLogger('test')


def test_bulk_system_unenroll_by_sql_query_only_unenrolls_correct_systems(core_session, test_four_virtual_aapm_agents):
    user_info = core_session.get_current_session_user_info().json()['Result']

    agents, _ = test_four_virtual_aapm_agents
    all_agent_ids, all_server_ids = _setup_agents(core_session, agents)
    unenroll_agent_ids = all_agent_ids[:2]
    unenroll_server_ids = all_server_ids[:2]
    keep_agent_ids = all_agent_ids[2:]

    _validate_aapm_agent_details(core_session, all_agent_ids, True)

    sql_query = RedrockController.get_query_for_ids('Server', unenroll_server_ids)
    _, success = ResourceManager.unenroll_multiple_systems_by_query(core_session, sql_query)
    assert success, f"Unenroll Multiple systems by query failed: {sql_query}"

    _validate_aapm_agent_details(core_session, unenroll_agent_ids, False)
    _validate_aapm_agent_details(core_session, keep_agent_ids, True)

    username = user_info['Name']
    start_type = 'Cloud.Core.AsyncOperation.BulkSystemUnenrollClient.StartQuery.Multi'
    end_type = 'Cloud.Core.AsyncOperation.BulkSystemUnenrollClient.Success.Multi'
    start_message = f'{username} initiated unenroll of multiple systems'
    end_message = f'{username} successfully unenrolled {len(unenroll_server_ids)} systems'

    RedrockController.expect_event_message_by_type(core_session, start_type, start_message)
    RedrockController.expect_event_message_by_type(core_session, end_type, end_message)


@pytest.mark.pas_failed
def test_bulk_system_unenroll_by_ids_only_unenrolls_correct_systems(core_session, test_four_virtual_aapm_agents):
    user_info = core_session.get_current_session_user_info().json()['Result']

    agents, _ = test_four_virtual_aapm_agents
    all_agent_ids, all_server_ids = _setup_agents(core_session, agents)
    unenroll_agent_ids = all_agent_ids[:2]
    unenroll_server_ids = all_server_ids[:2]
    keep_agent_ids = all_agent_ids[2:]

    _validate_aapm_agent_details(core_session, all_agent_ids, True)

    _, success = ResourceManager.unenroll_multiple_systems(core_session, unenroll_server_ids)
    assert success, f"Unenroll multiple systems failed: {unenroll_server_ids}"

    _validate_aapm_agent_details(core_session, unenroll_agent_ids, False)
    _validate_aapm_agent_details(core_session, keep_agent_ids, True)

    username = user_info['Name']
    start_type = 'Cloud.Core.AsyncOperation.BulkSystemUnenrollClient.StartQuery.Multi'
    end_type = 'Cloud.Core.AsyncOperation.BulkSystemUnenrollClient.Success.Multi'
    start_message = f'{username} initiated unenroll of multiple systems'
    end_message = f'{username} successfully unenrolled {len(unenroll_server_ids)} systems'

    RedrockController.expect_event_message_by_type(core_session, start_type, start_message)
    RedrockController.expect_event_message_by_type(core_session, end_type, end_message)


def test_bulk_system_unenroll_by_ids_only_unenrolls_correct_systems_fast_track(core_session,
                                                                               test_four_virtual_aapm_agents):
    user_info = core_session.get_current_session_user_info().json()['Result']

    agents, _ = test_four_virtual_aapm_agents
    all_agent_ids, all_server_ids = _setup_agents(core_session, agents)
    unenroll_agent_ids = all_agent_ids[:2]
    unenroll_server_ids = all_server_ids[:2]
    keep_agent_ids = all_agent_ids[2:]

    _validate_aapm_agent_details(core_session, all_agent_ids, True)

    _, success = ResourceManager.unenroll_multiple_systems(core_session, unenroll_server_ids, wait_time=0,
                                              SkipIfAgentReconciliationEnabled=True, run_sync=True)
    assert success, f"Unenroll multiple systems failed: {unenroll_server_ids}"

    _validate_aapm_agent_details(core_session, unenroll_agent_ids, False)
    _validate_aapm_agent_details(core_session, keep_agent_ids, True)

    username = user_info['Name']
    start_type = 'Cloud.Core.AsyncOperation.BulkSystemUnenrollClient.StartQuery.Multi'
    end_type = 'Cloud.Core.AsyncOperation.BulkSystemUnenrollClient.Success.Multi'
    start_message = f'{username} initiated unenroll of multiple systems'
    end_message = f'{username} successfully unenrolled {len(unenroll_server_ids)} systems'

    RedrockController.expect_event_message_by_type(core_session, start_type, start_message)
    RedrockController.expect_event_message_by_type(core_session, end_type, end_message)


def test_bulk_system_unenroll_by_api_set_correct_systems(core_session, test_four_virtual_aapm_agents):
    agents, _ = test_four_virtual_aapm_agents
    all_agent_ids, all_server_ids = _setup_agents(core_session, agents)
    unenroll_agent_ids = all_agent_ids[:2]
    unenroll_server_ids = all_server_ids[:2]
    keep_agent_ids = all_agent_ids[2:]
    _validate_aapm_agent_details(core_session, all_agent_ids, True)

    some_set_name = "ApiSet" + guid()
    SetsManager.create_manual_collection(core_session, some_set_name, "Server", None)
    set_id = SetsManager.get_collection_id(core_session, some_set_name, "Server")
    SetsManager.update_members_collection(core_session, 'add', list(unenroll_server_ids), 'Server', set_id)

    collection_and_filters = SetsManager.get_object_collection_and_filter_by_name(core_session, some_set_name, "Server")
    filters = collection_and_filters['Filters']

    logger.info(f'Manual set {collection_and_filters} - members - {unenroll_server_ids}')
    _, success = ResourceManager.unenroll_multiple_systems_by_query(core_session, filters)
    assert success is True, f'Unenroll systems job failed when expected success'

    SetsManager.delete_collection(core_session, set_id)
    _validate_aapm_agent_details(core_session, unenroll_agent_ids, False)
    _validate_aapm_agent_details(core_session, keep_agent_ids, True)


def test_bulk_system_unenroll_by_api_set_correct_systems_fast_track(core_session, test_four_virtual_aapm_agents):
    agents, _ = test_four_virtual_aapm_agents
    all_agent_ids, all_server_ids = _setup_agents(core_session, agents)
    unenroll_agent_ids = all_agent_ids[:2]
    unenroll_server_ids = all_server_ids[:2]
    keep_agent_ids = all_agent_ids[2:]
    _validate_aapm_agent_details(core_session, all_agent_ids, True)

    some_set_name = "ApiSet" + guid()
    SetsManager.create_manual_collection(core_session, some_set_name, "Server", None)
    set_id = SetsManager.get_collection_id(core_session, some_set_name, "Server")
    SetsManager.update_members_collection(core_session, 'add', list(unenroll_server_ids), 'Server', set_id)

    collection_and_filters = SetsManager.get_object_collection_and_filter_by_name(core_session, some_set_name, "Server")
    filters = collection_and_filters['Filters']

    logger.info(f'Manual set {collection_and_filters} - members - {unenroll_server_ids}')
    _, success = ResourceManager.unenroll_multiple_systems_by_query(core_session, filters, wait_time=0,
                                                                         SkipIfAgentReconciliationEnabled=True,
                                                                         run_sync=True)
    assert success, f'Unenroll systems job failed when expected success: {unenroll_server_ids}'

    SetsManager.delete_collection(core_session, set_id)
    _validate_aapm_agent_details(core_session, unenroll_agent_ids, False)
    _validate_aapm_agent_details(core_session, keep_agent_ids, True)


def test_overlapping_requests_succeed(core_session, test_ten_virtual_aapm_agents):
    agents, _ = test_ten_virtual_aapm_agents
    all_agent_ids, all_server_ids = _setup_agents(core_session, agents)
    server_ids1 = all_server_ids[:4]
    server_ids2 = all_server_ids[4:6]
    server_ids3 = all_server_ids[6:]
    _validate_aapm_agent_details(core_session, all_agent_ids, True)

    jobID1, success1 = ResourceManager.unenroll_multiple_systems(core_session, server_ids1, wait_time=-1)
    jobID2, success2 = ResourceManager.unenroll_multiple_systems(core_session, server_ids1, wait_time=-1)  # redundancy deliberate
    jobID3, success3 = ResourceManager.unenroll_multiple_systems(core_session, server_ids2, wait_time=-1)
    jobID4, success4 = ResourceManager.unenroll_multiple_systems(core_session, server_ids3)  # wait on final call

    assert success1 and success2 and success3 and success4, "One of the unenroll operations failed."

    #Wait for all all jobs to finish
    ResourceManager.wait_for_job_state_succeeded(core_session, jobID1)
    ResourceManager.wait_for_job_state_succeeded(core_session, jobID2)
    ResourceManager.wait_for_job_state_succeeded(core_session, jobID3)
    ResourceManager.wait_for_job_state_succeeded(core_session, jobID4)

    _validate_aapm_agent_details(core_session, all_agent_ids, False)


def test_redundant_requests_succeed(core_session, test_four_virtual_aapm_agents):
    agents, _ = test_four_virtual_aapm_agents
    all_agent_ids, all_server_ids = _setup_agents(core_session, agents)
    server_ids1 = all_server_ids[:2]
    server_ids2 = all_server_ids[2:]
    _validate_aapm_agent_details(core_session, all_agent_ids, True)

    jobID1, success1 = ResourceManager.unenroll_multiple_systems(core_session, server_ids1)
    jobID2, success2 = ResourceManager.unenroll_multiple_systems(core_session, server_ids2)
    jobID3, success3 = ResourceManager.unenroll_multiple_systems(core_session, server_ids1)
    jobID4, success4 = ResourceManager.unenroll_multiple_systems(core_session, server_ids2)

    assert success1 and success2 and success3 and success4, "One of the unenroll operations failed."

    #Wait for all all jobs to finish
    ResourceManager.wait_for_job_state_succeeded(core_session, jobID1)
    ResourceManager.wait_for_job_state_succeeded(core_session, jobID2)
    ResourceManager.wait_for_job_state_succeeded(core_session, jobID3)
    ResourceManager.wait_for_job_state_succeeded(core_session, jobID4)

    _validate_aapm_agent_details(core_session, all_agent_ids, False)


def test_bulk_system_unenroll_honours_skipPwdRecon_option(core_session, test_ten_virtual_aapm_agents):
    agents, _ = test_ten_virtual_aapm_agents
    all_agent_ids, all_server_ids = _setup_agents(core_session, agents)
    unenroll_agent_ids = all_agent_ids[:4]
    pwdRecon_agent_ids = all_agent_ids[4:6]
    keep_agent_ids = all_agent_ids[6:]
    unenroll_server_ids = all_server_ids[:4]
    pwdRecon_server_ids = all_server_ids[4:6]
    keep_server_ids = all_server_ids[6:]

    #Set Pwd recon for the second set of systems
    for server_id in pwdRecon_server_ids:
        result = RedrockController.get_system(core_session, server_id)
        assert len(result) != 0
        system = result[0]["Row"]
        ResourceManager.update_system(core_session, server_id, system["Name"], system["FQDN"],
                                      system["ComputerClass"],
                                      allowautomaticlocalaccountmaintenance=True)

    all_agent_ids = unenroll_agent_ids + pwdRecon_agent_ids + keep_agent_ids
    _validate_aapm_agent_details(core_session, all_agent_ids, True)

    _, success = ResourceManager.unenroll_multiple_systems(core_session, unenroll_server_ids + pwdRecon_server_ids,
                                                                SkipIfAgentReconciliationEnabled=True)
    assert success, f"unenroll multiple systems failed: {unenroll_server_ids + pwdRecon_server_ids}"

    _validate_aapm_agent_details(core_session, unenroll_agent_ids, False)
    _validate_aapm_agent_details(core_session, pwdRecon_agent_ids, True)
    _validate_aapm_agent_details(core_session, keep_agent_ids, True)

    #Now, uneroll the remaining agents with SkipIfAgentReconciliationEnabled=False

    _, success = ResourceManager.unenroll_multiple_systems(core_session, pwdRecon_server_ids + keep_server_ids,
                                                                SkipIfAgentReconciliationEnabled=False)
    assert success, f"Unenroll multiple systems failed: {pwdRecon_server_ids + keep_server_ids}"

    _validate_aapm_agent_details(core_session, all_agent_ids, False)


@pytest.mark.parametrize('simulate_failure', [True, False])
def test_bulk_system_unenroll_job_fails_due_to_invalid_request_missing_query(core_session, simulate_failure):

    if simulate_failure:
        set_query = ""
    else:
        set_query = "@@Favorites"

    request = core_session.apirequest(
        EndPoints.BULK_UNENROLL,
        Util.scrub_dict({
            'SetQuery': set_query,
            'SkipIfAgentReconciliationEnabled': True,
        })
    )

    request_json = request.json()
    result, success = request_json['Result'], request_json['success']
    logger.info(success)
    assert not simulate_failure == success, f"Query success was unexpected value, with message {result}"


@pytest.mark.parametrize('simulate_failure', [True, False])
def test_bulk_system_unenroll_job_fails_due_to_invalid_request_no_query_or_ids(core_session, simulate_failure):

    if simulate_failure:
        request = core_session.apirequest(EndPoints.BULK_UNENROLL,
                                          Util.scrub_dict({'SkipIfAgentReconciliationEnabled': True}))
    else:
        request = core_session.apirequest(EndPoints.BULK_UNENROLL, Util.scrub_dict(
            {'SetQuery': "@@Favorites", 'SkipIfAgentReconciliationEnabled': True}))

    request_json = request.json()
    result, success = request_json['Result'], request_json['success']
    assert not simulate_failure == success, f"Query success was unexpected value, with message {result}"


@pytest.mark.parametrize('simulate_failure', [True, False])
def test_bulk_system_unenroll_job_fails_due_to_invalid_request_no_query_or_ids_fast_track(core_session,
                                                                                          simulate_failure,
                                                                                          test_four_virtual_aapm_agents):
    agents, _ = test_four_virtual_aapm_agents
    _, server_ids = _setup_agents(core_session, agents)

    if simulate_failure:
        request = core_session.apirequest(EndPoints.BULK_UNENROLL,
                                          Util.scrub_dict({'SkipIfAgentReconciliationEnabled': True, 'RunSync': True}))
    else:
        sql_query = RedrockController.get_query_for_ids('Server', server_ids)
        request = core_session.apirequest(EndPoints.BULK_UNENROLL, Util.scrub_dict(
            {'SetQuery': sql_query, 'SkipIfAgentReconciliationEnabled': True, 'RunSync': True}))

    request_json = request.json()
    result, success = request_json['Result'], request_json['success']
    logger.info(success)
    assert not simulate_failure == success, f"Query success was unexpected value, with message {result}"


@pytest.mark.parametrize('simulate_failure', [True, False])
def test_bulk_system_unenroll_job_fails_due_to_invalid_request_empty_id_list(core_session, simulate_failure,
                                                                             test_four_virtual_aapm_agents):
    agents, _ = test_four_virtual_aapm_agents
    _, server_ids = _setup_agents(core_session, agents)

    if simulate_failure:
        request = core_session.apirequest(EndPoints.BULK_UNENROLL,
                                          Util.scrub_dict({'Ids': [], 'SkipIfAgentReconciliationEnabled': True}))
    else:
        request = core_session.apirequest(EndPoints.BULK_UNENROLL, Util.scrub_dict(
            {'Ids': server_ids, 'SkipIfAgentReconciliationEnabled': False}))

    request_json = request.json()
    result, success = request_json['Result'], request_json['success']
    assert not simulate_failure == success, f"Query success was unexpected value, with message {result}"


@pytest.mark.parametrize('simulate_failure', [True, False])
def test_bulk_system_unenroll_job_fails_due_to_invalid_request_query_and_id_list(core_session, simulate_failure,
                                                                                 test_four_virtual_aapm_agents):
    agents, _ = test_four_virtual_aapm_agents
    _, server_ids = _setup_agents(core_session, agents)

    if simulate_failure:
        request = core_session.apirequest(EndPoints.BULK_UNENROLL, Util.scrub_dict(
            {'SetQuery': "@@Favorites", 'Ids': server_ids, 'SkipIfAgentReconciliationEnabled': True}))
    else:
        request = core_session.apirequest(EndPoints.BULK_UNENROLL, Util.scrub_dict(
            {'Ids': server_ids, 'SkipIfAgentReconciliationEnabled': True}))

    request_json = request.json()
    result, success = request_json['Result'], request_json['success']
    assert not simulate_failure == success, f"Query success was unexpected value, with message {result}"


@pytest.mark.parametrize('simulate_failure', [True, False])
def test_bulk_system_unenroll_job_fails_due_to_request_query_returning_zero_rows_fast_track(core_session,
                                                                                            simulate_failure,
                                                                                            test_four_virtual_aapm_agents):
    agents, _ = test_four_virtual_aapm_agents
    _, server_ids = _setup_agents(core_session, agents)

    if simulate_failure:
        invalid_query = f"select * from Server where ID = '{guid()}'"
        request = core_session.apirequest(EndPoints.BULK_UNENROLL, Util.scrub_dict(
            {'SetQuery': invalid_query, 'Ids': server_ids, 'SkipIfAgentReconciliationEnabled': True, 'RunSync': True}))
    else:
        valid_query = RedrockController.get_query_for_ids('Server', server_ids)
        request = core_session.apirequest(EndPoints.BULK_UNENROLL, Util.scrub_dict(
            {'SetQuery': valid_query, 'SkipIfAgentReconciliationEnabled': True, 'RunSync': True}))

    request_json = request.json()
    result, success = request_json['Result'], request_json['success']
    assert not simulate_failure == success, f"Query success was unexpected value, with message {result}"


@pytest.mark.parametrize('simulate_failure', [True, False])
def test_bulk_system_unenroll_job_fails_due_to_invalid_request_query_string_fast_track(core_session, simulate_failure,
                                                                                       test_four_virtual_aapm_agents):
    agents, _ = test_four_virtual_aapm_agents
    _, server_ids = _setup_agents(core_session, agents)

    if simulate_failure:
        invalid_query = f"invalid query string"  # invalid sql query... should fail
        request = core_session.apirequest(EndPoints.BULK_UNENROLL, Util.scrub_dict(
            {'SetQuery': invalid_query, 'Ids': server_ids, 'SkipIfAgentReconciliationEnabled': True, 'RunSync': True}))
    else:
        valid_query = RedrockController.get_query_for_ids('Server', server_ids)
        request = core_session.apirequest(EndPoints.BULK_UNENROLL, Util.scrub_dict(
            {'SetQuery': valid_query, 'SkipIfAgentReconciliationEnabled': True, 'RunSync': True}))

    request_json = request.json()
    result, success = request_json['Result'], request_json['success']
    assert not simulate_failure == success, f"Query success was unexpected value, with message {result}"


@pytest.mark.parametrize('simulate_failure', [True, False])
def test_bulk_system_unenroll_job_fails_due_to_invalid_request_missing_all_fields(core_session, simulate_failure):
    if simulate_failure:
        request = core_session.apirequest(EndPoints.BULK_UNENROLL, Util.scrub_dict({}))
    else:
        request = core_session.apirequest(EndPoints.BULK_UNENROLL, Util.scrub_dict(
            {'SetQuery': "@@Favorites", 'SkipIfAgentReconciliationEnabled': True}))

    request_json = request.json()
    result, success = request_json['Result'], request_json['success']
    assert not simulate_failure == success, f"Query success was unexpected value, with message {result}"


def test_app_management_user_can_create_job_but_not_unenroll_servers(core_session, users_and_roles,
                                                                     test_four_virtual_aapm_agents):
    agents, _ = test_four_virtual_aapm_agents
    agent_ids, server_ids = _setup_agents(core_session, agents)

    requestor_session = users_and_roles.get_session_for_user('Application Management')

    user_info = requestor_session.get_current_session_user_info().json()['Result']

    _, result = ResourceManager.unenroll_multiple_systems(requestor_session, server_ids)
    assert result, "Job did not execute"

    _validate_aapm_agent_details(core_session, agent_ids, True)

    username = user_info['Name']
    start_type = 'Cloud.Core.AsyncOperation.BulkSystemUnenrollClient.Start.Multi'
    end_type = 'Cloud.Core.AsyncOperation.BulkSystemUnenrollClient.Failure.Multi'
    start_message = f'{username} initiated unenroll of {len(server_ids)} systems'
    end_message = f'{username} failed to unenroll {len(server_ids)} of {len(server_ids)} systems'

    RedrockController.expect_event_message_by_type(core_session, start_type, start_message)
    RedrockController.expect_event_message_by_type(core_session, end_type, end_message)


def test_bulk_system_unenroll_works_with_built_in_set(core_session, clean_users, users_and_roles,
                                                      get_environment, test_four_virtual_aapm_agents):
    Engines = get_environment
    if Engines == "AWS - PLV8":
        agents, _ = test_four_virtual_aapm_agents
        agent_ids, server_ids = _setup_agents(core_session, agents)

        right_data = ("Privileged Access Service Power User", "role_Privileged Access Service Power User")

        requester_session = users_and_roles.get_session_for_user(right_data[0])
        role_info = users_and_roles.get_role(right_data[0])

        _validate_aapm_agent_details(core_session, agent_ids, True)

        for system_id in server_ids:
            permission_string = 'Grant,View,Edit,Delete,ManageSession,AgentAuth,RequestZoneRole,AddAccount,' \
                                'UnlockAccount '
            result, success = ResourceManager.assign_system_permissions(core_session,
                                                                        permission_string,
                                                                        role_info['Name'], role_info['ID'], "Role",
                                                                        system_id)
            assert success, "Did not set system permissions " + result

        ResourceManager.unenroll_multiple_systems_by_query(requester_session, '@@Unix Servers')

        # not asserting success or failure, the admin may have access to systems created by other tests which
        # would not succeed

        _validate_aapm_agent_details(core_session, agent_ids, False)

    else:
        skip('todo: Fix this test to work on azure')


@pytest.mark.parametrize('explicit_missing_delete_permission', [True, False])
def test_missing_permissions_on_systems(core_session, users_and_roles,
                                        explicit_missing_delete_permission, test_four_virtual_aapm_agents):
    # System 0-1 has delete permissions
    # System 2-3 has no delete permissions
    agents, _ = test_four_virtual_aapm_agents
    agent_ids, server_ids = _setup_agents(core_session, agents)

    requester_session = users_and_roles.get_session_for_user("Privileged Access Service Power User")
    results_role = users_and_roles.get_role("Privileged Access Service Power User")

    for system_id in server_ids:
        if system_id in server_ids[:2]:
            permission_string = 'Grant,View,Edit,Delete,ManageSession,AgentAuth,RequestZoneRole,AddAccount,UnlockAccount'
        else:
            if not explicit_missing_delete_permission:
                continue
            permission_string = 'Grant,View,Edit,ManageSession,AgentAuth,RequestZoneRole,AddAccount,UnlockAccount'
        logger.info(system_id)
        logger.info(permission_string)
        result, success = ResourceManager.assign_system_permissions(core_session, permission_string,
                                                                    results_role['Name'], results_role['ID'], "Role",
                                                                    system_id)
        assert success, "Did not set system permissions " + result

    _, success = ResourceManager.unenroll_multiple_systems(requester_session, server_ids)
    assert success, f"Unenroll multiple systems failed: {server_ids}"

    _validate_aapm_agent_details(core_session, agent_ids[:2], False)
    _validate_aapm_agent_details(core_session, agent_ids[2:], True)


def _validate_aapm_agent_details(session, agent_ids, expected):
    query = RedrockController.get_query_for_ids('centrifyclients', agent_ids, columns='ResourceID, FeatureAAPM')
    results = RedrockController.get_result_rows(
        RedrockController.redrock_query(session, query))

    # make sure num of systems match
    assert len(results) == len(agent_ids)

    for row in results:
        assert row["FeatureAAPM"] is expected


def _setup_agents(session, agents):
    for agent in agents:
        agent.enroll(session, True)

    all_agent_ids = [agent.agentProfileId for agent in agents]
    all_server_ids = [agent.computerUuid for agent in agents]

    return all_agent_ids, all_server_ids