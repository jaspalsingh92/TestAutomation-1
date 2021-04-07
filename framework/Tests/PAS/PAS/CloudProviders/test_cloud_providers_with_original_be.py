import pytest
import logging
from Utils.assets import get_asset_path


logger = logging.getLogger('test')

pytestmark = [pytest.mark.ui, pytest.mark.cloudprovider, pytest.mark.root_login, pytest.mark.cbe]

@pytest.mark.parametrize("browser_extension_path_override", [get_asset_path('CentrifyChromeExtension_ver_207.zip')], indirect=True)
@pytest.mark.parametrize("user_rights", ['Privileged Access Service Administrator'], indirect=True)
def test_old_browser_extension_works(live_aws_cloud_provider_and_accounts, grant_permission_to_root_account, cds_be_ui):
    """
    Tests to see if the original browser extension works with cloud providers

    If at some point in the future it won't work, this test can be changed to verify
    the user is informed that the be is too old and won't work
    """
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