import logging
import pytest
from Shared.API.infrastructure import ResourceManager
from Shared.API.redrock import RedrockController
from Shared.UI.Centrify.selectors import Div

logger = logging.getLogger("test")


@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_add_system_account_with_win_rm(core_session, pas_windows_setup):
    """C2536 Add system with managed account with WinRM http setting
           validate the added Account with win rm and check out password after 5 minutes"""

    # Getting system details.
    system_id, account_id, sys_info, connector_id, user_password = pas_windows_setup(True)

    # Verifying Default management mode should be 'RpcOverTcp'
    system_rows = RedrockController.get_computer_with_ID(core_session, system_id)
    assert system_rows['ManagementMode'] == 'RpcOverTcp', "Default Management mode is not RpcOverTcp"
    logger.info("Default Management mode is RPC Over TCP")

    # Checkout Password
    checkout_password_result, checkout_password_success = ResourceManager. \
        check_out_password(core_session,
                           lifetime=1,
                           accountid=account_id)
    assert checkout_password_success, f"Failed to checkout password due to {checkout_password_result}"
    logger.info("Password checkout successfully")

    assert checkout_password_result['Password'] != user_password, "Password is same after adding managed account"
    logger.info("Password updated after adding managed account")

    success, response = ResourceManager.update_system(core_session, system_id, sys_info[0],
                                                      sys_info[1], 'Windows',
                                                      proxycollectionlist=connector_id,
                                                      chooseConnector="on", managementmode="WinRMOverHttp")
    assert success, "Failed to update system"
    logger.info(f"Successfully updated system '{sys_info[0]}'")

    # Adding account in portal.
    acc_result, acc_success = ResourceManager.add_account(core_session, sys_info[6],
                                                          password=user_password, host=system_id,
                                                          ismanaged=True)
    assert acc_success, f"Failed to add account in the portal: {acc_result}"
    logger.info(f"Successfully added account {sys_info[6]} in the portal")

    # Checkout Password after changing management mode to WinRMOverHttp
    checkout_password_winrm, checkout_password_success = ResourceManager. \
        check_out_password(core_session,
                           lifetime=1,
                           accountid=acc_result)
    assert checkout_password_success, f"Failed to checkout password due to {checkout_password_winrm}"
    logger.info("Password checkout successfully")

    assert checkout_password_winrm['Password'] != user_password, "Password is same after adding managed account"
    logger.info("Password updated after adding managed account")


@pytest.mark.ui
@pytest.mark.pasui
@pytest.mark.pas
@pytest.mark.bhavna
def test_add_system_invalid_proxy_account(pas_config, core_ui):
    """C1822 Add Windows resource after clearing valid managed account and invalid proxy account
        validate the added invalid proxy and valid manage Account Activity log's
    """
    core_ui = core_ui
    account_details = pas_config
    sys_data = account_details['Windows_infrastructure_data']
    core_ui.navigate('Resources', 'Systems')
    core_ui.launch_modal('Add System')
    core_ui.input('Name', sys_data['system_name'])
    core_ui.input('FQDN', sys_data['FQDN'])
    core_ui.step('Next >')
    core_ui.step('Next >')
    core_ui.check('SetupProxyAccount')
    core_ui.input('ProxyUser', sys_data['invalid_proxy_username'])
    core_ui.input('ProxyUserPassword', sys_data['invalid_proxy_password'])
    core_ui.check('ProxyUserIsManaged')
    core_ui.step('Next >')
    core_ui.step('Finish')
    core_ui.expect_disappear(Div('Verification failed. Bad proxy account credentials.'), 'worng pop message is not '
                                                                                         'getting launch',
                             time_to_wait=90)
