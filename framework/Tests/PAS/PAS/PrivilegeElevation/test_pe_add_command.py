import pytest
import logging
from Shared.endpoint_manager import EndPoints
from Shared.API.privilege_elevation import PrivilegeElevation
from Shared.util import Util

logger = logging.getLogger("test")

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_privilege_elevation_add_command_linux(core_session):
    """
    Test case: Test for all valid params for ApplyTo as Linux
    """

    session = core_session

    result, success = PrivilegeElevation.add_pe_command(session, "Restart any linux service" + Util.random_string(), "systemctl restart", "Linux", "Restart any linux service", 6, "usr/sbin/systemctl", {}, {})
    
    assert success is True, f'PrivilegeElevation add command has failed {result}'

    #Clean up
    resp, success = PrivilegeElevation.del_pe_command(session, ident=result['Result']['ID'])
    assert success is True, f'PrivilegeElevation add command cleanup has failed {resp}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_privilege_elevation_add_command_win(core_session):
    """
    Test case: Test for all valid params for ApplyTo as Windows
    """

    session = core_session

    result, success = PrivilegeElevation.add_pe_command(session, "Restart any windows service" + Util.random_string(), "netsh", "Windows", "Restart any windows service", 3, "netsh", {}, {})
    
    assert success is True, f'PrivilegeElevation add command has failed {result}'

    #Clean up
    resp, success = PrivilegeElevation.del_pe_command(session, ident=result['Result']['ID'])
    assert success is True, f'PrivilegeElevation add command cleanup has failed {resp}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_privilege_elevation_add_command_winlinux(core_session):
    """
    Test case: Test for all valid params for ApplyTo as Windows,Linux
    """

    session = core_session

    result, success = PrivilegeElevation.add_pe_command(session, "All commands" + Util.random_string(), "*", "Linux,Windows", "Run all commands", 0, "*", {}, {})
    
    assert success is True, f'PrivilegeElevation add command has failed {result}'

    #Clean up
    resp, success = PrivilegeElevation.del_pe_command(session, ident=result['Result']['ID'])
    assert success is True, f'PrivilegeElevation add command cleanup has failed {resp}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_privilege_elevation_add_command_all_required_params(core_session):
    """
    Test case: Test for all required params
    """

    session = core_session

    result, success = PrivilegeElevation.add_pe_command(session, "All commands" + Util.random_string(), "*", "Linux,Windows")
    
    assert success is True, f'PrivilegeElevation add command has failed {result}'

    #Clean up
    resp, success = PrivilegeElevation.del_pe_command(session, ident=result['Result']['ID'])
    assert success is True, f'PrivilegeElevation add command cleanup has failed {resp}'

# Negative cases

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_privilege_elevation_add_command_no_name(core_session):
    """
    Test case: Test for all required params except no name
    """

    session = core_session

    args = Util.scrub_dict({
            'CommandPattern': "test",
            'ApplyTo': "Linux"
        })

    result = session.apirequest(
        EndPoints.PRIVILEGE_ELEVATION_ADD_COMMAND, args)
    result_json = result.json()
    
    assert result_json['success'] is False, f'PrivilegeElevation add command has failed {result_json}'
    assert "Missing required parameter: Name" in result_json['Exception'], f'PrivilegeElevation add command should fail with error Missing required parameter: Name {result_json}'
    
@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_privilege_elevation_add_command_no_commandPattern(core_session):
    """
    Test case: Test for all required params except no CommandPattern
    """

    session = core_session

    args = Util.scrub_dict({
            'Name': "asdf",
            'ApplyTo': "Linux"
        })

    result = session.apirequest(
        EndPoints.PRIVILEGE_ELEVATION_ADD_COMMAND, args)
    result_json = result.json()
    
    assert result_json['success'] is False, f'PrivilegeElevation add command has failed {result_json}'
    assert "Missing required parameter: CommandPattern" in result_json['Exception'], f'PrivilegeElevation add command should fail with error Missing required parameter: CommandPattern {result_json}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_privilege_elevation_add_command_no_applyTo(core_session):
    """
    Test case: Test for all required params except no ApplyTo
    """

    session = core_session

    args = Util.scrub_dict({
            'Name': "LOTR",
            'CommandPattern': "EyeOfSauron"
        })

    result = session.apirequest(
        EndPoints.PRIVILEGE_ELEVATION_ADD_COMMAND, args)
    result_json = result.json()
    
    assert result_json['success'] is False, f'PrivilegeElevation add command has failed {result_json}'
    assert "Parameter 'ApplyTo' must be specified." == result_json['Message'], f'PrivilegeElevation add command should fail with error Missing required parameter: ApplyTo {result_json}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_privilege_elevation_add_command_InvalidPlatform(core_session):
    """
    Test case: Test for all valid params except platform
    """

    session = core_session

    result, success = PrivilegeElevation.add_pe_command(session, "All commands", "*", "Mac")
    
    assert success is False, f'PrivilegeElevation add command has failed {result}'
    assert "PrivilegeElevationPlatformNotSupportedException" in result['Message'], f'PrivilegeElevation add command should fail with error PlatformNotSupportedException {result}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_privilege_elevation_add_command_InvalidApplyTo(core_session):
    """
    Test case: Test for all valid params except ApplyTo
    """

    session = core_session

    result, success = PrivilegeElevation.add_pe_command(session, "All commands", "*", applyTo=345)
    
    assert success is False, f'PrivilegeElevation add command has failed {result}'
    assert "Parameter 'ApplyTo' must be specified." == result['Message'], f'PrivilegeElevation add command should fail with error Parameter ApplyTo must be specified. {result}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_privilege_elevation_add_command_InvalidName(core_session):
    """
    Test case: Test for all valid params except Name
    """

    session = core_session

    result, success = PrivilegeElevation.add_pe_command(session, 123*876, "*", "Linux")
    
    assert success is False, f'PrivilegeElevation add command has failed {result}'
    assert "Invalid data type for parameter: Name." in result['Exception'], f'PrivilegeElevation add command should fail with error Invalid data type {result}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_privilege_elevation_add_command_InvalidCommandPattern(core_session):
    """
    Test case: Test for all valid params except commandPattern
    """

    session = core_session

    result, success = PrivilegeElevation.add_pe_command(session, "123*876", False, "Linux")
    
    assert success is False, f'PrivilegeElevation add command has failed {result}'
    assert "Invalid data type for parameter: CommandPattern." in result['Exception'], f'PrivilegeElevation add command should fail with error Invalid data type {result}'


@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_privilege_elevation_add_command_EmptyName(core_session):
    """
    Test case: Test for all valid params except empty name
    """

    session = core_session

    result, success = PrivilegeElevation.add_pe_command(session, "", "*", "Linux")
    
    assert success is False, f'PrivilegeElevation add command has failed {result}'
    assert "Invalid arguments passed to the server." == result['Message'], f'PrivilegeElevation add command should fail with error Invalid args passed to the server {result}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_privilege_elevation_add_command_EmptyCommandPattern(core_session):
    """
    Test case: Test for all valid params except empty commandPattern
    """

    session = core_session

    result, success = PrivilegeElevation.add_pe_command(session, "12#$##", "", "Linux")
    
    assert success is False, f'PrivilegeElevation add command has failed {result}'
    assert "Invalid arguments passed to the server." == result['Message'], f'PrivilegeElevation add command should fail with error Invalid  arguments passed to the server {result}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_privilege_elevation_add_command_EmptyApplyTo(core_session):
    """
    Test case: Test for all valid params except empty ApplyTo
    """

    session = core_session

    result, success = PrivilegeElevation.add_pe_command(session, "12#$##", "&uy545^&", "")
    
    assert success is False, f'PrivilegeElevation add command has failed {result}'
    assert "PrivilegeElevationPlatformNotSupportedException" in result['Message'], f'PrivilegeElevation add command should fail with error PrivilegeElevationPlatformNotSupportedException {result}'

@pytest.mark.api
@pytest.mark.cclient_privelevation
def test_privilege_elevation_add_command_Duplicate(core_session):
    """
    Test case: Test for when duplicate command is added
    """

    session = core_session
    cmdName = "cmd" + Util.random_string()
    result, success = PrivilegeElevation.add_pe_command(session, cmdName, "systemctl restart network", "Linux")
    
    assert success is True, f'PrivilegeElevation add command has failed {result}'
    
    result, success = PrivilegeElevation.add_pe_command(session, cmdName, "systemctl restart network", "Linux")
    
    assert success is False, f'PrivilegeElevation add command has failed {result}'
    assert f"Privilege elevation command &#39;{cmdName}&#39; already exists" in result['Message'], f'PrivilegeElevation add command should fail with errorPrivilege elevation command &#39;{cmdName}&#39; already exists {result}'

#Add more tests for v2