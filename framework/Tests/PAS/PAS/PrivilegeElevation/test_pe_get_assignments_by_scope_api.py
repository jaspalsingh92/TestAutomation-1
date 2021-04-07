import logging

import pytest

from Shared.API.agent import get_PE_ASSIGNMENTS_Data
from Shared.API.infrastructure import ResourceManager
from Shared.API.privilege_elevation import PrivilegeElevation
from Shared.API.sets import SetsManager
from Shared.util import Util
from Utils.guid import guid

"""
GetAssignmentsByScope
1. commandID works, also scope is global works
2. commandName works
3. commandID and commandName not provided, should still pass
4. ScopeType not provided, should fail
5. Both Command and Command ID provided, should fail
6. Invalid command ID, should fail ??
7. Invalid command Name should fail ??
8. Invalid scopeID, should fail
9. Test no rules, should pass
10. Power User can access
11. PE admin can access
12.PE admin without view permission on system not able to access
13.Power User without view permission on system set not able to access
14.Scope is Collection: inherit on and off
15.Scope is System: inherit on and off
"""
logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_commandID_global_case(core_session, setup_generic_pe_command_with_no_rules):
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

    results, isSuccess = PrivilegeElevation.get_pe_assignments_by_scope(core_session, scopeType="Global",
                                                                        commandID=commandID)
    assert isSuccess, f"GetAssignmentsByScope failed for commandID: {commandID}, " \
                      f"reason: {results}"
    rule_info_list = [rule_info]
    assert len(results['Result']) == 1 and \
           PrivilegeElevation.check_rules_info_in_api_response(rule_info_list, results), \
        f"GetAssignmentsByScope complete check failed: {ruleID}"


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

    results, isSuccess = PrivilegeElevation.get_pe_assignments_by_scope(core_session, scopeType="Global"
                                                                        , command=commandName)
    assert isSuccess, f"GetAssignmentsByScope failed for commandName: {commandName}, " \
                      f"reason: {results}"
    rule_info_list = [rule_info]

    assert len(results['Result']) == 1 and \
           PrivilegeElevation.check_rules_info_in_api_response(rule_info_list, results), \
        f"GetAssignmentsByScope complete check failed: {ruleID}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_commandID_commandName_not_provided(core_session, setup_generic_pe_command_with_no_rules, create_resources):
    commandName, commandID = setup_generic_pe_command_with_no_rules

    admin_user = core_session.get_user()
    admin_user_name = admin_user.get_login_name()
    admin_user_id = admin_user.get_id()

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
    rule_info1 = get_PE_ASSIGNMENTS_Data(commandID=commandID, commandName=commandName, principalType="Role",
                                        principal="System Administrator", scopeType="System",
                                        scope=added_system_id, principalId=None, bypassChallenge=False)
    ruleID1, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                  scopeType=rule_info1['ScopeType'],
                                                                  scope=rule_info1['Scope'],
                                                                  principalType=rule_info1['PrincipalType'],
                                                                  principal=rule_info1['Principal'])

    assert isSuccess, f" Adding rule assignment 1 failed"
    rule_info1['ID'] = ruleID1

    #Add assignment 2
    rule_info2 = rule_info1
    ruleID2, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                  scopeType=rule_info2['ScopeType'],
                                                                  scope=rule_info2['Scope'],
                                                                  principalType=rule_info2['PrincipalType'],
                                                                  principal=rule_info2['Principal'])

    assert isSuccess, f" Adding rule assignment 2 failed"
    rule_info2['ID'] = ruleID2

    results, isSuccess = PrivilegeElevation.get_pe_assignments_by_scope(core_session, scopeType="System",
                                                                        scope=added_system_id)
    assert isSuccess, f"GetAssignmentsByScope failed when commandID and " \
                      f"commandName not provided. reason: {results}"
    rule_info_list = [rule_info1, rule_info2]
    assert len(results['Result']) == 2 and PrivilegeElevation.check_rules_info_in_api_response(
        rule_info_list,
        results), \
        f"GetAssignmentsByScope complete check failed: {ruleID1} : {ruleID2}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_scopeType_not_provided(core_session, setup_pe_one_command_one_rule):
    commandName, commandID, ruleID = setup_pe_one_command_one_rule
    results, isSuccess = PrivilegeElevation.get_pe_assignments_by_scope(core_session, commandID=commandID)
    assert not isSuccess and results['Message'] == "Unexpected null arguments passed to the server.", \
        f"GetAssignmentsByScope passed when scopeType not provided reason: {results}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_invalid_commandID(core_session):
    commandID = "abcd_xyz"
    results, isSuccess = PrivilegeElevation.get_pe_assignments_by_scope(core_session, scopeType="Global",
                                                                        commandID=commandID)
    assert not isSuccess and results['Message'] == "Privilege Elevation Command not found.", \
        f"GetAssignmentsByScope passed when invalid commandID provided, commandID: {commandID}, reason: {results}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_invalid_commandName(core_session):
    commandName = "abcd_xyz"
    results, isSuccess = PrivilegeElevation.get_pe_assignments_by_scope(core_session, scopeType="Global",
                                                                        command=commandName)
    assert not isSuccess and results['Message'] == "Privilege Elevation Command not found.", \
        f"GetAssignmentsByScope passed when invalid commandID provided, commandName: {commandName}, reason: {results}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_invalid_scopeID(core_session):
    scope = "abcd_xyz"
    results, isSuccess = PrivilegeElevation.get_pe_assignments_by_scope(core_session, scopeType="System",
                                                                        scope=scope)
    assert isSuccess and len(results['Result']) == 0, \
        f"GetAssignmentsByScope failed when invalid scopeID provided, scopeID: {scope}, reason: {results}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_commandName_commandID_provided(core_session, setup_pe_one_command_one_rule):
    commandName, commandID, ruleID = setup_pe_one_command_one_rule
    results, isSuccess = PrivilegeElevation.get_pe_assignments_by_scope(core_session, scopeType="Global",
                                                                        commandID=commandID, command=commandName)
    assert not isSuccess and results['Message'] == "Cannot specify both ID and name for Command in request", \
        f"GetAssignmentsByScope passed when both commandName and commandID passed, reason: {results}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_no_rules(core_session, setup_generic_pe_command_with_no_rules):
    commandName, commandID = setup_generic_pe_command_with_no_rules
    results, isSuccess = PrivilegeElevation.get_pe_assignments_by_scope(core_session, scopeType="Global",
                                                                        commandID=commandID)
    assert isSuccess and len(
        results['Result']) == 0, f"GetAssignmentsByScope for no assignments failed, reason: {results}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_power_user_has_access(core_session, setup_generic_pe_command_with_no_rules, users_and_roles):
    commandName, commandID = setup_generic_pe_command_with_no_rules

    # Get User
    requester_session = users_and_roles.get_session_for_user('Privileged Access Service Power User')
    response = requester_session.get_current_session_user_info()
    user_info = response.json()['Result']

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
    results, isSuccess = PrivilegeElevation.get_pe_assignments_by_scope(requester_session, scopeType="Global",
                                                                        commandID=commandID)
    assert isSuccess, f"GetAssignmentsByScope for PAS power user failed, reason: {results}"
    rule_info_list = [rule_info]
    assert len(results['Result']) == 1 and PrivilegeElevation.check_rules_info_in_api_response(
        rule_info_list,
        results), \
        f"GetAssignmentsByScope complete check failed: {ruleID}"


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
    results, isSuccess = PrivilegeElevation.get_pe_assignments_by_scope(requester_session, scopeType="Global",
                                                                        commandID=commandID)
    assert isSuccess, f"GetAssignmentsByScope for PAS power user failed, reason: {results}"
    rule_info_list = [rule_info]
    assert len(results['Result']) == 1 and PrivilegeElevation.check_rules_info_in_api_response(
        rule_info_list,
        results), \
        f"GetAssignmentsByScope complete check failed: {ruleID}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_regular_user_on_system(core_session, setup_generic_pe_command_with_no_rules,
                                users_and_roles, create_resources):
    commandName, commandID = setup_generic_pe_command_with_no_rules

    admin_user = core_session.get_user()
    admin_user_name = admin_user.get_login_name()
    admin_user_id = admin_user.get_id()

    # Get User
    requester_session = users_and_roles.get_session_for_user()
    response = requester_session.get_current_session_user_info()
    user_info = response.json()['Result']

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
    rule_info = get_PE_ASSIGNMENTS_Data(commandID=commandID, commandName=commandName, principalType="User",
                                        principal=user_info['Name'], scopeType="System",
                                        scope=added_system_id, principalId=None, bypassChallenge=False)
    ruleID, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                  scopeType=rule_info['ScopeType'],
                                                                  scope=rule_info['Scope'],
                                                                  principalType=rule_info['PrincipalType'],
                                                                  principal=rule_info['Principal'])

    assert isSuccess, f" Adding rule assignment failed"
    rule_info['ID'] = ruleID

    # This user does not have view permission on DB, so should fail
    results, isSuccess = PrivilegeElevation.get_pe_assignments_by_scope(requester_session, scopeType="System",
                                                                        commandID=commandID, scope=added_system_id)
    assert not isSuccess and results['Message'] == \
           "You are not authorized to perform this operation. Please contact your IT helpdesk.", \
        f"GetAssignmentsByScope for regular user with no view permissions on a system passed, reason: {results}"

    # GetAssignmentByScope should succeed if admin does the API request
    results, isSuccess = PrivilegeElevation.get_pe_assignments_by_scope(core_session, scopeType="System",
                                                                        commandID=commandID, scope=added_system_id)
    assert isSuccess, f"GetAssignmentsByScope for admin user failed, reason: {results}"
    rule_info_list = [rule_info]
    assert len(results['Result']) == 1 and \
           PrivilegeElevation.check_rules_info_in_api_response(rule_info_list, results), \
        f"GetAssignmentsByScope complete check failed: {ruleID}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_regular_user_on_system_set(core_session, setup_generic_pe_command_with_no_rules,
                                    users_and_roles, create_resources, create_manual_set):
    commandName, commandID = setup_generic_pe_command_with_no_rules

    admin_user = core_session.get_user()
    admin_user_name = admin_user.get_login_name()
    admin_user_id = admin_user.get_id()

    # Get User
    requester_session = users_and_roles.get_session_for_user()
    response = requester_session.get_current_session_user_info()
    user_info = response.json()['Result']

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
    assert result['success'], "setting admin collection permissions failed: " + result

    # Add assignment
    rule_info = get_PE_ASSIGNMENTS_Data(commandID=commandID, commandName=commandName, principalType="User",
                                        principal=user_info['Name'], scopeType="Collection",
                                        scope=set_id, principalId=None, bypassChallenge=False)
    ruleID, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                  scopeType=rule_info['ScopeType'],
                                                                  scope=rule_info['Scope'],
                                                                  principalType=rule_info['PrincipalType'],
                                                                  principal=rule_info['Principal'])

    assert isSuccess, f" Adding rule assignment failed"
    rule_info['ID'] = ruleID

    # This user does not have view permission on DB, so should fail
    results, isSuccess = PrivilegeElevation.get_pe_assignments_by_scope(requester_session, scopeType="Collection",
                                                                        commandID=commandID, scope=set_id)
    assert not isSuccess and results['Message'] == \
           "You are not authorized to perform this operation. Please contact your IT helpdesk.", \
        f"GetAssignmentsByScope for regular user with no view permissions on a collection passed, reason: {results}"

    # GetAssignmentByScope should succeed if admin does the API request
    results, isSuccess = PrivilegeElevation.get_pe_assignments_by_scope(core_session, scopeType="Collection",
                                                                        commandID=commandID, scope=set_id)
    assert isSuccess, f"GetAssignmentsByScope for admin user failed, reason: {results}"
    rule_info_list = [rule_info]
    assert len(results['Result']) == 1 and \
           PrivilegeElevation.check_rules_info_in_api_response(rule_info_list, results), \
        f"GetAssignmentsByScope complete check failed: {ruleID}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_scope_collection(core_session, setup_generic_pe_command_with_no_rules,
                          users_and_roles, create_resources, create_manual_set):
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

    admin_user = core_session.get_user()
    admin_user_name = admin_user.get_login_name()
    admin_user_id = admin_user.get_id()

    # Add System
    added_system_id = create_resources(core_session, 1, "Unix")[0]['ID']
    logger.debug(f"Successfully added a System: {added_system_id}")

    # Create Set and the system to this set
    set_id = create_manual_set(
        core_session, "Server", object_ids=[added_system_id])['ID']

    logger.debug(f"Successfully created a set and added system to that set: {set_id}")

    # Create Set2 and the system to this set
    set_id2 = create_manual_set(
        core_session, "Server", object_ids=[added_system_id])['ID']

    logger.debug(f"Successfully created a set and added system to that set: {set_id2}")

    # Give all permissions to the admin
    permission_string = 'Grant,View,Edit,Delete,ManageSession,AgentAuth,RequestZoneRole,AddAccount,UnlockAccount,' \
                        'ManagePrivilegeElevationAssignment'
    result = SetsManager.set_collection_resource_permissions(core_session, permission_string,
                                                             admin_user_name, admin_user_id, set_id,
                                                             "User")
    assert result['success'], "setting admin collection permissions failed: " + result

    # same for set 2
    result = SetsManager.set_collection_resource_permissions(core_session, permission_string,
                                                             admin_user_name, admin_user_id, set_id2,
                                                             "User")
    assert result['success'], "setting admin collection permissions failed: " + result

    # Add assignment for set 1
    rule_info2 = get_PE_ASSIGNMENTS_Data(commandID=commandID, commandName=commandName, principalType="User",
                                         principal=admin_user_name, scopeType="Collection",
                                         scope=set_id, principalId=admin_user_id,
                                         bypassChallenge=True)
    ruleID2, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                   scopeType=rule_info2['ScopeType'],
                                                                   scope=rule_info2['Scope'],
                                                                   principalType=rule_info2['PrincipalType'],
                                                                   principalID=rule_info2['PrincipalId'],
                                                                   byPassChallenge=True,
                                                                   starts=rule_info2['Starts'],
                                                                   expires=rule_info2['Expires'])
    assert isSuccess, f" Adding rule assignment for set 1 failed"
    rule_info2['ID'] = ruleID2

    # Add assignment for set 2
    rule_info3 = get_PE_ASSIGNMENTS_Data(commandID=commandID, commandName=commandName, principalType="User",
                                         principal=admin_user_name, scopeType="Collection",
                                         scope=set_id2, principalId=admin_user_id,
                                         bypassChallenge=True)
    ruleID3, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                   scopeType=rule_info3['ScopeType'],
                                                                   scope=rule_info3['Scope'],
                                                                   principalType=rule_info3['PrincipalType'],
                                                                   principalID=rule_info3['PrincipalId'],
                                                                   byPassChallenge=True,
                                                                   starts=rule_info3['Starts'],
                                                                   expires=rule_info3['Expires'])
    assert isSuccess, f" Adding rule assignment on set 2 failed"
    rule_info3['ID'] = ruleID3

    # Since inherit is off, we should get only 1 assignment, although there are 3 assignments in total
    results, isSuccess = PrivilegeElevation.get_pe_assignments_by_scope(core_session, scopeType="Collection",
                                                                        inherit=False, scope=set_id)
    assert isSuccess , f"GetAssignmentsByScope for collection with inheritance off failed, " \
                                           f"reason: {results}"

    rule_info_list = [rule_info2]
    assert len(results['Result']) == 1 and PrivilegeElevation.check_rules_info_in_api_response(
        rule_info_list,
        results), \
        f"GetAssignmentsByScope complete check failed: {ruleID1} : {ruleID2}"

    # With inheritance on, we should get 2 assignments, although there are 3 assignments in total
    results, isSuccess = PrivilegeElevation.get_pe_assignments_by_scope(core_session, scopeType="Collection",
                                                                        inherit=True, scope=set_id)
    assert isSuccess , f"GetAssignmentsByScope for collection with inheritance off failed, " \
                                           f"reason: {results}"

    rule_info_list = [rule_info1, rule_info2]

    # >= for parallel runs, since we don't know how many global assignments would be present in the results
    assert len(results['Result']) >= 2 and PrivilegeElevation.check_rules_info_in_api_response(
        rule_info_list,
        results), \
        f"GetAssignmentsByScope complete check failed: {ruleID1} : {ruleID2}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_scope_system(core_session, setup_generic_pe_command_with_no_rules,
                      users_and_roles, create_resources, create_manual_set):
    commandName, commandID = setup_generic_pe_command_with_no_rules

    admin_user = core_session.get_user()
    admin_user_name = admin_user.get_login_name()
    admin_user_id = admin_user.get_id()

    # Add System
    added_system_id = create_resources(core_session, 1, "Unix")[0]['ID']
    logger.debug(f"Successfully added a System: {added_system_id}")

    # Add System 2
    added_system_id2 = create_resources(core_session, 1, "Unix")[0]['ID']
    logger.debug(f"Successfully added a System: {added_system_id2}")

    # Create Set and the system 1 to this set
    set_id = create_manual_set(
        core_session, "Server", object_ids=[added_system_id])['ID']

    logger.debug(f"Successfully created a set and added system to that set: {set_id}")

    # Create Set2 and add both systems to this set
    set_id2 = create_manual_set(
        core_session, "Server", object_ids=[added_system_id, added_system_id2])['ID']

    logger.debug(f"Successfully created a set and added both system to that set: {set_id2}")

    # Create Set3 and the system 2 to this set
    set_id3 = create_manual_set(
        core_session, "Server", object_ids=[added_system_id2])['ID']

    logger.debug(f"Successfully created a set and added system 2 to that set: {set_id3}")

    # Give all permissions to the admin
    permission_string = 'Grant,View,Edit,Delete,ManageSession,AgentAuth,RequestZoneRole,AddAccount,UnlockAccount,' \
                        'ManagePrivilegeElevationAssignment'
    result = SetsManager.set_collection_resource_permissions(core_session, permission_string,
                                                             admin_user_name, admin_user_id, set_id,
                                                             "User")
    assert result['success'], "setting admin collection permissions failed: " + result

    # same for set 2
    result = SetsManager.set_collection_resource_permissions(core_session, permission_string,
                                                             admin_user_name, admin_user_id, set_id2,
                                                             "User")
    assert result['success'], "setting admin collection permissions failed: " + result

    #same for set 3
    result = SetsManager.set_collection_resource_permissions(core_session, permission_string,
                                                             admin_user_name, admin_user_id, set_id3,
                                                             "User")
    assert result['success'], "setting admin collection permissions failed: " + result

    # Adding rules

    # First add global assignment
    rule_info1 = get_PE_ASSIGNMENTS_Data(commandID=commandID, commandName=commandName, principalType="Role",
                                         principal="System Administrator", scopeType="Global",
                                         scope=None, principalId=None, bypassChallenge=False)
    ruleID1, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                   scopeType=rule_info1['ScopeType'],
                                                                   principalType=rule_info1['PrincipalType'],
                                                                   principal=rule_info1['Principal'])
    assert isSuccess, f" Adding rule assignment 1 failed"
    rule_info1['ID'] = ruleID1

    # Add Assignment for system1
    rule_info2 = get_PE_ASSIGNMENTS_Data(commandID=commandID, commandName=commandName, principalType="User",
                                         principal=admin_user_name, scopeType="System",
                                         scope=added_system_id, principalId=admin_user_id,
                                         bypassChallenge=True)
    ruleID2, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                   scopeType=rule_info2['ScopeType'],
                                                                   scope=rule_info2['Scope'],
                                                                   principalType=rule_info2['PrincipalType'],
                                                                   principalID=rule_info2['PrincipalId'],
                                                                   byPassChallenge=True,
                                                                   starts=rule_info2['Starts'],
                                                                   expires=rule_info2['Expires'])
    assert isSuccess, f" Adding rule assignment for system 1 failed"
    rule_info2['ID'] = ruleID2

    # Add Assignment for system2
    rule_info3 = get_PE_ASSIGNMENTS_Data(commandID=commandID, commandName=commandName, principalType="User",
                                         principal=admin_user_name, scopeType="System",
                                         scope=added_system_id2, principalId=admin_user_id,
                                         bypassChallenge=True)
    ruleID3, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                   scopeType=rule_info3['ScopeType'],
                                                                   scope=rule_info3['Scope'],
                                                                   principalType=rule_info3['PrincipalType'],
                                                                   principalID=rule_info3['PrincipalId'],
                                                                   byPassChallenge=True,
                                                                   starts=rule_info3['Starts'],
                                                                   expires=rule_info3['Expires'])
    assert isSuccess, f" Adding rule assignment on system 2 failed"
    rule_info3['ID'] = ruleID3

    # Add assignment for set 1
    rule_info4 = get_PE_ASSIGNMENTS_Data(commandID=commandID, commandName=commandName, principalType="User",
                                         principal=admin_user_name, scopeType="Collection",
                                         scope=set_id, principalId=admin_user_id,
                                         bypassChallenge=True)
    ruleID4, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                   scopeType=rule_info4['ScopeType'],
                                                                   scope=rule_info4['Scope'],
                                                                   principalType=rule_info4['PrincipalType'],
                                                                   principalID=rule_info4['PrincipalId'],
                                                                   byPassChallenge=True,
                                                                   starts=rule_info4['Starts'],
                                                                   expires=rule_info4['Expires'])
    assert isSuccess, f" Adding rule assignment on set 1 failed"
    rule_info4['ID'] = ruleID4

    # Add assignment for set 2
    rule_info5 = get_PE_ASSIGNMENTS_Data(commandID=commandID, commandName=commandName, principalType="User",
                                         principal=admin_user_name, scopeType="Collection",
                                         scope=set_id2, principalId=admin_user_id,
                                         bypassChallenge=True)
    ruleID5, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                   scopeType=rule_info5['ScopeType'],
                                                                   scope=rule_info5['Scope'],
                                                                   principalType=rule_info5['PrincipalType'],
                                                                   principalID=rule_info5['PrincipalId'],
                                                                   byPassChallenge=True,
                                                                   starts=rule_info5['Starts'],
                                                                   expires=rule_info5['Expires'])
    assert isSuccess, f" Adding rule assignment on set 2 failed"
    rule_info5['ID'] = ruleID5

    # Add assignment for set 3
    rule_info6 = get_PE_ASSIGNMENTS_Data(commandID=commandID, commandName=commandName, principalType="User",
                                         principal=admin_user_name, scopeType="Collection",
                                         scope=set_id3, principalId=admin_user_id,
                                         bypassChallenge=True)
    ruleID6, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                   scopeType=rule_info6['ScopeType'],
                                                                   scope=rule_info6['Scope'],
                                                                   principalType=rule_info6['PrincipalType'],
                                                                   principalID=rule_info6['PrincipalId'],
                                                                   byPassChallenge=True,
                                                                   starts=rule_info6['Starts'],
                                                                   expires=rule_info6['Expires'])
    assert isSuccess, f" Adding rule assignment on set 3 failed"
    rule_info6['ID'] = ruleID6

    # Since inherit is off, we should get only 1 assignment, although there are 6 assignments in total
    results, isSuccess = PrivilegeElevation.get_pe_assignments_by_scope(core_session, scopeType="System",
                                                                        inherit=False, scope=added_system_id)
    assert isSuccess, f"GetAssignmentsByScope for system with inheritance off failed, " \
                                           f"reason: {results}"
    rule_info_list = [rule_info2]
    assert len(results['Result']) == 1 and PrivilegeElevation.check_rules_info_in_api_response(
        rule_info_list,
        results), \
        f"GetAssignmentsByScope complete check failed: {ruleID2}"

    # With inheritance on, we should get 4 assignments, although there are 6 assignments in total
    results, isSuccess = PrivilegeElevation.get_pe_assignments_by_scope(core_session, scopeType="System",
                                                                        inherit=True, scope=added_system_id)
    assert isSuccess, f"GetAssignmentsByScope for system with inheritance off failed, " \
                                           f"reason: {results}"
    rule_info_list = [rule_info1, rule_info2, rule_info4, rule_info5]

    # >= for parallel runs, since we don't know how many global assignments would be present in the results
    assert len(results['Result']) >= 4 and PrivilegeElevation.check_rules_info_in_api_response(
        rule_info_list,
        results), \
        f"GetAssignmentsByScope complete check failed: {ruleID1} : {ruleID2} : {ruleID3} : {ruleID4}"
