import pytest
import logging

from Shared.API.workflow import WorkflowApprovers

from Shared.Workflow.approve import ApproveRequest
from Shared.Workflow.reject import RejectRequest
from Shared.Workflow.checkace import CheckRowAce
from Shared.Workflow.VaultAccount.setup_cloud_provider import SetupCloudProviderAccount
from Shared.Workflow.VaultAccount.request.checkout import RequestVaultAccountCheckout
from Shared.Workflow.VaultAccount.request.login import RequestVaultAccountLogin
from Shared.Workflow.VaultAccount.attempt.checkout import VaultAccountCheckout
from Shared.Workflow.VaultAccount.attempt.root_account_login import RootAccountLogin
from Shared.Workflow.Scenario.windowed import WindowedScenario
from Shared.Workflow.Scenario.permanent import PermanentScenario
from Shared.Workflow.Scenario.disabled import DisabledScenario
from Shared.Workflow.Scenario.multipleapprover import MultipleApproverScenario

logger = logging.getLogger('test')

pytestmark = [pytest.mark.api, pytest.mark.workflow, pytest.mark.cloudprovider, pytest.mark.aws, pytest.mark.workflow]

lock_tenant = True

@pytest.fixture(scope="function")
def base_cloud_provider_workflow_setup(
        core_session,
        users_and_roles,
        live_aws_cloud_provider_and_accounts,
        aws_root_user_credentials,
        update_workflow_global_settings):
    cloud_provider_ids, iam_account_ids, access_key_ids, root_account_id, cloud_provider_name = live_aws_cloud_provider_and_accounts
    root_user_name, root_user_password = aws_root_user_credentials

    setup = SetupCloudProviderAccount(
        logger,
        users_and_roles,
        core_session,
        root_account_id,
        cloud_provider_ids[0],
        root_user_name,
        update_workflow_global_settings
    )

    yield setup, root_account_id

    setup.remove_granted_permissions('VaultAccount', 1 << 16)


@pytest.fixture(scope="function")
def cloud_provider_workflow_setup(
        base_cloud_provider_workflow_setup):
    setup, root_account_id = base_cloud_provider_workflow_setup

    setup.setup_limited_sessions()
    setup.setup_workflow_approvers(WorkflowApprovers.ONLY_AUTHENTICATED_USER)
    setup.setup_workflow_on_object(True)
    setup.setup_limited_permissions()

    yield setup, root_account_id


@pytest.fixture(scope="function")
def cloud_provider_multi_approver_workflow_setup(
        base_cloud_provider_workflow_setup):
    setup, root_account_id = base_cloud_provider_workflow_setup

    setup.setup_limited_sessions()
    setup.setup_workflow_approvers(WorkflowApprovers.AUTHENTICATED_USER_AND_PAS_USER)
    setup.setup_workflow_on_object(True)
    setup.setup_limited_permissions()

    yield setup, root_account_id


@pytest.fixture(scope="function")
def cloud_provider_global_workflow_setup(base_cloud_provider_workflow_setup):
    setup, root_account_id = base_cloud_provider_workflow_setup

    setup.setup_limited_sessions()
    setup.setup_workflow_approvers(WorkflowApprovers.ONLY_AUTHENTICATED_USER)
    setup.setup_global_workflow()
    setup.setup_limited_permissions()

    yield setup, root_account_id


def test_request_windowed_checkout_root_account_password(
        cloud_provider_workflow_setup,
        core_session):
    """
    https://testrail.centrify.com/index.php?/cases/view/1317497
    """

    setup, root_account_id = cloud_provider_workflow_setup

    request = RequestVaultAccountCheckout(logger, root_account_id)
    approve = ApproveRequest(logger)
    reject = RejectRequest(logger)
    attempt = VaultAccountCheckout(logger, root_account_id)
    check_ace = CheckRowAce(logger, core_session, root_account_id, 'VaultAccount', 1 << 16)
    scenario = WindowedScenario(logger, 'Windowed checkout')

    scenario.run(setup, request, approve, reject, attempt, check_ace)


def test_request_global_workflow_checkout_root_account_password(
        cloud_provider_global_workflow_setup,
        core_session):
    """
    https://testrail.centrify.com/index.php?/cases/view/1317497
    """

    setup, root_account_id = cloud_provider_global_workflow_setup

    request = RequestVaultAccountCheckout(logger, root_account_id)
    approve = ApproveRequest(logger)
    reject = RejectRequest(logger)
    attempt = VaultAccountCheckout(logger, root_account_id)
    check_ace = CheckRowAce(logger, core_session, root_account_id, 'VaultAccount', 1 << 16)
    scenario = WindowedScenario(logger, 'Windowed checkout')
    disabled_scenario = DisabledScenario(logger, 'Global approval enabled but object workflow disabled')

    scenario.run(setup, request, approve, reject, attempt, check_ace)

    # Reset permissions
    setup.remove_granted_permissions('VaultAccount', 1 << 16)
    # Remove workflow setting on the secret
    setup.setup_workflow_on_object(False)

    disabled_scenario.run(setup, request, approve, reject, attempt, check_ace)


def test_request_multiple_approver_checkout_root_account_password(
        cloud_provider_multi_approver_workflow_setup,
        core_session):
    """
    https://testrail.centrify.com/index.php?/cases/view/1317497
    """

    setup, root_account_id = cloud_provider_multi_approver_workflow_setup

    request = RequestVaultAccountCheckout(logger, root_account_id)
    approve = ApproveRequest(logger)
    reject = RejectRequest(logger)
    attempt = VaultAccountCheckout(logger, root_account_id)
    check_ace = CheckRowAce(logger, core_session, root_account_id, 'VaultAccount', 1 << 16)
    scenario = MultipleApproverScenario(logger, 'Multiple approver checkout')

    scenario.run(setup, request, approve, reject, attempt, check_ace)


def test_request_permanent_checkout_root_account_password(
        cloud_provider_workflow_setup,
        core_session):
    """
    https://testrail.centrify.com/index.php?/cases/view/1317497
    """

    setup, root_account_id = cloud_provider_workflow_setup

    request = RequestVaultAccountCheckout(logger, root_account_id)
    approve = ApproveRequest(logger)
    reject = RejectRequest(logger)
    attempt = VaultAccountCheckout(logger, root_account_id)
    check_ace = CheckRowAce(logger, core_session, root_account_id, 'VaultAccount', 1 << 16)
    scenario = PermanentScenario(logger, 'Permanent checkout')

    scenario.run(setup, request, approve, reject, attempt, check_ace)


def test_request_windowed_login_root_account(
        cloud_provider_workflow_setup,
        core_session):
    """
    https://testrail.centrify.com/index.php?/cases/view/1317497
    """

    setup, root_account_id = cloud_provider_workflow_setup

    request = RequestVaultAccountLogin(logger, root_account_id)
    approve = ApproveRequest(logger)
    reject = RejectRequest(logger)
    attempt = RootAccountLogin(logger, root_account_id)
    check_ace = CheckRowAce(logger, core_session, root_account_id, 'VaultAccount', 1 << 16 | 1 << 7)
    scenario = WindowedScenario(logger, 'Windowed login')

    scenario.run(setup, request, approve, reject, attempt, check_ace)


def test_request_permanent_login_root_account(
        cloud_provider_workflow_setup,
        core_session):
    """
    https://testrail.centrify.com/index.php?/cases/view/1317497
    """

    setup, root_account_id = cloud_provider_workflow_setup

    request = RequestVaultAccountLogin(logger, root_account_id)
    approve = ApproveRequest(logger)
    reject = RejectRequest(logger)
    attempt = RootAccountLogin(logger, root_account_id)
    check_ace = CheckRowAce(logger, core_session, root_account_id, 'VaultAccount', 1 << 16 | 1 << 7)
    scenario = PermanentScenario(logger, 'Windowed login')

    scenario.run(setup, request, approve, reject, attempt, check_ace)


def test_request_multiple_approver_permanent_login_root_account_password(
        cloud_provider_multi_approver_workflow_setup,
        core_session):
    """
    https://testrail.centrify.com/index.php?/cases/view/1317497
    """

    setup, root_account_id = cloud_provider_multi_approver_workflow_setup

    request = RequestVaultAccountLogin(logger, root_account_id)
    approve = ApproveRequest(logger)
    reject = RejectRequest(logger)
    attempt = RootAccountLogin(logger, root_account_id)
    check_ace = CheckRowAce(logger, core_session, root_account_id, 'VaultAccount', 1 << 16 | 1 << 7)
    scenario = MultipleApproverScenario(logger, 'Permanent login')

    scenario.run(setup, request, approve, reject, attempt, check_ace)


def test_request_global_workflow_login_root_account_password(
        cloud_provider_global_workflow_setup,
        core_session):
    """
    https://testrail.centrify.com/index.php?/cases/view/1317497
    """

    setup, root_account_id = cloud_provider_global_workflow_setup

    request = RequestVaultAccountLogin(logger, root_account_id)
    approve = ApproveRequest(logger)
    reject = RejectRequest(logger)
    attempt = RootAccountLogin(logger, root_account_id)
    check_ace = CheckRowAce(logger, core_session, root_account_id, 'VaultAccount', 1 << 16 | 1 << 7)
    scenario = WindowedScenario(logger, 'Windowed login')
    disabled_scenario = DisabledScenario(logger, 'Global approval enabled but object workflow disabled')

    scenario.run(setup, request, approve, reject, attempt, check_ace)

    # Reset permissions
    setup.remove_granted_permissions('VaultAccount', 1 << 16 | 1 << 7)
    # Remove workflow setting on the secret
    setup.setup_workflow_on_object(False)

    disabled_scenario.run(setup, request, approve, reject, attempt, check_ace)