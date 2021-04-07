import logging

import pytest

from Shared.API.infrastructure import ResourceManager
from Shared.API.privilege_elevation import PrivilegeElevation
from Shared.API.sets import SetsManager
from Shared.centrify_session_manager import CentrifySessionManager

"""
CanManagePrivilegeElevation
1. Invalid ScopeType
2. Invalid Scope
3. Missing ScopeType
4. Missing scope
5. sys admin without explicit manageAssignment should pass for system
6. sys admin without explicit manageAssignment should pass for system set
7. Global: if sysadmin passes, if not fails
8. System: has MA permission on system passes, if not fails
9. Collection: has MA and "Edit" on collection then pass, if not fails
10. Check case of "Global System Permissions"
11. Verify AD Group permissions for a system.
12. Verify AD Group permission for a system set.
13. Non-server Collection should return false.
"""

logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_invalid_scopeType(core_session):
    canManage, isSuccess = PrivilegeElevation.can_manage_pe(core_session, scopeType="test")
    assert not isSuccess, f"Can Manage Privilege Elevation passed with invalid scopeType, reason: {canManage}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_invalid_scope(core_session):
    scope = "abc_xyz"
    canManage, isSuccess = PrivilegeElevation.can_manage_pe(core_session, scopeType="System",
                                                            scope=scope)
    assert not isSuccess, f"Can Manage Privilege Elevation passed with invalid scope: {scope}, reason: {canManage}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_missing_scopeType(core_session):
    canManage, isSuccess = PrivilegeElevation.can_manage_pe(core_session)
    assert not isSuccess, f"Can Manage Privilege Elevation passed when no params provided, reason: {canManage}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_missing_scope(core_session):
    canManage, isSuccess = PrivilegeElevation.can_manage_pe(core_session, scopeType="System")
    assert not isSuccess, f"Can Manage Privilege Elevation passed when scope not provided, " \
                          f"reason: {canManage}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_sysadmin_without_explicit_pe_assignment_system(core_session, users_and_roles, create_resources):
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

    # This sysadmin user does not have ManageAssignment permission, should still pass
    canManage, isSuccess = PrivilegeElevation.can_manage_pe(core_session, scopeType="System",
                                                            scope=added_system_id)
    assert isSuccess and canManage, f"Can Manage Privilege Elevation for sysadmin user without MA permissions on a " \
                                    f"system failed, reason: {canManage}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_sysadmin_without_explicit_pe_assignment_system_set(core_session, users_and_roles, create_manual_set):
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

    # This sysadmin user does not have ManageAssignment permission, should still pass
    canManage, isSuccess = PrivilegeElevation.can_manage_pe(core_session, scopeType="Collection",
                                                            scope=set_id)
    assert isSuccess and canManage, f"Can Manage Privilege Elevation for sysadmin user without MA permissions on a " \
                                    f"system set failed, reason: {canManage}"

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_global_scenario(core_session, users_and_roles):
    # Get User
    requester_session = users_and_roles.get_session_for_user()
    response = requester_session.get_current_session_user_info()
    user_info = response.json()['Result']
    logger.info(user_info)

    # Since not sys admin should fail
    canManage, isSuccess = PrivilegeElevation.can_manage_pe(requester_session, scopeType="Global")
    assert isSuccess and not canManage, f"Can Manage Privilege Elevation for normal user passed for Global scopeType, " \
                                        f"reason: {canManage}"

    # Get PAS power User
    requester_session = users_and_roles.get_session_for_user('Privileged Access Service Power User')
    response = requester_session.get_current_session_user_info()
    user_info = response.json()['Result']
    logger.info(user_info)

    # Since not sys admin should fail
    canManage, isSuccess = PrivilegeElevation.can_manage_pe(requester_session, scopeType="Global")
    assert isSuccess and not canManage, f"Can Manage Privilege Elevation for PAS Power user passed for Global " \
                                        f"scopeType, reason: {canManage}"

    # With sysadmin should pass
    canManage, isSuccess = PrivilegeElevation.can_manage_pe(core_session, scopeType="Global")
    assert isSuccess and canManage, f"Can Manage Privilege Elevation for sysadmin user failed for Global scopeType, " \
                                    f"reason: {canManage}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_system_scenario(core_session, users_and_roles, create_resources):
    admin_user = core_session.get_user()
    admin_user_name = admin_user.get_login_name()
    admin_user_id = admin_user.get_id()

    # Get User
    requester_session = users_and_roles.get_session_for_user('Privilege Elevation Management')
    response = requester_session.get_current_session_user_info()
    user_info = response.json()['Result']
    logger.info(user_info)

    # Add System
    added_system_id = create_resources(core_session, 1, "Unix")[0]['ID']

    logger.info(f"Successfully added a System: {added_system_id}")

    # Give all permissions to the admin
    permission_string = 'Grant,View,Edit,Delete,ManageSession,AgentAuth,RequestZoneRole,AddAccount,UnlockAccount,' \
                        'ManagePrivilegeElevationAssignment'
    result, success = ResourceManager.assign_system_permissions(core_session, permission_string,
                                                                admin_user_name, admin_user_id, "User",
                                                                added_system_id)
    assert success, f"Unable to set system permissions for admin: {result}"

    # Give all permission but the ManageAssignment permission to the PE User
    permission_string = 'Grant,View,Edit,Delete,ManageSession,AgentAuth,RequestZoneRole,AddAccount,UnlockAccount'
    result, success = ResourceManager.assign_system_permissions(core_session, permission_string,
                                                                user_info['Name'], user_info['Id'], "User",
                                                                added_system_id)
    assert success, f"Unable to set system permissions for user: {result}"

    # This user does not have ManageAssignment permission, so should fail
    canManage, isSuccess = PrivilegeElevation.can_manage_pe(requester_session, scopeType="System",
                                                            scope=added_system_id)
    assert isSuccess and not canManage, f"Can Manage Privilege Elevation for PE user with no MA permissions on a " \
                                        f"system passed, reason: {canManage}"

    # Add MA permission to the user on the system
    permission_string = 'Grant,View,Edit,Delete,ManageSession,AgentAuth,RequestZoneRole,AddAccount,UnlockAccount,' \
                        'ManagePrivilegeElevationAssignment'
    result, success = ResourceManager.assign_system_permissions(core_session, permission_string,
                                                                user_info['Name'], user_info['Id'], "User",
                                                                added_system_id)
    assert success, f"Unable to set system permissions for user: {result}"

    # Should pass now
    canManage, isSuccess = PrivilegeElevation.can_manage_pe(requester_session, scopeType="System",
                                                            scope=added_system_id)
    assert isSuccess and canManage, f"Can Manage Privilege Elevation for PE user with MA permissions on a " \
                                    f"system failed, reason: {canManage}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_collection_scenario(core_session, users_and_roles, create_resources, create_manual_set):
    admin_user = core_session.get_user()
    admin_user_name = admin_user.get_login_name()
    admin_user_id = admin_user.get_id()

    # Get User
    requester_session = users_and_roles.get_session_for_user('Privileged Access Service Power User')
    response = requester_session.get_current_session_user_info()
    user_info = response.json()['Result']
    logger.info(user_info)

    # Add System
    added_system_id = create_resources(core_session, 1, "Unix")[0]['ID']
    logger.info(f"Successfully added a System: {added_system_id}")

    # Create Set and the system to this set
    set_id = create_manual_set(
        core_session, "Server", object_ids=[added_system_id])['ID']

    logger.info(f"Successfully created a set and added system to that set: {set_id}")

    # Give all permissions to the admin on the set
    permission_string = 'Grant,View,Edit,Delete'
    result = SetsManager.set_collection_permissions(core_session, permission_string,
                                                    admin_user_name, admin_user_id, set_id)
    logger.info(result)
    assert result['success'], "assigning collection permissions on the set for the user, failed: " + result

    # Give all permissions to the admin on the ResourceSet
    permission_string = 'Grant,View,Edit,Delete,ManageSession,AgentAuth,RequestZoneRole,AddAccount,UnlockAccount,' \
                        'ManagePrivilegeElevationAssignment'
    result = SetsManager.set_collection_resource_permissions(core_session, permission_string,
                                                             admin_user_name, admin_user_id, set_id)
    logger.info(result)
    assert result['success'], "assigning collection permissions on the resource set  for the user failed: " + result

    # Give all permission for the user on the set
    permission_string = 'Grant,View,Edit,Delete'
    result = SetsManager.set_collection_permissions(core_session, permission_string,
                                                    user_info['Name'], user_info['Id'], set_id)
    assert result['success'], "assigning collection permissions on the set for the user, failed: " + result

    # Give all permission but the MA permission to the PAS user on the resource Set
    permission_string = 'Grant,View,Edit,Delete,ManageSession,AgentAuth,RequestZoneRole,AddAccount,UnlockAccount'
    result = SetsManager.set_collection_resource_permissions(core_session, permission_string,
                                                             user_info['Name'], user_info['Id'], set_id)
    assert result['success'], "assigning collection permissions on the resource set  for the user failed: " + result

    new_set = SetsManager.get_collection(requester_session, set_id)
    logger.info(new_set)

    # This user does not have MA permission, so should fail
    canManage, isSuccess = PrivilegeElevation.can_manage_pe(requester_session, scopeType="Collection",
                                                            scope=set_id)
    assert isSuccess and not canManage, f"Can Manage Privilege Elevation for PAS power user with no MA permissions on " \
                                        f"a set passed, reason: {canManage}"

    # Now assign MA permission but not Edit permission to the user
    permission_string = 'Grant,View,Delete'
    result = SetsManager.set_collection_permissions(core_session, permission_string,
                                                    user_info['Name'], user_info['Id'], set_id)
    assert result['success'], "assigning collection permissions for the user failed: " + result

    # This user does not have Edit permission, so should fail
    canManage, isSuccess = PrivilegeElevation.can_manage_pe(requester_session, scopeType="Collection",
                                                            scope=set_id)
    assert isSuccess and not canManage, f"Can Manage Privilege Elevation for PAS power user with no Edit permissions on " \
                                        f"a set passed, reason: {canManage}"

    # Now assign MA permission and Edit permission to the user
    permission_string = 'Grant,View,Edit,Delete,ManageSession,AgentAuth,RequestZoneRole,AddAccount,UnlockAccount,' \
                        'ManagePrivilegeElevationAssignment'
    result = SetsManager.set_collection_resource_permissions(core_session, permission_string,
                                                             user_info['Name'], user_info['Id'], set_id,
                                                             "User")
    assert result['success'], "assigning collection permissions for the user failed: " + result

    permission_string = 'Grant,View,Edit,Delete'
    result = SetsManager.set_collection_permissions(core_session, permission_string,
                                                    user_info['Name'], user_info['Id'], set_id)
    assert result['success'], "assigning collection permissions for the user failed: " + result

    # This user has Edit and MA permissions on the set, should pass
    canManage, isSuccess = PrivilegeElevation.can_manage_pe(requester_session, scopeType="Collection",
                                                            scope=set_id)
    assert isSuccess and canManage, f"Can Manage Privilege Elevation for PAS power user with Edit and MA permissions on " \
                                    f"a set failed, reason: {canManage}"

    # This sysadmin user does have MA permission, so should pass
    canManage, isSuccess = PrivilegeElevation.can_manage_pe(core_session, scopeType="Collection",
                                                            scope=set_id)
    assert isSuccess and canManage, f"Can Manage Privilege Elevation for sys admin user with MA permissions on " \
                                    f"a set failed, reason: {canManage}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_global_system_permissions(core_session, users_and_roles, create_resources):
    # Get User
    requester_session = users_and_roles.get_session_for_user('Privileged Access Service Power User')
    response = requester_session.get_current_session_user_info()
    user_info = response.json()['Result']
    logger.info(user_info)

    # Assign global system permissions to the PAS power User
    permission_string = 'Grant,View,Edit,Delete,ManageSession,AgentAuth,RequestZoneRole,AddAccount,UnlockAccount,' \
                        'ManagePrivilegeElevationAssignment'
    result, success = ResourceManager.assign_system_permissions(core_session, permission_string,
                                                                user_info['Name'], user_info['Id'], "User")
    assert success, f"Unable to set global system permissions: {result}"

    # Add System
    added_system_id = create_resources(core_session, 1, "Unix")[0]['ID']
    logger.info(f"Successfully added a System: {added_system_id}")

    result, success = PrivilegeElevation.can_manage_pe(requester_session, scopeType="System", scope=added_system_id)
    assert success and result, f"Can Manage Privilege Elevation for PAS power user with MA permissions failed:" \
                               f"{result}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_adUser_permission_through_adGroup_system(core_session, setup_aduser, setup_user_in_ad_group, create_resources):
    adUser, adUserPwd, adGroup = setup_user_in_ad_group
    if adGroup is None:
        pytest.skip("Cannot retreive ad group info")
    # Setup another ad user that's not part of above adGroup
    adUser2, adUserPwd2 = setup_aduser
    # Add System
    added_system_id = create_resources(core_session, 1, "Unix")[0]['ID']
    logger.info(f"Successfully added a System: {added_system_id}")

    # Give all permissions to the ad group
    permission_string = 'Grant,View,Edit,Delete,ManageSession,AgentAuth,RequestZoneRole,AddAccount,UnlockAccount,' \
                        'ManagePrivilegeElevationAssignment'
    result, success = ResourceManager.assign_system_permissions(core_session, permission_string,
                                                                adGroup['DisplayName'], adGroup['InternalName'],
                                                                "Group",
                                                                added_system_id)
    assert success, f"Unable to assign system permissions to adgroup: {result}"

    ad_user_session = CentrifySessionManager(
        core_session.url, core_session.tenant_id)
    ad_user_session.security_login(
        core_session.tenant_id,
        adUser['SystemName'],
        adUserPwd
    )

    # Should pass
    result, success = PrivilegeElevation.can_manage_pe(ad_user_session, scopeType="System", scope=added_system_id)
    assert success and result, f"Can Manage Privilege Elevation for adUser within an adgroup with MA permissions failed:" \
                               f"{result}"

    ad_user_session = CentrifySessionManager(
        core_session.url, core_session.tenant_id)
    ad_user_session.security_login(
        core_session.tenant_id,
        adUser2['SystemName'],
        adUserPwd2
    )

    # Should fail
    result, success = PrivilegeElevation.can_manage_pe(ad_user_session, scopeType="System", scope=added_system_id)
    assert success and not result, f"Can Manage Privilege Elevation for adUser not within an adgroup with MA " \
                                   f"permissions passed: {result}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_adUser_permission_through_adGroup_system_set(core_session, setup_aduser, setup_user_in_ad_group,
                                                      create_resources,
                                                      create_manual_set):
    adUser, adUserPwd, adGroup = setup_user_in_ad_group
    if adGroup is None:
        pytest.skip("Cannot retreive ad group info")
    # Setup another ad user that's not part of above adGroup
    adUser2, adUserPwd2 = setup_aduser
    # Add System
    added_system_id = create_resources(core_session, 1, "Unix")[0]['ID']
    logger.info(f"Successfully added a System: {added_system_id}")

    # Create Set and the system to this set
    set_id = create_manual_set(
        core_session, "Server", object_ids=[added_system_id])['ID']

    logger.info(f"Successfully created a set and added system to that set: {set_id}")

    # Give all permissions to the ad group on the set
    permission_string = 'Grant,View,Edit,Delete'
    result = SetsManager.set_collection_permissions(core_session, permission_string,
                                                    adGroup['DisplayName'], adGroup['InternalName'], set_id,
                                                    ptype="Group")
    logger.info(result)
    assert result['success'], "assigning admin collection permissions on the set failed: " + result

    # Give all permissions to the ad group on the ResourceSet
    permission_string = 'Grant,View,Edit,Delete,ManageSession,AgentAuth,RequestZoneRole,AddAccount,UnlockAccount,' \
                        'ManagePrivilegeElevationAssignment'
    result = SetsManager.set_collection_resource_permissions(core_session, permission_string,
                                                             adGroup['DisplayName'], adGroup['InternalName'], set_id,
                                                             ptype="Group")
    logger.info(result)
    assert result['success'], "assigning admin collection permissions on the resourceSet failed: " + result

    ad_user_session = CentrifySessionManager(
        core_session.url, core_session.tenant_id)
    ad_user_session.security_login(
        core_session.tenant_id,
        adUser['SystemName'],
        adUserPwd
    )

    # should pass
    result, success = PrivilegeElevation.can_manage_pe(ad_user_session, scopeType="Collection", scope=set_id)
    assert success and result, f"Can Manage Privilege Elevation for adUser within an adgroup with MA permissions failed:" \
                               f"{result}"

    ad_user_session = CentrifySessionManager(
        core_session.url, core_session.tenant_id)
    ad_user_session.security_login(
        core_session.tenant_id,
        adUser2['SystemName'],
        adUserPwd2
    )

    # Should fail
    result, success = PrivilegeElevation.can_manage_pe(ad_user_session, scopeType="System", scope=added_system_id)
    assert success and not result, f"Can Manage Privilege Elevation for adUser not within an adgroup with MA " \
                                   f"permissions passed: {result}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_nonServer_collection_scenario(core_session, users_and_roles, create_resources, create_manual_set):
    admin_user = core_session.get_user()
    admin_user_name = admin_user.get_login_name()
    admin_user_id = admin_user.get_id()

    # Create nonServer Set
    set_id = create_manual_set(core_session, "VaultDatabase").get("ID", None)
    assert set_id is not None, f"set_id cannot be empty"

    logger.info(f"Successfully created a set: {set_id}")

    # Give all permissions to the admin on the set
    permission_string = 'Grant,View,Edit,Delete'
    result = SetsManager.set_collection_permissions(core_session, permission_string,
                                                    admin_user_name, admin_user_id, set_id)
    logger.info(result)
    assert result['success'], "assigning collection permissions on the set for the admin user, failed: " + result

    # Not a server collection, should fail
    canManage, isSuccess = PrivilegeElevation.can_manage_pe(core_session, scopeType="Collection",
                                                            scope=set_id)
    assert isSuccess and not canManage, f"Can Manage Privilege Elevation for nonServer set passed, reason: {canManage}"
