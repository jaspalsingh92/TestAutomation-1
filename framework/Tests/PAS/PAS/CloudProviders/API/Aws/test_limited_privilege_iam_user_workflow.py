import pytest
import logging

from Shared.API.workflow import WorkflowApprovers

from Shared.Workflow.approve import ApproveRequest
from Shared.Workflow.reject import RejectRequest
from Shared.Workflow.checkace import CheckRowAce
from Shared.Workflow.VaultAccount.setup_cloud_provider import SetupCloudProviderAccount
from Shared.Workflow.VaultAccount.request.retrieve_access_key import RequestRetrieveAccessKey
from Shared.Workflow.VaultAccount.attempt.retrieve_access_key import RetrieveAccessKey
from Shared.Workflow.Scenario.windowed import WindowedScenario
from Shared.Workflow.Scenario.permanent import PermanentScenario
from Shared.Workflow.Scenario.disabled import DisabledScenario
from Shared.Workflow.Scenario.multipleapprover import MultipleApproverScenario

logger = logging.getLogger('test')

pytestmark = [pytest.mark.api, pytest.mark.workflow, pytest.mark.cloudprovider, pytest.mark.aws, pytest.mark.iam_user, pytest.mark.workflow]

lock_tenant = True


@pytest.fixture(scope="function")
def base_iam_user_workflow_setup(
        core_session,
        users_and_roles,
        live_aws_cloud_provider_and_accounts,
        aws_iam_user_1_name,
        aws_root_user_credentials,
        update_workflow_global_settings,
        aws_iam_user_credentials):
    cloud_provider_ids, iam_account_ids, access_key_ids, root_account_id, cloud_provider_name = live_aws_cloud_provider_and_accounts
    root_user_name, root_user_password = aws_root_user_credentials

    setup = SetupCloudProviderAccount(
        logger,
        users_and_roles,
        core_session,
        iam_account_ids[0],
        cloud_provider_ids[0],
        aws_iam_user_1_name,
        update_workflow_global_settings
    )

    yield setup, iam_account_ids[0], access_key_ids[0]

    setup.remove_granted_permissions('VaultAccount', 1 << 16)


@pytest.fixture(scope="function")
def iam_user_workflow_setup(
        base_iam_user_workflow_setup):
    setup, account_id, access_key_id = base_iam_user_workflow_setup

    setup.setup_limited_sessions()
    setup.setup_workflow_approvers(WorkflowApprovers.ONLY_AUTHENTICATED_USER)
    setup.setup_workflow_on_object(True)
    setup.setup_limited_permissions()

    yield setup, account_id, access_key_id


@pytest.fixture(scope="function")
def iam_user_multi_approver_workflow_setup(
        base_iam_user_workflow_setup):
    setup, account_id, access_key_id = base_iam_user_workflow_setup

    setup.setup_limited_sessions()
    setup.setup_workflow_approvers(WorkflowApprovers.AUTHENTICATED_USER_AND_PAS_USER)
    setup.setup_workflow_on_object(True)
    setup.setup_limited_permissions()

    yield setup, account_id, access_key_id


@pytest.fixture(scope="function")
def iam_user_global_workflow_setup(base_iam_user_workflow_setup):
    setup, account_id, access_key_id = base_iam_user_workflow_setup

    setup.setup_limited_sessions()
    setup.setup_workflow_approvers(WorkflowApprovers.ONLY_AUTHENTICATED_USER)
    setup.setup_global_workflow()
    setup.setup_limited_permissions()

    yield setup, account_id, access_key_id


def test_request_windowed_retrieve_access_key(
        iam_user_workflow_setup,
        core_session):
    """
    https://testrail.centrify.com/index.php?/cases/view/1317497
    """

    setup, account_id, access_key_id = iam_user_workflow_setup

    request = RequestRetrieveAccessKey(logger, account_id)
    approve = ApproveRequest(logger)
    reject = RejectRequest(logger)
    attempt = RetrieveAccessKey(logger, account_id, access_key_id)
    check_ace = CheckRowAce(logger, core_session, account_id, 'VaultAccount', 1 << 16)
    scenario = WindowedScenario(logger, 'Windowed access key retrieve')

    scenario.run(setup, request, approve, reject, attempt, check_ace)


def test_request_global_workflow_retrieve_access_key(
        iam_user_global_workflow_setup,
        core_session):
    """
    https://testrail.centrify.com/index.php?/cases/view/1317497
    """

    setup, account_id, access_key_id = iam_user_global_workflow_setup

    request = RequestRetrieveAccessKey(logger, account_id)
    approve = ApproveRequest(logger)
    reject = RejectRequest(logger)
    attempt = RetrieveAccessKey(logger, account_id, access_key_id)
    check_ace = CheckRowAce(logger, core_session, account_id, 'VaultAccount', 1 << 16)
    scenario = WindowedScenario(logger, 'Global approval windowed access key retrieve')
    disabled_scenario = DisabledScenario(logger, 'Global approval windowed access key retrieve when workflow disabled')

    scenario.run(setup, request, approve, reject, attempt, check_ace)

    # Reset permissions
    setup.remove_granted_permissions('VaultAccount', 1 << 16)
    # Remove workflow setting on the object
    setup.setup_workflow_on_object(False)

    disabled_scenario.run(setup, request, approve, reject, attempt, check_ace)


def test_request_multiple_approver_retrieve_access_key(
        iam_user_multi_approver_workflow_setup,
        core_session):
    """
    https://testrail.centrify.com/index.php?/cases/view/1317497
    """

    setup, account_id, access_key_id = iam_user_multi_approver_workflow_setup

    request = RequestRetrieveAccessKey(logger, account_id)
    approve = ApproveRequest(logger)
    reject = RejectRequest(logger)
    attempt = RetrieveAccessKey(logger, account_id, access_key_id)
    check_ace = CheckRowAce(logger, core_session, account_id, 'VaultAccount', 1 << 16)
    scenario = MultipleApproverScenario(logger, 'Multiple approver windowed access key retrieve')

    scenario.run(setup, request, approve, reject, attempt, check_ace)


def test_request_permanent_retrieve_access_key(
        iam_user_workflow_setup,
        core_session):
    """
    https://testrail.centrify.com/index.php?/cases/view/1317497
    """

    setup, account_id, access_key_id = iam_user_workflow_setup

    request = RequestRetrieveAccessKey(logger, account_id)
    approve = ApproveRequest(logger)
    reject = RejectRequest(logger)
    attempt = RetrieveAccessKey(logger, account_id, access_key_id)
    check_ace = CheckRowAce(logger, core_session, account_id, 'VaultAccount', 1 << 16)
    scenario = PermanentScenario(logger, 'Permanent access key retrieve')

    scenario.run(setup, request, approve, reject, attempt, check_ace)