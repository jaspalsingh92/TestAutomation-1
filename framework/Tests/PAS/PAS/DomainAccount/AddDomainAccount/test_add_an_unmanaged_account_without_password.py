import pytest
from Shared.API.infrastructure import ResourceManager
from Shared.API.redrock import RedrockController
from Shared.API.server import ServerManager
from Shared.UI.Centrify.selectors import GridRow, GridCell, DisabledButton

import logging

logger = logging.getLogger("test")


@pytest.mark.ui
@pytest.mark.bhavna
@pytest.mark.pas_skip("manage password is not fixed yet CC-71239")
def test_changed_unmanaged_to_managed(domain_config_data, get_admin_user_function, core_session, core_ui):
    """
    TCID: C1331, Add an unmanaged account without password and changed unmanaged to managed
    :return:
    """
    conf = domain_config_data
    name = conf['pas_bat_scenario1_infrastructure_data'][0]
    domain_name = name["Domain_name3"]
    script = "Select * FROM VaultDomain"
    request = RedrockController.redrock_query(core_session, script)
    directory_service_ID = None
    directory_service_Name = None
    directory_service_Admin_ID = None
    for directory_service in request:
        directory_service = directory_service['Row']
        if directory_service['Name'] == name["Domain_name3"]:
            directory_service_ID = directory_service['ID']
            directory_service_Name = directory_service['Name']
            directory_service_Admin_ID = directory_service['Administrator']
            break
    permissions = "Grant,View,Edit,Delete,AddAccount"

    result, add_domain_account_success = ResourceManager.set_domain_account_permissions(core_session, permissions,
                                                                                        "System Administrator",
                                                                                        "sysadmin",
                                                                                        id=directory_service_ID,
                                                                                        ptype="Role",

                                                                                        pvid=directory_service_ID,
                                                                                        rowkey=directory_service_ID)
    assert add_domain_account_success, f'Failed to set add account permission in the domain {result}'
    logger.info(f"add account permission set successfully in the Domain.")
    account, add_domain_success = ResourceManager.get_administrative_account(core_session, "administrator")
    logger.info(f" Successfully get Domain for adding Administrative account.")
    assert add_domain_success, f'Failed to get Domain account {account}'
    name = conf['pas_bat_scenario1_infrastructure_data']
    pvid = account[0]
    domains_name = account[0]
    domain_name_list = []
    for domain_name in name:
        for key, value in domain_name.items():
            domain_name_list.append(value)
    logger.info(f"Set Administrative account for Domain. {domain_name_list}")
    result, add_admin_account_success, message = ResourceManager.set_administrative_account(core_session,
                                                                                            domain_name_list,
                                                                                            pvid=pvid['PVID'],
                                                                                            user=domains_name[
                                                                                                'FullyQualifiedName'])
    assert add_admin_account_success, f'Failed to set administrative account {message}'
    logger.info(f"Administrative account Set successfully in the Domain.{message}")

    result, success = ResourceManager.update_domain_accounts(core_session, directory_service_Name,
                                                             directory_service_Admin_ID, directory_service_ID,
                                                             allowautomaticaccountmaintenance=True)
    assert success, f'failed to update the domain'
    logger.info(f"update account successfully in the Domain{result}")

    data = conf['pas_scenario1_new_accounts'][0]
    account_name = data['Managed_account']
    ui = core_ui
    ui.navigate("Resources", "Domains")
    ui.search(domain_name['Domain_name3'])
    ui.click_row(GridRow(domain_name['Domain_name3']))
    ui.user_menu("Reload Rights")
    ui._waitUntilSettled()
    ui.launch_modal("Add", modal_title="Add Account")
    ui.input("User", account_name)
    ui.uncheck("IsManaged")
    ui.button("Add")
    ui.expect(GridCell("Missing Password"), f'Password is not missing')

    ui.right_click(GridCell(account_name))
    right_click_values = ui.get_list_of_right_click_element_values("Update Password")
    assert "Checkout" not in right_click_values, f'Checkout option is appeared'
    logger.info(f"All right click option:{right_click_values}")
    account_id = None
    results = ServerManager.get_all_accounts(core_session)

    for result in results:
        if result['User'] == account_name:
            account_id = result['ID']

    added_account = ui._searchAndExpect(GridCell(account_name), f'account is not getting added')
    added_account.try_click()
    ui._waitUntilSettled()

    ui.tab("Settings")
    ui.check("IsManaged")

    ui.save()
    ui._waitUntilSettled()

    ui.expect(DisabledButton("Save"), f'Account did not get managed')

    result = RedrockController.get_account_activity(core_session, account_id)
    counter = 0
    while counter < 10:
        result = RedrockController.get_account_activity(core_session, account_id)
        if result[0]['Detail'].__contains__("SYSTEM$"):
            break
    counter += 1
    assert f'SYSTEM$ changed domain account "{account_name}" password for {domain_name["Domain_name3"]}' in result[0]['Detail'], f'could not able to change password'
    logger.info(f"All Activity's are: , {result}")
    result, success = ResourceManager.del_account(core_session, account_id)
    assert success, f'Account did not get delete{result}'
    logger.info(f"Account got deleted successfully, {result}")
