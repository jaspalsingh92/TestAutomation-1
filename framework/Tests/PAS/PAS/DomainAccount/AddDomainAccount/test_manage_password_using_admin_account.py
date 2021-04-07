import pytest
from Shared.API.infrastructure import ResourceManager
from Shared.API.redrock import RedrockController
from Shared.API.server import ServerManager
from Shared.UI.Centrify.selectors import GridRow, DisabledTextBox
import logging

logger = logging.getLogger("test")


@pytest.mark.ui
@pytest.mark.bhavna
@pytest.mark.pas_skip("manage password is not fixed yet CC-71239")
def test_manage_account_for_valid_domain_account(domain_config_data, core_ui, core_session):
    """
    TCID: C1330: Manage password using administrative account for a valid domain account
    :param core_ui: To Open the UI
    :param core_session: To create the session

    """
    conf = domain_config_data
    name = conf['pas_bat_scenario1_infrastructure_data'][0]
    domain_name = name["Domain_name3"]

    data = conf['pas_scenario1_new_accounts'][0]
    account_name = data['Managed_account']

    ui = core_ui
    ui.navigate("Resources", "Domains")
    ui.search(domain_name)
    ui.click_row(GridRow(domain_name))
    ui.user_menu("Reload Rights")
    ui._waitUntilSettled()
    ui.launch_modal("Add", modal_title="Add Account")

    ui.input("User", account_name)
    ui.uncheck("IsManaged")
    ui.input("Password", "aaa")
    ui.check("IsManaged")
    check_disabled_textbox = ui.expect(DisabledTextBox("Password"), f'Text box is still enabled')
    assert check_disabled_textbox, f'Password Text Box is not disabled'
    ui.button("Add")
    ui.user_menu("Reload Rights")
    ui._waitUntilSettled()
    account_id = None
    results = ServerManager.get_all_accounts(core_session)

    for result in results:
        if result['User'] == account_name:
            account_id = result['ID']
    while True:
        result, success = ResourceManager.get_account_information(core_session, account_id)
        if result['VaultAccount']['Row']['Status'] != "Missing Password":
            break
        else:
            continue

    activity = RedrockController.get_account_activity(core_session, account_id)
    detail = []

    for activity_detail in activity:
        detail.append(activity_detail['Detail'])
    assert f'SYSTEM$ changed domain account "{account_name}" password for {domain_name}' in detail[
         0], f'could not able to change password'
    logger.info(f"detail list are: , {detail}")
    result, success = ResourceManager.del_account(core_session, account_id)
    assert success, f'Account did not get delete '
    logger.info(f"result is, {result}")
