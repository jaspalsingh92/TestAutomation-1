import logging
import re

import pytest

from Fixtures.PAS.Platform import users_and_roles
from Shared.API.agent import get_PE_ASSIGNMENTS_Data
from Shared.API.infrastructure import ResourceManager
from Shared.API.privilege_elevation import PrivilegeElevation
from Shared.API.sets import SetsManager
from Shared.util import Util
from Utils.guid import guid

"""
GetAssignments
1. Normal Check, everything works
2. CommandID not provided, should fail
3. Wrong commandID provided, should fail
3. Invalid scopeID fails: system and set
4. providing principal and princiapID should fail
5. Multiple rules returned
6. Power User can access
8. PE admin can access
10.PE admin without view permission on system not able to access
11.Power User without view permission on system set not able to access
"""

logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_normal_case(core_session, setup_generic_pe_command_with_no_rules):
    commandName, commandID = setup_generic_pe_command_with_no_rules
    rule_info = get_PE_ASSIGNMENTS_Data(commandID=commandID, commandName=commandName, principalType="Role",
                                        principal="System Administrator", scopeType="Global",
                                        scope=None, principalId=None, bypassChallenge=True)
    ruleID, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                  scopeType=rule_info['ScopeType'],
                                                                  principalType=rule_info['PrincipalType'],
                                                                  principal=rule_info['Principal'],
                                                                  byPassChallenge=rule_info['BypassChallenge'],
                                                                  starts=rule_info['Starts'],
                                                                  expires=rule_info['Expires'])
    assert isSuccess, f" Adding rule assignment failed"
    rule_info['ID'] = ruleID

    results, isSuccess = PrivilegeElevation.get_assignments(core_session, commandID=commandID, principalType="Role",
                                                            principal="System Administrator")
    assert isSuccess, f"Get Assignments failed for commandID: {commandID}, reason: {results}"
    rule_info_list = [rule_info]
    assert len(results['Result']) == 1 and \
           PrivilegeElevation.check_rules_info_in_api_response(rule_info_list, results), \
        f"Get Assignments complete check failed: {ruleID}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_commandID_not_provided(core_session):
    results, isSuccess = PrivilegeElevation.get_assignments(core_session, commandID="", principalType="Role",
                                                            principal="System Administrator")
    assert not isSuccess and results['Message'] == "Invalid arguments passed to the server.", \
        f"Get Assignments passed when commandID not provided, reason: {results}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_invalid_commandID(core_session):
    commandID = "abcd_xyz"
    results, isSuccess = PrivilegeElevation.get_assignments(core_session, commandID=commandID, principalType="Role",
                                                            principal="System Administrator")
    assert not isSuccess and results['Message'] == "Privilege Elevation Command not found.", \
        f"Get Assignments passed when invalid commandID provided, commandID: {commandID}, reason: {results}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_invalid_scopeID(core_session, setup_pe_one_command_one_rule):
    commandName, commandID, ruleID = setup_pe_one_command_one_rule
    scopeID = "abcd_xyz"
    results, isSuccess = PrivilegeElevation.get_assignments(core_session, commandID=commandID, principalType="Role",
                                                            principal="System Administrator", scope=scopeID,
                                                            scopeType="System")
    assert isSuccess and len(results['Result']) == 0, f"Get Assignments failed when invalid scopeID provided," \
                                                      f" scopeID: {scopeID}, reason: {results}"

    # Try the same for Collection
    results, isSuccess = PrivilegeElevation.get_assignments(core_session, commandID=commandID, principalType="Role",
                                                            principal="System Administrator", scope=scopeID,
                                                            scopeType="Collection")
    assert isSuccess and len(results['Result']) == 0, f"Get Assignments failed when invalid scopeID provided, " \
                                                      f"scopeID: {scopeID}, reason: {results}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_missing_scopeID(core_session, setup_pe_one_command_one_rule):
    commandName, commandID, ruleID = setup_pe_one_command_one_rule
    results, isSuccess = PrivilegeElevation.get_assignments(core_session, commandID=commandID, principalType="Role",
                                                            principal="System Administrator",
                                                            scopeType="System")
    assert not isSuccess and results['Message'] == "Parameter 'Scope' must be specified.", \
        f"Get Assignments passed when scopeID not provided for system, commandID: {commandID}, reason: {results}"

    # Try the same for Collection
    results, isSuccess = PrivilegeElevation.get_assignments(core_session, commandID=commandID, principalType="Role",
                                                            principal="System Administrator",
                                                            scopeType="System")
    assert not isSuccess and results['Message'] == "Parameter 'Scope' must be specified.", \
        f"Get Assignments passed when scopeID not provided for Collection, commandID: {commandID}, reason: {results}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_principal_principalID_provided(core_session, setup_pe_one_command_one_rule):
    commandName, commandID, ruleID = setup_pe_one_command_one_rule
    results, isSuccess = PrivilegeElevation.get_assignments(core_session, commandID=commandID, principalType="Role",
                                                            principal="System Administrator", principalID="randomStuff")
    assert not isSuccess and results['Message'] == "Cannot specify both ID and name for Principal in request", \
        f"Get Assignments passed when both principal and pricipalID passed, reason: {results}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_multiple_rules(core_session, setup_generic_pe_command_with_no_rules):
    commandName, commandID = setup_generic_pe_command_with_no_rules

    # Add first rule assignment
    rule_info1 = get_PE_ASSIGNMENTS_Data(commandID=commandID, commandName=commandName, principalType="Role",
                                         principal="System Administrator", scopeType="Global",
                                         scope=None, principalId=None, bypassChallenge=False)
    ruleID1, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                   scopeType=rule_info1['ScopeType'],
                                                                   principalType=rule_info1['PrincipalType'],
                                                                   principal=rule_info1['Principal'])
    assert isSuccess, f" Adding first rule assignment failed"
    rule_info1['ID'] = ruleID1

    # Add second rule assignment
    rule_info2 = get_PE_ASSIGNMENTS_Data(commandID=commandID, commandName=commandName, principalType="Role",
                                         principal="System Administrator", scopeType="Global",
                                         scope=None, principalId=None, bypassChallenge=True)
    ruleID2, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                   scopeType=rule_info2['ScopeType'],
                                                                   principalType=rule_info2['PrincipalType'],
                                                                   principal=rule_info2['Principal'],
                                                                   byPassChallenge=rule_info2['BypassChallenge'],
                                                                   starts=rule_info2['Starts'],
                                                                   expires=rule_info2['Expires'])
    assert isSuccess, f" Adding second rule assignment failed"
    rule_info2['ID'] = ruleID2

    # Get both assignments
    results, isSuccess = PrivilegeElevation.get_assignments(core_session, commandID=commandID, principalType="Role",
                                                            principal="System Administrator")
    assert isSuccess, f"Get Assignments for two assignments failed, reason: {results}"

    rule_info_list = [rule_info1, rule_info2]
    assert len(results['Result']) == 2 and PrivilegeElevation.check_rules_info_in_api_response(
        rule_info_list,
        results), \
        f"GetAssignments complete check failed: {ruleID1} : {ruleID2}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_power_user_has_access(core_session, setup_generic_pe_command_with_no_rules, users_and_roles):
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

    # Get User
    requester_session = users_and_roles.get_session_for_user('Privileged Access Service Power User')
    response = requester_session.get_current_session_user_info()
    user_info = response.json()['Result']
    logger.info(user_info)

    # This user inherited View permission, so should be able to see the rule
    results, isSuccess = PrivilegeElevation.get_assignments(requester_session, commandID=commandID,
                                                            principalType="Role",
                                                            principal="System Administrator")
    assert isSuccess, f"Get Assignments for PAS power user failed, reason: {results}"

    rule_info_list = [rule_info]
    assert len(results['Result']) == 1 and \
           PrivilegeElevation.check_rules_info_in_api_response(rule_info_list, results), \
        f"GetAssignments complete check failed: {ruleID}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_user_has_access(core_session, setup_generic_pe_command_with_no_rules, users_and_roles):
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

    # Get User
    requester_session = users_and_roles.get_session_for_user('Privilege Elevation Management')
    response = requester_session.get_current_session_user_info()
    user_info = response.json()['Result']
    logger.info(user_info)

    # This user inherited View permission, so should be able to see the rule
    results, isSuccess = PrivilegeElevation.get_assignments(requester_session, commandID=commandID,
                                                            principalType="Role",
                                                            principal="System Administrator")
    assert isSuccess, f"Get Assignments for PE user failed, reason: {results}"
    rule_info_list = [rule_info]
    assert len(results['Result']) == 1 and \
           PrivilegeElevation.check_rules_info_in_api_response(rule_info_list, results), \
        f"GetAssignments complete check failed: {ruleID}"


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

    # This user does not have view permission on DB, so should return no results
    results, isSuccess = PrivilegeElevation.get_assignments(requester_session, commandID=commandID,
                                                            principalType=rule_info['PrincipalType'],
                                                            principal=user_info['Name'],
                                                            scopeType=rule_info['ScopeType'],
                                                            scope=rule_info['Scope'])
    assert isSuccess and len(results['Result']) == 0, \
        f"Get Assignments for regular user on system failed, reason: {results}"

    #GetAssignment should succeed if admin does the API request
    results, isSuccess = PrivilegeElevation.get_assignments(core_session, commandID=commandID,
                                                            principalType=rule_info['PrincipalType'],
                                                            principal=user_info['Name'],
                                                            scopeType=rule_info['ScopeType'],
                                                            scope=rule_info['Scope'])
    assert isSuccess, f"Get Assignments for admin user failed, reason: {results}"
    rule_info_list = [rule_info]
    assert len(results['Result']) == 1 and \
           PrivilegeElevation.check_rules_info_in_api_response(rule_info_list, results), \
        f"GetAssignments complete check failed: {ruleID}"


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
    logger.info(result)
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

    # This user does not have view permission on DB, so should return no results
    results, isSuccess = PrivilegeElevation.get_assignments(requester_session, commandID=commandID,
                                                            principalType=rule_info['PrincipalType'],
                                                            principal=user_info['Name'],
                                                            scopeType=rule_info['ScopeType'],
                                                            scope=rule_info['Scope'])
    assert isSuccess and len(results['Result']) == 0, \
        f"Get Assignments for regular user on system failed, reason: {results}"

    #GetAssignment should succeed if admin does the API request
    results, isSuccess = PrivilegeElevation.get_assignments(core_session, commandID=commandID,
                                                            principalType=rule_info['PrincipalType'],
                                                            principal=user_info['Name'],
                                                            scopeType=rule_info['ScopeType'],
                                                            scope=rule_info['Scope'])
    assert isSuccess, f"Get Assignments for admin user failed, reason: {results}"
    rule_info_list = [rule_info]
    assert len(results['Result']) == 1 and \
           PrivilegeElevation.check_rules_info_in_api_response(rule_info_list, results), \
        f"Get Assignments complete check failed: {ruleID}"
