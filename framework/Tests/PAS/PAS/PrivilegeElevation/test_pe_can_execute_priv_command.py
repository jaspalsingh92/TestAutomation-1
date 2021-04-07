import logging

import pytest
from Shared.API.agent import get_PE_ASSIGNMENTS_Data
from Shared.API.infrastructure import ResourceManager
from Shared.API.privilege_elevation import PrivilegeElevation
from Shared.endpoint_manager import EndPoints
from Shared.util import Util
from Utils.guid import guid

logger = logging.getLogger("test")

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_starts_expires(core_session, setup_generic_pe_command_with_no_rules, cleanup_servers):

    # Add System
    sys_name = "test_pe_can_execute_priv_command" + guid()
    sys_fqdn = "fqdn" + guid()
    added_system_id, system_success_status = ResourceManager.add_system(core_session, name=sys_name,
                                                                        fqdn=sys_fqdn,
                                                                        computerclass="Unix",
                                                                        sessiontype="Ssh")
    assert system_success_status, f'Adding system failed returned status {system_success_status}'
    logger.debug(f"Successfully added a System: {added_system_id}")

    cleanup_servers.append(added_system_id)

    commandName, commandID = setup_generic_pe_command_with_no_rules

    # Get Admin info
    admin_user = core_session.get_user()
    admin_user_name = admin_user.get_login_name()
    admin_user_id = admin_user.get_id()

    # Add assignment
    asmnt_info = get_PE_ASSIGNMENTS_Data(commandID=commandID, commandName=commandName, principalType="User",
                                         principal=admin_user_name, scopeType="Global",
                                         scope=None, principalId=admin_user_id,
                                         bypassChallenge=True)
    asmntID, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                   scopeType=asmnt_info['ScopeType'],
                                                                   principalType=asmnt_info['PrincipalType'],
                                                                   principalID=asmnt_info['PrincipalId'],
                                                                   byPassChallenge=True,
                                                                   starts=asmnt_info['Starts'],
                                                                   expires=asmnt_info['Expires'])
    assert isSuccess, f" Adding assignment failed"
    asmnt_info['ID'] = asmntID

    # Get assignments
    results, isSuccess = PrivilegeElevation.can_execute_priv_command(core_session,
                                                                     user=admin_user_name, system=sys_name,
                                                                     command="sudo date")
    assert isSuccess, f"CanExecutePrivilegeCommand failed, reason: {results}"

    
    assert len(results['PrivilegeElevationCommands']) == 1, f"Only single command should exist {results}"
    results_assignments = results['PrivilegeElevationCommands'][0]['Assignments']

    assert len(results_assignments) == 1 and results_assignments[0]['Starts'] == asmnt_info['Starts'] \
           and results_assignments[0]['Expires'] == asmnt_info['Expires'], f"Starts/Expires not matching {results}"
    #clean up
    errMsg, isSuccess = PrivilegeElevation.del_pe_rule_assignment(core_session, asmntID)
    assert isSuccess is True, f'Test test_starts_expires failed to clean up {errMsg}'


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_can_execute_priv_command_sys_asmnt_on_user(core_session, setup_generic_pe_command_with_no_rules, cleanup_servers):
    # Add System
    sys_name = "test_pe_can_execute_priv_command" + guid()
    sys_fqdn = "fqdn" + guid()
    added_system_id, system_success_status = ResourceManager.add_system(core_session, name=sys_name,
                                                                        fqdn=sys_fqdn,
                                                                        computerclass="Unix",
                                                                        sessiontype="Ssh")
    assert system_success_status, f'Adding system failed returned status {system_success_status}'
    logger.debug(f"Successfully added a System: {added_system_id}")

    cleanup_servers.append(added_system_id)

    commandName, commandID = setup_generic_pe_command_with_no_rules

    # Get Admin info
    admin_user = core_session.get_user()
    admin_user_name = admin_user.get_login_name()
    admin_user_id = admin_user.get_id()

    # Add assignment
    asmnt_info = get_PE_ASSIGNMENTS_Data(commandID=commandID, commandName=commandName, principalType="User",
                                         principal=admin_user_name, scopeType="System",
                                         scope=added_system_id, principalId=admin_user_id,
                                         bypassChallenge=True)
    asmntID, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                   scopeType=asmnt_info['ScopeType'],
                                                                   scope=asmnt_info['Scope'],
                                                                   principalType=asmnt_info['PrincipalType'],
                                                                   principalID=asmnt_info['PrincipalId'],
                                                                   byPassChallenge=True,
                                                                   starts=asmnt_info['Starts'],
                                                                   expires=asmnt_info['Expires'])
    assert isSuccess, f"Adding assignment failed"
    asmnt_info['ID'] = asmntID

    results, isSuccess = PrivilegeElevation.can_execute_priv_command(core_session,
                                                                     user=admin_user_name, system=sys_name,
                                                                     command="sudo date")
    assert isSuccess, f"CanExecutePrivilegeCommand failed, reason: {results}"

    assert len(results['PrivilegeElevationCommands']) == 1, f"Only single command should exist {results}"
    results_assignments = results['PrivilegeElevationCommands'][0]['Assignments']

    assert len(results_assignments) == 1 and results['Granted'], f"Granted should be true"
    PrivilegeElevation.check_can_execute_priv_command_results(asmnt_info, results['PrivilegeElevationCommands'][0]), f"All params not matching {results}"
    #clean up
    errMsg, isSuccess = PrivilegeElevation.del_pe_rule_assignment(core_session, asmntID)
    assert isSuccess is True, f'PrivilegeElevation add assignment failed to clean up {errMsg}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_can_execute_priv_command_set_asmnt_on_user(core_session, setup_generic_pe_command_with_no_rules, create_manual_set, cleanup_servers):
    # Add System
    sys_name = "test_pe_can_execute_priv_command" + guid()
    sys_fqdn = "fqdn" + guid()
    added_system_id, system_success_status = ResourceManager.add_system(core_session, name=sys_name,
                                                                        fqdn=sys_fqdn,
                                                                        computerclass="Unix",
                                                                        sessiontype="Ssh")
    assert system_success_status, f'Adding system failed returned status {system_success_status}'
    logger.debug(f"Successfully added a System: {added_system_id}")
    cleanup_servers.append(added_system_id)

    # Create Set and the system to this set
    set_id = create_manual_set(
        core_session, "Server", object_ids=[added_system_id])['ID']
    logger.debug(f"Successfully created a set and added system to that set: {set_id}")

    commandName, commandID = setup_generic_pe_command_with_no_rules
    
    # Get Admin info
    admin_user = core_session.get_user()
    admin_user_name = admin_user.get_login_name()
    admin_user_id = admin_user.get_id()

    # Add assignment
    asmnt_info = get_PE_ASSIGNMENTS_Data(commandID=commandID, commandName=commandName, principalType="User",
                                         principal=admin_user_name, scopeType="Collection",
                                         scope=set_id, principalId=admin_user_id,
                                         bypassChallenge=True)
    asmntID, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                   scopeType=asmnt_info['ScopeType'],
                                                                   scope=asmnt_info['Scope'],
                                                                   principalType=asmnt_info['PrincipalType'],
                                                                   principalID=asmnt_info['PrincipalId'],
                                                                   byPassChallenge=True,
                                                                   starts=asmnt_info['Starts'],
                                                                   expires=asmnt_info['Expires'])
    assert isSuccess, f"Adding assignment failed"
    asmnt_info['ID'] = asmntID

    results, isSuccess = PrivilegeElevation.can_execute_priv_command(core_session,
                                                                     user=admin_user_name, system=sys_name,
                                                                     command="sudo date")
    assert isSuccess, f"CanExecutePrivilegeCommand failed, reason: {results}"

    assert len(results['PrivilegeElevationCommands']) == 1, f"Only single command should exist {results}"
    results_assignments = results['PrivilegeElevationCommands'][0]['Assignments']

    assert len(results_assignments) == 1 and results['Granted'], f"Granted should be true"
    PrivilegeElevation.check_can_execute_priv_command_results(asmnt_info, results['PrivilegeElevationCommands'][0]), f"All params not matching {results}"
    #clean up
    errMsg, isSuccess = PrivilegeElevation.del_pe_rule_assignment(core_session, asmntID)
    assert isSuccess is True, f'PrivilegeElevation add assignment failed to clean up {errMsg}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_can_execute_priv_command_sys_asmnt_on_sysadmin_role(core_session, setup_generic_pe_command_with_no_rules, cleanup_servers):
    # Add System
    sys_name = "test_pe_can_execute_priv_command" + guid()
    sys_fqdn = "fqdn" + guid()
    added_system_id, system_success_status = ResourceManager.add_system(core_session, name=sys_name,
                                                                        fqdn=sys_fqdn,
                                                                        computerclass="Unix",
                                                                        sessiontype="Ssh")
    assert system_success_status, f'Adding system failed returned status {system_success_status}'
    logger.debug(f"Successfully added a System: {added_system_id}")

    cleanup_servers.append(added_system_id)

    commandName, commandID = setup_generic_pe_command_with_no_rules

    # Get Admin info
    admin_user = core_session.get_user()
    admin_user_name = admin_user.get_login_name()
    admin_user_id = admin_user.get_id()

    # Add assignment
    asmnt_info = get_PE_ASSIGNMENTS_Data(commandID=commandID, commandName=commandName, principalType="Role",
                                         principal="System Administrator", scopeType="System",
                                         scope=added_system_id, principalId=None,
                                         bypassChallenge=True)
    asmntID, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                   scopeType=asmnt_info['ScopeType'],
                                                                   scope=asmnt_info['Scope'],
                                                                   principalType=asmnt_info['PrincipalType'],
                                                                   principal=asmnt_info['Principal'],
                                                                   byPassChallenge=True,
                                                                   starts=asmnt_info['Starts'],
                                                                   expires=asmnt_info['Expires'])
    assert isSuccess, f"Adding assignment failed"
    asmnt_info['ID'] = asmntID

    results, isSuccess = PrivilegeElevation.can_execute_priv_command(core_session,
                                                                     user=admin_user_name, system=sys_name,
                                                                     command="sudo date")
    assert isSuccess, f"CanExecutePrivilegeCommand failed, reason: {results}"

    assert len(results['PrivilegeElevationCommands']) == 1, f"Only single command should exist {results}"
    results_assignments = results['PrivilegeElevationCommands'][0]['Assignments']

    assert len(results_assignments) == 1 and results['Granted'], f"Granted should be true"
    PrivilegeElevation.check_can_execute_priv_command_results(asmnt_info, results['PrivilegeElevationCommands'][0]), f"All params not matching {results}"
    #clean up
    errMsg, isSuccess = PrivilegeElevation.del_pe_rule_assignment(core_session, asmntID)
    assert isSuccess is True, f'PrivilegeElevation add assignment failed to clean up {errMsg}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_can_execute_priv_command_sys_asmnt_on_non_sysadmin_role(core_session, setup_generic_pe_command_with_no_rules, users_and_roles, cleanup_servers):
    # Add System
    sys_name = "test_pe_can_execute_priv_command" + guid()
    sys_fqdn = "fqdn" + guid()
    added_system_id, system_success_status = ResourceManager.add_system(core_session, name=sys_name,
                                                                        fqdn=sys_fqdn,
                                                                        computerclass="Unix",
                                                                        sessiontype="Ssh")
    assert system_success_status, f'Adding system failed returned status {system_success_status}'
    logger.debug(f"Successfully added a System: {added_system_id}")

    cleanup_servers.append(added_system_id)

    commandName, commandID = setup_generic_pe_command_with_no_rules
    role = users_and_roles.populate_role({'Name': "can_exec_role" + guid(), "Rights": ["Admin Portal Login"]})
    # Get User
    userobj = users_and_roles.populate_user({'Name': 'user' + guid()})
    #Add user to role
    users_and_roles.add_user_to_role(userobj, role)
    
    # Add assignment
    asmnt_info = get_PE_ASSIGNMENTS_Data(commandID=commandID, commandName=commandName, principalType="Role",
                                         principalId=role['ID'], scopeType="System",
                                         scope=added_system_id, principal=None,
                                         bypassChallenge=True)
    asmntID, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                   scopeType=asmnt_info['ScopeType'],
                                                                   scope=asmnt_info['Scope'],
                                                                   principalType=asmnt_info['PrincipalType'],
                                                                   principalID=asmnt_info['PrincipalId'],
                                                                   byPassChallenge=True,
                                                                   starts=asmnt_info['Starts'],
                                                                   expires=asmnt_info['Expires'])
    assert isSuccess, f"Adding assignment failed"
    asmnt_info['ID'] = asmntID

    results, isSuccess = PrivilegeElevation.can_execute_priv_command(core_session,
                                                                     user=userobj.get_login_name(), system=sys_name,
                                                                     command="sudo date")
    assert isSuccess, f"CanExecutePrivilegeCommand failed, reason: {results}"

    assert len(results['PrivilegeElevationCommands']) == 1, f"Only single command should exist {results}"
    results_assignments = results['PrivilegeElevationCommands'][0]['Assignments']

    assert len(results_assignments) == 1 and results['Granted'], f"Granted should be true"
    PrivilegeElevation.check_can_execute_priv_command_results(asmnt_info, results['PrivilegeElevationCommands'][0]), f"All params not matching {results}"
    #clean up
    errMsg, isSuccess = PrivilegeElevation.del_pe_rule_assignment(core_session, asmntID)
    assert isSuccess is True, f'PrivilegeElevation add assignment failed to clean up {errMsg}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_can_execute_priv_command_set_asmnt_on_sysadmin_role(core_session, setup_generic_pe_command_with_no_rules, create_manual_set, cleanup_servers):
    # Add System
    sys_name = "test_pe_can_execute_priv_command" + guid()
    sys_fqdn = "fqdn" + guid()
    added_system_id, system_success_status = ResourceManager.add_system(core_session, name=sys_name,
                                                                        fqdn=sys_fqdn,
                                                                        computerclass="Unix",
                                                                        sessiontype="Ssh")
    assert system_success_status, f'Adding system failed returned status {system_success_status}'
    logger.debug(f"Successfully added a System: {added_system_id}")
    cleanup_servers.append(added_system_id)

    # Create Set and the system to this set
    set_id = create_manual_set(
        core_session, "Server", object_ids=[added_system_id])['ID']
    logger.debug(f"Successfully created a set and added system to that set: {set_id}")

    commandName, commandID = setup_generic_pe_command_with_no_rules
    
    # Get Admin info
    admin_user = core_session.get_user()
    admin_user_name = admin_user.get_login_name()
    admin_user_id = admin_user.get_id()

    # Add assignment
    asmnt_info = get_PE_ASSIGNMENTS_Data(commandID=commandID, commandName=commandName, principalType="Role",
                                         principal="System Administrator", scopeType="Collection",
                                         scope=set_id, principalId=None,
                                         bypassChallenge=True)
    asmntID, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                   scopeType=asmnt_info['ScopeType'],
                                                                   scope=asmnt_info['Scope'],
                                                                   principalType=asmnt_info['PrincipalType'],
                                                                   principal=asmnt_info['Principal'],
                                                                   byPassChallenge=True,
                                                                   starts=asmnt_info['Starts'],
                                                                   expires=asmnt_info['Expires'])
    assert isSuccess, f"Adding assignment failed"
    asmnt_info['ID'] = asmntID

    results, isSuccess = PrivilegeElevation.can_execute_priv_command(core_session,
                                                                     user=admin_user_name, system=sys_name,
                                                                     command="sudo date")
    assert isSuccess, f"CanExecutePrivilegeCommand failed, reason: {results}"

    assert len(results['PrivilegeElevationCommands']) == 1, f"Only single command should exist {results}"
    results_assignments = results['PrivilegeElevationCommands'][0]['Assignments']

    assert len(results_assignments) == 1 and results['Granted'], f"Granted should be true"
    PrivilegeElevation.check_can_execute_priv_command_results(asmnt_info, results['PrivilegeElevationCommands'][0]), f"All params not matching {results}"
    #clean up
    errMsg, isSuccess = PrivilegeElevation.del_pe_rule_assignment(core_session, asmntID)
    assert isSuccess is True, f'PrivilegeElevation add assignment failed to clean up {errMsg}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_can_execute_priv_command_set_asmnt_on_non_sysadmin_role(core_session, setup_generic_pe_command_with_no_rules, create_manual_set, users_and_roles, cleanup_servers):
    # Add System
    sys_name = "test_pe_can_execute_priv_command" + guid()
    sys_fqdn = "fqdn" + guid()
    added_system_id, system_success_status = ResourceManager.add_system(core_session, name=sys_name,
                                                                        fqdn=sys_fqdn,
                                                                        computerclass="Unix",
                                                                        sessiontype="Ssh")
    assert system_success_status, f'Adding system failed returned status {system_success_status}'
    logger.debug(f"Successfully added a System: {added_system_id}")
    cleanup_servers.append(added_system_id)

    # Create Set and the system to this set
    set_id = create_manual_set(
        core_session, "Server", object_ids=[added_system_id])['ID']
    logger.debug(f"Successfully created a set and added system to that set: {set_id}")

    commandName, commandID = setup_generic_pe_command_with_no_rules
    role = users_and_roles.populate_role({'Name': "can_exec_role" + guid(), "Rights": ["Admin Portal Login"]})
    # Get User
    userobj = users_and_roles.populate_user({'Name': 'user' + guid()})
    #Add user to role
    users_and_roles.add_user_to_role(userobj, role)

    # Add assignment
    asmnt_info = get_PE_ASSIGNMENTS_Data(commandID=commandID, commandName=commandName, principalType="Role",
                                         principal=role['Name'], scopeType="Collection",
                                         scope=set_id, principalId=None,
                                         bypassChallenge=True)
    asmntID, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                   scopeType=asmnt_info['ScopeType'],
                                                                   scope=asmnt_info['Scope'],
                                                                   principalType=asmnt_info['PrincipalType'],
                                                                   principal=asmnt_info['Principal'],
                                                                   byPassChallenge=True,
                                                                   starts=asmnt_info['Starts'],
                                                                   expires=asmnt_info['Expires'])
    assert isSuccess, f"Adding assignment failed"
    asmnt_info['ID'] = asmntID

    results, isSuccess = PrivilegeElevation.can_execute_priv_command(core_session,
                                                                     user=userobj.get_login_name(), system=sys_name,
                                                                     command="sudo date")
    assert isSuccess, f"CanExecutePrivilegeCommand failed, reason: {results}"

    assert len(results['PrivilegeElevationCommands']) == 1, f"Only single command should exist {results}"
    results_assignments = results['PrivilegeElevationCommands'][0]['Assignments']

    assert len(results_assignments) == 1 and results['Granted'], f"Granted should be true"
    PrivilegeElevation.check_can_execute_priv_command_results(asmnt_info, results['PrivilegeElevationCommands'][0]), f"All params not matching {results}"
    #clean up
    errMsg, isSuccess = PrivilegeElevation.del_pe_rule_assignment(core_session, asmntID)
    assert isSuccess is True, f'PrivilegeElevation add assignment failed to clean up {errMsg}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_can_execute_priv_command_sys_asmnt_on_adgroup(core_session, setup_generic_pe_command_with_no_rules, setup_user_in_ad_group, cleanup_servers):
    # Add System
    sys_name = "test_pe_can_execute_priv_command" + guid()
    sys_fqdn = "fqdn" + guid()
    added_system_id, system_success_status = ResourceManager.add_system(core_session, name=sys_name,
                                                                        fqdn=sys_fqdn,
                                                                        computerclass="Unix",
                                                                        sessiontype="Ssh")
    assert system_success_status, f'Adding system failed returned status {system_success_status}'
    logger.debug(f"Successfully added a System: {added_system_id}")

    cleanup_servers.append(added_system_id)

    commandName, commandID = setup_generic_pe_command_with_no_rules
    
    aduser, _, adgroup = setup_user_in_ad_group
    if adgroup is None:
        pytest.skip("Cannot create adgroup")
    
    # Add assignment
    asmnt_info = get_PE_ASSIGNMENTS_Data(commandID=commandID, commandName=commandName, principalType="Group",
                                         principal=adgroup['DisplayName'], scopeType="System",
                                         scope=added_system_id, principalId=None,
                                         bypassChallenge=True)
    asmntID, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                   scopeType=asmnt_info['ScopeType'],
                                                                   scope=asmnt_info['Scope'],
                                                                   principalType=asmnt_info['PrincipalType'],
                                                                   principal=asmnt_info['Principal'],
                                                                   byPassChallenge=True,
                                                                   starts=asmnt_info['Starts'],
                                                                   expires=asmnt_info['Expires'])
    assert isSuccess, f"Adding assignment failed"
    asmnt_info['ID'] = asmntID

    results, isSuccess = PrivilegeElevation.can_execute_priv_command(core_session,
                                                                     user=aduser['SystemName'], system=sys_name,
                                                                     command="sudo date")
    assert isSuccess, f"CanExecutePrivilegeCommand failed, reason: {results}"

    assert len(results['PrivilegeElevationCommands']) == 1, f"Only single command should exist {results}"
    results_assignments = results['PrivilegeElevationCommands'][0]['Assignments']

    assert len(results_assignments) == 1 and results['Granted'], f"Granted should be true"
    PrivilegeElevation.check_can_execute_priv_command_results(asmnt_info, results['PrivilegeElevationCommands'][0]), f"All params not matching {results}"
    #clean up
    errMsg, isSuccess = PrivilegeElevation.del_pe_rule_assignment(core_session, asmntID)
    assert isSuccess is True, f'PrivilegeElevation add assignment failed to clean up {errMsg}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_can_execute_priv_command_set_asmnt_on_adgroup(core_session, setup_user_in_ad_group, setup_generic_pe_command_with_no_rules_all_OS, create_manual_set, users_and_roles, cleanup_servers):
    # Add System
    sys_name = "test_pe_can_execute_priv_command" + guid()
    sys_fqdn = "fqdn" + guid()
    added_system_id, system_success_status = ResourceManager.add_system(core_session, name=sys_name,
                                                                        fqdn=sys_fqdn,
                                                                        computerclass="Windows",
                                                                        sessiontype="Rdp")
    assert system_success_status, f'Adding system failed returned status {system_success_status}'
    logger.debug(f"Successfully added a System: {added_system_id}")
    cleanup_servers.append(added_system_id)

    # Create Set and the system to this set
    set_id = create_manual_set(
        core_session, "Server", object_ids=[added_system_id])['ID']
    logger.debug(f"Successfully created a set and added system to that set: {set_id}")

    commandName, commandID = setup_generic_pe_command_with_no_rules_all_OS
    
    aduser, _, adgroup = setup_user_in_ad_group
    if adgroup is None:
        pytest.skip("Cannot create adgroup")

    # Add assignment
    asmnt_info = get_PE_ASSIGNMENTS_Data(commandID=commandID, commandName=commandName, principalType="Group",
                                         principal=adgroup['DisplayName'], scopeType="Collection",
                                         scope=set_id, principalId=None,
                                         bypassChallenge=True)
    asmntID, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                   scopeType=asmnt_info['ScopeType'],
                                                                   scope=asmnt_info['Scope'],
                                                                   principalType=asmnt_info['PrincipalType'],
                                                                   principal=asmnt_info['Principal'],
                                                                   byPassChallenge=True,
                                                                   starts=asmnt_info['Starts'],
                                                                   expires=asmnt_info['Expires'])
    assert isSuccess, f"Adding assignment failed"
    asmnt_info['ID'] = asmntID

    results, isSuccess = PrivilegeElevation.can_execute_priv_command(core_session,
                                                                     user=aduser['SystemName'], system=sys_name,
                                                                     command="sc stop cagent")
    assert isSuccess, f"CanExecutePrivilegeCommand failed, reason: {results}"

    assert len(results['PrivilegeElevationCommands']) == 1, f"Only single command should exist {results}"
    results_assignments = results['PrivilegeElevationCommands'][0]['Assignments']

    assert len(results_assignments) == 1 and results['Granted'], f"Granted should be true"
    PrivilegeElevation.check_can_execute_priv_command_results(asmnt_info, results['PrivilegeElevationCommands'][0]), f"All params not matching {results}"
    #clean up
    errMsg, isSuccess = PrivilegeElevation.del_pe_rule_assignment(core_session, asmntID)
    assert isSuccess is True, f'PrivilegeElevation add assignment failed to clean up {errMsg}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_can_execute_priv_command_user_not_exist(core_session, cleanup_servers):
    session = core_session
    sys_name = "test_pe_can_execute_priv_command" + guid()
    sys_fqdn = "fqdn" + guid()
    added_system_id, system_success_status = ResourceManager.add_system(core_session, name=sys_name,
                                                                        fqdn=sys_fqdn,
                                                                        computerclass="Windows",
                                                                        sessiontype="Rdp")
    assert system_success_status, f'Adding system failed returned status {system_success_status}'
    logger.debug(f"Successfully added a System: {added_system_id}")
    cleanup_servers.append(added_system_id)
    
    args = Util.scrub_dict({
            'User': "userNotExist",
            'System': added_system_id,
            'Command': "sc stop cagent"
        })

    response = session.apirequest(
        EndPoints.PRIVILEGE_ELEVATION_CAN_EXECUTE_PE, args)
    response_json = response.json()
    logger.info(f"Response from PE canExecutePrivilegeCommand: {response_json}")
    assert not response_json['success'], f"CanExecutePrivilegeCommand failed, reason: {response_json}"
    assert response_json['Message'] == "User userNotExist not found; they may have been deleted or the directory may be unavailable.", f"CanExecutePrivilegeCommand failed, reason: {response_json}"

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_can_execute_priv_command_system_not_exist(core_session, cleanup_servers):
    session = core_session
    admin_user = core_session.get_user()
    admin_user_name = admin_user.get_login_name()
    
    args = Util.scrub_dict({
            'User': admin_user_name,
            'System': "SysNotExist",
            'Command': "sc stop cagent"
        })

    response = session.apirequest(
        EndPoints.PRIVILEGE_ELEVATION_CAN_EXECUTE_PE, args)
    response_json = response.json()
    logger.info(f"Response from PE canExecutePrivilegeCommand: {response_json}")
    assert not response_json['success'], f"CanExecutePrivilegeCommand failed, reason: {response_json}"
    assert response_json['Message'] == "Computer SysNotExist does not exist.", f"CanExecutePrivilegeCommand failed, reason: {response_json}"

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_can_execute_priv_command_user_not_passed(core_session, cleanup_servers):
    session = core_session
    
    args = Util.scrub_dict({
            'System': "SysNotExist",
            'Command': "sc stop cagent"
        })

    response = session.apirequest(
        EndPoints.PRIVILEGE_ELEVATION_CAN_EXECUTE_PE, args)
    response_json = response.json()
    logger.info(f"Response from PE canExecutePrivilegeCommand: {response_json}")
    assert not response_json['success'], f"CanExecutePrivilegeCommand failed, reason: {response_json}"
    assert response_json['Message'] == "Parameter 'User' must be specified.", f"CanExecutePrivilegeCommand failed, reason: {response_json}"

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_can_execute_priv_command_sys_not_passed(core_session, cleanup_servers):
    session = core_session
    
    args = Util.scrub_dict({
            'User': "eyeOfSauron",
            'Command': "sc stop cagent"
        })

    response = session.apirequest(
        EndPoints.PRIVILEGE_ELEVATION_CAN_EXECUTE_PE, args)
    response_json = response.json()
    logger.info(f"Response from PE canExecutePrivilegeCommand: {response_json}")
    assert not response_json['success'], f"CanExecutePrivilegeCommand failed, reason: {response_json}"
    assert response_json['Message'] == "Parameter 'System' must be specified.", f"CanExecutePrivilegeCommand failed, reason: {response_json}"

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_can_execute_priv_command_cmd_not_passed(core_session, cleanup_servers):
    session = core_session
    
    args = Util.scrub_dict({
            'User': "eyeOfSauron",
            'System': "hobbiton"
        })

    response = session.apirequest(
        EndPoints.PRIVILEGE_ELEVATION_CAN_EXECUTE_PE, args)
    response_json = response.json()
    logger.info(f"Response from PE canExecutePrivilegeCommand: {response_json}")
    assert not response_json['success'], f"CanExecutePrivilegeCommand failed, reason: {response_json}"
    assert response_json['Message'] == "Parameter 'Command' must be specified.", f"CanExecutePrivilegeCommand failed, reason: {response_json}"

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_can_execute_priv_command_sys_no_asmnt_on_user(core_session , cleanup_servers, users_and_roles):
    # Add System
    sys_name = "test_pe_can_execute_priv_command" + guid()
    sys_fqdn = "fqdn" + guid()
    added_system_id, system_success_status = ResourceManager.add_system(core_session, name=sys_name,
                                                                        fqdn=sys_fqdn,
                                                                        computerclass="Unix",
                                                                        sessiontype="Ssh")
    assert system_success_status, f'Adding system failed returned status {system_success_status}'
    logger.debug(f"Successfully added a System: {added_system_id}")

    cleanup_servers.append(added_system_id)

    userobj = users_and_roles.populate_user({'Name': 'user' + guid()})
    
    results, isSuccess = PrivilegeElevation.can_execute_priv_command(core_session,
                                                                     user=userobj.get_login_name(), system=sys_name,
                                                                     command="sudo date")
    
    assert isSuccess, f"CanExecutePrivilegeCommand failed, reason: {results}"
    assert not results['Granted'], f"Granted should be true: {results}"

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_can_execute_priv_command_sys_no_asmnt_on_role(core_session , cleanup_servers, users_and_roles):
    # Add System
    sys_name = "test_pe_can_execute_priv_command" + guid()
    sys_fqdn = "fqdn" + guid()
    added_system_id, system_success_status = ResourceManager.add_system(core_session, name=sys_name,
                                                                        fqdn=sys_fqdn,
                                                                        computerclass="Unix",
                                                                        sessiontype="Ssh")
    assert system_success_status, f'Adding system failed returned status {system_success_status}'
    logger.debug(f"Successfully added a System: {added_system_id}")

    cleanup_servers.append(added_system_id)
    role = users_and_roles.populate_role({'Name': "can_exec_role" + guid(), "Rights": ["Admin Portal Login"]})
    
    userobj = users_and_roles.populate_user({'Name': 'user' + guid()})
    users_and_roles.add_user_to_role(userobj, role)
    results, isSuccess = PrivilegeElevation.can_execute_priv_command(core_session,
                                                                     user=userobj.get_login_name(), system=sys_name,
                                                                     command="sudo date")
    
    assert isSuccess, f"CanExecutePrivilegeCommand failed, reason: {results}"
    assert not results['Granted'], f"Granted should be true: {results}"

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_can_execute_priv_command_sys_asmnt_no_user_in_non_sysadmin_role(core_session, setup_generic_pe_command_with_no_rules_all_OS, users_and_roles, cleanup_servers):
    # Add System
    sys_name = "test_pe_can_execute_priv_cmd123" + guid()
    sys_fqdn = "fqdn123" + guid()
    added_system_id, system_success_status = ResourceManager.add_system(core_session, name=sys_name,
                                                                        fqdn=sys_fqdn,
                                                                        computerclass="Windows",
                                                                        sessiontype="Rdp")
    assert system_success_status, f'Adding system failed returned status {system_success_status}'
    logger.debug(f"Successfully added a System: {added_system_id}")

    cleanup_servers.append(added_system_id)

    commandName, commandID = setup_generic_pe_command_with_no_rules_all_OS
    role = users_and_roles.populate_role({'Name': "can_exec_role123" + guid(), "Rights": ["Admin Portal Login"]})
    # Get User
    userobj1 = users_and_roles.populate_user({'Name': 'can_exec_user123' + guid()})
    # Add assignment
    asmnt_info = get_PE_ASSIGNMENTS_Data(commandID=commandID, commandName=commandName, principalType="Role",
                                         principalId=role['ID'], scopeType="System",
                                         scope=added_system_id, principal=None,
                                         bypassChallenge=True)
    asmntID, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                   scopeType=asmnt_info['ScopeType'],
                                                                   scope=asmnt_info['Scope'],
                                                                   principalType=asmnt_info['PrincipalType'],
                                                                   principalID=asmnt_info['PrincipalId'],
                                                                   byPassChallenge=True,
                                                                   starts=asmnt_info['Starts'],
                                                                   expires=asmnt_info['Expires'])
    assert isSuccess, f"Adding assignment failed"

    results, isSuccess = PrivilegeElevation.can_execute_priv_command(core_session,
                                                                     user=userobj1.get_login_name(), system=sys_name,
                                                                     command="sudo date")
    assert isSuccess, f"CanExecutePrivilegeCommand failed, reason: {results}"
    assert not results['Granted'], f"Granted should be false: {results}"
    #clean up
    errMsg, isSuccess = PrivilegeElevation.del_pe_rule_assignment(core_session, asmntID)
    assert isSuccess is True, f'PrivilegeElevation add assignment failed to clean up {errMsg}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_can_execute_priv_command_sys_no_asmnt_on_adgroup(core_session, setup_user_in_ad_group, cleanup_servers):
    # Add System
    sys_name = "test_pe_can_execute_priv_command" + guid()
    sys_fqdn = "fqdn" + guid()
    added_system_id, system_success_status = ResourceManager.add_system(core_session, name=sys_name,
                                                                        fqdn=sys_fqdn,
                                                                        computerclass="Unix",
                                                                        sessiontype="Ssh")
    assert system_success_status, f'Adding system failed returned status {system_success_status}'
    logger.debug(f"Successfully added a System: {added_system_id}")

    cleanup_servers.append(added_system_id)
    
    aduser, _, adgroup = setup_user_in_ad_group
    if adgroup is None:
        pytest.skip("Cannot create adgroup")
    
    results, isSuccess = PrivilegeElevation.can_execute_priv_command(core_session,
                                                                     user=aduser['SystemName'], system=sys_name,
                                                                     command="sudo date")
    assert isSuccess, f"CanExecutePrivilegeCommand failed, reason: {results}"
    assert not results['Granted'], f"Granted should be false: {results}"

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_can_execute_priv_command_sys_asmnt_no_aduser_in_adgroup(core_session, setup_generic_pe_command_with_no_rules, setup_user_in_ad_group, setup_aduser, cleanup_servers):
    # Add System
    sys_name = "test_pe_can_execute_priv_command" + guid()
    sys_fqdn = "fqdn" + guid()
    added_system_id, system_success_status = ResourceManager.add_system(core_session, name=sys_name,
                                                                        fqdn=sys_fqdn,
                                                                        computerclass="Unix",
                                                                        sessiontype="Ssh")
    assert system_success_status, f'Adding system failed returned status {system_success_status}'
    logger.debug(f"Successfully added a System: {added_system_id}")

    cleanup_servers.append(added_system_id)

    commandName, commandID = setup_generic_pe_command_with_no_rules
    
    aduser, _, adgroup = setup_user_in_ad_group
    if adgroup is None:
        pytest.skip("Cannot create adgroup")
    
    # Add assignment
    asmnt_info = get_PE_ASSIGNMENTS_Data(commandID=commandID, commandName=commandName, principalType="Group",
                                         principal=adgroup['DisplayName'], scopeType="System",
                                         scope=added_system_id, principalId=None,
                                         bypassChallenge=True)
    asmntID, isSuccess = PrivilegeElevation.add_pe_rule_assignment(core_session, commandID=commandID,
                                                                   scopeType=asmnt_info['ScopeType'],
                                                                   scope=asmnt_info['Scope'],
                                                                   principalType=asmnt_info['PrincipalType'],
                                                                   principal=asmnt_info['Principal'],
                                                                   byPassChallenge=True,
                                                                   starts=asmnt_info['Starts'],
                                                                   expires=asmnt_info['Expires'])
    assert isSuccess, f"Adding assignment failed"

    aduser1, _ = setup_aduser
    results, isSuccess = PrivilegeElevation.can_execute_priv_command(core_session,
                                                                     user=aduser1['SystemName'], system=sys_name,
                                                                     command="sudo date")
    assert isSuccess, f"CanExecutePrivilegeCommand failed, reason: {results}"
    assert not results['Granted'], f"Granted should be false: {results}"
    #clean up
    errMsg, isSuccess = PrivilegeElevation.del_pe_rule_assignment(core_session, asmntID)
    assert isSuccess is True, f'PrivilegeElevation add assignment failed to clean up {errMsg}'
