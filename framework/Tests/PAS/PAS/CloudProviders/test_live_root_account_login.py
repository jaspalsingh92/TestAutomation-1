import pytest
import logging

logger = logging.getLogger("test")

pytestmark = [pytest.mark.ui, pytest.mark.cloudprovider, pytest.mark.root_login, pytest.mark.cbe]


def _test_root_account_login(ui, user, root_account_id, cloud_provider_ids, grant_permission):
    grant_permission(user, root_account_id, 'View,Login,Naked')
    ui.navigate('Resources', 'Cloud Providers')
    ui.action_by_guid(
        'Login',
        cloud_provider_ids
    )
    ui.switch_to_pop_up_window()

    found_url = ui.wait_for_url_match('https://console.aws.amazon.com/billing/home', max_seconds_to_wait=180)
    assert found_url is True, f'Login failed for AWS root account under poor networking conditions. Check screenshots'


def _test_root_account_login_same_session_amazon(ui, user, root_account_id, cloud_provider_ids, grant_permission):
    """
    On an amazon.com registered root account, the tab will start already logged in because the auth cookie behaves differently
    than when the root account was registered on AWS. Do the same flow, but then we have to wait for the billing/home tab twice.
    """
    ui.close_browser()
    ui.switch_to_main_window()
    ui.action_by_guid(
        'Login',
        cloud_provider_ids
    )
    ui.switch_to_pop_up_window()

    found_url = ui.wait_for_url_match('amazon.com/ap/signin', max_seconds_to_wait=180)
    assert found_url is True, f'Second login in same session didn\'t visit signin page. Check screenshots'

    found_url = ui.wait_for_url_match('https://console.aws.amazon.com/billing/home', max_seconds_to_wait=180)
    assert found_url is True, f'Second login in same session failed for AWS root account. Check screenshots'


@pytest.mark.parametrize("user_rights", ['Privileged Access Service Administrator'], indirect=True)
def test_root_account_login_works_on_unmodified_network(live_aws_cloud_provider_and_accounts, grant_permission_to_root_account, cds_be_ui):
    ui, user = cds_be_ui
    cloud_provider_ids, iam_account_ids, access_key_ids, root_account_id, cloud_provider_name = live_aws_cloud_provider_and_accounts
    _test_root_account_login(ui, user, root_account_id, cloud_provider_ids, grant_permission_to_root_account)


@pytest.mark.parametrize("user_rights", ['Privileged Access Service Administrator'], indirect=True)
def test_root_account_login_works_from_accounts(live_aws_cloud_provider_and_accounts, grant_permission_to_root_account, cds_be_ui):
    ui, user = cds_be_ui
    cloud_provider_ids, iam_account_ids, access_key_ids, root_account_id, cloud_provider_name = live_aws_cloud_provider_and_accounts
    grant_permission_to_root_account(user, root_account_id, 'View,Login,Naked')
    ui.navigate('Resources', 'Accounts')
    ui.click_set('AWS Root Accounts')
    ui.action_by_guid(
        'Login',
        root_account_id
    )
    ui.switch_to_pop_up_window()

    found_url = ui.wait_for_url_match('https://console.aws.amazon.com/billing/home', max_seconds_to_wait=180)
    assert found_url is True, f'Login failed for AWS root account under poor networking conditions. Check screenshots'


@pytest.mark.parametrize('force_poor_network', [True], indirect=True)
@pytest.mark.parametrize('force_production_build', [True], indirect=True)
@pytest.mark.parametrize("user_rights", ['Privileged Access Service Administrator'], indirect=True)
def test_root_account_login_works_on_slow_network(live_aws_cloud_provider_and_accounts, grant_permission_to_root_account, cds_be_ui):
    ui, user = cds_be_ui
    cloud_provider_ids, iam_account_ids, access_key_ids, root_account_id, cloud_provider_name = live_aws_cloud_provider_and_accounts
    _test_root_account_login(ui, user, root_account_id, cloud_provider_ids, grant_permission_to_root_account)


@pytest.mark.parametrize('force_poor_network', [True], indirect=True)
@pytest.mark.parametrize('force_production_build', [True], indirect=True)
@pytest.mark.parametrize("user_rights", ['Privileged Access Service Administrator'], indirect=True)
def test_amazon_root_account_login_works_on_slow_network(live_amazon_aws_cloud_provider_and_root_account, grant_permission_to_root_account, cds_be_ui):
    ui, user = cds_be_ui
    cloud_provider_ids, root_account_id = live_amazon_aws_cloud_provider_and_root_account
    _test_root_account_login(ui, user, root_account_id, cloud_provider_ids, grant_permission_to_root_account)


@pytest.mark.skip("This requires a configured amazon.com account")
@pytest.mark.parametrize("user_rights", ['Privileged Access Service Administrator'], indirect=True)
def test_amazon_root_account_login_twice_works_on_unmodified_network(live_amazon_aws_cloud_provider_and_root_account, grant_permission_to_root_account, cds_be_ui):
    ui, user = cds_be_ui
    cloud_provider_ids, root_account_id = live_amazon_aws_cloud_provider_and_root_account
    # First login in this browser session
    _test_root_account_login(ui, user, root_account_id, cloud_provider_ids, grant_permission_to_root_account)
    # Second login in this browser session
    _test_root_account_login_same_session_amazon(ui, user, root_account_id, cloud_provider_ids, grant_permission_to_root_account)

