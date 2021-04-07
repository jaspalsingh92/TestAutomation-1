import pytest
from Shared.API.infrastructure import ResourceManager
from Shared.API.redrock import RedrockController
from Shared.API.server import ServerManager
from Shared.UI.Centrify.SubSelectors.grids import GridCell
from Shared.UI.Centrify.selectors import GridRow, CheckedCheckbox, Div, HoverOnToolTip
import logging

logger = logging.getLogger("test")


@pytest.mark.ui
@pytest.mark.bhavna
@pytest.mark.pas_skip("manage password is not fixed yet CC-71239")
def test_add_managed_account_without_password(domain_config_data, core_session, core_ui):
    """
    TCID: C1329: Add a managed account without password
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
    ui.expect(CheckedCheckbox("IsManaged"), f'Checkbox is not checked already')
    expected_tooltip_value = "When enabled, the domain administrative account is used to set and manage a password for this account."
    ui.input("User", account_name)
    tooltip_element = ui._searchAndExpect(HoverOnToolTip("x-img tooltip-icon x-box-item x-img-default"),
                                          f'Could not able to get the tooltip value')
    tooltip_element.try_click()
    actual_tooltip_value = ui._searchAndExpect(Div(expected_tooltip_value),
                                               f'could not able to find the tool tip value')
    actual_tooltip_message = actual_tooltip_value.text
    assert expected_tooltip_value in actual_tooltip_message, f'tooltip text is not matching'
    logger.info(f"ToolTip text: {actual_tooltip_value}")
    ui.button("Add")
    ui.user_menu("Reload Rights")
    ui._waitUntilSettled()
    account_id = None
    results = ServerManager.get_all_accounts(core_session)

    for result in results:
        if result['User'] == account_name:
            account_id = result['ID']
    ui.expect(GridCell("Missing Password"), f'Password is not missing')
    while True:
        result, success = ResourceManager.get_account_information(core_session, account_id)
        if result['VaultAccount']['Row']['Status'] != "Missing Password":
            break
        else:
            continue
    activity = RedrockController.get_account_activity(core_session, account_id)
    detail = []
    for activity_logs in activity:
        detail.append(activity_logs['Detail'])
    assert f'SYSTEM$ changed domain account "{account_name}" password for {domain_name}' in detail[0], \
        f'could not able to change password'
    logger.info(f"ToolTip text: {detail}")
    result, success = ResourceManager.del_account(core_session, account_id)
    assert success, f"Account did not get deleted"
    logger.info(f"deleted account response: {success}")
