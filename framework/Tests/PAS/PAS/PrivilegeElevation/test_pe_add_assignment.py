import datetime
import pytest
import logging
from Shared.endpoint_manager import EndPoints
from Shared.API.infrastructure import ResourceManager
from Shared.API.sets import SetsManager
from Shared.util import Util
from Shared.API.agent import *
from Shared.API.privilege_elevation import PrivilegeElevation
from Utils.guid import guid

logger = logging.getLogger("test")
"""
Tests:
1. Test for all valid params with Global scope, principal as normal user id added by sysadmin user
2. Test for all valid params with Global scope, principal as normal user name added by sysadmin user
3. Test for all valid params with Global scope, principal as role id added by sysadmin user
4. Test for all valid params with Global scope, principal as normal user name added by sysadmin user
5. Test for all valid params with Global scope, principal as adgroup id added by sysadmin user
6. Test for all valid params with Global scope, principal as adgroup name added by sysadmin user
7. Test for all valid params with System scope, principal as normal user added by sysadmin user
8. Test for all valid params with Collection scope, principal as normal user added by sysadmin user
9. Test for all valid params with System scope, principal as role added by sysadmin user
10. Test for all valid params with Collection scope, principal as role added by sysadmin user
11. Test for all valid params with System scope, principal as adgroup name added by sysadmin user
12. Test for all valid params with Collection scope, principal as adgroup name added by sysadmin user
13. Test for all valid params with Collection scope, principal as adgroup name added by non sysadmin user
14. Test for all valid params with Collection scope, principal as adgroup name added by non sysadmin role
15. Test for all valid params with Global scope, principal as normal name, bypass challenge as true added by sysadmin user
16. Test for all valid params with Global scope, principal as normal user id, valid starts and expires added by sysadmin user
17. Test for all required params except PrivilegeElevationCommand
18. Test for all required params except scopetype
19. Test for all required params except scope
20. Test for all required params except principaltype
21. Test for all required params except principal or principalId
22. Test for all valid params except PrivilegeElevationCommand doesn't exist
23. Test for all valid params except invalid ScopeType
24. Test for all valid params except system doesn't exist
25. Test for all valid params except set doesn't exist
26. Test for all valid params except PrincipalType
27. Test for all valid params except principal user doesn't exist
28. Test for all valid params except principal role doesn't exist
29. Test for all valid params except principal userid doesn't exist
30. Test for all valid params except principal roleid doesn't exist
31. Test for all valid params except bypass challenge invalid type
32. Test for all valid params except starts invalid time
33. Test for all valid params except expires invalid time
34. Test for principal as role and scope as system and the user (not sysadmin) has no Manage Assignment permission on the system
35. Test for principal as ad group and scope as system and the user has no Manage Assignment permission on the system
36. All tests related to Invalid starts/Expires
37. Sysadmin without MA permission on system should pass
38. Sysadmin without MA permission on system set should pass
39. Test for all valid params and, principal as user and scope as set
40. Test for dynamic set is not allowed
41. Test for all valid params with Collection scope, principal as adgroup name added by non sysadmin user with no edit permission on set
42. Test for all valid params with Collection scope, principal as adgroup name added by non sysadmin user with no Manage Assignment permission on set
43. Test for all valid params with Collection scope, principal as adgroup name added by non sysadmin role with no edit permission on set
44. Test for all valid params with Collection scope, principal as adgroup name added by non sysadmin role with no Manage Assignment permission on set
"""

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_add_assignment_user_id(core_session, users_and_roles, setup_generic_pe_command_with_no_rules_all_OS):
    """
    Test case: Test for all valid params with Global scope, principal as normal user id added by sysadmin user
    """

    session = core_session
    userobj = users_and_roles.populate_user({'Name': 'user1'})
    _, cmdId = setup_generic_pe_command_with_no_rules_all_OS

    asmntId, isSuccess = PrivilegeElevation.add_pe_rule_assignment(session, cmdId, principalType="User", principalID=userobj.get_id(), scopeType="Global", scope="Global", byPassChallenge=False)
    
    assert isSuccess is True, f'PrivilegeElevation add assignment has failed'

    #clean up
    errMsg, isSuccess = PrivilegeElevation.del_pe_rule_assignment(session, asmntId)
    assert isSuccess is True, f'PrivilegeElevation add assignment failed to clean up {errMsg}'
    

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_add_assignment_user_name(core_session, users_and_roles, setup_generic_pe_command_with_no_rules_all_OS):
    """
    Test case: Test for all valid params with Global scope, principal as normal user id added by sysadmin user
    """

    session = core_session
    userobj = users_and_roles.populate_user({'Name': 'user1'})
    _, cmdId = setup_generic_pe_command_with_no_rules_all_OS

    asmntId, isSuccess = PrivilegeElevation.add_pe_rule_assignment(session, cmdId, principalType="User", principalID=userobj.get_login_name(), scopeType="Global", scope="Global", byPassChallenge=False)
    assert isSuccess is True, f'PrivilegeElevation add assignment has failed'

    #clean up
    errMsg, isSuccess = PrivilegeElevation.del_pe_rule_assignment(session, asmntId)
    assert isSuccess is True, f'PrivilegeElevation add assignment failed to clean up {errMsg}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_add_assignment_role_id(core_session, users_and_roles, setup_generic_pe_command_with_no_rules_all_OS):
    """
    Test case: Test for all valid params with Global scope, principal as role id added by sysadmin user
    """

    session = core_session
    role = users_and_roles.populate_role({'Name': "role1", "Rights": ["Admin Portal Login"]})
    _, cmdId = setup_generic_pe_command_with_no_rules_all_OS

    asmntId, isSuccess = PrivilegeElevation.add_pe_rule_assignment(session, cmdId, principalType="Role", principalID=role['ID'], scopeType="Global", scope="Global", byPassChallenge=False)
    assert isSuccess is True, f'PrivilegeElevation add assignment has failed'

    #clean up
    errMsg, isSuccess = PrivilegeElevation.del_pe_rule_assignment(session, asmntId)
    assert isSuccess is True, f'PrivilegeElevation add assignment failed to clean up {errMsg}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_add_assignment_role_name(core_session, users_and_roles, setup_generic_pe_command_with_no_rules_all_OS):
    """
    Test case: Test for all valid params with Global scope, principal as role name added by sysadmin user
    """

    session = core_session
    role = users_and_roles.populate_role({'Name': "role1", "Rights": ["Admin Portal Login"]})
    _, cmdId = setup_generic_pe_command_with_no_rules_all_OS

    asmntId, isSuccess = PrivilegeElevation.add_pe_rule_assignment(session, cmdId, principalType="Role", principal=role['Name'], scopeType="Global", scope="Global", byPassChallenge=False)    
    assert isSuccess is True, f'PrivilegeElevation add assignment has failed'

    #clean up
    errMsg, isSuccess = PrivilegeElevation.del_pe_rule_assignment(session, asmntId)
    assert isSuccess is True, f'PrivilegeElevation add assignment failed to clean up {errMsg}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_add_assignment_adgroup_id(core_session, setup_adgroup, setup_generic_pe_command_with_no_rules_all_OS):
    """
    Test case: Test for all valid params with Global scope, principal as adgroup id added by sysadmin user
    """
    session = core_session
    _, cmdId = setup_generic_pe_command_with_no_rules_all_OS
    ad_group = setup_adgroup
    if ad_group is None:
        pytest.skip("Cannot retreive ad group info")
    asmntId, isSuccess = PrivilegeElevation.add_pe_rule_assignment(session, cmdId, principalType="Group", principalID=ad_group['InternalName'], scopeType="Global", scope="Global", byPassChallenge=False)    
    assert isSuccess is True, f'PrivilegeElevation add assignment has failed'

    #clean up
    errMsg, isSuccess = PrivilegeElevation.del_pe_rule_assignment(session, asmntId)
    assert isSuccess is True, f'PrivilegeElevation add assignment failed to clean up {errMsg}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_add_assignment_adgroup_name(core_session, setup_adgroup, setup_generic_pe_command_with_no_rules_all_OS):
    """
    Test case: Test for all valid params with Global scope, principal as adgroup name added by sysadmin user
    """
    session = core_session
    _, cmdId = setup_generic_pe_command_with_no_rules_all_OS
    ad_group = setup_adgroup
    if ad_group is None:
        pytest.skip("Cannot retreive ad group info")
    
    asmntId, isSuccess = PrivilegeElevation.add_pe_rule_assignment(session, cmdId, principalType="Group", principal=ad_group['DisplayName'], scopeType="Global", scope="Global", byPassChallenge=False)    
    assert isSuccess is True, f'PrivilegeElevation add assignment has failed'

    #clean up
    errMsg, isSuccess = PrivilegeElevation.del_pe_rule_assignment(session, asmntId)
    assert isSuccess is True, f'PrivilegeElevation add assignment failed to clean up {errMsg}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
@pytest.mark.parametrize('operating_system', ["Unix", "Windows"])
def test_pe_add_assignment_for_user_on_system(core_session, create_resources, users_and_roles, setup_generic_pe_command_with_no_rules_all_OS, operating_system):
    """
    Test case: Test for all valid params with System scope, principal as normal user added by sysadmin user
    """

    session = core_session
    userobj = users_and_roles.populate_user({'Name': 'user1'})
    _, cmdId = setup_generic_pe_command_with_no_rules_all_OS
    system = create_resources(core_session, 1, operating_system)
    admin_user = core_session.get_user()
    admin_user_name = admin_user.get_login_name()
    admin_user_id = admin_user.get_id()

    # Give Manage Assignments and View permission to admin user on this system
    permission_string = 'View,ManagePrivilegeElevationAssignment'
    result, success = ResourceManager.assign_system_permissions(core_session, permission_string,
                                                                admin_user_name, admin_user_id, "User",
                                                                system[0]['ID'])
    assert success, f"Failed to assign system permissions {result}"

    asmntId, isSuccess = PrivilegeElevation.add_pe_rule_assignment(session, cmdId, principalType="User", principalID=userobj.get_login_name(), scopeType="System", scope=system[0]['ID'], byPassChallenge=False)    
    assert isSuccess is True, f'PrivilegeElevation add assignment has failed'

    #clean up
    errMsg, isSuccess = PrivilegeElevation.del_pe_rule_assignment(session, asmntId)
    assert isSuccess is True, f'PrivilegeElevation add assignment failed to clean up {errMsg}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
@pytest.mark.parametrize('operating_system', ["Unix", "Windows"])
def test_pe_add_assignment_for_user_on_set(core_session, create_resources, users_and_roles, create_manual_set, setup_generic_pe_command_with_no_rules_all_OS, operating_system):
    """
    Test case: Test for all valid params with Collection scope, principal as normal user added by sysadmin user
    """

    session = core_session
    userobj = users_and_roles.populate_user({'Name': 'user1'})
    _, cmdId = setup_generic_pe_command_with_no_rules_all_OS
    system = create_resources(core_session, 1, operating_system)
    
    # Create Set and the system to this set
    set_id = create_manual_set(
        core_session, "Server", object_ids=[system[0]['ID']])['ID']
    logger.debug(f"Successfully created a set and added system to that set: {set_id}")

    admin_user = core_session.get_user()
    admin_user_name = admin_user.get_login_name()
    admin_user_id = admin_user.get_id()

    # Give the manage assignments permission to admin user on this set
    permission_string = 'View,ManagePrivilegeElevationAssignment'
    result = SetsManager.set_collection_resource_permissions(core_session, permission_string, admin_user_name, admin_user_id, set_id, "User")
    assert result["success"] is True, f'setting collection permissions failed: {result}'

    asmntId, isSuccess = PrivilegeElevation.add_pe_rule_assignment(session, cmdId, principalType="User", principalID=userobj.get_login_name(), scopeType="Collection", scope=set_id, byPassChallenge=False)    
    assert isSuccess is True, f'PrivilegeElevation add assignment has failed'

    #clean up
    errMsg, isSuccess = PrivilegeElevation.del_pe_rule_assignment(session, asmntId)
    assert isSuccess is True, f'PrivilegeElevation add assignment failed to clean up {errMsg}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
@pytest.mark.parametrize('operating_system', ["Unix", "Windows"])
def test_pe_add_assignment_for_role_on_system(core_session, create_resources, users_and_roles, setup_generic_pe_command_with_no_rules_all_OS, operating_system):
    """
    Test case: Test for all valid params with System scope, principal as role added by sysadmin user
    """

    session = core_session
    role = users_and_roles.populate_role({'Name': "role1", "Rights": ["Admin Portal Login"]})
    _, cmdId = setup_generic_pe_command_with_no_rules_all_OS
    system = create_resources(core_session, 1, operating_system)
    admin_user = core_session.get_user()
    admin_user_name = admin_user.get_login_name()
    admin_user_id = admin_user.get_id()

    # Give all permissions but the manage assignments permission to admin user on this system
    permission_string = 'View,ManagePrivilegeElevationAssignment'
    result, success = ResourceManager.assign_system_permissions(core_session, permission_string,
                                                                admin_user_name, admin_user_id, "User",
                                                                system[0]['ID'])
    assert success, f"Failed to assign system permissions {result}"

    asmntId, isSuccess = PrivilegeElevation.add_pe_rule_assignment(session, cmdId, principalType="Role", principal=role["Name"], scopeType="System", scope=system[0]['ID'], byPassChallenge=False)    
    assert isSuccess is True, f'PrivilegeElevation add assignment has failed'

    #clean up
    errMsg, isSuccess = PrivilegeElevation.del_pe_rule_assignment(session, asmntId)
    assert isSuccess is True, f'PrivilegeElevation add assignment failed to clean up {errMsg}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
@pytest.mark.parametrize('operating_system', ["Unix", "Windows"])
def test_pe_add_assignment_for_role_on_set(core_session, create_resources, users_and_roles, create_manual_set, setup_generic_pe_command_with_no_rules_all_OS, operating_system):
    """
    Test case: Test for all valid params with Collection scope, principal as role added by sysadmin user
    """

    session = core_session
    role = users_and_roles.populate_role({'Name': "role1", "Rights": ["Admin Portal Login"]})
    _, cmdId = setup_generic_pe_command_with_no_rules_all_OS
    system = create_resources(core_session, 1, operating_system)

    # Create Set and the system to this set
    set_id = create_manual_set(
        core_session, "Server", object_ids=[system[0]['ID']])['ID']
    logger.debug(f"Successfully created a set and added system to that set: {set_id}")

    admin_user = core_session.get_user()
    admin_user_name = admin_user.get_login_name()
    admin_user_id = admin_user.get_id()

    # Give the manage assignments permission to admin user on this system
    permission_string = 'View,ManagePrivilegeElevationAssignment'
    result = SetsManager.set_collection_resource_permissions(core_session, permission_string, role["Name"], role["ID"], set_id, "Role")
    assert result["success"] is True, f'setting collection permissions failed: {result}'

 
    
    asmntId, isSuccess = PrivilegeElevation.add_pe_rule_assignment(session, cmdId, principalType="Role", principal=role["Name"], scopeType="Collection", scope=set_id, byPassChallenge=False)    
    assert isSuccess is True, f'PrivilegeElevation add assignment has failed'

    #clean up
    errMsg, isSuccess = PrivilegeElevation.del_pe_rule_assignment(session, asmntId)
    assert isSuccess is True, f'PrivilegeElevation add assignment failed to clean up {errMsg}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
@pytest.mark.parametrize('operating_system', ["Unix", "Windows"])
def test_pe_add_assignment_for_group_on_system(core_session, create_resources, setup_adgroup, setup_generic_pe_command_with_no_rules_all_OS, operating_system):
    """
    Test case: Test for all valid params with System scope, principal as adgroup name added by sysadmin user
    """

    session = core_session
    ad_group = setup_adgroup
    if ad_group is None:
        pytest.skip("Cannot retreive ad group info")
    
    _, cmdId = setup_generic_pe_command_with_no_rules_all_OS
    system = create_resources(core_session, 1, operating_system)


    admin_user = core_session.get_user()
    admin_user_name = admin_user.get_login_name()
    admin_user_id = admin_user.get_id()

    # Give all permissions but the manage assignments permission to admin user on this system
    permission_string = 'View,ManagePrivilegeElevationAssignment'
    result, success = ResourceManager.assign_system_permissions(core_session, permission_string,
                                                                admin_user_name, admin_user_id, "User",
                                                                system[0]['ID'])
    assert success, f"Failed to assign system permissions {result}"

    asmntId, isSuccess = PrivilegeElevation.add_pe_rule_assignment(session, cmdId, principalType="Group", principal=ad_group["DisplayName"], scopeType="System", scope=system[0]['ID'], byPassChallenge=False)    
    assert isSuccess is True, f'PrivilegeElevation add assignment has failed'

    #clean up
    errMsg, isSuccess = PrivilegeElevation.del_pe_rule_assignment(session, asmntId)
    assert isSuccess is True, f'PrivilegeElevation add assignment failed to clean up {errMsg}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
@pytest.mark.parametrize('operating_system', ["Unix", "Windows"])
def test_pe_add_assignment_for_group_on_set(core_session, create_resources, setup_adgroup, create_manual_set, setup_generic_pe_command_with_no_rules_all_OS, operating_system):
    """
    Test case: Test for all valid params with Collection scope, principal as adgroup name added by sysadmin user
    """

    session = core_session
    ad_group = setup_adgroup
    if ad_group is None:
        pytest.skip("Cannot retreive ad group info")
    
    _, cmdId = setup_generic_pe_command_with_no_rules_all_OS
    system = create_resources(core_session, 1, operating_system)

    # Create Set and the system to this set
    set_id = create_manual_set(
        core_session, "Server", object_ids=[system[0]['ID']])['ID']
    logger.debug(f"Successfully created a set and added system to that set: {set_id}")

    admin_user = core_session.get_user()
    admin_user_name = admin_user.get_login_name()
    admin_user_id = admin_user.get_id()

    # Give the manage assignments permission to admin user on this system
    permission_string = 'View,ManagePrivilegeElevationAssignment'
    result = SetsManager.set_collection_resource_permissions(core_session, permission_string, admin_user_name, admin_user_id, set_id, "User")
    assert result["success"] is True, f'setting collection permissions failed: {result}'

    asmntId, isSuccess = PrivilegeElevation.add_pe_rule_assignment(session, cmdId, principalType="Group", principal=ad_group["DisplayName"], scopeType="Collection", scope=set_id, byPassChallenge=False)    
    assert isSuccess is True, f'PrivilegeElevation add assignment has failed'

    #clean up
    errMsg, isSuccess = PrivilegeElevation.del_pe_rule_assignment(session, asmntId)
    assert isSuccess is True, f'PrivilegeElevation add assignment failed to clean up {errMsg}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
@pytest.mark.parametrize('operating_system', ["Unix", "Windows"])
def test_pe_add_assignment_for_group_on_set_by_non_sysadmin_user(core_session, create_resources, setup_adgroup, create_manual_set, setup_generic_pe_command_with_no_rules_all_OS, users_and_roles, operating_system):
    """
    Test case: Test for all valid params with Collection scope, principal as adgroup name added by non sysadmin user
    """

    session = core_session
    ad_group = setup_adgroup
    if ad_group is None:
        pytest.skip("Cannot retreive ad group info")
    
    _, cmdId = setup_generic_pe_command_with_no_rules_all_OS
    system = create_resources(core_session, 1, operating_system)

    # Get User
    requester_session = users_and_roles.get_session_for_user('Privilege Elevation Management')
    response = requester_session.get_current_session_user_info()
    user_info = response.json()['Result']

    # Create Set and the system to this set
    set_id = create_manual_set(
        core_session, "Server", object_ids=[system[0]['ID']])['ID']
    logger.debug(f"Successfully created a set and added system to that set: {set_id}")

    # Give the manage assignments member permission to cloud user on this set
    permission_string = 'View,ManagePrivilegeElevationAssignment'
    result = SetsManager.set_collection_resource_permissions(core_session, permission_string, user_info['Name'], user_info['Id'], set_id, "User")
    assert result["success"] is True, f'setting collection permissions failed: {result}'

    # Give the edit permission to cloud user on this set
    permission_string = 'View, Edit'
    result = SetsManager.set_collection_permissions(core_session, permission_string, user_info['Name'], user_info['Id'], set_id, "User")
    assert result['success'], f'assigning collection permissions on the resource set for the user failed: {result}'

    # user should be able to add assignment for anyone if it has Edit permission and ManagePermissionElevationAssignment as member permission on the set
    asmntId1, isSuccess = PrivilegeElevation.add_pe_rule_assignment(requester_session, cmdId, principalType="Group", principal=ad_group["DisplayName"], scopeType="Collection", scope=set_id, byPassChallenge=False)    
    assert isSuccess is True, f'PrivilegeElevation add assignment has failed'

    asmntId2, isSuccess = PrivilegeElevation.add_pe_rule_assignment(requester_session, cmdId, principalType="Group", principal=ad_group["DisplayName"], scopeType="System", scope=system[0]['ID'], byPassChallenge=False)    
    assert isSuccess is True, f'PrivilegeElevation add assignment has failed'

    #clean up
    errMsg, isSuccess = PrivilegeElevation.del_pe_rule_assignment(session, asmntId1)
    assert isSuccess is True, f'PrivilegeElevation add assignment failed to clean up {errMsg}'
    errMsg, isSuccess = PrivilegeElevation.del_pe_rule_assignment(session, asmntId2)
    assert isSuccess is True, f'PrivilegeElevation add assignment failed to clean up {errMsg}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
@pytest.mark.parametrize('operating_system', ["Unix", "Windows"])
def test_pe_add_assignment_for_group_on_set_by_non_sysadmin_role(core_session, create_resources, setup_adgroup, create_manual_set, setup_generic_pe_command_with_no_rules_all_OS, users_and_roles, operating_system):
    """
    Test case: Test for all valid params with Collection scope, principal as adgroup name added by non sysadmin role
    """

    session = core_session
    ad_group = setup_adgroup
    if ad_group is None:
        pytest.skip("Cannot retreive ad group info")
    
    role = users_and_roles.populate_role({'Name': "role1", "Rights": ["Admin Portal Login"]})
    _, cmdId = setup_generic_pe_command_with_no_rules_all_OS
    system = create_resources(core_session, 1, operating_system)

    # Get User
    requester_session = users_and_roles.get_session_for_user('Privilege Elevation Management')
    response = requester_session.get_current_session_user_info()
    user_info = response.json()['Result']
    logger.debug(requester_session.get_user())
    #Add user to role
    users_and_roles.add_user_to_role(requester_session.get_user(), role)

    # Create Set and the system to this set
    set_id = create_manual_set(
        core_session, "Server", object_ids=[system[0]['ID']])['ID']
    logger.debug(f"Successfully created a set and added system to that set: {set_id}")

    # Give the manage assignments member permission to cloud user on this set
    permission_string = 'View,ManagePrivilegeElevationAssignment'
    result = SetsManager.set_collection_resource_permissions(core_session, permission_string, role['Name'], role['ID'], set_id, "Role")
    assert result["success"] is True, f'setting collection permissions failed: {result}'

    # Give the edit permission to cloud user on this set
    permission_string = 'View,Edit'
    result = SetsManager.set_collection_permissions(core_session, permission_string, role['Name'], role['ID'], set_id, "Role")
    assert result['success'], f'assigning collection permissions on the resource set for the user failed: {result}'

    # user should be able to add assignment for anyone if it has Edit permission and ManagePermissionElevationAssignment as member permission on the set
    asmntId1, isSuccess = PrivilegeElevation.add_pe_rule_assignment(requester_session, cmdId, principalType="Group", principal=ad_group["DisplayName"], scopeType="Collection", scope=set_id, byPassChallenge=False)    
    assert isSuccess is True, f'PrivilegeElevation add assignment has failed'

    asmntId2, isSuccess = PrivilegeElevation.add_pe_rule_assignment(requester_session, cmdId, principalType="Group", principal=ad_group["DisplayName"], scopeType="System", scope=system[0]['ID'], byPassChallenge=False)    
    assert isSuccess is True, f'PrivilegeElevation add assignment has failed'

    #clean up
    errMsg, isSuccess = PrivilegeElevation.del_pe_rule_assignment(session, asmntId1)
    assert isSuccess is True, f'PrivilegeElevation add assignment failed to clean up {errMsg}'
    errMsg, isSuccess = PrivilegeElevation.del_pe_rule_assignment(session, asmntId2)
    assert isSuccess is True, f'PrivilegeElevation add assignment failed to clean up {errMsg}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_add_assignment_bypass_challenge_enabled(core_session, users_and_roles, setup_generic_pe_command_with_no_rules_all_OS):
    """
    Test case: Test for all valid params with Global scope, principal as normal name, bypass challenge as true added by sysadmin user
    """

    session = core_session
    userobj = users_and_roles.populate_user({'Name': 'user1'})
    _, cmdId = setup_generic_pe_command_with_no_rules_all_OS

    asmntId, isSuccess = PrivilegeElevation.add_pe_rule_assignment(session, cmdId, principalType="User", principalID=userobj.get_id(), scopeType="Global", scope="Global", byPassChallenge=True)    
    assert isSuccess is True, f'PrivilegeElevation add assignment has failed'

    #clean up
    errMsg, isSuccess = PrivilegeElevation.del_pe_rule_assignment(session, asmntId)
    assert isSuccess is True, f'PrivilegeElevation add assignment failed to clean up {errMsg}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_add_assignment_starts_expires(core_session, users_and_roles, setup_generic_pe_command_with_no_rules_all_OS):
    """
    Test case: Test for all valid params with Global scope, principal as normal user id, valid starts and expires added by sysadmin user
    """

    session = core_session
    userobj = users_and_roles.populate_user({'Name': 'user1'})
    _, cmdId = setup_generic_pe_command_with_no_rules_all_OS

    asmntId, isSuccess = PrivilegeElevation.add_pe_rule_assignment(session, cmdId, principalType="User", principalID=userobj.get_id(), scopeType="Global", scope="Global", byPassChallenge=True, starts="2020-12-10T12:30:00Z", expires="2020-12-10T15:30:00Z")    
    assert isSuccess is True, f'PrivilegeElevation add assignment has failed'

    #clean up
    errMsg, isSuccess = PrivilegeElevation.del_pe_rule_assignment(session, asmntId)
    assert isSuccess is True, f'PrivilegeElevation add assignment failed to clean up {errMsg}'

# Negative cases

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_add_assignment_no_command_id(core_session, users_and_roles):
    """
    Test case: Test for all required params except PrivilegeElevationCommand
    """

    session = core_session
    userobj = users_and_roles.populate_user({'Name': 'user1'})
    
    args = get_PE_ADD_ASSIGNMENTS_Data(None, "User", "Global", principal=userobj.get_login_name(), scope="Global", bypassChallenge=False)
    response = session.apirequest(EndPoints.PRIVILEGE_ELEVATION_ADD_RULE_ASSIGNMENT, args)
    
    try:
        resp = response.json()
    except Exception:
        pytest.fail(f'Cannot decode response: {response}')
    
    assert resp["success"] is False, f'PrivilegeElevation add assignment failed to fail {resp}'
    assert "Missing required parameter: PrivilegeElevationCommand" in resp["Exception"], f'PrivilegeElevation add assignment should fail with missing param PrivilegeElevationCommand {resp}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_add_assignment_no_scopetype(core_session):
    """
    Test case: Test for all required params except scopetype
    """

    session = core_session
    args = get_PE_ADD_ASSIGNMENTS_Data("Go Super Saiyan", "User", None, principal="Goku", scope="Global", bypassChallenge=False)

    response = session.apirequest(EndPoints.PRIVILEGE_ELEVATION_ADD_RULE_ASSIGNMENT, args)
    
    try:
        resp = response.json()
    except Exception:
        pytest.fail(f'Cannot decode response: {response}')
    
    assert resp["success"] is False, f'PrivilegeElevation add assignment failed to fail {resp}'
    assert  "Value cannot be null.\r\nParameter name: ScopeType" in resp["Exception"], f'PrivilegeElevation add assignment should fail with missing ScopeType {resp}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_add_assignment_no_scope(core_session):
    """
    Test case:Test for all required params except scope
    """

    session = core_session
    args = get_PE_ADD_ASSIGNMENTS_Data("Final Flash", "User", "System", principal="Vegeta", scope=None, bypassChallenge=False)
    
    response = session.apirequest(EndPoints.PRIVILEGE_ELEVATION_ADD_RULE_ASSIGNMENT, args)
    
    try:
        resp = response.json()
    except Exception:
        pytest.fail(f'Cannot decode response: {response}')
    
    assert resp["success"] is False, f'PrivilegeElevation add assignment failed to fail {resp}'
    assert resp["Message"] == "Parameter 'Scope' must be specified.", f'PrivilegeElevation add assignment should fail with missing scope error {resp}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_add_assignment_no_principaltype(core_session):
    """
    Test case: Test for all required params except principaltype
    """

    session = core_session
    args = get_PE_ADD_ASSIGNMENTS_Data("SomeCommand", None, "Global", principal="Gohan", scope=None, bypassChallenge=False)

    response = session.apirequest(EndPoints.PRIVILEGE_ELEVATION_ADD_RULE_ASSIGNMENT, args)
    
    try:
        resp = response.json()
    except Exception:
        pytest.fail(f'Cannot decode response: {response}')
    
    assert resp["success"] is False, f'PrivilegeElevation add assignment failed to fail {resp}'
    assert "Value cannot be null.\r\nParameter name: PrincipalType" in resp["Exception"], f'PrivilegeElevation add assignment should fail with missing PrincipalType error {resp}'
    
@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_add_assignment_no_principal(core_session):
    """
    Test case: Test for all required params except principal or principalId
    """

    session = core_session
    args = get_PE_ADD_ASSIGNMENTS_Data("SomeCommand", "User", "Global", scope="Global", bypassChallenge=False)
    
    response = session.apirequest(EndPoints.PRIVILEGE_ELEVATION_ADD_RULE_ASSIGNMENT, args)
    
    try:
        resp = response.json()
    except Exception:
        pytest.fail(f'Cannot decode response: {response}')
    
    assert resp["success"] is False, f'PrivilegeElevation add assignment failed to fail {resp}'
    assert "Must specify either Principal or PrincipalId in request' must be specified" in resp["Exception"], f'PrivilegeElevation add assignment should fail with missing Principal error {resp}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_add_assignment_command_not_exist(core_session, users_and_roles):
    """
    Test case: Test for all valid params except PrivilegeElevationCommand doesn't exist
    """

    session = core_session
    userobj = users_and_roles.populate_user({'Name': 'user1'})

    response = session.apirequest(EndPoints.PRIVILEGE_ELEVATION_ADD_RULE_ASSIGNMENT, get_PE_ADD_ASSIGNMENTS_Data("CommandNotExist", "User", "Global", principalId=userobj.get_id(), scope="Global", bypassChallenge=True, starts="2020-12-10T12:30:00Z", expires="2020-12-10T15:30:00Z"))
    
    try:
        resp = response.json()
    except Exception:
        pytest.fail(f'Cannot decode response: {response}')
    
    assert resp["success"] is False, f'PrivilegeElevation add assignment has failed to fail {resp}'
    assert resp['Message'] == 'Privilege Elevation Command not found.', f'PrivilegeElevation add assignment should fail with command not found error {resp}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_add_assignment_invalid_scopetype(core_session, users_and_roles, setup_generic_pe_command_with_no_rules_all_OS):
    """
    Test case: Test for all valid params except invalid ScopeType
    """

    session = core_session
    userobj = users_and_roles.populate_user({'Name': 'user1'})
    _, cmdId = setup_generic_pe_command_with_no_rules_all_OS

    response = session.apirequest(EndPoints.PRIVILEGE_ELEVATION_ADD_RULE_ASSIGNMENT, get_PE_ADD_ASSIGNMENTS_Data(cmdId, "User", "ScopeNotExist", scope="Global",  principalId=userobj.get_id(), bypassChallenge=True, starts="2020-12-10T12:30:00Z", expires="2020-12-10T15:30:00Z"))
    
    try:
        resp = response.json()
    except Exception:
        pytest.fail(f'Cannot decode response: {response}')
    
    assert resp["success"] is False, f'PrivilegeElevation add assignment has failed to fail {resp}'
    assert resp['Message'] == 'Specified argument was out of the range of valid values.\r\nParameter name: ScopeType', f'PrivilegeElevation add assignment should fail with ScopeType not found error {resp}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_add_assignment_system_scope_not_exist(core_session, users_and_roles, setup_generic_pe_command_with_no_rules_all_OS):
    """
    Test case: Test for all valid params except system doesn't exist
    """

    session = core_session
    userobj = users_and_roles.populate_user({'Name': 'user1'})
    _, cmdId = setup_generic_pe_command_with_no_rules_all_OS

    response = session.apirequest(EndPoints.PRIVILEGE_ELEVATION_ADD_RULE_ASSIGNMENT, get_PE_ADD_ASSIGNMENTS_Data(cmdId, "User", scopeType="System", scope="SystemNotExist",  principalId=userobj.get_id(), bypassChallenge=True, starts="2020-12-10T12:30:00Z", expires="2020-12-10T15:30:00Z"))
    
    try:
        resp = response.json()
    except Exception:
        pytest.fail(f'Cannot decode response: {response}')
    
    assert resp["success"] is False, f'PrivilegeElevation add assignment has failed to fail {resp}'
    assert 'ResourceNotExistException' in resp['Message'], f'PrivilegeElevation add assignment should fail with ResourceNotExistException {resp}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_add_assignment_set_scope_not_exist(core_session, users_and_roles, setup_generic_pe_command_with_no_rules_all_OS):
    """
    Test case: Test for all valid params except set doesn't exist
    """

    session = core_session
    userobj = users_and_roles.populate_user({'Name': 'user1'})
    _, cmdId = setup_generic_pe_command_with_no_rules_all_OS

    response = session.apirequest(EndPoints.PRIVILEGE_ELEVATION_ADD_RULE_ASSIGNMENT, get_PE_ADD_ASSIGNMENTS_Data(cmdId, "User", scopeType="Collection", scope="CollectionNotExist",principalId=userobj.get_id(), bypassChallenge=True, starts="2020-12-10T12:30:00Z", expires="2020-12-10T15:30:00Z"))
    
    try:
        resp = response.json()
    except Exception:
        pytest.fail(f'Cannot decode response: {response}')
    
    assert resp["success"] is False, f'PrivilegeElevation add assignment has failed to fail {resp}'
    assert 'Set does not exist' == resp['Message'], f'PrivilegeElevation add assignment should fail with Set does not exist {resp}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_add_assignment_principal_not_valid(core_session, users_and_roles, setup_generic_pe_command_with_no_rules_all_OS):
    """
    Test case: Test for all valid params except PrincipalType
    """

    session = core_session
    userobj = users_and_roles.populate_user({'Name': 'user1'})
    _, cmdId = setup_generic_pe_command_with_no_rules_all_OS

    response = session.apirequest(EndPoints.PRIVILEGE_ELEVATION_ADD_RULE_ASSIGNMENT, get_PE_ADD_ASSIGNMENTS_Data(cmdId, scopeType="Global", scope="Global", principalType="Invalid", principalId=userobj.get_id(), bypassChallenge=True, starts="2020-12-10T12:30:00Z", expires="2020-12-10T15:30:00Z"))
    
    try:
        resp = response.json()
    except Exception:
        pytest.fail(f'Cannot decode response: {response}')
    
    assert resp["success"] is False, f'PrivilegeElevation add assignment has failed to fail {resp}'
    assert 'Specified argument was out of the range of valid values.\r\nParameter name: PrincipalType' == resp['Message'], f'PrivilegeElevation add assignment should fail with PrincipalType out of range error {resp}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_add_assignment_principal_user_not_exist(core_session, setup_generic_pe_command_with_no_rules_all_OS):
    """
    Test case: Test for all valid params except principal user doesn't exist
    """

    session = core_session
    _, cmdId = setup_generic_pe_command_with_no_rules_all_OS

    response = session.apirequest(EndPoints.PRIVILEGE_ELEVATION_ADD_RULE_ASSIGNMENT, get_PE_ADD_ASSIGNMENTS_Data(cmdId, scopeType="Global", scope="Global", principalType="User", principal="UserNotExist", bypassChallenge=True, starts="2020-12-10T12:30:00Z", expires="2020-12-10T15:30:00Z"))
    
    try:
        resp = response.json()
    except Exception:
        pytest.fail(f'Cannot decode response: {response}')
    
    assert resp["success"] is False, f'PrivilegeElevation add assignment has failed to fail {resp}'
    assert 'Principal cannot be found' == resp['Message'], f'PrivilegeElevation add assignment should fail with Principal cannot be found {resp}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_add_assignment_principal_role_not_exist(core_session, setup_generic_pe_command_with_no_rules_all_OS):
    """
    Test case: Test for all valid params except principal role doesn't exist
    """

    session = core_session
    _, cmdId = setup_generic_pe_command_with_no_rules_all_OS

    response = session.apirequest(EndPoints.PRIVILEGE_ELEVATION_ADD_RULE_ASSIGNMENT, get_PE_ADD_ASSIGNMENTS_Data(cmdId, scopeType="Global", scope="Global", principalType="Role", principal="RoleNotExist", bypassChallenge=True, starts="2020-12-10T12:30:00Z", expires="2020-12-10T15:30:00Z"))
    
    try:
        resp = response.json()
    except Exception:
        pytest.fail(f'Cannot decode response: {response}')
    
    assert resp["success"] is False, f'PrivilegeElevation add assignment has failed to fail {resp}'
    assert 'Principal cannot be found' == resp['Message'], f'PrivilegeElevation add assignment should fail with Principal cannot be found {resp}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_add_assignment_principal_userid_not_exist(core_session, setup_generic_pe_command_with_no_rules_all_OS):
    """
    Test case: Test for all valid params except principal userid doesn't exist
    """

    session = core_session
    _, cmdId = setup_generic_pe_command_with_no_rules_all_OS

    response = session.apirequest(EndPoints.PRIVILEGE_ELEVATION_ADD_RULE_ASSIGNMENT, get_PE_ADD_ASSIGNMENTS_Data(cmdId, scopeType="Global", scope="Global", principalType="User", principalId="UserIdNotExist", bypassChallenge=True, starts="2020-12-10T12:30:00Z", expires="2020-12-10T15:30:00Z"))
    
    try:
        resp = response.json()
    except Exception:
        pytest.fail(f'Cannot decode response: {response}')
    
    assert resp["success"] is False, f'PrivilegeElevation add assignment has failed to fail {resp}'
    assert 'Principal cannot be found' == resp['Message'], f'PrivilegeElevation add assignment should fail with Principal cannot be found {resp}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_add_assignment_principal_roleid_not_exist(core_session, setup_generic_pe_command_with_no_rules_all_OS):
    """
    Test case: Test for all valid params except principal roleid doesn't exist
    """

    session = core_session
    _, cmdId = setup_generic_pe_command_with_no_rules_all_OS

    response = session.apirequest(EndPoints.PRIVILEGE_ELEVATION_ADD_RULE_ASSIGNMENT, get_PE_ADD_ASSIGNMENTS_Data(cmdId, scopeType="Global", scope="Global", principalType="Role", principalId="RoleIdNotExist", bypassChallenge=True, starts="2020-12-10T12:30:00Z", expires="2020-12-10T15:30:00Z"))
    
    try:
        resp = response.json()
    except Exception:
        pytest.fail(f'Cannot decode response: {response}')
    
    assert resp["success"] is False, f'PrivilegeElevation add assignment has failed to fail {resp}'
    assert 'Principal cannot be found' == resp['Message'], f'PrivilegeElevation add assignment should fail with Principal cannot be found {resp}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_add_assignment_bypass_challenge_invalidtype(core_session, setup_generic_pe_command_with_no_rules_all_OS, users_and_roles):
    """
    Test case: Test for all valid params except bypass challenge invalid type
    """

    session = core_session
    _, cmdId = setup_generic_pe_command_with_no_rules_all_OS
    userobj = users_and_roles.populate_user({'Name': 'user1'})

    response = session.apirequest(EndPoints.PRIVILEGE_ELEVATION_ADD_RULE_ASSIGNMENT, get_PE_ADD_ASSIGNMENTS_Data(cmdId, scopeType="Global", scope="Global", principalType="User",  principalId=userobj.get_id(), bypassChallenge="Invalid", starts="2020-12-10T12:30:00Z", expires="2020-12-10T15:30:00Z"))
    
    try:
        resp = response.json()
    except Exception:
        pytest.fail(f'Cannot decode response: {response}')
    
    assert resp["success"] is False, f'PrivilegeElevation add assignment has failed to fail {resp}'
    assert 'Invalid arguments passed to the server.' == resp['Message'], f'PrivilegeElevation add assignment should fail with Invalid arguments passed to the server. {resp}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_add_assignment_starts_invalidtime(core_session, setup_generic_pe_command_with_no_rules_all_OS, users_and_roles):
    """
    Test case: Test for all valid params except starts invalid time
    """

    session = core_session
    _, cmdId = setup_generic_pe_command_with_no_rules_all_OS
    userobj = users_and_roles.populate_user({'Name': 'user1'})

    response = session.apirequest(EndPoints.PRIVILEGE_ELEVATION_ADD_RULE_ASSIGNMENT, get_PE_ADD_ASSIGNMENTS_Data(cmdId, scopeType="Global", scope="Global", principalType="User",  principalId=userobj.get_id(), bypassChallenge=True, starts="2020-126-10T12:30:00Z", expires="2020-12-10T15:30:00Z"))
    
    try:
        resp = response.json()
    except Exception:
        pytest.fail(f'Cannot decode response: {response}')
    
    assert resp["success"] is False, f'PrivilegeElevation add assignment has failed to fail {resp}'
    assert 'Invalid arguments passed to the server.' == resp['Message'], f'PrivilegeElevation add assignment should fail with Invalid arguments passed to the server. {resp}'

    
@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_add_assignment_expires_invalidtime(core_session, setup_generic_pe_command_with_no_rules_all_OS, users_and_roles):
    """
    Test case: Test for all valid params except expires invalid time
    """

    session = core_session
    _, cmdId = setup_generic_pe_command_with_no_rules_all_OS
    userobj = users_and_roles.populate_user({'Name': 'user1'})

    response = session.apirequest(EndPoints.PRIVILEGE_ELEVATION_ADD_RULE_ASSIGNMENT, get_PE_ADD_ASSIGNMENTS_Data(cmdId, scopeType="Global", scope="Global", principalType="User",  principalId=userobj.get_id(), bypassChallenge=True, starts="2020-12-10T12:30:00Z", expires="2020-126-10T15:30:00Z"))
    
    try:
        resp = response.json()
    except Exception:
        pytest.fail(f'Cannot decode response: {response}')
    
    assert resp["success"] is False, f'PrivilegeElevation add assignment has failed to fail {resp}'
    assert 'Invalid arguments passed to the server.' == resp['Message'], f'PrivilegeElevation add assignment should fail with Invalid arguments passed to the server. {resp}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
@pytest.mark.parametrize('operating_system', ["Unix", "Windows"])
def test_pe_add_assignment_no_manage_assignment_permission_on_system(core_session, create_resources, users_and_roles, setup_generic_pe_command_with_no_rules_all_OS, operating_system):
    """
    Test case: Test for principal as role and scope as system and the user (not sysadmin) has no Manage Assignment permission on the system
    """

    session = core_session
    role = users_and_roles.populate_role({'Name': "role12345", "Rights": ["Admin Portal Login"]})
    userobj = users_and_roles.populate_user({'Name': 'user1'})
    users_and_roles.add_user_to_role(userobj, role)
    
    user_session = users_and_roles.get_session_for_specific_user(userobj)

    _, cmdId = setup_generic_pe_command_with_no_rules_all_OS
    system = create_resources(core_session, 1, operating_system)
    
    # Give all permissions to the user except ManagePrivilegeElevationAssignment
    permission_string = 'Grant,View,Edit,Delete,ManageSession,AgentAuth,RequestZoneRole,AddAccount,UnlockAccount'
    result, success = ResourceManager.assign_system_permissions(core_session, permission_string,
                                                               role['Name'],  role['ID'], "Role",
                                                                system[0]['ID'])
    assert success, f"Did not set admin system permissions: {result}"

    response = user_session.apirequest(EndPoints.PRIVILEGE_ELEVATION_ADD_RULE_ASSIGNMENT, get_PE_ADD_ASSIGNMENTS_Data(cmdId, scopeType="System", scope=system[0]['ID'], principalType="Role", principal=role["Name"], bypassChallenge=False))
    
    try:
        resp = response.json()
    except Exception:
        pytest.fail(f'Cannot decode response: {response}')
    
    assert resp["success"] is False, f'PrivilegeElevation add assignment has failed {resp}'
    assert resp["Message"] == 'You are not authorized to perform this operation. Please contact your IT helpdesk.', f'PrivilegeElevation add asssignment should fail with unauthorized error {resp}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
@pytest.mark.parametrize('operating_system', ["Unix", "Windows"])
def test_pe_add_assignment_no_manage_assignment_permission_on_set(core_session, users_and_roles, create_resources, create_manual_set, setup_generic_pe_command_with_no_rules_all_OS, operating_system):
    """
    Test case: Test for principal as ad group and scope as system and the user has no Manage Assignment permission on the system
    """

    session = core_session
    admin_user = core_session.get_user()
    admin_user_name = admin_user.get_login_name()
    admin_user_id = admin_user.get_id()
    role = users_and_roles.populate_role({'Name': "role12345", "Rights": ["Admin Portal Login"]})
    userobj = users_and_roles.populate_user({'Name': 'user1'})
    users_and_roles.add_user_to_role(userobj, role)
    
    user_session = users_and_roles.get_session_for_specific_user(userobj)
    
    _, cmdId = setup_generic_pe_command_with_no_rules_all_OS
    system = create_resources(core_session, 1, operating_system)  

    # Create Set and the system to this set
    set_id = create_manual_set(
        core_session, "Server", object_ids=[system[0]['ID']])['ID']
    logger.debug(f"Successfully created a set and added system to that set: {set_id}")

    # Give all permissions but MA to the admin on the ResourceSet
    permission_string = 'Grant,View,Edit,Delete,ManageSession,AgentAuth,RequestZoneRole,AddAccount,UnlockAccount'
    result = SetsManager.set_collection_resource_permissions(core_session, permission_string,
                                                             admin_user_name, admin_user_id, set_id)
    assert result['success'], f"assigning collection permissions on the resource set for the user failed: {result}"

    response = user_session.apirequest(EndPoints.PRIVILEGE_ELEVATION_ADD_RULE_ASSIGNMENT, get_PE_ADD_ASSIGNMENTS_Data(cmdId, scopeType="Collection", scope=set_id, principalType="Role", principal=role["Name"], bypassChallenge=False))
    
    try:
        resp = response.json()
    except Exception:
        pytest.fail(f'Cannot decode response: {response}')
    
    assert resp["success"] is False, f'PrivilegeElevation add assignment has failed {resp}'
    assert resp["Message"] == 'You are not authorized to perform this operation. Please contact your IT helpdesk.', f'PrivilegeElevation add asssignment should fail with unauthorized error {resp}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_invalid_starts_expires(core_session, setup_generic_pe_command_with_no_rules_all_OS):  
    """
    Test case: All tests related to Invalid starts/Expires
    """

    _, commandID = setup_generic_pe_command_with_no_rules_all_OS
    admin_user = core_session.get_user()
    admin_user_name = admin_user.get_login_name()
    principalType = "User"
    principal = admin_user_name
    scopeType = "Global"

    # Add assignment
    assignmentID, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                  scopeType=scopeType,
                                                                  principalType=principalType, principal=principal,
                                                                  starts="abc_xyz", expires="abc_xyz")
    assert not isSuccess, f" Adding assignment passed with invalid starts/expires"

    timeNow = datetime.datetime.now().replace(microsecond=0).isoformat() + "Z"
    # Add assignment
    assignmentID, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                  scopeType=scopeType,
                                                                  principalType=principalType, principal=principal,
                                                                  starts=timeNow)
    assert not isSuccess, f" Adding assignment passed with no expires value"

    # Add assignment
    assignmentID, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                  scopeType=scopeType,
                                                                  principalType=principalType, principal=principal,
                                                                  expires=timeNow)
    assert not isSuccess, f" Adding assignment passed with no starts value"

    starts = datetime.datetime.now().replace(microsecond=0).isoformat() + "Z"
    expires = (datetime.datetime.now() - datetime.timedelta(minutes=10)).replace(microsecond=0).isoformat() + "Z"
    # Add assignment
    assignmentID, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                  scopeType=scopeType,
                                                                  principalType=principalType, principal=principal,
                                                                  starts=starts, expires=expires)
    assert not isSuccess, f" Adding assignment passed with invalid starts/expires"

@pytest.mark.api
@pytest.mark.cclient_privelevation
@pytest.mark.parametrize('operating_system', ["Unix", "Windows"])
def test_add_assignment_sysadmin_without_ma_permission_on_system(core_session, create_resources,
                                                                 setup_generic_pe_command_with_no_rules_all_OS, operating_system):
    """
    Testcase: Sysadmin without MA permission on system should pass
    """
    commandName, commandID = setup_generic_pe_command_with_no_rules_all_OS
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
    assgnmnt_info = get_PE_ASSIGNMENTS_Data(commandID=commandID, commandName=commandName, principalType="User",
                                        principal=admin_user_name, scopeType="System",
                                        scope=added_system_id, principalId=None, bypassChallenge=False)

    assgnmntID, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                  scopeType=assgnmnt_info['ScopeType'],
                                                                  scope=assgnmnt_info['Scope'],
                                                                  principalType=assgnmnt_info['PrincipalType'],
                                                                  principal=assgnmnt_info['Principal'],
                                                                  byPassChallenge=False)

    assert isSuccess, f" Adding assignment failed"
    assgnmnt_info['ID'] = assgnmntID

    # Make sure assgnmnt info is correct
    results, isSuccess = PrivilegeElevation.list_pe_assignments(core_session, commandID=commandID)
    assert isSuccess, f"List Assignments for sysadmin user failed, reason: {results}"

    assgnmnt_info_list = [assgnmnt_info]
    assert len(results['Result']) == 1 and PrivilegeElevation.check_rules_info_in_api_response(
        assgnmnt_info_list,
        results), \
        f"List Assignments complete check failed: {assgnmntID}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_add_assignment_sysadmin_without_ma_permission_on_system_set(core_session, create_manual_set,
                                                                     setup_generic_pe_command_with_no_rules_all_OS):
    """
    Testcase: Sysadmin without MA permission on system set should pass
    """
    commandName, commandID = setup_generic_pe_command_with_no_rules_all_OS
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
    assgnmnt_info = get_PE_ASSIGNMENTS_Data(commandID=commandID, commandName=commandName, principalType="User",
                                        principal=admin_user_name, scopeType="Collection",
                                        scope=set_id, principalId=None, bypassChallenge=False)

    assgnmntID, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                  scopeType=assgnmnt_info['ScopeType'],
                                                                  scope=assgnmnt_info['Scope'],
                                                                  principalType=assgnmnt_info['PrincipalType'],
                                                                  principal=assgnmnt_info['Principal'],
                                                                  byPassChallenge=False)

    assert isSuccess, f" Adding assignment failed"
    assgnmnt_info['ID'] = assgnmntID

    # Make sure assgnmnt info is correct
    results, isSuccess = PrivilegeElevation.list_pe_assignments(core_session, commandID=commandID)
    assert isSuccess, f"List Assignments for sysadmin user failed, reason: {results}"

    assgnmnt_info_list = [assgnmnt_info]
    assert len(results['Result']) == 1 and PrivilegeElevation.check_rules_info_in_api_response(
        assgnmnt_info_list,
        results), \
        f"List Assignments complete check failed: {assgnmntID}"

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_add_assignment_for_user_on_dynamic_set(core_session, users_and_roles, create_dynamic_set, setup_generic_pe_command_with_no_rules_all_OS):
    """
    Test case: Test for dynamic set is not allowed
    """

    session = core_session
    userobj = users_and_roles.populate_user({'Name': 'user1'})
    _, cmdId = setup_generic_pe_command_with_no_rules_all_OS
    
    set_id = create_dynamic_set(core_session, "Server", f"Select ID From Server Where Server.Name='{'kryptonians' + guid()}'")['ID']
    logger.info(f"Successfully created a set and added system to that set: {set_id}")

    response = session.apirequest(EndPoints.PRIVILEGE_ELEVATION_ADD_RULE_ASSIGNMENT, get_PE_ADD_ASSIGNMENTS_Data(cmdId, scopeType="Collection", scope=set_id, principalType="User", principal=userobj.get_login_name(), bypassChallenge=False))
    
    try:
        resp = response.json()
    except Exception:
        pytest.fail(f'Cannot decode response: {response}')
    
    assert resp["success"] is False, f'PrivilegeElevation add assignment has failed {resp}'
    assert 'DynamicSetNotSupportedException' in resp["Message"], f'PrivilegeElevation add asssignment should fail with DynamicSetNotSupportedException {resp}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
@pytest.mark.parametrize('operating_system', ["Unix", "Windows"])
def test_pe_add_assignment_for_group_on_set_by_non_sysadmin_user_no_edit_perm(core_session, create_resources, setup_adgroup, create_manual_set, setup_generic_pe_command_with_no_rules_all_OS, users_and_roles, operating_system):
    """
    Test case: Test for all valid params with Collection scope, principal as adgroup name added by non sysadmin user with no edit permission on set
    """

    session = core_session
    ad_group = setup_adgroup
    if ad_group is None:
        pytest.skip("Cannot retreive ad group info")
    
    _, cmdId = setup_generic_pe_command_with_no_rules_all_OS
    system = create_resources(core_session, 1, operating_system)

    # Get User
    requester_session = users_and_roles.get_session_for_user('Privilege Elevation Management')
    response = requester_session.get_current_session_user_info()
    user_info = response.json()['Result']

    # Create Set and the system to this set
    set_id = create_manual_set(
        core_session, "Server", object_ids=[system[0]['ID']])['ID']
    logger.debug(f"Successfully created a set and added system to that set: {set_id}")

    # Give the manage assignments member permission to cloud user on this set
    permission_string = 'View,ManagePrivilegeElevationAssignment'
    result = SetsManager.set_collection_resource_permissions(core_session, permission_string, user_info['Name'], user_info['Id'], set_id, "User")
    assert result["success"] is True, f'setting collection permissions failed: {result}'

    # Give the only View permission to cloud user on this set
    permission_string = 'View'
    result = SetsManager.set_collection_permissions(core_session, permission_string, user_info['Name'], user_info['Id'], set_id, "User")
    assert result['success'], f'assigning collection permissions on the resource set for the user failed: {result}'

    # user should be able to add assignment for system but not on collection if it has View permission and ManagePermissionElevationAssignment as member permission on the set
    response = requester_session.apirequest(EndPoints.PRIVILEGE_ELEVATION_ADD_RULE_ASSIGNMENT, get_PE_ADD_ASSIGNMENTS_Data(cmdId, scopeType="Collection", scope=set_id, principalType="Group", principal=ad_group["DisplayName"], bypassChallenge=False))
    
    try:
        resp = response.json()
    except Exception:
        pytest.fail(f'Cannot decode response: {response}')

    assert resp["success"] is False, f'PrivilegeElevation add assignment has failed {resp}'
    assert resp["Message"] == 'Attempted to perform an unauthorized operation.', f'PrivilegeElevation add asssignment should fail with unauthorized error {resp}'

    asmntId2, isSuccess = PrivilegeElevation.add_pe_rule_assignment(requester_session, cmdId, principalType="Group", principal=ad_group["DisplayName"], scopeType="System", scope=system[0]['ID'], byPassChallenge=False)    
    assert isSuccess is True, f'PrivilegeElevation add assignment has failed'
    
    #clean up
    errMsg, isSuccess = PrivilegeElevation.del_pe_rule_assignment(session, asmntId2)
    assert isSuccess is True, f'PrivilegeElevation add assignment failed to clean up {errMsg}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
@pytest.mark.parametrize('operating_system', ["Unix", "Windows"])
def test_pe_add_assignment_for_group_on_set_by_non_sysadmin_user_no_ma_perm(core_session, create_resources, setup_adgroup, create_manual_set, setup_generic_pe_command_with_no_rules_all_OS, users_and_roles, operating_system):
    """
    Test case: Test for all valid params with Collection scope, principal as adgroup name added by non sysadmin user with no manage assignment permission on set
    """

    session = core_session
    ad_group = setup_adgroup
    if ad_group is None:
        pytest.skip("Cannot retreive ad group info")
    
    _, cmdId = setup_generic_pe_command_with_no_rules_all_OS
    system = create_resources(core_session, 1, operating_system)

    # Get User
    requester_session = users_and_roles.get_session_for_user('Privilege Elevation Management')
    response = requester_session.get_current_session_user_info()
    user_info = response.json()['Result']

    # Create Set and the system to this set
    set_id = create_manual_set(
        core_session, "Server", object_ids=[system[0]['ID']])['ID']
    logger.debug(f"Successfully created a set and added system to that set: {set_id}")

    # Give the manage assignments member permission to cloud user on this set
    permission_string = 'View'
    result = SetsManager.set_collection_resource_permissions(core_session, permission_string, user_info['Name'], user_info['Id'], set_id, "User")
    assert result["success"] is True, f'setting collection permissions failed: {result}'

    # Give the only View permission to cloud user on this set
    permission_string = 'View, Edit'
    result = SetsManager.set_collection_permissions(core_session, permission_string, user_info['Name'], user_info['Id'], set_id, "User")
    assert result['success'], f'assigning collection permissions on the resource set for the user failed: {result}'

    # user shouldn't be able to add assignment for system  and collection if it has Edit permission and ManagePermissionElevationAssignment as member permission on the set
    response = requester_session.apirequest(EndPoints.PRIVILEGE_ELEVATION_ADD_RULE_ASSIGNMENT, get_PE_ADD_ASSIGNMENTS_Data(cmdId, scopeType="System", scope=system[0]['ID'], principalType="Group", principal=ad_group["DisplayName"], bypassChallenge=False))
    
    try:
        resp = response.json()  
    except Exception:
        pytest.fail(f'Cannot decode response: {response}')

    assert resp["success"] is False, f'PrivilegeElevation add assignment has failed {resp}'
    assert resp["Message"] == 'You are not authorized to perform this operation. Please contact your IT helpdesk.', f'PrivilegeElevation add asssignment should fail with unauthorized error {resp}'

    response = requester_session.apirequest(EndPoints.PRIVILEGE_ELEVATION_ADD_RULE_ASSIGNMENT, get_PE_ADD_ASSIGNMENTS_Data(cmdId, scopeType="Collection", scope=set_id, principalType="Group", principal=ad_group["DisplayName"], bypassChallenge=False))
    
    try:
        resp = response.json()  
    except Exception:
        pytest.fail(f'Cannot decode response: {response}')

    assert resp["success"] is False, f'PrivilegeElevation add assignment has failed {resp}'
    assert resp["Message"] == 'Attempted to perform an unauthorized operation.', f'PrivilegeElevation add asssignment should fail with unauthorized error {resp}'


@pytest.mark.api
@pytest.mark.cclient_privelevation
@pytest.mark.parametrize('operating_system', ["Unix", "Windows"])
def test_pe_add_assignment_for_group_on_set_by_non_sysadmin_role_no_edit_perm(core_session, create_resources, setup_adgroup, create_manual_set, setup_generic_pe_command_with_no_rules_all_OS, users_and_roles, operating_system):
    """
    Test case: Test for all valid params with Collection scope, principal as adgroup name added by non sysadmin role with no edit permission
    """

    session = core_session
    ad_group = setup_adgroup
    if ad_group is None:
        pytest.skip("Cannot retreive ad group info")
    
    role = users_and_roles.populate_role({'Name': "role1", "Rights": ["Admin Portal Login"]})
    _, cmdId = setup_generic_pe_command_with_no_rules_all_OS
    system = create_resources(core_session, 1, operating_system)

    # Get User
    requester_session = users_and_roles.get_session_for_user('Privilege Elevation Management')
    response = requester_session.get_current_session_user_info()
    user_info = response.json()['Result']
    logger.debug(requester_session.get_user())
    #Add user to role
    users_and_roles.add_user_to_role(requester_session.get_user(), role)

    # Create Set and the system to this set
    set_id = create_manual_set(
        core_session, "Server", object_ids=[system[0]['ID']])['ID']
    logger.debug(f"Successfully created a set and added system to that set: {set_id}")

    # Give the manage assignments member permission to cloud user on this set
    permission_string = 'View,ManagePrivilegeElevationAssignment'
    result = SetsManager.set_collection_resource_permissions(core_session, permission_string, role['Name'], role['ID'], set_id, "Role")
    assert result["success"] is True, f'setting collection permissions failed: {result}'

    # Give the View permission to cloud user on this set
    permission_string = 'View'
    result = SetsManager.set_collection_permissions(core_session, permission_string, role['Name'], role['ID'], set_id, "Role")
    assert result['success'], f'assigning collection permissions on the resource set for the user failed: {result}'

    # user should be able to add assignment for system but not on Collection if it has View permission and ManagePermissionElevationAssignment as member permission on the set
    response = requester_session.apirequest(EndPoints.PRIVILEGE_ELEVATION_ADD_RULE_ASSIGNMENT, get_PE_ADD_ASSIGNMENTS_Data(cmdId, scopeType="Collection", scope=set_id, principalType="Group", principal=ad_group["DisplayName"], bypassChallenge=False))
    
    try:
        resp = response.json()  
    except Exception:
        pytest.fail(f'Cannot decode response: {response}')

    assert resp["success"] is False, f'PrivilegeElevation add assignment has failed {resp}'
    assert resp["Message"] == 'Attempted to perform an unauthorized operation.', f'PrivilegeElevation add asssignment should fail with unauthorized error {resp}'


    asmntId2, isSuccess = PrivilegeElevation.add_pe_rule_assignment(requester_session, cmdId, principalType="Group", principal=ad_group["DisplayName"], scopeType="System", scope=system[0]['ID'], byPassChallenge=False)    
    assert isSuccess is True, f'PrivilegeElevation add assignment has failed'

    #clean up
    errMsg, isSuccess = PrivilegeElevation.del_pe_rule_assignment(session, asmntId2)
    assert isSuccess is True, f'PrivilegeElevation add assignment failed to clean up {errMsg}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
@pytest.mark.parametrize('operating_system', ["Unix", "Windows"])
def test_pe_add_assignment_for_group_on_set_by_non_sysadmin_role_no_ma_perm(core_session, create_resources, setup_adgroup, create_manual_set, setup_generic_pe_command_with_no_rules_all_OS, users_and_roles, operating_system):
    """
    Test case: Test for all valid params with Collection scope, principal as adgroup name added by non sysadmin role with no Manage Assignment permission
    """

    session = core_session
    ad_group = setup_adgroup
    if ad_group is None:
        pytest.skip("Cannot retreive ad group info")
    
    role = users_and_roles.populate_role({'Name': "role1", "Rights": ["Admin Portal Login"]})
    _, cmdId = setup_generic_pe_command_with_no_rules_all_OS
    system = create_resources(core_session, 1, operating_system)

    # Get User
    requester_session = users_and_roles.get_session_for_user('Privilege Elevation Management')
    response = requester_session.get_current_session_user_info()
    user_info = response.json()['Result']
    logger.debug(requester_session.get_user())
    #Add user to role
    users_and_roles.add_user_to_role(requester_session.get_user(), role)

    # Create Set and the system to this set
    set_id = create_manual_set(
        core_session, "Server", object_ids=[system[0]['ID']])['ID']
    logger.debug(f"Successfully created a set and added system to that set: {set_id}")

    # Give the View member permission to cloud user on this set
    permission_string = 'View'
    result = SetsManager.set_collection_resource_permissions(core_session, permission_string, role['Name'], role['ID'], set_id, "Role")
    assert result["success"] is True, f'setting collection permissions failed: {result}'

    # Give the edit permission to cloud user on this set
    permission_string = 'View,Edit'
    result = SetsManager.set_collection_permissions(core_session, permission_string, role['Name'], role['ID'], set_id, "Role")
    assert result['success'], f'assigning collection permissions on the resource set for the user failed: {result}'

    # user should be able to add assignment for system but not on Collection if it has View permission and ManagePermissionElevationAssignment as member permission on the set
    response = requester_session.apirequest(EndPoints.PRIVILEGE_ELEVATION_ADD_RULE_ASSIGNMENT, get_PE_ADD_ASSIGNMENTS_Data(cmdId, scopeType="Collection", scope=set_id, principalType="Group", principal=ad_group["DisplayName"], bypassChallenge=False))
    
    try:
        resp = response.json()  
    except Exception:
        pytest.fail(f'Cannot decode response: {response}')

    assert resp["success"] is False, f'PrivilegeElevation add assignment has failed {resp}'
    assert resp["Message"] == 'Attempted to perform an unauthorized operation.', f'PrivilegeElevation add asssignment should fail with unauthorized error {resp}'

    response = requester_session.apirequest(EndPoints.PRIVILEGE_ELEVATION_ADD_RULE_ASSIGNMENT, get_PE_ADD_ASSIGNMENTS_Data(cmdId, scopeType="System", scope=system[0]['ID'], principalType="Group", principal=ad_group["DisplayName"], bypassChallenge=False))
    
    try:
        resp = response.json()  
    except Exception:
        pytest.fail(f'Cannot decode response: {response}')

    assert resp["success"] is False, f'PrivilegeElevation add assignment has failed {resp}'
    assert resp["Message"] == 'You are not authorized to perform this operation. Please contact your IT helpdesk.', f'PrivilegeElevation add asssignment should fail with unauthorized error {resp}'
