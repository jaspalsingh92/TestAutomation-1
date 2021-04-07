import re
import logging

import pytest

from Shared.API.infrastructure import ResourceManager
from Shared.API.privilege_elevation import PrivilegeElevation
from Shared.API.sets import SetsManager
from Shared.util import Util
from Utils.guid import guid

logger = logging.getLogger("test")

"""
1. Basic Delete test
2. Pass commandName
3. pass commandID
4. pass commandID and commandName
5. pass No parameters
6. test delete command with assignments
7. Basic delete assignment
8. DelCommand with no PE permission
9. DelCommand as nonadmin with PE permission
10.command not exists
11.assignment not exists
12.delCommand system permissions scenario
13.delCommand system set permissions scenario
14.delCommand global permissions scenario
15.delAssignment system permissions scenario
16.delAssignment system set permissions scenario
17.delAssignment global permissions scenario
18.delAssignment passes with sysadmin without MA permission on system
19.delAssignment passes with sysadmin without MA permission on system set
"""


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_delete_command_basic(core_session, setup_generic_pe_command_with_no_rules):
    logger.info("test_delete_command_basic")
    commandName, commandID = setup_generic_pe_command_with_no_rules

    # Trying to add a new Command with same name should fail
    _, isSuccess = PrivilegeElevation.add_pe_command(core_session, commandName, "*", "Windows")
    assert not isSuccess, "Creating duplicate privilege command succeeded"

    # Delete the command
    result, isSuccess = PrivilegeElevation.del_pe_command(core_session, ident=commandID)
    assert isSuccess, f"Deleting command failed: {result}"

    # Creating command with same name should now succeed
    _, isSuccess = PrivilegeElevation.add_pe_command(core_session, commandName, "*", "Linux")
    assert isSuccess, f"Creating command with same name after deleting it, failed"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_delete_command_passing_name(core_session, setup_generic_pe_command_with_no_rules):
    logger.info("test_delete_command_passing_name")
    commandName, commandID = setup_generic_pe_command_with_no_rules

    # Delete the command with name, should succeed
    result, isSuccess = PrivilegeElevation.del_pe_command(core_session, name=commandName)
    assert isSuccess, f"Deleting command with name failed: {result}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_delete_command_passing_id(core_session, setup_generic_pe_command_with_no_rules):
    logger.info("test_delete_command_passing_id")
    commandName, commandID = setup_generic_pe_command_with_no_rules

    # Delete the command with name, should succeed
    result, isSuccess = PrivilegeElevation.del_pe_command(core_session, ident=commandID)
    assert isSuccess, f"Deleting command with ID failed: {result}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_delete_command_passing_id_and_name(core_session, setup_generic_pe_command_with_no_rules):
    logger.info("test_delete_command_passing_id_and_name")
    commandName, commandID = setup_generic_pe_command_with_no_rules

    # Delete the command with name, should succeed
    result, isSuccess = PrivilegeElevation.del_pe_command(core_session, ident=commandID, name=commandName)
    assert not isSuccess, f"Deleting command with ID and name passed: {result}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_delete_command_pass_no_params(core_session):
    logger.info("test_delete_command_pass_no_params")

    # Delete the command with name, should succeed
    result, isSuccess = PrivilegeElevation.del_pe_command(core_session)
    assert not isSuccess, f"Deleting command without params passed: {result}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_delete_command_with_assignments(core_session, setup_generic_pe_command_with_no_rules):
    logger.info("test_delete_command_with_assignments")
    commandName, commandID = setup_generic_pe_command_with_no_rules

    # Add assignment
    principalType = "Role"
    principal = "System Administrator"
    scopeType = "Global"
    ruleID, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                  scopeType=scopeType,
                                                                  principalType=principalType, principal=principal)

    assert isSuccess, f" Adding rule assignment failed"

    # Make sure rule assignment is available
    results, isSuccess = PrivilegeElevation.list_pe_assignments(core_session, command=commandName)
    assert isSuccess, f"List assignments API call failed: {results}"
    logger.debug(f"List pe assignments response: {results}")
    assert PrivilegeElevation.check_rule_in_list_pe_assignments_response(ruleID, results, True), \
        f"ruleID not present in list of pe assignments response"

    # Delete the command with name, should succeed
    result, isSuccess = PrivilegeElevation.del_pe_command(core_session, name=commandName)
    assert isSuccess, f"Deleting command failed: {result}"

    # Make sure list assignment fails
    results, isSuccess = PrivilegeElevation.list_pe_assignments(core_session, command=commandName)
    assert not isSuccess, f"List assignments API call not failed after deleting associated command: {results}"
    logger.debug(f"List pe assignments response: {results}")


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_delete_assignment(core_session, setup_generic_pe_command_with_no_rules):
    logger.info("test_delete_assignment")
    commandName, commandID = setup_generic_pe_command_with_no_rules

    # Add 2 assignments
    principalType = "Role"
    principal = "System Administrator"
    scopeType = "Global"
    ruleID1, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                   scopeType=scopeType,
                                                                   principalType=principalType, principal=principal)
    assert isSuccess, f" Adding rule assignment failed"

    ruleID2, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                   scopeType=scopeType,
                                                                   principalType=principalType, principal=principal)
    assert isSuccess, f" Adding rule assignment failed"

    # Delete rule2
    result, isSuccess = PrivilegeElevation.del_pe_rule_assignment(core_session, ruleID2)
    assert isSuccess, f" Deleting rule assignment 2 failed: {result}"

    result, isSuccess = PrivilegeElevation.list_pe_assignments(core_session, command=commandName)
    assert isSuccess, f"List assignments API call failed: {result}"

    # Make sure result doesn't have rule2 but has rule1
    assert PrivilegeElevation.check_rule_in_list_pe_assignments_response(ruleID1, result, True), \
        f"ruleID1 not present in list of pe assignments response"
    assert PrivilegeElevation.check_rule_in_list_pe_assignments_response(ruleID2, result, False), \
        f"ruleID2 present in list of pe assignments response"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_del_command_with_no_pe_permission(users_and_roles, core_session, setup_generic_pe_command_with_no_rules):
    logger.info("test_pe_command_non_admin_user_with_no_pe_permission")
    requester_session = users_and_roles.get_session_for_user()

    commandName, commandID = setup_generic_pe_command_with_no_rules

    # Trying to add a new Command with same name should fail
    _, isSuccess = PrivilegeElevation.add_pe_command(core_session, commandName, "*", "Windows")
    assert not isSuccess, "Creating duplicate privilege command succeeded"

    # Delete the command as a user with no permissions should fail
    result, isSuccess = PrivilegeElevation.del_pe_command(requester_session, ident=commandID)
    assert not isSuccess, f"Deleting command as a user with no permissions passed: {result}"

    # Creating command with same name should still fail
    _, isSuccess = PrivilegeElevation.add_pe_command(core_session, commandName, "*", "Linux")
    assert not isSuccess, f"Creating command with same name passed"

    # Deleting it for cleanup
    result, isSuccess = PrivilegeElevation.del_pe_command(core_session, name=commandName)
    assert isSuccess, f"Deleting command for cleanup failed: {result}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_del_command_nonadmin_with_pe_permission(users_and_roles, core_session,
                                                    setup_generic_pe_command_with_no_rules):
    logger.info("test_pe_command_non_admin_user_with_no_pe_permission")

    commandName, commandID = setup_generic_pe_command_with_no_rules
    requester_session = users_and_roles.get_session_for_user('Privilege Elevation Management')

    # Trying to add a new Command with same name should fail
    _, isSuccess = PrivilegeElevation.add_pe_command(core_session, commandName, "*", "Windows")
    assert not isSuccess, "Creating duplicate privilege command succeeded"

    # Delete the command as a non-admin user with pe permission should succeed
    result, isSuccess = PrivilegeElevation.del_pe_command(requester_session, name=commandName)
    assert isSuccess, f"Deleting command as a non-admin user with pe permission failed: {result}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_del_command_notexists(core_session):
    commandName = "Doesn'tExist"
    result, isSuccess = PrivilegeElevation.del_pe_command(core_session, name=commandName)
    assert not isSuccess, f" Deleting a non existing pe command passed: {commandName}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_del_assignment_notexists(core_session):
    ruleID = guid()
    result, isSuccess = PrivilegeElevation.del_pe_rule_assignment(core_session, ruleID=ruleID)
    assert not isSuccess, f" Deleting a non existing pe rule assignment passed: {ruleID}"


"""
 User has "Privilege Elevation Management", the rule assignment is on
 a system where user doesn't have "Manage Assignment" permission
 Result: Command should be deleted successfully, and assignment too.
"""


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_del_command_scenario1(core_session, setup_generic_pe_command_with_no_rules, users_and_roles,
                                  create_resources):
    commandName, commandID = setup_generic_pe_command_with_no_rules
    requester_session = users_and_roles.get_session_for_user('Privilege Elevation Management')
    response = requester_session.get_current_session_user_info()
    user_info = response.json()['Result']
    logger.debug(f"del_command_scenario1 - user_info: {user_info}")

    admin_user = core_session.get_user()
    admin_user_name = admin_user.get_login_name()
    admin_user_id = admin_user.get_id()

    # Add System
    added_system_id = create_resources(core_session, 1, "Unix")[0]['ID']
    logger.debug(f"Successfully added a System: {added_system_id}")

    # Give all permissions but the manage assignments permission to admin user on this system
    permission_string = 'Grant,View,Edit,Delete,ManageSession,AgentAuth,RequestZoneRole,AddAccount,UnlockAccount,' \
                        'ManagePrivilegeElevationAssignment'
    result, success = ResourceManager.assign_system_permissions(core_session, permission_string,
                                                                admin_user_name, admin_user_id, "User",
                                                                added_system_id)
    assert success, f"Did not set system permissions {result}"

    # Add assignment
    principalType = "User"
    principal = user_info['Name']
    scopeType = "System"
    scope = added_system_id
    ruleID, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                  scopeType=scopeType, scope=scope,
                                                                  principalType=principalType, principal=principal)

    assert isSuccess, f" Adding rule assignment failed"

    # Make sure rule assignment is available
    results, isSuccess = PrivilegeElevation.list_pe_assignments(core_session, command=commandName)
    assert isSuccess, f"List assignments API call failed: {results}"
    logger.debug(f"List pe assignments response: {results}")
    assert PrivilegeElevation.check_rule_in_list_pe_assignments_response(ruleID, results, True), \
        f"ruleID not present in list of pe assignments response"

    # Deleting command should be successful, assignments too
    result, isSuccess = PrivilegeElevation.del_pe_command(requester_session, name=commandName)
    assert isSuccess, f"Deleting command as a non-admin user with pe permission failed: {result}"

    # Deleting assignment explicitly should fail
    result, isSuccess = PrivilegeElevation.del_pe_rule_assignment(requester_session, ruleID)
    assert not isSuccess, f"Deleting an already deleted assignment passed: {ruleID}"
    assert re.findall('Privilege Elevation Assignment not found', result), \
        f"Deleting an already deleted assignment failed with unknown exception: {result}"


"""
 User has "Privilege Elevation Management", the rule assignment is on
 a set where user doesn't have "Manage Assignment" permission
 Result: Command should be deleted successfully and related assignments too.
"""


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_del_command_scenario2(core_session, setup_generic_pe_command_with_no_rules, users_and_roles,
                                  create_resources, create_manual_set):
    commandName, commandID = setup_generic_pe_command_with_no_rules
    requester_session = users_and_roles.get_session_for_user('Privilege Elevation Management')
    response = requester_session.get_current_session_user_info()
    user_info = response.json()['Result']
    logger.debug(f"del_command_scenario2 user_info: {user_info}")

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

    # Give all permissions to admin user on this set
    permission_string = 'Grant,View,Edit,Delete,ManageSession,AgentAuth,RequestZoneRole,AddAccount,UnlockAccount,' \
                        'ManagePrivilegeElevationAssignment'
    result = SetsManager.set_collection_resource_permissions(core_session, permission_string,
                                                             admin_user_name, admin_user_id, set_id,
                                                             "User")
    assert result['success'], "setting collection permissions failed: " + result

    # Add assignment
    principalType = "User"
    principal = user_info['Name']
    scopeType = "Collection"
    scope = set_id
    ruleID, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                  scopeType=scopeType, scope=scope,
                                                                  principalType=principalType, principal=principal)

    assert isSuccess, f" Adding rule assignment failed"

    # Make sure rule assignment is available
    results, isSuccess = PrivilegeElevation.list_pe_assignments(core_session, command=commandName)
    assert isSuccess, f"List assignments API call failed: {results}"
    logger.debug(f"List pe assignments response: {results}")
    assert PrivilegeElevation.check_rule_in_list_pe_assignments_response(ruleID, results, True), \
        f"ruleID not present in list of pe assignments response"

    # Deleting command should be successful, assignments too
    result, isSuccess = PrivilegeElevation.del_pe_command(requester_session, name=commandName)
    assert isSuccess, f"Deleting command as a non-admin user with pe permission failed: {result}"

    # Deleting assignmnent explicitly should fail
    result, isSuccess = PrivilegeElevation.del_pe_rule_assignment(requester_session, ruleID)
    assert not isSuccess, f"Deleting an already deleted assignment passed: {ruleID}"
    assert re.findall('Privilege Elevation Assignment not found', result), \
        f"Deleting an already deleted assignment failed with unknown exception: {result}"


"""
 User has "Privilege Elevation Management", the rule assignment is global.
 Result: Command should be deleted successfully, also the assignments.
"""


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_del_command_scenario3(core_session, setup_pe_one_command_one_rule, users_and_roles):
    commandName, commandID, ruleID = setup_pe_one_command_one_rule
    requester_session = users_and_roles.get_session_for_user('Privilege Elevation Management')
    response = requester_session.get_current_session_user_info()
    user_info = response.json()['Result']
    logger.debug(f"del_command_scenario3 - user_info: {user_info}")

    # Make sure rule assignment is available
    results, isSuccess = PrivilegeElevation.list_pe_assignments(core_session, command=commandName)
    assert isSuccess, f"List assignments API call failed: {results}"
    logger.debug(f"List pe assignments response: {results}")
    assert PrivilegeElevation.check_rule_in_list_pe_assignments_response(ruleID, results, True), \
        f"ruleID not present in list of pe assignments response"

    # Deleting command should be successful, along with assignments
    result, isSuccess = PrivilegeElevation.del_pe_command(requester_session, name=commandName)
    assert isSuccess, f"Deleting command as a non-admin user with pe permission failed: {result}"

    # Deleting assignment explicitly should fail, as assignment is already deleted
    result, isSuccess = PrivilegeElevation.del_pe_rule_assignment(requester_session, ruleID)
    assert not isSuccess, f"Deleting an already deleted assignment passed: {ruleID}"
    assert re.findall('Privilege Elevation Assignment not found', result), \
        f"Deleting an already deleted assignment failed with unknown exception: {result}"


"""
 User has "Privilege Elevation Management", the rule assignment is on
 a system where user doesn't have "Manage Assignment" permission
 Result: assignment shouldn't be deleted.
"""


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_del_assignment_scenario1(core_session, setup_generic_pe_command_with_no_rules, users_and_roles,
                                     create_resources):
    commandName, commandID = setup_generic_pe_command_with_no_rules
    requester_session = users_and_roles.get_session_for_user('Privilege Elevation Management')
    response = requester_session.get_current_session_user_info()
    user_info = response.json()['Result']
    logger.debug(f"del_assignment_scenario1 user_info: {user_info}")

    admin_user = core_session.get_user()
    admin_user_name = admin_user.get_login_name()
    admin_user_id = admin_user.get_id()

    # Add System
    added_system_id = create_resources(core_session, 1, "Unix")[0]['ID']
    logger.debug(f"Successfully added a System: {added_system_id}")

    # Give all permissions but the manage assignments permission to admin user on this system
    permission_string = 'Grant,View,Edit,Delete,ManageSession,AgentAuth,RequestZoneRole,AddAccount,UnlockAccount'
    result, success = ResourceManager.assign_system_permissions(core_session, permission_string,
                                                                admin_user_name, admin_user_id, "User",
                                                                added_system_id)
    assert success, f"Did not set system permissions: {result}"

    # Add assignment
    principalType = "User"
    principal = user_info['Name']
    scopeType = "System"
    scope = added_system_id
    ruleID, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                  scopeType=scopeType, scope=scope,
                                                                  principalType=principalType, principal=principal)

    assert isSuccess, f" Adding rule assignment failed"

    # Make sure rule assignment is available
    results, isSuccess = PrivilegeElevation.list_pe_assignments(core_session, command=commandName)
    assert isSuccess, f"List assignments API call failed: {results}"
    logger.debug(f"List pe assignments response: {results}")
    assert PrivilegeElevation.check_rule_in_list_pe_assignments_response(ruleID, results, True), \
        f"ruleID not present in list of pe assignments response"

    # Deleting assignment explicitly should fail
    result, isSuccess = PrivilegeElevation.del_pe_rule_assignment(requester_session, ruleID)
    assert not isSuccess, f"Deleting rule assignment with no manage permission on system passed: {ruleID}"
    assert re.findall('unauthorized', result), \
        f"Deleting rule assignment with no manage permission on system did not fail with unauthorized exception: {ruleID}" \
        f": {result}"


"""
 User has "Privilege Elevation Management", the rule assignment is on
 a set where user doesn't have "Manage Assignment" permission
 Result: Assignment shouldn't be deleted.
"""


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_del_assignment_scenario2(core_session, setup_generic_pe_command_with_no_rules, users_and_roles,
                                     create_resources, create_manual_set):
    commandName, commandID = setup_generic_pe_command_with_no_rules
    requester_session = users_and_roles.get_session_for_user('Privilege Elevation Management')
    response = requester_session.get_current_session_user_info()
    user_info = response.json()['Result']
    logger.debug(f"del_assignment_scenario2 - user_info: {user_info}")

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

    # Give all permissions to admin user on this set
    permission_string = 'Grant,View,Edit,Delete,ManageSession,AgentAuth,RequestZoneRole,AddAccount,UnlockAccount,' \
                        'ManagePrivilegeElevationAssignment'
    result = SetsManager.set_collection_resource_permissions(core_session, permission_string,
                                                             admin_user_name, admin_user_id, set_id,
                                                             "User")
    assert result['success'], "setting collection permissions failed: " + result

    # Add assignment
    principalType = "User"
    principal = user_info['Name']
    scopeType = "Collection"
    scope = set_id
    ruleID, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                  scopeType=scopeType, scope=scope,
                                                                  principalType=principalType, principal=principal)

    assert isSuccess, f" Adding rule assignment failed"

    # Make sure rule assignment is available
    results, isSuccess = PrivilegeElevation.list_pe_assignments(core_session, command=commandName)
    assert isSuccess, f"List assignments API call failed: {results}"
    logger.debug(f"List pe assignments response: {results}")
    assert PrivilegeElevation.check_rule_in_list_pe_assignments_response(ruleID, results, True), \
        f"ruleID not present in list of pe assignments response"

    # Deleting assignmnent explicitly should fail
    result, isSuccess = PrivilegeElevation.del_pe_rule_assignment(requester_session, ruleID)
    assert not isSuccess, f"Deleting rule assignment with no manage permission on system passed: {result}"
    assert re.findall('unauthorized', result), \
        f"Deleting rule assignment with no manage permission on system did not fail with unauthorized exception: {result}"


"""
 User has "Privilege Elevation Management", the rule assignment is global.
 Result: Assignment shouldn't be deleted. Since user is not sysadmin.
"""


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_del_assignment_scenario3(core_session, setup_pe_one_command_one_rule, users_and_roles):
    commandName, commandID, ruleID = setup_pe_one_command_one_rule
    requester_session = users_and_roles.get_session_for_user('Privilege Elevation Management')
    response = requester_session.get_current_session_user_info()
    user_info = response.json()['Result']
    logger.debug(f"del_assignment_scenario3: {user_info}")

    # Make sure rule assignment is available
    results, isSuccess = PrivilegeElevation.list_pe_assignments(core_session, command=commandName)
    assert isSuccess, f"List assignments API call failed: {results}"
    logger.debug(f"List pe assignments response: {results}")
    assert PrivilegeElevation.check_rule_in_list_pe_assignments_response(ruleID, results, True), \
        f"ruleID not present in list of pe assignments response"

    # Deleting assignment explicitly should fail
    result, isSuccess = PrivilegeElevation.del_pe_rule_assignment(requester_session, ruleID)
    assert not isSuccess, f"Deleting rule assignment with no manage permission on system passed: {ruleID}"
    assert re.findall('unauthorized', result), \
        f"Deleting rule assignment with no manage permission on system did not fail with unauthorized exception: {ruleID}"


"""
1. Add a command
2. Add a system
3. Assign a rule for this system
4. Make sure assignment is listed
5. Delete the System
6. Make sure assignment is deleted too.
"""


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_del_assignment_on_system_delete(core_session, setup_generic_pe_command_with_no_rules, create_resources):
    commandName, commandID = setup_generic_pe_command_with_no_rules

    admin_user = core_session.get_user()
    admin_user_name = admin_user.get_login_name()
    admin_user_id = admin_user.get_id()

    # Add System
    added_system_id = create_resources(core_session, 1, "Unix")[0]['ID']
    logger.debug(f"Successfully added a System: {added_system_id}")

    # Give all permissions but the manager assignments permission to admin user on this system
    permission_string = 'Grant,View,Edit,Delete,ManageSession,AgentAuth,RequestZoneRole,AddAccount,UnlockAccount,' \
                        'ManagePrivilegeElevationAssignment'
    result, success = ResourceManager.assign_system_permissions(core_session, permission_string,
                                                                admin_user_name, admin_user_id, "User",
                                                                added_system_id)
    assert success, "Did not set system permissions " + result

    # Add assignment
    principalType = "User"
    principal = admin_user_name
    scopeType = "System"
    scope = added_system_id
    ruleID, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                  scopeType=scopeType, scope=scope,
                                                                  principalType=principalType, principal=principal)

    assert isSuccess, f" Adding rule assignment failed"

    # Make sure rule assignment is available
    results, isSuccess = PrivilegeElevation.list_pe_assignments(core_session, command=commandName)
    assert isSuccess and len(results['Result']) == 1, f"List assignments API call failed: {results}"
    logger.debug(results)

    # Delete System
    result, isSuccess = ResourceManager.del_system(core_session, added_system_id)
    assert isSuccess, f"deleting System failed: {result}"

    # Make sure rule assignment is not available anymore
    results, isSuccess = PrivilegeElevation.list_pe_assignments(core_session, command=commandName)
    assert isSuccess and len(results['Result']) == 0, f"List assignments API call failed: {results}"
    logger.info(results)


"""
1. Add a command
2. Add a system
3. Add a set and add system from #2
3. Assign a rule for this set
4. Make sure assignment is listed
5. Delete the set
6. Make sure assignment is deleted too.
"""


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_del_assignment_on_set_delete(core_session, setup_generic_pe_command_with_no_rules, create_resources):
    commandName, commandID = setup_generic_pe_command_with_no_rules

    admin_user = core_session.get_user()
    admin_user_name = admin_user.get_login_name()
    admin_user_id = admin_user.get_id()

    # Add System
    added_system_id = create_resources(core_session, 1, "Unix")[0]['ID']
    logger.debug(f"Successfully added a System: {added_system_id}")

    # Create Set and the system to this set
    set_name = "set_" + Util.random_string()
    is_create, set_id = SetsManager.create_manual_collection(
        core_session, set_name, "Server", object_ids=[added_system_id])

    assert is_create, f"Successfully created a set and added system to that set: {set_id}"

    # Give all permissions to admin user on this set
    permission_string = 'Grant,View,Edit,Delete,ManageSession,AgentAuth,RequestZoneRole,AddAccount,UnlockAccount,' \
                        'ManagePrivilegeElevationAssignment'
    result = SetsManager.set_collection_resource_permissions(core_session, permission_string,
                                                             admin_user_name, admin_user_id, set_id,
                                                             "User")
    logger.info(result)
    assert result['success'], "setting collection permissions failed: " + result

    # Add assignment
    principalType = "User"
    principal = admin_user_name
    scopeType = "Collection"
    scope = set_id
    ruleID, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                  scopeType=scopeType, scope=scope,
                                                                  principalType=principalType, principal=principal)

    assert isSuccess, f" Adding rule assignment failed"

    # Make sure rule assignment is available
    results, isSuccess = PrivilegeElevation.list_pe_assignments(core_session, command=commandName)
    assert isSuccess and len(results['Result']) == 1, f"List assignments API call failed: {results}"
    logger.info(results)

    # Delete Set
    isSuccess, results = SetsManager.delete_collection(core_session, set_id)
    assert isSuccess, f"Deleting set failed: {results}"

    # Make sure rule assignment is not available
    results, isSuccess = PrivilegeElevation.list_pe_assignments(core_session, command=commandName)
    assert isSuccess and len(results['Result']) == 0, f"List assignments API call failed: {results}"
    logger.info(results)


@pytest.mark.api
@pytest.mark.cclient_privelevation
@pytest.mark.parametrize('operating_system', ["Unix", "Windows"])
def test_delete_assignment_sysadmin_without_ma_permission_on_system(core_session, create_resources,
                                                                    setup_generic_pe_command_with_no_rules,
                                                                    operating_system):
    commandName, commandID = setup_generic_pe_command_with_no_rules
    admin_user = core_session.get_user()
    admin_user_name = admin_user.get_login_name()
    admin_user_id = admin_user.get_id()

    # Add System
    added_system_id = create_resources(core_session, 1, operating_system)[0]['ID']
    logger.info(f"Successfully added a System: {added_system_id}")

    # Give all permissions but MA to the admin
    permission_string = 'Grant,View,Edit,Delete,ManageSession,AgentAuth,RequestZoneRole,AddAccount,UnlockAccount'
    result, success = ResourceManager.assign_system_permissions(core_session, permission_string,
                                                                admin_user_name, admin_user_id, "User",
                                                                added_system_id)
    assert success, f"Unable to set system permissions for admin: {result}"

    # Add assignment
    principalType = "User"
    principal = admin_user_name
    scopeType = "System"
    scope = added_system_id
    ruleID, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                  scopeType=scopeType, scope=scope,
                                                                  principalType=principalType, principal=principal)

    assert isSuccess, f" Adding rule assignment failed"

    # Make sure rule assignment is available
    results, isSuccess = PrivilegeElevation.list_pe_assignments(core_session, command=commandName)
    assert isSuccess and len(results['Result']) == 1, f"List assignments API call failed: {results}"

    # Deleting assignment explicitly should pass
    result, isSuccess = PrivilegeElevation.del_pe_rule_assignment(core_session, ruleID)
    assert isSuccess, f"Deleting rule assignment with no manage permission on system as sysadmin failed: {ruleID}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_delete_assignment_sysadmin_without_ma_permission_on_system_set(core_session, create_manual_set,
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
    logger.info(result)
    assert result['success'], "assigning collection permissions on the set for the user, failed: " + result

    # Give all permissions but MA to the admin on the ResourceSet
    permission_string = 'Grant,View,Edit,Delete,ManageSession,AgentAuth,RequestZoneRole,AddAccount,UnlockAccount'
    result = SetsManager.set_collection_resource_permissions(core_session, permission_string,
                                                             admin_user_name, admin_user_id, set_id)
    assert result['success'], "assigning collection permissions on the resource set for the user failed: " + result

    # Add assignment
    principalType = "User"
    principal = admin_user_name
    scopeType = "Collection"
    scope = set_id
    ruleID, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                  scopeType=scopeType, scope=scope,
                                                                  principalType=principalType, principal=principal)

    assert isSuccess, f" Adding rule assignment failed"

    # Make sure rule assignment is available
    results, isSuccess = PrivilegeElevation.list_pe_assignments(core_session, command=commandName)
    assert isSuccess and len(results['Result']) == 1, f"List assignments API call failed: {results}"

    # Deleting assignment explicitly should pass
    result, isSuccess = PrivilegeElevation.del_pe_rule_assignment(core_session, ruleID)
    assert isSuccess, f"Deleting rule assignment with no manage permission on system as sysadmin failed: {ruleID}"
