import logging
import re

import pytest

from Fixtures.PAS.Platform import users_and_roles
from Shared.API.agent import get_PE_ASSIGNMENTS_Data, get_PE_Command_Data
from Shared.API.infrastructure import ResourceManager
from Shared.API.privilege_elevation import PrivilegeElevation
from Shared.API.sets import SetsManager
from Shared.util import Util
from Utils.guid import guid

"""
GetAssignments
1. Just commandID
2. Just commandName
3. Both commandID and commandName provided, should fail
4. CommandID and commandName not provided, should fail
5. Wrong commandID provided, should fail
6. Power User can access
7. PE admin can access
8. Regular user has no access
"""

logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_just_id_case(core_session, setup_generic_pe_command_with_no_rules):
    commandName, commandID = setup_generic_pe_command_with_no_rules
    command_info = get_PE_Command_Data(name=commandName, commandPattern="*", applyTo="Linux")
    command_info['ID'] = commandID
    command_info['ApplyToMask'] = 1

    results, isSuccess = PrivilegeElevation.get_pe_command(core_session, ident=commandID)
    assert isSuccess, f"Get API failed for commandID: {commandID}, reason: {results}"

    PrivilegeElevation.check_command_info_in_api_response(command_info, results['Result'])


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_just_name_case(core_session, setup_generic_pe_command_with_no_rules):
    commandName, commandID = setup_generic_pe_command_with_no_rules
    command_info = get_PE_Command_Data(name=commandName, commandPattern="*", applyTo="Linux")
    command_info['ID'] = commandID
    command_info['ApplyToMask'] = 1

    results, isSuccess = PrivilegeElevation.get_pe_command(core_session, name=commandName)
    assert isSuccess, f"Get API failed for commandName: {commandName}, reason: {results}"

    PrivilegeElevation.check_command_info_in_api_response(command_info, results['Result'])


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_id_name_provided(core_session, setup_generic_pe_command_with_no_rules):
    commandName, commandID = setup_generic_pe_command_with_no_rules

    results, isSuccess = PrivilegeElevation.get_pe_command(core_session, name=commandName, ident=commandID)
    assert not isSuccess and results['Message'] == "Cannot specify both ID and name for Command in request", \
        f"Get API failed passed when both commandID and commandName provided: {commandName}, commandID: {commandID}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_params_not_provided(core_session):
    results, isSuccess = PrivilegeElevation.get_pe_command(core_session)
    assert not isSuccess and results['Message'] == "Parameter 'ID/Name' must be specified.", \
        f"Get API passed when no params provided, reason: {results}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_invalid_commandID(core_session):
    commandID = "abcd_xyz"
    results, isSuccess = PrivilegeElevation.get_pe_command(core_session, ident=commandID)
    assert not isSuccess and results['Message'] == "Privilege Elevation Command not found.", \
        f"Get API passed when invalid commandID provided, commandID: {commandID}"


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_power_user_has_access(core_session, setup_generic_pe_command_with_no_rules, users_and_roles):
    commandName, commandID = setup_generic_pe_command_with_no_rules
    command_info = get_PE_Command_Data(name=commandName, commandPattern="*", applyTo="Linux")
    command_info['ID'] = commandID
    command_info['ApplyToMask'] = 1

    # Get User
    requester_session = users_and_roles.get_session_for_user('Privileged Access Service Power User')

    # This user inherited View permission, so should be able to see the command
    results, isSuccess = PrivilegeElevation.get_pe_command(requester_session, ident=commandID)
    assert isSuccess, f"Get API by PAS power user failed for commandID: {commandID}, reason: {results}"

    PrivilegeElevation.check_command_info_in_api_response(command_info, results['Result'])


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_pe_user_has_access(core_session, setup_generic_pe_command_with_no_rules, users_and_roles):
    commandName, commandID = setup_generic_pe_command_with_no_rules
    command_info = get_PE_Command_Data(name=commandName, commandPattern="*", applyTo="Linux")
    command_info['ID'] = commandID
    command_info['ApplyToMask'] = 1

    # Get User
    requester_session = users_and_roles.get_session_for_user('Privilege Elevation Management')

    # This user inherited View permission, so should be able to see the command
    results, isSuccess = PrivilegeElevation.get_pe_command(requester_session, ident=commandID)
    assert isSuccess, f"Get API by PE user failed for commandID: {commandID}, reason: {results}"

    PrivilegeElevation.check_command_info_in_api_response(command_info, results['Result'])


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_regular_user_has_no_access(core_session, setup_generic_pe_command_with_no_rules, users_and_roles):
    commandName, commandID = setup_generic_pe_command_with_no_rules

    # Get User
    requester_session = users_and_roles.get_session_for_user()

    results, isSuccess = PrivilegeElevation.get_pe_command(requester_session, ident=commandID)
    assert not isSuccess and results['Message'] == "You are not authorized to perform this operation. " \
                                                   "Please contact your IT helpdesk.", \
        f"Get API by regular user passed for commandID: {commandID}, reason: {results}"
