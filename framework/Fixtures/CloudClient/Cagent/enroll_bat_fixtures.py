import pytest
import logging
import datetime
import collections
from Utils.config_loader import Configs
from Utils.ssh_util import SshUtil
from Utils.guid import guid
from Shared.endpoint_manager import EndPoints
from Shared.data_manager import RequestData
from Shared.API.roles import RoleManager
from Shared.API.users import UserManager
from Shared.API.sets import SetsManager
from Shared.API.agent import *
from Shared.util import Util
from Shared.API.redrock import RedrockController
from Shared.API.infrastructure import ResourceManager
from Shared.winrm_commands import create_multiple_users, winrm_helper
from Shared.pas_sshutils import ssh_manager
from Utils.powershell import run_local_powershell_command
from Utils.winrm import WinRM

logger = logging.getLogger("framework")


@pytest.fixture(scope='session')
def generic_cagent_enroll_root():
    """Prepare SSH session for cagent enrollment test.

    :return: Returns SshUtil() object to be used to run commands."""
    config = Configs().get_yaml_node_as_tuple("agents", "generic_cagent_unix")
    sshutil = SshUtil(config)
    yield sshutil
    logger.info("unenrolling the cagent")
    sshutil.send_command("cunenroll -md")

@pytest.fixture(scope='session')
def generic_cagent_enroll_win_admin():
    """
    Provide a WinRM connection to the Windows server as Administrator
    """
    sys_config = Configs().get_yaml_node_as_tuple("agents", "generic_cagent_win")

    winrm_config = collections.namedtuple('winrm_config',
                                         ('hostname username password'))
    config = winrm_config(hostname = sys_config.hostname,
                          username = sys_config.admin_username,
                          password = sys_config.admin_password)
    logger.debug(f"winrm instantiated, Hostname {sys_config.hostname}")
    winrm = WinRM(config)
    yield winrm

    winrm.send_command("cunenroll -md")
    winrm.close()



@pytest.fixture(scope='function')
def agent_enrolled_windows_system_with_users(core_session_global, agent_enrolled_windows_system, users_and_roles, remote_users_qty1,
            cleanup_accounts, pas_ad_domain, pas_ad_administrative_account, cleanup_lapr_systems_and_domains, proxy_start_stop):
    config = Configs().get_yaml_node_as_tuple("agents", "generic_cagent_win")
    accounts_list = cleanup_accounts[0]
    domains_list = cleanup_lapr_systems_and_domains[1]
    systems_list = cleanup_lapr_systems_and_domains[0]
    user = remote_users_qty1
    proxycontrol = proxy_start_stop
    accountusers = [{"Name" : user[0], "Password" : "Hello123"}]

    logger.info("Users created " + str(len(accountusers)))
    for i,  val in enumerate(accountusers):
        logger.info(str(i) + ", Name: " +
                val["Name"] + "Password:" + val["Password"])

    logger.info("adding users on the enrolled system")
    system_id = agent_enrolled_windows_system["ResourceId"]
    winrm_session_as_admin = agent_enrolled_windows_system["Session"]
    adminuser = {"Name": config.admin_username, "Password": config.admin_password}

    domain_id = pas_ad_domain['ID']
    admin_id = pas_ad_administrative_account['ID']

    right_data = ("Privileged Access Service Power User", "role_Privileged Access Service Power User")

    requester_session = users_and_roles.get_session_for_user(right_data[0])
    role_info = users_and_roles.get_role(right_data[0])

    domains_list.append(pas_ad_domain)
    systems_list.append(system_id)

    logger.info("Setting Domain Administrator user as Administrative Account on domain.")
    result, success, response = ResourceManager.set_administrative_account(core_session_global, [pas_ad_domain['Name']], pas_ad_administrative_account['User'], pas_ad_administrative_account['ID'])

    logger.info("Setting Administrative Account on domain, but with no lapr settings enabled.")
    result, success = ResourceManager.update_domain_accounts(core_session_global, pas_ad_domain['Name'], admin_id, domain_id, allowautomaticlocalaccountmaintenance=True, allowmanuallocalaccountunlock=True)

    permission_string = 'Grant,View,Edit,Delete,ManageSession,AgentAuth,RequestZoneRole,AddAccount,UnlockAccount'
    result, success = ResourceManager.assign_system_permissions(core_session_global, permission_string, role_info['Name'], role_info['ID'], "Role", system_id)
    assert success, f"Did not set system permissions {result}"

    # Step 3 Create Accounts for testing
    logger.info("Adding Admin account")
    admin_account_id, add_account_success = ResourceManager.add_account(
        requester_session, adminuser['Name'], adminuser["Password"], system_id, ismanaged=False)
    assert add_account_success, "Failed to create  admin user"
    logger.info(f"Added root Account.  Id {admin_account_id}")
    accounts_list.append(admin_account_id)

    logger.info("Adding user for reconciliation")
    new_account_id, add_account_success = ResourceManager.add_account(
        requester_session, accountusers[0]['Name'], accountusers[0]['Password'], system_id, ismanaged=True)
    assert add_account_success, "Failed to create manged Account user: " + \
        accountusers[0]['Name'] + ", Verify CC  or agent settings and status"
    logger.info(f"Added Account for testing.  Id {new_account_id}")
    accounts_list.append(new_account_id)

    permission_string = "Owner,View,Manage,Delete,Login,Naked,UpdatePassword,RotatePassword,FileTransfer,UserPortalLogin"
    result, success = ResourceManager.assign_account_permissions(core_session_global,
                                                                    permission_string,
                                                                    role_info['Name'], role_info['ID'], "Role", new_account_id)
    assert success, "Did not set account permissions " + result

    # Get computer details for update
    result = RedrockController.get_system(requester_session, system_id)
    system = result[0]["Row"]

    # wait for managed password change event
    filter = [['AccountName', accountusers[0]['Name']]]
    RedrockController.wait_for_event_by_type_filter(requester_session, "Cloud.Server.LocalAccount.PasswordChange",
                                                    filter=filter, maximum_wait_second=120)  # wait for 120 seonds
    accounts = [{"Name": adminuser['Name'], "Password": adminuser["Password"], "Id": admin_account_id}, {"Name": accountusers[0]["Name"], "Password": accountusers[0]["Password"], "Id": new_account_id}]

    #  set proxy
    proxy = start_proxy_with_machinename(requester_session, proxycontrol, config.proxy_name)
    assert proxy != None, (f'Failed to find the connector {config.proxy_name}, Setup the connector properly before the test')


    result, success = ResourceManager.update_system(requester_session, system_id, system["Name"], system["FQDN"], 'Windows', domainid=domain_id, proxycollectionlist=proxy)
    assert success, (f'Failed to set reconciliation settings  {result}')

    result, success = ResourceManager.update_system(requester_session, system_id, system["Name"], system["FQDN"], 'Windows',  proxycollectionlist=proxy, allowautomaticlocalaccountmaintenance=True, allowmanuallocalaccountunlock=True)
    assert success, (f'Failed to set reconciliation settings  {result}')

    #  update_system  reset the  proxycollectionlist setting?  Set it again.
    result, success = ResourceManager.update_system(requester_session, system_id, system["Name"], system["FQDN"], 'Windows', domainid=domain_id, proxycollectionlist=proxy)
    assert success, (f'Failed to set reconciliation settings  {result}')


    # return acount ids, computer,
    yield [{"ResourceId": system_id, "ProxyId": proxy, "ResourceFQDN": system["FQDN"], "Accounts": accounts, "Session": winrm_session_as_admin}]

    result, success, message = ResourceManager.set_system_administrative_account(requester_session, system_id)
    assert success, f'Failed to remove administrative account on {message}'



@pytest.fixture(scope='function')
def agent_enrolled_unix_system_with_users(core_tenant, core_session_global, agent_enrolled_unix_system, users_and_roles, cleanup_accounts, create_unix_users, proxy_start_stop, detect_proxy):

    config = Configs().get_yaml_node_as_tuple("agents", "generic_cagent_unix")
    accounts_list = cleanup_accounts[0]
    proxycontrol = proxy_start_stop

    logger.info("adding users on the enrolled system")
    system_id = agent_enrolled_unix_system["ResourceId"]
    ssh_session = agent_enrolled_unix_system["Session"]
    adminuser = {"Name": config.username, "Password": config.password}

        # add users on target system
    accountusers = create_unix_users(ssh_session, "agent_", 2)
    logger.info("Users created " + str(len(accountusers)))
    for i,  val in enumerate(accountusers):
        logger.info(str(i) + ", Name: " +
                val["Name"] + "Password:" + val["Password"])



    right_data = ("Privileged Access Service Power User", "role_Privileged Access Service Power User")

    requester_session = users_and_roles.get_session_for_user(right_data[0])
    role_info = users_and_roles.get_role(right_data[0])

    permission_string = 'Grant,View,Edit,Delete,ManageSession,AgentAuth,RequestZoneRole,AddAccount,UnlockAccount'
    result, success = ResourceManager.assign_system_permissions(core_session_global,
                                                                    permission_string,
                                                                    role_info['Name'], role_info['ID'], "Role", system_id)
    assert success, "Did not set system permissions " + result

    # Step 3 Create Accounts for testing
    logger.info("Adding root account")
    admin_account_id, add_account_success = ResourceManager.add_account(
        requester_session, adminuser['Name'], adminuser["Password"], system_id, ismanaged=False)
    assert add_account_success, "Failed to create Account user: root"
    logger.info(f"Added root Account.  Id {admin_account_id}")
    accounts_list.append(admin_account_id)


    logger.info("Adding user for reconciliation")
    new_account_id, add_account_success = ResourceManager.add_account(
        requester_session, accountusers[0]['Name'], accountusers[0]['Password'], system_id, ismanaged=True)
    assert add_account_success, "Failed to create manged Account user: " + \
        accountusers[0]['Name'] + ", Verify CC  or agent settings and status"
    logger.info(f"Added Account for testing.  Id {new_account_id}")
    accounts_list.append(new_account_id)

    permission_string = "Owner,View,Manage,Delete,Login,Naked,UpdatePassword,RotatePassword,FileTransfer,UserPortalLogin"
    result, success = ResourceManager.assign_account_permissions(core_session_global,
                                                                    permission_string,
                                                                    role_info['Name'], role_info['ID'], "Role", new_account_id)
    assert success, "Did not set account permissions " + result

    # Get computer details for update
    result = RedrockController.get_system(requester_session, system_id)
    system = result[0]["Row"]

    # wait for managed password change event
    filter = [['AccountName', accountusers[0]['Name']]]
    RedrockController.wait_for_event_by_type_filter(requester_session, "Cloud.Server.LocalAccount.PasswordChange",
                                                    filter=filter, maximum_wait_second=120)  # wait for 20 seonds
    accounts = [{"Name": adminuser['Name'], "Password": adminuser["Password"], "Id": admin_account_id}, {"Name": accountusers[0]["Name"], "Password": accountusers[0]["Password"], "Id": new_account_id}]

    proxy = start_proxy_with_machinename(requester_session, proxycontrol, config.proxy_name)
    assert proxy != None, (f'Failed to find the connector {config.proxy_name}, Setup the  connector properly.')

    #  Set Admin Account and enable local account maintenance
    result, success = ResourceManager.update_system(
        requester_session, system_id, system["Name"], system["FQDN"], 'Unix', proxycollectionlist=proxy, adminaccountid=admin_account_id, allowautomaticlocalaccountmaintenance=True)
    assert success, (f'Failed to set administrative account {result}')


   # return acount ids, computer,
    yield [{"ResourceId": system_id, "ProxyId": proxy, "ResourceName":system["Name"], "Accounts": accounts, "Session": ssh_session}]

    result, success, message = ResourceManager.set_system_administrative_account(requester_session, system_id)
    assert success, f'Failed to remove administrative account on {message}'

@pytest.fixture(scope='function')
def agent_enrolled_windows_system(core_session_global, core_tenant, generic_cagent_enroll_win_admin, agent_enrollment_code):
    winrm_session_as_admin = generic_cagent_enroll_win_admin
    enroll_code = agent_enrollment_code
    resource_name = 'win_agent_' + guid()[0:5]

    # start the agent service
    winrm_session_as_admin.send_command("net start cagent")

    command = f"cenroll -f -F all -t {core_tenant['fqdn']} -c {enroll_code}  -N {resource_name}"
    logger.info(f"Enrolling the client: {command}")
    winrm_helper.enroll_agent(winrm_session_as_admin, command, wait=True)

    server_id = RedrockController.get_server_id_by_name(core_session_global, resource_name)
    yield {"ResourceId": server_id, "Session": winrm_session_as_admin}

@pytest.fixture(scope='function')
def agent_enrolled_unix_system(core_session_global, core_tenant, generic_cagent_enroll_root, agent_enrollment_code):
    ssh_session = generic_cagent_enroll_root
    enroll_code = agent_enrollment_code
    resource_name = 'unix_agent_' + guid()[0:5]
    logger.info("enrolling the cagent")
    command = f"cenroll -f -F all -t {core_tenant['fqdn']} -c {enroll_code}  -N {resource_name}"
    ssh_manager.enroll_agent(ssh_session, command, wait=True)

    server_id = RedrockController.get_server_id_by_name(core_session_global, resource_name)
    yield {"ResourceId": server_id, "Session": ssh_session}


@pytest.fixture(scope='session')
def agent_enrollment_code(core_session_global):
    """Create an Enrollment code to be used for agent enrollment.

    :return: a string containing enrollment code
    """
    curr_date = datetime.datetime.now() + datetime.timedelta(days=10)
    session = core_session_global
    response = session.apirequest(EndPoints.ADD_ENROLLMENT_CODE, RequestData.get_ADD_ENROLLMENT_CODE(
        "sysadmin", "System Administrator", "Role", "true", "false", str(curr_date.date().strftime("%m/%d/%Y")), "true", "true"))
    response_json = response.json()
    logger.info("Response Enrollment Code Returned: " + response.text)
    enrollCode = ''
    if response_json['success'] is True:
        enrollCode = response_json['Result']['EnrollmentCode']
        yield enrollCode
    else:
        logger.error("Failed to get enrollment code")

    logger.info("Deleting the Enrollment code")
    if enrollCode != '':
        session.apirequest(EndPoints.DELETE_ENROLLMENT_CODE,
                           RequestData.get_DEL_ENROLLMENT_CODE(enrollCode, enrollCode))


@pytest.fixture(scope='function')
def agent_get_role(core_session_global):
    """Creates a random role to be used for agent enrollment

    :return: role name (str)
    """
    session = core_session_global
    response = RoleManager.create_random_role(session)
    logger.debug("Role created: " + response['Name'])
    yield response["Name"]
    RoleManager.delete_role(session, response['_RowKey'])
    logger.debug("Role deleted: " + response['Name'])


@pytest.fixture(scope='function')
def agent_get_user(core_tenant_global, core_session_global):
    """Creates a random user to be used for agent enrollment

    :return: agent name (str)
    """
    session = core_session_global
    tenant = core_tenant_global
    username = tenant['admin_user']
    suffix = username.split("@")[1]

    response = UserManager.create_random_user(session, suffix)
    logger.debug("User created: " +
                 response['Name'] + " uuid: " + response['Uuid'])
    response1 = UserManager.create_random_user(session, suffix)
    logger.debug("User created: " +
                 response1['Name'] + " uuid: " + response1['Uuid'])
    yield response["Name"], response1["Name"]
    UserManager.delete_user(session, response['Uuid'])
    logger.debug("User deleted: " + response['Name'])
    UserManager.delete_user(session, response1['Uuid'])
    logger.debug("User deleted: " + response1['Name'])


@pytest.fixture(scope='function')
def agent_get_set(core_session_global):
    """Creates a resource set to be used for agent enrollment

    :return: set name
    """
    session = core_session_global
    set_name = "set_" + Util.random_string()
    is_create, set_id = SetsManager.create_manual_collection(
        session, set_name, "Server", None)
    if is_create:
        logger.debug("Resource set created: " + set_name)
        yield set_name
    else:
        logger.error("Error in creating resource set: " + set_name)
    is_create, response = SetsManager.delete_collection(session, set_id)
    if is_create:
        logger.debug("Resource set deleted: " + set_name)


@pytest.fixture(scope='function')
def agent_enroll_with_no_features_v3(core_session_global):
    """ EnrollV3 : Enroll a mock Agent using EnrollV3 Rest API
                   Unenrolls the mock agent during clean-up phase
        Returns: EnrollV3Result (json)
    """
    logger.debug("EnrollV3 with no features")
    session = core_session_global
    agentVersion = "19.1"
    agentName = "testing_lrpc_agent_"+guid()
    enrollResult = session.apirequest(
        EndPoints.ENROLL_V3, get_ENROLL_V3_Data(agentVersion, agentName)).json()
    assert enrollResult["success"] is True and enrollResult[
        "Result"] is not None, f'Enroll Failed: {enrollResult}'
    yield enrollResult
    logger.debug(" Agent Unenroll")
    unenrollResult = session.apirequest(EndPoints.UNENROLL, get_UNENROLL_Data(
        True, enrollResult["Result"]["Uuid"])).json()
    assert unenrollResult["success"] is True and unenrollResult[
        "Result"] is not None, f'UnEnroll Failed: {unenrollResult}'

def start_proxy_with_machinename(core_session, start_stop_proxy, machineName):
    proxycontrol = start_stop_proxy
    proxy_query = f"select ID, Online, Version, MachineName from Proxy order by Online DESC"

    rows = RedrockController.get_result_rows(RedrockController.redrock_query(core_session, proxy_query))

    for item in rows:
        try:
            if str(item['MachineName']).lower() == machineName.lower():
                if item['Online'] == True:
                    return item["ID"]
                proxycontrol(item["ID"], True)
                return item["ID"]
        except Exception: # there will be multiple proxies with same machine name
            logger.debug(f"Failed to start connector {item['ID']}, Name {item['MachineName']}, ignoring ")
    return None

@pytest.fixture(scope='function')
def check_and_mount_smb():
    """1. Checks /proc/mounts to see if <cagent_constants.smbMountPath> is mounted
       2. If not, mount it
       3. Check if the entry is present in /etc/fstab
       4. If not, add it
    """
    logger.debug(" Check and Mount SMB")
    config = Configs().get_yaml_node_as_tuple("agents", "generic_cagent_unix")
    ssh_session = SshUtil(config)

    config = Configs().get_yaml_node_as_tuple("agents", "cagent_constants")
    testConfig = Configs().get_yaml_node_as_tuple("agents", "cagent_test_constants")

    retval, output, stderr = ssh_session.send_command(
        f"cat /proc/mounts | grep {testConfig.localMountPath}")
    assert len(stderr) == 0, f'Failure in Checking Mounted Drives: {stderr}'
    mountedFlag = re.findall(f"{testConfig.localMountPath}", output)
    if len(mountedFlag) == 0:
        retval, _, stderr = ssh_session.send_command(
            f"sudo mkdir -p {testConfig.localMountPath}")
        assert retval == 0 and len(
            stderr) == 0, f'Unable to Create local Mount Directory: {stderr}'

        retval, output, stderr = ssh_session.send_command(
            f"sudo mount -t cifs -o username={config.buildSystemFileAccessUserName},password={config.buildSystemFileAccessPassword} {testConfig.buildMountPath} {testConfig.localMountPath}")

        assert retval == 0 and len(
            stderr) == 0, f'Mounting Build Machine Path Failed: {stderr}'

    retval, output, stderr = ssh_session.send_command(
        f"cat /etc/fstab | grep {testConfig.localMountPath}")
    assert len(stderr) == 0, f'Failure in Checking /etc/fstab: {stderr}'

    if len(re.findall(f"{testConfig.localMountPath}", output)) == 0:

        # Create Credentails file
        retval, output, stderr = ssh_session.send_command(
            f"echo -e 'username={config.buildSystemFileAccessUserName}\npassword={config.buildSystemFileAccessPassword}' > /root/.smbcredentials")
        assert len(stderr) == 0, f'Failure in creating smbCredentials file'

        retval, output, stderr = ssh_session.send_command(
            f" chmod 600 /root/.smbcredentials")
        assert len(
            stderr) == 0, f'Failure in setting smbCrednetials file permissions'

        command = 'echo "' + testConfig.buildMountPath + " " + testConfig.localMountPath + \
            ' cifs _netdev,credentials=/root/.smbcredentials,dir_mode=0755,file_mode=0755,uid=0,gid=0 0 0" | sudo tee -a /etc/fstab'

        retval, output, stderr = ssh_session.send_command(f"{command}")
        assert len(stderr) == 0, f'Failure in adding an entry to /etc/fstab'
    yield True
