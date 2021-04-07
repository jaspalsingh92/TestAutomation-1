import pytest
import logging
import re
import os
from Utils.config_loader import Configs
from Shared.API.infrastructure import ResourceManager
from Shared.API.jobs import JobManager
from Shared.API.redrock import RedrockController
from Shared.util import Util
from Shared.pas_sshutils import ssh_manager

logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.daily
@pytest.mark.cps
@pytest.mark.pas_broken
@pytest.mark.unix_agent
@pytest.mark.client_account_management
class Test_Client_Account_Management_Unix:

    # NOTE: 
    #      Config file :Config\Environment\CloudClient\Agents.yaml  agents->generic_cagent_unix
    #      These tests stop and start cloud connector. Specfiy the connector for each system  to avoid stopping the connector that is used by other tests.
    #           - list all connectors to be used for tests in Config\environment\connectors.yaml
    #           - specfiy the connector to be used for each test system  in Config\environment\agents.yaml, Attribute: 'connector_name'
    #      Agent must be installed on the target system before starting the test

    @staticmethod
    def test_unix_client_system_connection(core_session, agent_enrolled_unix_system_with_users, proxy_start_stop):

        """
        This  test verifies connection to a unix system using Client, Connectors 
            Steps for this scenario:
                * Enroll an unix system.
                * stop the agent, start the connector  and verify connection to the system (only connector is available)
                    - Verify success
                * stop the connector verify connection to the system
                    - Verify failure
                * Start the agent and verify connection to the system (only Agent is available)
                    - Verify success
               * Start the connector and verify connection to the system (Both agent and connector are available)
                    - Verify success
        """

        """
            Testrail Link:
                https://testrail.centrify.com/index.php?/cases/view/1293084
                https://testrail.centrify.com/index.php?/cases/view/1293085
                https://testrail.centrify.com/index.php?/cases/view/1293086
        """

        # verfiy the test is run with single thread.
        assert 'PYTEST_XDIST_WORKER_COUNT' not in os.environ, \
            f'This test cannot be run with multiple threads due to starting and stopping connectors'

        enrolledsystems = agent_enrolled_unix_system_with_users
        session = enrolledsystems[0]["Session"]
        resourceid = enrolledsystems[0]["ResourceId"]
        proxyid = enrolledsystems[0]["ProxyId"]
        proxycontrol = proxy_start_stop

        logger.info("stop the agent")
        ssh_manager.ssh_stop_agent(session)
        logger.info("start the connector")
        proxycontrol(proxyid, True)

        logger.info("Testing connection to the computer,  Connector is ready")
        result, success = ResourceManager.get_system_health(core_session, resourceid)
        assert success and result == 'OK', f"Unable to verify system is reachable {result} {success}"

        # stop Conector , Should fail
        logger.info("Stopping  the connector")
        proxycontrol(proxyid, False)
        logger.info("Testing connection to the system")
        result, success = ResourceManager.get_system_health(core_session, resourceid)
        assert success and result != 'OK', f"cerify system is reachable {result} {success}"

        # Start agent
        logger.info("Starting the agent")
        ssh_manager.ssh_start_agent(session, True)
        logger.info("Testing connection to the computer, agent is available.")
        result, success = ResourceManager.get_system_health(core_session, resourceid)
        assert success and result == 'OK', f"Unable to verify system is reachable {result} {success}"

        # verify account again, both connector and agent are running 
        proxycontrol(proxyid, True)
        logger.info("Testing connection to the computer, both agent and connector are available")
        result, success = ResourceManager.get_system_health(core_session, resourceid)
        assert success and result == 'OK', f"Unable to verify system is reachable {result} {success}"

    @staticmethod
    def test_unix_client_account_verification(core_session, agent_enrolled_unix_system_with_users, proxy_start_stop):

        """
        This  test verifies accounts using Client, Connectors
            Steps for this scenario:
                * Enroll an unix system and create a managed account and an unmanaged account.
                * Verify the managed account's password is changed.
                * stop the agent, start connector and verify both accounts (only connector is availabe)
                    - Verify success
                * stop the connector and verify both accounts
                    - Verify failure
                * Start the agent and verify both accounts (only Agent is availabe)
                    - Verify success
               * Start the connector and verify both accounts (Both agent and connector are available)
                    - Verify success
        """

        """
            Testrail Link:
                https://testrail.centrify.com/index.php?/cases/view/1293456
                https://testrail.centrify.com/index.php?/cases/view/1293457
                https://testrail.centrify.com/index.php?/cases/view/1293458
        """

        # verfiy the test is run with single thread.
        assert 'PYTEST_XDIST_WORKER_COUNT' not in os.environ, \
            f'This test cannot be run with multiple threads due to starting and stopping connectors'

        enrolledsystems = agent_enrolled_unix_system_with_users
        accounts = enrolledsystems[0]["Accounts"]
        proxyid = enrolledsystems[0]["ProxyId"]
        session = enrolledsystems[0]["Session"]
        proxycontrol = proxy_start_stop

        logger.info("stop the agent")
        ssh_manager.ssh_stop_agent(session)
        logger.info("start the connector")
        proxycontrol(proxyid, True)

        logger.info("Verifying accounts, Connector is available")
        for i, val in enumerate(accounts):
            logger.info(str(i) + ", Name: " + val["Name"])
            verify_pass_result, verify_pass_success = ResourceManager.check_account_health(core_session, val["Id"])
            assert verify_pass_result == 'OK', "Verify Failed on Account: " + val['Name'] + ", " + verify_pass_result

        # stop Conector , Should fail
        logger.info("Stopping  the connector")
        proxycontrol(proxyid, False)
        logger.info("Verifying accounts, no agent or connector")
        for i, val in enumerate(accounts):
            verify_pass_result, verify_pass_success = ResourceManager.check_account_health(core_session, val["Id"])
            assert verify_pass_result != 'OK', "Verify success on Account: " + val['Name'] + ", " + verify_pass_result

        # Start agent
        logger.info("Starting the agent")
        ssh_manager.ssh_start_agent(session, True)

        logger.info("Verifying accounts, agent is available.")
        for i, val in enumerate(accounts):
            verify_pass_result, verify_pass_success = ResourceManager.check_account_health(core_session, val["Id"])
            assert verify_pass_result == 'OK', "Verify failed on Account: " + val['Name'] + ", " + verify_pass_result

        # verify account again, both connector and agent are running
        proxycontrol(proxyid, True)
        logger.info("Verifying accounts, both agent and connector are available")
        for i, val in enumerate(accounts):
            verify_pass_result, verify_pass_success = ResourceManager.check_account_health(core_session, val["Id"])
            assert verify_pass_result == 'OK', "Verify Failed on Account: " + val['Name'] + ", " + verify_pass_result

    @staticmethod
    def test_unix_client_account_rotate_reconciliation(users_and_roles, unix_machine_environment_config,
                                                       agent_enrolled_unix_system_with_users, proxy_start_stop):

        """
        This  test verifies password reconcilation using  agent, connector and both during rotate operation
            Steps for this scenario:
                * Enroll an unix system and create a managed account.
                * Verify the managed account's password is rotated.
                * Change the password of the account on the target system
                * stop the agent, start connector and rotate the password of managed account (only connector is availabe)
                    - Verify success
                    - Verify OperationMode is Connector
                * Change the password of the account on the target system
                * stop the connector and rotate the password of managed account
                    - Verify failure
                * Start the agent and rotate the password of managed account (only Agent is availabe)
                    - Verify success
                    - Verify OperationMode is Client
               * Change the password of the account on the target system
               * Start the connector and rotate the password of managed account (Both agent and connector are available)
                    - Verify success
                    - Verify OperationMode is Client
        """

        """
            Testrail Link:
                https://testrail.centrify.com/index.php?/cases/view/1293459
                https://testrail.centrify.com/index.php?/cases/view/1293460
                https://testrail.centrify.com/index.php?/cases/view/1293461
        """

        # verfiy the test is run with single thread.
        assert 'PYTEST_XDIST_WORKER_COUNT' not in os.environ, \
            f'This test cannot be run with multiple threads due to starting and stopping connectors'

        enrolledsystems = agent_enrolled_unix_system_with_users
        accounts = enrolledsystems[0]["Accounts"]
        resourceId = enrolledsystems[0]["ResourceId"]
        proxyid = enrolledsystems[0]["ProxyId"]
        session = enrolledsystems[0]["Session"]
        proxycontrol = proxy_start_stop

        conf = unix_machine_environment_config
        success_message = conf['success_message']

        right_data = ("Privileged Access Service Power User", "role_Privileged Access Service Power User")

        requester_session = users_and_roles.get_session_for_user(right_data[0])

        accountuser = accounts[1]

        logger.info("stop the agent")
        ssh_manager.ssh_stop_agent(session)
        proxycontrol(proxyid, True)

        # count managed password change events
        filter = [['AccountName', accountuser['Name']], ['ComputerID', resourceId]]

        # set a different password for the user
        ssh_manager.change_sshuser_password(session, accountuser['Name'], "differentpassword3", success_message)

        logger.info("Rotate account and verify reconciliation, Connector is available")
        result, success = ResourceManager.rotate_password(requester_session, accountuser["Id"])
        assert result["Result"], "Reconciliation failed, Rotate password failed: " + accountuser['Name']

        # verify operationMode
        rows = RedrockController.wait_for_event_by_type_filter(requester_session,
                                                               "Cloud.Server.LocalAccount.PasswordRotate",
                                                               filter=filter)
        eventcount = len(rows)
        logger.info(f"# of Cloud.Server.LocalAccount.PasswordRotate events : {eventcount}")
        assert rows[0]["OperationMode"] == "Connector", "Failed to verify OperationMode is Connector"

        # stop Connector, Should fail
        logger.info("Stopping  the connector")
        proxycontrol(proxyid, False)
        # set a different password for the user
        ssh_manager.change_sshuser_password(session, accountuser['Name'], "differentpassword4", success_message)

        logger.info(f"# of Cloud.Server.LocalAccount.PasswordRotate events : {eventcount}")
        result, success = ResourceManager.rotate_password(requester_session, accountuser["Id"])
        assert result[
                   "Result"] == False, f"Reconciliation success, Rotate password is successfull: {accountuser['Name']}"

        # Start agent
        logger.info("Starting the agent")
        ssh_manager.ssh_start_agent(session, True)
        # set a different password for the user
        ssh_manager.change_sshuser_password(session, accountuser['Name'], "differentpassword5", success_message)

        logger.info("Rotate account and verify reconciliation, Agent is available")
        result, success = ResourceManager.rotate_password(requester_session, accountuser["Id"])
        assert result["Result"], "Reconciliation failed, Rotate password failed: " + accountuser['Name']

        # verify operationMode
        rows = RedrockController.wait_for_event_by_type_filter(requester_session,
                                                               "Cloud.Server.LocalAccount.PasswordRotate",
                                                               filter=filter, count=eventcount + 1)
        eventcount = len(rows)
        logger.info(f"# of Cloud.Server.LocalAccount.PasswordRotate events : {eventcount}")
        assert rows[0]["OperationMode"] == "Client", "Failed to verify OperationMode is Client"

        # verify account again, both connector and agent are running
        logger.info("Starting connector")
        proxycontrol(proxyid, True)
        # set a different password
        ssh_manager.change_sshuser_password(session, accountuser['Name'], "differentpassword3", success_message)

        logger.info("Rotate account and verify reconciliation, client and connector are available")
        result, success = ResourceManager.rotate_password(requester_session, accountuser["Id"])
        assert result["Result"], "Reconciliation failed, Rotate password failed: " + accountuser['Name']

        # verify operationMode
        rows = RedrockController.wait_for_event_by_type_filter(requester_session,
                                                               "Cloud.Server.LocalAccount.PasswordRotate",
                                                               filter=filter, count=eventcount + 1)
        eventcount = len(rows)
        logger.info(f"# of Cloud.Server.LocalAccount.PasswordRotate events {eventcount}")
        assert rows[0]["OperationMode"] == "Client", "Failed to verify OperationMode is Client"

    @staticmethod
    def test_unix_client_account_checkout_reconciliation(users_and_roles, unix_machine_environment_config,
                                                         agent_enrolled_unix_system_with_users, proxy_start_stop):

        """
        This  test verifies password reconcilation using  agent, connector and both during checkout operation
            Steps for this scenario:
                * Enroll an unix system and create a managed account.
                * Verify the managed account's password is rotated.
                * Change the password of the account on the target system
                * stop the agent and checkout the password of managed account(only connector is availabe)
                    - Verify success
                    - Verify OperationMode is Connector
                * Verify managed acount
                    - Verify success
                * Change the password of the account on the target system
                * stop the connector and checkout the password of managed account
                    - Verify failure
                * Start the agent and checkout the password of managed account (only Agent is availabe)
                    - Verify success
                    - Verify OperationMode is Client
                * Verify managed acount
                    - Verify success
                * Change the password of the account on the target system
                * Start the connector and checkout the password of managed account (Both agent and connector are available)
                    - Verify success
                    - Verify OperationMode is Client
                * Verify managed acount
                    - Verify success
        """

        """
            Testrail Link:
                https://testrail.centrify.com/index.php?/cases/view/1293462
                https://testrail.centrify.com/index.php?/cases/view/1293463
                https://testrail.centrify.com/index.php?/cases/view/1293464
        """

        # verfiy the test is run with single thread.
        assert 'PYTEST_XDIST_WORKER_COUNT' not in os.environ, \
            f'This test cannot be run with multiple threads due to starting and stopping connectors'

        enrolledsystems = agent_enrolled_unix_system_with_users
        accounts = enrolledsystems[0]["Accounts"]
        resourceId = enrolledsystems[0]["ResourceId"]
        proxyid = enrolledsystems[0]["ProxyId"]
        session = enrolledsystems[0]["Session"]
        proxycontrol = proxy_start_stop

        conf = unix_machine_environment_config
        success_message = conf['success_message']

        right_data = ("Privileged Access Service Power User", "role_Privileged Access Service Power User")

        requester_session = users_and_roles.get_session_for_user(right_data[0])

        accountuser = accounts[1]

        logger.info("stop the agent")
        ssh_manager.ssh_stop_agent(session)
        proxycontrol(proxyid, True)

        # count managed password change events
        filter = [['AccountName', accountuser['Name']], ['ComputerID', resourceId]]

        # set a different password for the user
        ssh_manager.change_sshuser_password(session, accountuser['Name'], "differentpassword3", success_message)

        logger.info("Rotate account and verify reconciliation, Connector is available")
        result, success = ResourceManager.check_out_password(requester_session, 1, accountuser["Id"])
        assert success, "Reconciliation failed during checkout, Account " + accountuser['Name']
        verify_pass_result, verify_pass_success = ResourceManager.check_account_health(requester_session,
                                                                                       accountuser["Id"])
        assert verify_pass_result == 'OK', f"Verify Failed on Account: {accountuser['Name']}"

        # verify operationMode
        rows = RedrockController.wait_for_event_by_type_filter(
            requester_session, "Cloud.Server.LocalAccount.AdministrativeResetAccountPassword",
                                                               filter=filter)
        eventcount = len(rows)
        logger.info(f"# of Cloud.Server.LocalAccount.AdministrativeResetAccountPassword events : {eventcount}")
        assert rows[0]["OperationMode"] == "Connector", "Failed to verify OperationMode"

        # stop Connector, Should fail
        logger.info("Stopping  the connector")
        proxycontrol(proxyid, False)

        # set a different password for the user
        ssh_manager.change_sshuser_password(session, accountuser['Name'], "differentpassword4", success_message)

        verify_pass_result, verify_pass_success = ResourceManager.check_account_health(requester_session,
                                                                                       accountuser["Id"])
        assert verify_pass_result != 'OK', f"Verify Failed on Account: {accountuser['Name']}"

        # Start agent
        logger.info("Starting the agent")
        ssh_manager.ssh_start_agent(session, True)
        # set a different password for the user
        ssh_manager.change_sshuser_password(session, accountuser['Name'], "differentpassword5", success_message)

        logger.info("Rotate account and verify reconciliation, Agent is available")
        result, success = ResourceManager.check_out_password(requester_session, 1, accountuser["Id"])
        assert success, f"Reconciliation failed during checkout, Account {accountuser['Name']}"

        verify_pass_result, verify_pass_success = ResourceManager.check_account_health(requester_session,
                                                                                       accountuser["Id"])
        assert verify_pass_result == 'OK', f"Verify Failed on account: {accountuser['Name']}"

        # verify operationMode
        rows = RedrockController.wait_for_event_by_type_filter(
            requester_session, "Cloud.Server.LocalAccount.AdministrativeResetAccountPassword",
            filter=filter, count=eventcount + 1)
        eventcount = len(rows)
        logger.info(f"# of Cloud.Server.LocalAccount.AdministrativeResetAccountPassword events : {eventcount}")
        assert rows[0]["OperationMode"] == "Client", "Failed to verify OperationMode is Client"

        # verify account again, both connector and agent are running
        logger.info("Starting connector")
        proxycontrol(proxyid, True)
        # set a different password
        ssh_manager.change_sshuser_password(session, accountuser['Name'], "differentpassword3", success_message)

        logger.info("Rotate account and verify reconciliation, client and connector are available")
        result, success = ResourceManager.check_out_password(requester_session, 1, accountuser["Id"])
        assert success, f"Reconciliation failed during checkout, Account {accountuser['Name']}"

        verify_pass_result, verify_pass_success = ResourceManager.check_account_health(requester_session,
                                                                                       accountuser["Id"])
        assert verify_pass_result == 'OK', f"Verify Failed on Account: {accountuser['Name']}"

        # verify operationMode
        rows = RedrockController.wait_for_event_by_type_filter(
            requester_session, "Cloud.Server.LocalAccount.AdministrativeResetAccountPassword",
            filter=filter, count=eventcount + 1)
        eventcount = len(rows)
        logger.info(f"# of Cloud.Server.LocalAccount.AdministrativeResetAccountPassword events : {eventcount}")
        assert rows[0]["OperationMode"] == "Client", "Failed to verify OperationMode is Client"
