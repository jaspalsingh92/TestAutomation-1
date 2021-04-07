import logging
import pytest

from Shared.API.cloud_provider import CloudProviderManager
from Shared.API.infrastructure import ResourceManager
from Shared.endpoint_manager import EndPoints
from Utils.guid import guid

logger = logging.getLogger("test")


pytestmark = [pytest.mark.api, pytest.mark.cloudprovider]


def _is_valid_html(text, username=None):
    text = str(text)
    if "Something went wrong" in text:
        return False
    if username is not None and username not in text:
        return False

    return text.startswith("<!DOCTYPE html>")\
        and text.endswith("</html>")\
        and "//signin.aws.amazon.com" in text


def _all_permissions_rotate():
    return ['View', 'Login', 'Naked', 'UpdatePassword', 'RotatePassword']


def _all_permissions_login():
    return ['View', 'Login', 'Naked']


def _set_permissions(session, limited_user, cloud_provider_id, account_id, provider_permissions, root_acct_permissions):
    if isinstance(provider_permissions, list):
        provider_permissions = ",".join(provider_permissions)
    if isinstance(root_acct_permissions, list):
        root_acct_permissions = ",".join(root_acct_permissions)

    assert isinstance(provider_permissions, str), f"Invalid arguments passed to _set_permissions provider_permissions {provider_permissions}"
    assert isinstance(root_acct_permissions, str), f"Invalid arguments passed to _set_permissions root_acct_permissions {root_acct_permissions}"

    result, success = ResourceManager.assign_account_permissions(session, root_acct_permissions,
                                                                 limited_user.get_login_name(),
                                                                 limited_user.get_id(), "User",
                                                                 account_id)
    assert success, f"Failed to execute API call to set permissions {result}"

    result, success = CloudProviderManager.set_cloud_provider_permissions(session, provider_permissions, limited_user.get_login_name(),
                                                                          limited_user.get_id(), "User", cloud_provider_id)
    assert success, f"Failed to execute API call to set permissions {result}"


def test_login_web_account_no_params(core_session):

    request = core_session.apirequest(EndPoints.LOGIN_CLOUD_WEB_ACCOUNT, {})
    logger.debug("Login Web cloud provider called with no parameters, returned: " + request.text)

    text = request.text

    assert not _is_valid_html(text), "Should fail if no parameters passed"


@pytest.mark.parametrize('user_rights', ['Application Management'], indirect=True)
def test_login_succeeds_with_permissions(core_session, fake_cloud_provider_root_account, cds_session):

    account_id, username, password, cloud_provider_id, test_did_cleaning = fake_cloud_provider_root_account
    requester_session, limited_user = cds_session

    provider_permissions = "View"
    root_acct_permissions = _all_permissions_login()
    _set_permissions(core_session, limited_user, cloud_provider_id, account_id, provider_permissions, root_acct_permissions)

    result = CloudProviderManager.login_web_cloud_provider(requester_session, account_id, operation="login")
    assert _is_valid_html(result), f"Expected to pass after permissions applied"


@pytest.mark.parametrize('user_rights', ['Application Management'], indirect=True)
def test_rotate_succeeds_with_permissions(core_session, fake_cloud_provider_root_account, cds_session):

    account_id, username, password, cloud_provider_id, test_did_cleaning = fake_cloud_provider_root_account
    requester_session, limited_user = cds_session

    provider_permissions = "View"
    root_acct_permissions = _all_permissions_rotate()
    _set_permissions(core_session, limited_user, cloud_provider_id, account_id, provider_permissions, root_acct_permissions)

    result = CloudProviderManager.login_web_cloud_provider(requester_session, account_id, operation="rotate")
    assert _is_valid_html(result), f"Expected to pass after permissions applied"


@pytest.mark.parametrize('user_rights', ['Application Management'], indirect=True)
def test_login_fails_without_provider_view_permission(core_session, fake_cloud_provider_root_account, cds_session):

    account_id, username, password, cloud_provider_id, test_did_cleaning = fake_cloud_provider_root_account
    requester_session, limited_user = cds_session

    provider_permissions = "None"  # <-- This is what's different to cause the fail
    root_acct_permissions = _all_permissions_login()
    _set_permissions(core_session, limited_user, cloud_provider_id, account_id, provider_permissions, root_acct_permissions)

    result = CloudProviderManager.login_web_cloud_provider(requester_session, account_id, operation="login")
    assert not _is_valid_html(result), f"Expected to fail without provider view permission"


@pytest.mark.parametrize("missing_permissions", ['Login', 'Naked', 'View'])
@pytest.mark.parametrize('user_rights', ['Application Management'], indirect=True)
def test_login_fails_missing_root_account_permission(core_session, fake_cloud_provider_root_account, cds_session, missing_permissions):

    account_id, username, password, cloud_provider_id, test_did_cleaning = fake_cloud_provider_root_account
    requester_session, limited_user = cds_session

    provider_permissions = "View"
    root_acct_permissions = _all_permissions_login()

    root_acct_permissions.remove(missing_permissions)

    _set_permissions(core_session, limited_user, cloud_provider_id, account_id, provider_permissions, root_acct_permissions)

    result = CloudProviderManager.login_web_cloud_provider(requester_session, account_id, operation="login")
    assert not _is_valid_html(result), f"Expected to fail without provider {missing_permissions} permission on root account"


@pytest.mark.parametrize("missing_permissions", ['Login', 'Naked', 'View', 'UpdatePassword', 'RotatePassword'])
@pytest.mark.parametrize('user_rights', ['Application Management'], indirect=True)
def test_rotate_fails_missing_root_account_permission(core_session, fake_cloud_provider_root_account, cds_session, missing_permissions):

    account_id, username, password, cloud_provider_id, test_did_cleaning = fake_cloud_provider_root_account
    requester_session, limited_user = cds_session

    provider_permissions = "View"
    root_acct_permissions = _all_permissions_rotate()

    root_acct_permissions.remove(missing_permissions)

    _set_permissions(core_session, limited_user, cloud_provider_id, account_id, provider_permissions, root_acct_permissions)

    result = CloudProviderManager.login_web_cloud_provider(requester_session, account_id, operation="rotate")
    assert not _is_valid_html(result), f"Expected to fail without provider {missing_permissions} permission on root account"


@pytest.mark.parametrize('user_rights', ['Application Management'], indirect=True)
def test_rotate_fails_if_policy_disables_it(core_session, fake_cloud_provider_root_account, cds_session):

    account_id, username, password, cloud_provider_id, test_did_cleaning = fake_cloud_provider_root_account
    requester_session, limited_user = cds_session

    provider_permissions = "View"
    root_acct_permissions = _all_permissions_rotate()

    _set_permissions(core_session, limited_user, cloud_provider_id, account_id, provider_permissions, root_acct_permissions)

    result, success = CloudProviderManager.update_cloud_provider(core_session, cloud_provider_id, "Aws",
                                                                 name=f"new name{guid()}",
                                                                 description="Policy rotate disabled for api test",
                                                                 enable_unmanaged_password_rotation=False)
    assert success, f"Failed to update cloud provider {result}"

    result = CloudProviderManager.login_web_cloud_provider(requester_session, account_id, operation="rotate")
    assert not _is_valid_html(result), f"Expected to fail with policy set to no rotations"
