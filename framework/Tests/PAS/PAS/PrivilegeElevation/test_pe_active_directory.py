'''
there are three tests to be written:
1. sys_admin can grant "ManageAssignment" permission to the ad group
2. aduser gets permission from the adgroup permission => As part of test_pe_can_manage_priv_elev
3. aduser's priority will be higher than the one got through adgroup
'''
import logging

from Shared.API.infrastructure import ResourceManager
from Utils.guid import guid

logger = logging.getLogger("test")
def test_sys_admin_grant_to_adGroup(core_session, setup_adgroup):
    adGroup = setup_adgroup
    if adGroup is None:
        pytest.skip("Cannot retreive ad group info")
        
    # Add System
    sys_name = "test_pe_can_manage_priv_elev" + guid()
    sys_fqdn = "fqdn" + guid()

    added_system_id, system_success_status = ResourceManager.add_system(core_session, name=sys_name,
                                                                        fqdn=sys_fqdn,
                                                                        computerclass="Unix",
                                                                        sessiontype="Ssh")

    assert system_success_status, f'Adding system failed returned status {system_success_status}'
    logger.info(f"Successfully added a System: {added_system_id}")

    # Give all permissions to the ad group
    permission_string = 'Grant,View,Edit,Delete,ManageSession,AgentAuth,RequestZoneRole,AddAccount,UnlockAccount,' \
                        'ManagePrivilegeElevationAssignment'
    result, success = ResourceManager.assign_system_permissions(core_session, permission_string,
                                                                adGroup['DisplayName'], adGroup['InternalName'],
                                                                "Group",
                                                                added_system_id)
    assert success, f"Unable to assign system permissions to adgroup: {result}"

"""
#Commenting this for now, Not seeing, priority wise results

def test_adUser_perimssion_priority(core_session, setup_user_in_ad_group, test_virtual_agent, setup_generic_pe_stuff_2):
    agent=test_virtual_agent
    adUser, adGroup, adID = setup_user_in_ad_group
    taskID1, ruleID1, taskID2, ruleID2 = setup_generic_pe_stuff_2

    #set assignment to Group
    grantSet = [{
        "Principal": adGroup['DisplayName'],
        "PrincipalId": adGroup['InternalName'],
        "PType": "Group",
        "Rights": "View,Execute,BypassMFA"
    }]
    result, isSuccess = PrivilegeElevation.set_pe_assignment_permissions(core_session, ruleID1, grantSet)
    logger.info("GroupSet:")
    logger.info(result)
    assert isSuccess

    #set assignment to user
    grantSet = [{
        "Principal": adUser['DisplayName'],
        "PrincipalId": adUser['InternalName'],
        "PType": "User",
        "Rights": "View,Execute,BypassMFA"
    }]
    result, isSuccess = PrivilegeElevation.set_pe_assignment_permissions(core_session, ruleID2, grantSet)
    logger.info("UserSet:")
    logger.info(result)
    assert isSuccess

    result, isSuccess = PrivilegeElevation.get_commands(core_session, agent.resourceName, adUser['DisplayName'])
    logger.info("GetCommands:")
    logger.info(result)
    assert isSuccess

    #Make Sure task2 appears before task1
    for assignment in result:
        if 'GlobalAssignments' in assignment:
            assert assignment['GlobalAssignments'][0]['PrivilegeElevationTask'] == taskID2
            assert assignment['GlobalAssignments'][1]['PrivilegeElevationTask'] == taskID1
"""