from Shared.API.infrastructure import ResourceManager
from Shared.UI.Centrify.selectors import GridRowByGuid
import pytest
import logging

logger = logging.getLogger("test")


@pytest.mark.ui
@pytest.mark.pas
@pytest.mark.workflow
def test_check_policy_page(core_session, setup_pas_system_for_unix, core_admin_ui):
    """
    Test Case ID: C2089
    Test Case Description: Check policy page after changing account workflow
    :param core_session: Creates API session
    :param setup_pas_system_for_unix: Creates a Unix System with Account.
    :param core_admin_ui: Authenticates Centrify UI session.
    """
    system_id, account_id, sys_info = setup_pas_system_for_unix
    system_name = sys_info[0]
    ui = core_admin_ui
    ui.navigate('Resources', 'Systems')
    ui.search(system_name)
    ui.click_row(GridRowByGuid(system_id))
    ui.click_row(GridRowByGuid(account_id))
    ui.tab('Policy')
    expected_checkout_lifetime_value = 16
    ui.input('DefaultCheckoutTime', expected_checkout_lifetime_value)
    ui.save()
    ui.tab('Workflow')
    ui.select_option('WorkflowEnabled', 'No')
    ui.save()
    ui.tab('Policy')
    ui.refresh()
    account_info = ResourceManager.get_account_information(core_session, account_id)

    # Getting Checkout Time value
    actual_checkout_lifetime_value = account_info[0]['VaultAccount']['Row']['DefaultCheckoutTime']
    assert expected_checkout_lifetime_value == actual_checkout_lifetime_value, f'{expected_checkout_lifetime_value} ' \
                                                                               f'is not equal to ' \
                                                                               f'{actual_checkout_lifetime_value} '
    logger.info(f'Checkout Lifetime value i.e.{expected_checkout_lifetime_value} did not get removed after refreshing '
                f'the page.')
