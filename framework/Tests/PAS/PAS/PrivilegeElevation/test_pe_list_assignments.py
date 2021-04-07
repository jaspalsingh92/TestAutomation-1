import logging

import pytest

from Shared.API.infrastructure import ResourceManager
from Shared.API.privilege_elevation import PrivilegeElevation
from Shared.API.sets import SetsManager
from Shared.API.agent import *

"""
List Assignments
1. commandID works
2. commandName works
3. Nothing provided, should fail
4. Both Command and Command ID provided, should fail
5. Invalid command ID, should fail
6. Invalid command Name should fail
7. Multiple rules returned
8. Test no rules, should pass
8. Power User can access
9. PE admin can access
10.PE admin without view permission on system not able to access
11.Power User without view permission on system set not able to access
"""
logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_commandID_case(core_session, setup_generic_pe_command_with_no_rules):
    commandName, commandID = setup_generic_pe_command_with_no_rules
    rule_info = get_PE_ASSIGNMENTS_Data(commandID=commandID, commandName=commandName, principalType="Role",
                                        principal="System Administrator", scopeType="Global",
                                        scope=None, principalId=None, bypassChallenge=False)
    ruleID, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                  scopeType=rule_info['ScopeType'],
                                                                  principalType=rule_info['PrincipalType'],
                                                                  principal=rule_info['Principal'])
    assert isSuccess, f" Adding rule assignment failed"
    rule_info['ID'] = ruleID

    results, isSuccess = PrivilegeElevation.list_pe_assignments(core_session, commandID=commandID)
    assert isSuccess, f"List Assignments failed for commandID: {commandID}, reason: {results}"

    rule_info_list = [rule_info]
    assert len(results['Result']) == 1 and \
           PrivilegeElevation.check_rules_info_in_api_response(rule_info_list, results), \
        f"List Assignments complete check failed: {ruleID}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_commandName_case(core_session, setup_generic_pe_command_with_no_rules):
    commandName, commandID = setup_generic_pe_command_with_no_rules

    rule_info = get_PE_ASSIGNMENTS_Data(commandID=commandID, commandName=commandName, principalType="Role",
                                        principal="System Administrator", scopeType="Global",
                                        scope=None, principalId=None, bypassChallenge=False)
    ruleID, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                  scopeType=rule_info['ScopeType'],
                                                                  principalType=rule_info['PrincipalType'],
                                                                  principal=rule_info['Principal'])
    assert isSuccess, f" Adding rule assignment failed"
    rule_info['ID'] = ruleID

    results, isSuccess = PrivilegeElevation.list_pe_assignments(core_session, command=commandName)
    assert isSuccess, f"List Assignments failed for commandID: {commandID}, reason: {results}"

    rule_info_list = [rule_info]
    assert len(results['Result']) == 1 and \
           PrivilegeElevation.check_rules_info_in_api_response(rule_info_list, results), \
        f"List Assignments complete check failed: {ruleID}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_no_params_provided(core_session):
    results, isSuccess = PrivilegeElevation.list_pe_assignments(core_session)
    assert not isSuccess and results['Message'] == "Parameter 'Command/CommandId' must be specified.", \
        f"List Assignments passed/failed with unknown exception when no params provided, reason: {results}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_invalid_commandID(core_session):
    commandID = "abcd_xyz"
    results, isSuccess = PrivilegeElevation.list_pe_assignments(core_session, commandID=commandID)
    assert not isSuccess and results['Message'] == "Privilege Elevation Command not found.", \
        f"List Assignments passed/failed with unknown exception when invalid commandID provided, " \
        f"commandID: {commandID}, reason: {results}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_invalid_commandName(core_session):
    commandName = "abcd_xyz"
    results, isSuccess = PrivilegeElevation.list_pe_assignments(core_session, command=commandName)
    assert not isSuccess and results['Message'] == "Privilege Elevation Command not found.", \
        f"List Assignments passed/failed with unknown exception" \
        f" when invalid commandName provided, commandName: {commandName}, reason: {results}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_commandName_commandID_provided(core_session, setup_pe_one_command_one_rule):
    commandName, commandID, ruleID = setup_pe_one_command_one_rule
    results, isSuccess = PrivilegeElevation.list_pe_assignments(core_session, commandID=commandID, command=commandName)
    assert not isSuccess and results['Message'] == "Cannot specify both ID and name for Command in request", \
        f"List Assignments passed/failed with unknown exception when both " \
        f"commandName and commandID passed, reason: {results}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_multiple_rules(core_session, setup_generic_pe_command_with_no_rules):
    commandName, commandID = setup_generic_pe_command_with_no_rules

    # First Rule assignment
    rule_info1 = get_PE_ASSIGNMENTS_Data(commandID=commandID, commandName=commandName, principalType="Role",
                                         principal="System Administrator", scopeType="Global",
                                         scope=None, principalId=None, bypassChallenge=False)
    ruleID1, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                   scopeType=rule_info1['ScopeType'],
                                                                   principalType=rule_info1['PrincipalType'],
                                                                   principal=rule_info1['Principal'])
    assert isSuccess, f" Adding rule assignment 1 failed"
    rule_info1['ID'] = ruleID1

    # Get Admin info
    admin_user = core_session.get_user()
    admin_user_name = admin_user.get_login_name()
    admin_user_id = admin_user.get_id()

    # Add second rule assignment
    rule_info2 = get_PE_ASSIGNMENTS_Data(commandID=commandID, commandName=commandName, principalType="User",
                                         principal=admin_user_name, scopeType="Global",
                                         scope=None, principalId=admin_user_id,
                                         bypassChallenge=True)
    ruleID2, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                   scopeType=rule_info2['ScopeType'],
                                                                   principalType=rule_info2['PrincipalType'],
                                                                   principalID=rule_info2['PrincipalId'],
                                                                   byPassChallenge=True,
                                                                   starts=rule_info2['Starts'],
                                                                   expires=rule_info2['Expires'])
    assert isSuccess, f" Adding rule assignment 2 failed"
    rule_info2['ID'] = ruleID2

    # Get both assignments
    results, isSuccess = PrivilegeElevation.list_pe_assignments(core_session, commandID=commandID)
    assert isSuccess, f"List Assignments for two assignments failed, reason: {results}"

    rule_info_list = [rule_info1, rule_info2]
    assert len(results['Result']) == 2 and PrivilegeElevation.check_rules_info_in_api_response(
        rule_info_list,
        results), \
        f"List Assignments complete check failed: {ruleID1} : {ruleID2}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_no_rules(core_session, setup_generic_pe_command_with_no_rules):
    commandName, commandID = setup_generic_pe_command_with_no_rules
    results, isSuccess = PrivilegeElevation.list_pe_assignments(core_session, commandID=commandID)
    assert isSuccess and len(results['Result']) == 0, f"List Assignments for no assignments failed, reason: {results}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_power_user_has_access(core_session, setup_generic_pe_command_with_no_rules, users_and_roles):
    commandName, commandID = setup_generic_pe_command_with_no_rules

    # Get User
    requester_session = users_and_roles.get_session_for_user('Privileged Access Service Power User')
    response = requester_session.get_current_session_user_info()
    user_info = response.json()['Result']
    logger.debug(user_info)

    rule_info = get_PE_ASSIGNMENTS_Data(commandID=commandID, commandName=commandName, principalType="Role",
                                        principal="System Administrator", scopeType="Global",
                                        scope=None, principalId=None, bypassChallenge=False)
    ruleID, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                  scopeType=rule_info['ScopeType'],
                                                                  principalType=rule_info['PrincipalType'],
                                                                  principal=rule_info['Principal'])
    assert isSuccess, f" Adding rule assignment  failed"
    rule_info['ID'] = ruleID

    # This user inherited View permission, so should be able to see the rule
    results, isSuccess = PrivilegeElevation.list_pe_assignments(core_session, commandID=commandID)
    assert isSuccess, f"List Assignments for PAS power user failed, reason: {results}"

    rule_info_list = [rule_info]
    assert len(results['Result']) == 1 and PrivilegeElevation.check_rules_info_in_api_response(
        rule_info_list,
        results), \
        f"List Assignments complete check failed: {ruleID}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_user_has_access(core_session, setup_generic_pe_command_with_no_rules, users_and_roles):
    commandName, commandID = setup_generic_pe_command_with_no_rules

    # Get User
    requester_session = users_and_roles.get_session_for_user('Privilege Elevation Management')
    response = requester_session.get_current_session_user_info()
    user_info = response.json()['Result']
    logger.debug(user_info)

    rule_info = get_PE_ASSIGNMENTS_Data(commandID=commandID, commandName=commandName, principalType="Role",
                                        principal="System Administrator", scopeType="Global",
                                        scope=None, principalId=None, bypassChallenge=False)
    ruleID, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                  scopeType=rule_info['ScopeType'],
                                                                  principalType=rule_info['PrincipalType'],
                                                                  principal=rule_info['Principal'])
    assert isSuccess, f" Adding rule assignment  failed"
    rule_info['ID'] = ruleID

    # This user inherited View permission, so should be able to see the rule
    results, isSuccess = PrivilegeElevation.list_pe_assignments(core_session, commandID=commandID)
    assert isSuccess, f"List Assignments for PAS power user failed, reason: {results}"

    rule_info_list = [rule_info]
    assert len(results['Result']) == 1 and PrivilegeElevation.check_rules_info_in_api_response(
        rule_info_list,
        results), \
        f"List Assignments complete check failed: {ruleID}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_regular_user_with_no_view_permissions_on_system(core_session, setup_generic_pe_command_with_no_rules,
                                                    users_and_roles, create_resources):
    commandName, commandID = setup_generic_pe_command_with_no_rules

    admin_user = core_session.get_user()
    admin_user_name = admin_user.get_login_name()
    admin_user_id = admin_user.get_id()

    # Get User
    requester_session = users_and_roles.get_session_for_user()
    response = requester_session.get_current_session_user_info()
    user_info = response.json()['Result']
    logger.debug(user_info)

    # Add System
    added_system_id = create_resources(core_session, 1, "Unix")[0]['ID']
    logger.debug(f"Successfully added a System: {added_system_id}")

    # Give all permissions to the admin
    permission_string = 'Grant,View,Edit,Delete,ManageSession,AgentAuth,RequestZoneRole,AddAccount,UnlockAccount,' \
                        'ManagePrivilegeElevationAssignment'
    result, success = ResourceManager.assign_system_permissions(core_session, permission_string,
                                                                admin_user_name, admin_user_id, "User",
                                                                added_system_id)
    assert success, f"Did not set admin system permissions: {result}"


    # Add assignment
    principalType = "User"
    principal = user_info['Name']
    scopeType = "System"
    scope = added_system_id
    ruleID, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                  scopeType=scopeType, scope=scope,
                                                                  principalType=principalType, principal=principal)

    assert isSuccess, f" Adding rule assignment failed"

    # This user does not have view permission, so should fail
    results, isSuccess = PrivilegeElevation.list_pe_assignments(requester_session, commandID=commandID)
    assert not isSuccess and results['Message'] == \
           "You are not authorized to perform this operation. Please contact your IT helpdesk.", \
        f"List Assignments for regular user with no view permissions on a system passed/ failed with " \
        f"unknown exception, reason: {results}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_regular_user_with_no_view_permissions_on_system_set(core_session, setup_generic_pe_command_with_no_rules,
                                                               users_and_roles, create_resources, create_manual_set):
    commandName, commandID = setup_generic_pe_command_with_no_rules

    admin_user = core_session.get_user()
    admin_user_name = admin_user.get_login_name()
    admin_user_id = admin_user.get_id()

    # Get User
    requester_session = users_and_roles.get_session_for_user()
    response = requester_session.get_current_session_user_info()
    user_info = response.json()['Result']
    logger.debug(user_info)

    # Add System
    added_system_id = create_resources(core_session, 1, "Unix")[0]['ID']
    logger.debug(f"Successfully added a System: {added_system_id}")

    # Create Set and the system to this set
    set_id = create_manual_set(
        core_session, "Server", object_ids=[added_system_id])['ID']

    logger.debug(f"Successfully created a set and added system to that set: {set_id}")

    # Give all permissions to the admin
    permission_string = 'Grant,View,Edit,Delete,ManageSession,AgentAuth,RequestZoneRole,AddAccount,UnlockAccount,' \
                        'ManagePrivilegeElevationAssignment'
    result = SetsManager.set_collection_resource_permissions(core_session, permission_string,
                                                             admin_user_name, admin_user_id, set_id,
                                                             "User")
    logger.info(result)
    assert result['success'], "setting admin collection permissions failed: " + result

    # Add assignment
    principalType = "User"
    principal = user_info['Name']
    scopeType = "Collection"
    scope = set_id
    ruleID, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                  scopeType=scopeType, scope=scope,
                                                                  principalType=principalType, principal=principal)
    assert isSuccess, f" Adding rule assignment failed"

    # This user does not have view permission, so should fail
    results, isSuccess = PrivilegeElevation.list_pe_assignments(requester_session, commandID=commandID)
    assert not isSuccess and results['Message'] == \
           "You are not authorized to perform this operation. Please contact your IT helpdesk.", \
        f"List Assignments for regular user with no view permissions on a set passed/ failed with " \
        f"unknown exception, reason: {results}"
