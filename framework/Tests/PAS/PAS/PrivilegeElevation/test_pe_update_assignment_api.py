import logging
import datetime
import re

import pytest

from Shared.API.agent import get_PE_ASSIGNMENTS_Data
from Shared.API.infrastructure import ResourceManager
from Shared.API.privilege_elevation import PrivilegeElevation
from Shared.API.sets import SetsManager
from Shared.util import Util
from Utils.guid import guid

"""
UpdateAssignment
1. NormalCase, everything works
2. ruleID not provided, should fail
3. invalid ruleID, should fail
4. invalid bypassChallenge, should fail
4. No update parameters passed, should fail
5. Only BypassChallenge passed, should pass
6. starts and expires are invalid, should fail
7. Global: if sysadmin passes, if not fails
8. System: has MA permission on system passes, if not fails
9. Collection: has MA and "Edit" on collection then pass, if not fails
10. Sysadmin without MA permission passes on system
11. Sysadmin without MA permission passes on system set
"""

logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_normal_case(core_session, setup_generic_pe_command_with_no_rules):
    commandName, commandID = setup_generic_pe_command_with_no_rules

    rule_info = get_PE_ASSIGNMENTS_Data(commandID=commandID, commandName=commandName, principalType="Role",
                                        principal="System Administrator", scopeType="Global",
                                        scope=None, principalId=None, bypassChallenge=False)
    ruleID, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                  scopeType=rule_info['ScopeType'],
                                                                  principalType=rule_info['PrincipalType'],
                                                                  principal=rule_info['Principal'])
    assert isSuccess, f" Adding rule assignment  failed"
    rule_info['ID'] = ruleID
    starts = datetime.datetime.now().replace(microsecond=0).isoformat() + "Z"
    expires = (datetime.datetime.now() + datetime.timedelta(minutes=10)).replace(microsecond=0).isoformat() + "Z"
    rule_info['Starts'] = starts
    rule_info['Expires'] = expires
    rule_info['BypassChallenge'] = True

    results, isSuccess = PrivilegeElevation.update_pe_assignment(core_session, ruleID=ruleID, bypassChallenge=True,
                                                                 starts=starts,
                                                                 expires=expires)
    assert isSuccess, f"Update Assignment failed for ruleID: {ruleID}, reason: {results}"

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
def test_ruleID_not_provided(core_session):
    results, isSuccess = PrivilegeElevation.update_pe_assignment(core_session, bypassChallenge=False)
    assert not isSuccess and results['Message'] == "Parameter 'ID' must be specified.", \
        f"Update Assignment passed without ruleID, reason: {results}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_invalid_ruleID(core_session):
    ruleID = "abc_xyz"
    results, isSuccess = PrivilegeElevation.update_pe_assignment(core_session, ruleID=ruleID, bypassChallenge=False)
    assert not isSuccess and results['Message'] == "Privilege Elevation Assignment not found.", \
        f"Update Assignment passed with invalid ruleID: {ruleID}, reason: {results}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_invalid_bypassChallenge(core_session, setup_pe_one_command_one_rule):
    commandName, commandID, ruleID = setup_pe_one_command_one_rule
    results, isSuccess = PrivilegeElevation.update_pe_assignment(core_session, ruleID=ruleID, bypassChallenge="xyz")
    assert not isSuccess and results['Message'] == "String was not recognized as a valid Boolean.", \
        f"Update Assignment passed with invalid bypassChallenge: {ruleID}, reason: {results}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_no_params_provided(core_session, setup_pe_one_command_one_rule):
    commandName, commandID, ruleID = setup_pe_one_command_one_rule
    results, isSuccess = PrivilegeElevation.update_pe_assignment(core_session, ruleID=ruleID)
    assert not isSuccess and results['Message'] == "Parameter 'BypassChallenge/Starts/Expires' must be specified.", \
        f"Update Assignment passed when no params provided for ruleID: {ruleID}, reason: {results}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_no_bypassChallenge(core_session, setup_generic_pe_command_with_no_rules, users_and_roles):
    commandName, commandID = setup_generic_pe_command_with_no_rules

    rule_info = get_PE_ASSIGNMENTS_Data(commandID=commandID, commandName=commandName, principalType="Role",
                                        principal="System Administrator", scopeType="Global",
                                        scope=None, principalId=None, bypassChallenge=False)
    ruleID, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                  scopeType=rule_info['ScopeType'],
                                                                  principalType=rule_info['PrincipalType'],
                                                                  principal=rule_info['Principal'])
    assert isSuccess, f" Adding rule assignment  failed"
    rule_info['ID'] = ruleID

    # updated rules
    starts = datetime.datetime.now().replace(microsecond=0).isoformat() + "Z"
    expires = (datetime.datetime.now() + datetime.timedelta(minutes=10)).replace(microsecond=0).isoformat() + "Z"
    rule_info['Starts'] = starts
    rule_info['Expires'] = expires

    # With sysadmin should pass
    results, isSuccess = PrivilegeElevation.update_pe_assignment(core_session, ruleID=ruleID, starts=rule_info['Starts']
                                                                 , expires=rule_info['Expires'])
    assert isSuccess, f"Update Assignment for sysadmin user failed for Global rule, reason: {results}"

    # Make sure rules are actually updated
    results, isSuccess = PrivilegeElevation.list_pe_assignments(core_session, commandID=commandID)
    assert isSuccess, f"List Assignments for PAS power user failed, reason: {results}"

    rule_info_list = [rule_info]
    assert len(results['Result']) == 1 and PrivilegeElevation.check_rules_info_in_api_response(
        rule_info_list,
        results), \
        f"List Assignments complete check failed: {ruleID}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_only_bypassChallenge_passed(core_session, setup_pe_one_command_one_rule):
    commandName, commandID, ruleID = setup_pe_one_command_one_rule
    results, isSuccess = PrivilegeElevation.update_pe_assignment(core_session, ruleID=ruleID, bypassChallenge=False)
    assert isSuccess, f"Update Assignment failed when only bypassChallenge provided, ruleID: {ruleID}, " \
                      f"reason: {results}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_invalid_starts_expires(core_session, setup_pe_one_command_one_rule):
    commandName, commandID, ruleID = setup_pe_one_command_one_rule
    results, isSuccess = PrivilegeElevation.update_pe_assignment(core_session, ruleID=ruleID, starts="abc_xyz",
                                                                 expires="abc_xyz")
    assert not isSuccess and re.findall("The string was not recognized as a valid DateTime.", results['Message']), \
        f"Update Assignment passed when invalid starts/expires provided, ruleID: {ruleID}, reason: {results}"

    timeNow = datetime.datetime.now().replace(microsecond=0).isoformat() + "Z"
    results, isSuccess = PrivilegeElevation.update_pe_assignment(core_session, ruleID=ruleID,
                                                                 starts=timeNow)
    assert not isSuccess and results['Message'] == "Parameter 'Starts/Expires' must be specified.", \
        f"Update Assignment passed when only starts provided, ruleID: {ruleID}, reason: {results}"

    results, isSuccess = PrivilegeElevation.update_pe_assignment(core_session, ruleID=ruleID,
                                                                 expires=timeNow)
    assert not isSuccess and results['Message'] == "Parameter 'Starts/Expires' must be specified.", \
        f"Update Assignment passed when only expires provided, ruleID: {ruleID}, reason: {results}"

    starts = datetime.datetime.now().replace(microsecond=0).isoformat() + "Z"
    expires = (datetime.datetime.now() - datetime.timedelta(minutes=10)).replace(microsecond=0).isoformat() + "Z"

    results, isSuccess = PrivilegeElevation.update_pe_assignment(core_session, ruleID=ruleID, bypassChallenge=False,
                                                                 starts=starts,
                                                                 expires=expires)
    assert not isSuccess and results['Message'] == "Parameter 'Starts/Expires' is invalid.", \
        f"Update Assignment passed when invalid starts/expires provided, ruleID: {ruleID}, reason: {results}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_global_scenario(core_session, setup_generic_pe_command_with_no_rules, users_and_roles):
    commandName, commandID = setup_generic_pe_command_with_no_rules

    rule_info = get_PE_ASSIGNMENTS_Data(commandID=commandID, commandName=commandName, principalType="Role",
                                        principal="System Administrator", scopeType="Global",
                                        scope=None, principalId=None, bypassChallenge=False)
    ruleID, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                  scopeType=rule_info['ScopeType'],
                                                                  principalType=rule_info['PrincipalType'],
                                                                  principal=rule_info['Principal'])
    assert isSuccess, f" Adding rule assignment  failed"
    rule_info['ID'] = ruleID

    # Get User
    requester_session = users_and_roles.get_session_for_user('Privileged Access Service Power User')

    rule_info['BypassChallenge'] = True
    # Since not sys admin should fail
    results, isSuccess = PrivilegeElevation.update_pe_assignment(requester_session, ruleID=ruleID,
                                                                 bypassChallenge=True)
    assert not isSuccess, f"Update Assignment for PAS power user passed for Global rule, reason: {results}"

    # With sysadmin should pass
    results, isSuccess = PrivilegeElevation.update_pe_assignment(core_session, ruleID=ruleID, bypassChallenge=True)
    assert isSuccess, f"Update Assignment for sysadmin user failed for Global rule, reason: {results}"

    # Make sure rules are actually updated
    results, isSuccess = PrivilegeElevation.list_pe_assignments(core_session, commandID=commandID)
    assert isSuccess, f"List Assignments for PAS power user failed, reason: {results}"

    rule_info_list = [rule_info]
    assert len(results['Result']) == 1 and PrivilegeElevation.check_rules_info_in_api_response(
        rule_info_list,
        results), \
        f"List Assignments complete check failed: {ruleID}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_system_scenario(core_session, setup_generic_pe_command_with_no_rules,
                         users_and_roles, create_resources):
    commandName, commandID = setup_generic_pe_command_with_no_rules

    admin_user = core_session.get_user()
    admin_user_name = admin_user.get_login_name()
    admin_user_id = admin_user.get_id()

    # Get User
    requester_session = users_and_roles.get_session_for_user('Privilege Elevation Management')
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

    # Give all permission but the ManageAssignment permission to the PE User
    permission_string = 'Grant,View,Edit,Delete,ManageSession,AgentAuth,RequestZoneRole,AddAccount,UnlockAccount'
    result, success = ResourceManager.assign_system_permissions(core_session, permission_string,
                                                                user_info['Name'], user_info['Id'], "User",
                                                                added_system_id)
    assert success, f"Did not set PE user system permissions: {result}"

    # Add assignment
    rule_info = get_PE_ASSIGNMENTS_Data(commandID=commandID, commandName=commandName, principalType="User",
                                        principal=admin_user_name, scopeType="System",
                                        scope=added_system_id, principalId=None, bypassChallenge=False)

    ruleID, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                  scopeType=rule_info['ScopeType'],
                                                                  scope=rule_info['Scope'],
                                                                  principalType=rule_info['PrincipalType'],
                                                                  principal=rule_info['Principal'],
                                                                  byPassChallenge=False)

    assert isSuccess, f" Adding rule assignment failed"
    rule_info['ID'] = ruleID

    # This user does not have ManageAssignment permission, so should fail
    results, isSuccess = PrivilegeElevation.update_pe_assignment(requester_session, ruleID=ruleID,
                                                                 bypassChallenge=False)
    assert not isSuccess, f"Update Assignment for PE user with no MA permissions on a " \
                          f"system passed, reason: {results}"

    # Add MA permission to the user on the system
    permission_string = 'Grant,View,Edit,Delete,ManageSession,AgentAuth,RequestZoneRole,AddAccount,UnlockAccount,' \
                        'ManagePrivilegeElevationAssignment'
    result, success = ResourceManager.assign_system_permissions(core_session, permission_string,
                                                                user_info['Name'], user_info['Id'], "User",
                                                                added_system_id)
    assert success, f"Did not set PE user system permissions: {result}"

    # Should pass now
    results, isSuccess = PrivilegeElevation.update_pe_assignment(requester_session, ruleID=ruleID,
                                                                 bypassChallenge=False)
    assert isSuccess, f"Update Assignment for PE user with MA permissions on a " \
                      f"system failed, reason: {results}"

    # Make sure rules are actually updated
    results, isSuccess = PrivilegeElevation.list_pe_assignments(core_session, commandID=commandID)
    assert isSuccess, f"List Assignments for PAS power user failed, reason: {results}"

    rule_info_list = [rule_info]
    assert len(results['Result']) == 1 and PrivilegeElevation.check_rules_info_in_api_response(
        rule_info_list,
        results), \
        f"List Assignments complete check failed: {ruleID}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_collection_scenario(core_session, users_and_roles, create_resources, create_manual_set,
                             setup_generic_pe_command_with_no_rules):
    commandName, commandID = setup_generic_pe_command_with_no_rules

    admin_user = core_session.get_user()
    admin_user_name = admin_user.get_login_name()
    admin_user_id = admin_user.get_id()

    # Get User
    requester_session = users_and_roles.get_session_for_user('Privileged Access Service Power User')
    response = requester_session.get_current_session_user_info()
    user_info = response.json()['Result']

    # Add System
    added_system_id = create_resources(core_session, 1, "Unix")[0]['ID']
    logger.debug(f"Successfully added a System: {added_system_id}")

    # Create Set and the system to this set
    set_id = create_manual_set(
        core_session, "Server", object_ids=[added_system_id])['ID']

    logger.debug(f"Successfully created a set and added system to that set: {set_id}")

    # Give all permissions to the admin on the set
    permission_string = 'Grant,View,Edit,Delete'
    result = SetsManager.set_collection_permissions(core_session, permission_string,
                                                    admin_user_name, admin_user_id, set_id)
    assert result['success'], "setting admin collection permissions on the set failed: " + result

    # Give all permissions to the admin on the ResourceSet
    permission_string = 'Grant,View,Edit,Delete,ManageSession,AgentAuth,RequestZoneRole,AddAccount,UnlockAccount,' \
                        'ManagePrivilegeElevationAssignment'
    result = SetsManager.set_collection_resource_permissions(core_session, permission_string,
                                                             admin_user_name, admin_user_id, set_id)
    assert result['success'], "setting admin collection permissions on the resourceSet failed: " + result

    # Give all permission for the user on the set
    permission_string = 'Grant,View,Edit,Delete'
    result = SetsManager.set_collection_permissions(core_session, permission_string,
                                                    user_info['Name'], user_info['Id'], set_id)
    assert result['success'], "setting PAS power user collection permissions on the set failed: " + result

    # Give all permission but the MA permission to the PAS user on the resource Set
    permission_string = 'Grant,View,Edit,Delete,ManageSession,AgentAuth,RequestZoneRole,AddAccount,UnlockAccount'
    result = SetsManager.set_collection_resource_permissions(core_session, permission_string,
                                                             user_info['Name'], user_info['Id'], set_id)
    assert result['success'], "setting PAS power user collection permissions on the resourceSet failed: " + result

    # Add assignment
    rule_info = get_PE_ASSIGNMENTS_Data(commandID=commandID, commandName=commandName, principalType="User",
                                        principal=user_info['Name'], scopeType="Collection",
                                        scope=set_id, principalId=None, bypassChallenge=False)
    ruleID, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                  scopeType=rule_info['ScopeType'],
                                                                  scope=rule_info['Scope'],
                                                                  principalType=rule_info['PrincipalType'],
                                                                  principal=rule_info['Principal'],
                                                                  byPassChallenge=False)
    assert isSuccess, f" Adding rule assignment failed"
    rule_info['ID'] = ruleID

    # This user does not have MA permission, so should fail
    results, isSuccess = PrivilegeElevation.update_pe_assignment(requester_session, ruleID=ruleID,
                                                                 bypassChallenge=False)
    assert not isSuccess and results['Message'] == "Attempted to perform an unauthorized operation.", \
        f"UpdateAssignment for PAS power user with no MA permissions on a set passed, reason: {results}"

    # Now assign MA permission but not Edit permission to the user
    permission_string = 'Grant,View,Delete'
    result = SetsManager.set_collection_permissions(core_session, permission_string,
                                                    user_info['Name'], user_info['Id'], set_id)
    assert result['success'], "setting PAS power user collection permissions failed: " + result

    # This user does not have Edit permission, so should fail
    results, isSuccess = PrivilegeElevation.update_pe_assignment(requester_session, ruleID=ruleID,
                                                                 bypassChallenge=False)
    assert not isSuccess and results['Message'] == "Attempted to perform an unauthorized operation.", \
        f"UpdateAssignment for PAS power user with no Edit permissions on a set passed, reason: {results}"

    # Now assign MA permission and Edit permission to the user
    permission_string = 'Grant,View,Edit,Delete,ManageSession,AgentAuth,RequestZoneRole,AddAccount,UnlockAccount,' \
                        'ManagePrivilegeElevationAssignment'
    result = SetsManager.set_collection_resource_permissions(core_session, permission_string,
                                                             user_info['Name'], user_info['Id'], set_id,
                                                             "User")
    assert result['success'], "setting PAS power user collection permissions failed: " + result

    permission_string = 'Grant,View,Edit,Delete'
    result = SetsManager.set_collection_permissions(core_session, permission_string,
                                                    user_info['Name'], user_info['Id'], set_id)
    assert result['success'], "setting PAS power user collection permissions failed: " + result

    # updated rules
    starts = datetime.datetime.now().replace(microsecond=0).isoformat() + "Z"
    expires = (datetime.datetime.now() + datetime.timedelta(minutes=10)).replace(microsecond=0).isoformat() + "Z"
    rule_info['Starts'] = starts
    rule_info['Expires'] = expires
    rule_info['BypassChallenge'] = True

    # This user has Edit and MA permissions on the set, should pass
    results, isSuccess = PrivilegeElevation.update_pe_assignment(requester_session, ruleID=ruleID,
                                                                 bypassChallenge=rule_info['BypassChallenge'],
                                                                 starts=rule_info['Starts'],
                                                                 expires=rule_info['Expires'])
    assert isSuccess, f"UpdateAssignment for PAS power user with Edit and MA permissions on " \
                      f"a set failed, reason: {results}"

    # Make sure rules are actually updated
    results, isSuccess = PrivilegeElevation.list_pe_assignments(core_session, commandID=commandID)
    assert isSuccess, f"List Assignments for PAS power user failed, reason: {results}"

    rule_info_list = [rule_info]
    assert len(results['Result']) == 1 and PrivilegeElevation.check_rules_info_in_api_response(
        rule_info_list,
        results), \
        f"List Assignments complete check failed: {ruleID}"

    # Update rules
    rule_info['BypassChallenge'] = False

    # This sysadmin user does have MA permission, so should pass
    results, isSuccess = PrivilegeElevation.update_pe_assignment(core_session, ruleID=ruleID, bypassChallenge=False)
    assert isSuccess, f"UpdateAssignment for sys admin user with MA permissions on " \
                      f"a set failed, reason: {results}"

    # Make sure rules are actually updated
    results, isSuccess = PrivilegeElevation.list_pe_assignments(core_session, commandID=commandID)
    assert isSuccess, f"List Assignments for PAS power user failed, reason: {results}"

    rule_info_list = [rule_info]
    assert len(results['Result']) == 1 and PrivilegeElevation.check_rules_info_in_api_response(
        rule_info_list,
        results), \
        f"List Assignments complete check failed: {ruleID}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_update_assignment_sysadmin_without_ma_permission_on_system(core_session, create_resources,
                                                                    setup_generic_pe_command_with_no_rules):
    commandName, commandID = setup_generic_pe_command_with_no_rules
    admin_user = core_session.get_user()
    admin_user_name = admin_user.get_login_name()
    admin_user_id = admin_user.get_id()

    # Add System
    added_system_id = create_resources(core_session, 1, "Unix")[0]['ID']
    logger.info(f"Successfully added a System: {added_system_id}")

    # Give all permissions but MA to the admin
    permission_string = 'Grant,View,Edit,Delete,ManageSession,AgentAuth,RequestZoneRole,AddAccount,UnlockAccount'
    result, success = ResourceManager.assign_system_permissions(core_session, permission_string,
                                                                admin_user_name, admin_user_id, "User",
                                                                added_system_id)
    assert success, f"Unable to set system permissions for admin: {result}"

    # Add assignment
    rule_info = get_PE_ASSIGNMENTS_Data(commandID=commandID, commandName=commandName, principalType="User",
                                        principal=admin_user_name, scopeType="System",
                                        scope=added_system_id, principalId=None, bypassChallenge=False)

    ruleID, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                  scopeType=rule_info['ScopeType'],
                                                                  scope=rule_info['Scope'],
                                                                  principalType=rule_info['PrincipalType'],
                                                                  principal=rule_info['Principal'],
                                                                  byPassChallenge=False)

    assert isSuccess, f" Adding rule assignment failed"
    rule_info['ID'] = ruleID

    # Update rules
    rule_info['BypassChallenge'] = True

    # This sysadmin user doesn't have MA permission, should still pass
    results, isSuccess = PrivilegeElevation.update_pe_assignment(core_session, ruleID=ruleID, bypassChallenge=True)
    assert isSuccess, f"UpdateAssignment for sys admin user with MA permissions on " \
                      f"a set failed, reason: {results}"

    # Make sure assignments are actually updated
    results, isSuccess = PrivilegeElevation.list_pe_assignments(core_session, commandID=commandID)
    assert isSuccess, f"List Assignments for sysadmin user failed, reason: {results}"

    rule_info_list = [rule_info]
    assert len(results['Result']) == 1 and PrivilegeElevation.check_rules_info_in_api_response(
        rule_info_list,
        results), \
        f"List Assignments complete check failed: {ruleID}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_update_assignment_sysadmin_without_ma_permission_on_system_set(core_session, create_manual_set,
                                                                        setup_generic_pe_command_with_no_rules):
    commandName, commandID = setup_generic_pe_command_with_no_rules
    admin_user = core_session.get_user()
    admin_user_name = admin_user.get_login_name()
    admin_user_id = admin_user.get_id()

    # Create Set and the system to this set
    set_id = create_manual_set(
        core_session, "Server")['ID']

    logger.info(f"Successfully created a set and added system to that set: {set_id}")

    # Give all permissions to the admin on the set
    permission_string = 'Grant,View,Edit,Delete'
    result = SetsManager.set_collection_permissions(core_session, permission_string,
                                                    admin_user_name, admin_user_id, set_id)
    assert result['success'], "assigning collection permissions on the set for the user, failed: " + result

    # Give all permissions but MA to the admin on the ResourceSet
    permission_string = 'Grant,View,Edit,Delete,ManageSession,AgentAuth,RequestZoneRole,AddAccount,UnlockAccount'
    result = SetsManager.set_collection_resource_permissions(core_session, permission_string,
                                                             admin_user_name, admin_user_id, set_id)
    assert result['success'], "assigning collection permissions on the resource set for the user failed: " + result

    # Add assignment
    rule_info = get_PE_ASSIGNMENTS_Data(commandID=commandID, commandName=commandName, principalType="User",
                                        principal=admin_user_name, scopeType="Collection",
                                        scope=set_id, principalId=None, bypassChallenge=False)

    ruleID, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                  scopeType=rule_info['ScopeType'],
                                                                  scope=rule_info['Scope'],
                                                                  principalType=rule_info['PrincipalType'],
                                                                  principal=rule_info['Principal'],
                                                                  byPassChallenge=False)

    assert isSuccess, f" Adding rule assignment failed"
    rule_info['ID'] = ruleID

    # Update rules
    rule_info['BypassChallenge'] = True

    # This sysadmin user doesn't have MA permission, should still pass
    results, isSuccess = PrivilegeElevation.update_pe_assignment(core_session, ruleID=ruleID, bypassChallenge=True)
    assert isSuccess, f"UpdateAssignment for sys admin user with MA permissions on " \
                      f"a set failed, reason: {results}"

    # Make sure assignments are actually updated
    results, isSuccess = PrivilegeElevation.list_pe_assignments(core_session, commandID=commandID)
    assert isSuccess, f"List Assignments for sysadmin user failed, reason: {results}"

    rule_info_list = [rule_info]
    assert len(results['Result']) == 1 and PrivilegeElevation.check_rules_info_in_api_response(
        rule_info_list,
        results), \
        f"List Assignments complete check failed: {ruleID}"