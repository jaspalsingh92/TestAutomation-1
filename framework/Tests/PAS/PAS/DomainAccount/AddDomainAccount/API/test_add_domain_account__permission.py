import pytest
from Utils.guid import guid
from Shared.API.infrastructure import ResourceManager
from Shared.API.redrock import RedrockController

import logging

logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_add_account_unlock_account_permission(core_session, domain_config_data, get_admin_user_function):
    """
                      Steps for this scenario using API:
                        1)Get the domain that needs to be added managed account with add account permission
                        2)Set add account and unlock permission in the domain
              """
    conf = domain_config_data
    limited_sesh, limited_user = get_admin_user_function
    name = conf['pas_bat_scenario1_infrastructure_data'][0]
    script = "Select * FROM VaultDomain"
    request = RedrockController.redrock_query(core_session, script)
    for directory_service in request:
        if directory_service['Row']['Name'] == name["Domain_name2"]:
            directory_service = directory_service['Row']['ID']
            break
    permissions = "Grant,View,Edit,Delete,AddAccount,UnlockAccount"

    result, add_domain_account_success = ResourceManager.set_domain_account_permissions(core_session, permissions,
                                                                                        limited_user.get_login_name(),
                                                                                        limited_user.get_id(),
                                                                                        id=directory_service,
                                                                                        pvid=directory_service,
                                                                                        rowkey=directory_service)
    assert add_domain_account_success, f'Failed to set add account permission in the domain {result}'
    logger.info(f"add account permission set successfully in the Domain.")


@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_add_unmanaged_account_using_unlock_account_permission(core_session, domain_config_data, get_admin_user_module,
                                                               cleanup_accounts):
    """
                      Steps for this scenario using API:
                        1)Get the domain that needs to be added managed account with add account permission
                        2)Set the domain account permission
                        3)Add unmanaged account in that particular domain
              """
    conf = domain_config_data
    limited_sesh, limited_user = get_admin_user_module
    name = conf['pas_bat_scenario1_infrastructure_data'][0]
    data = conf['pas_scenario1_new_accounts'][0]
    script = "Select * FROM VaultDomain"
    account_name = f'{data["User_name"]}{guid()}'
    account_list = cleanup_accounts[0]
    request = RedrockController.redrock_query(core_session, script)
    for directory_service in request:
        if directory_service['Row']['Name'] == name["Domain_name2"]:
            directory_service = directory_service['Row']['ID']
            break
    permissions = "Grant,View,Edit,Delete,AddAccount,UnlockAccount"
    result, add_domain_account_success = ResourceManager.set_domain_account_permissions(core_session, permissions,
                                                                                        limited_user.get_login_name(),
                                                                                        limited_user.get_id(),
                                                                                        id=directory_service,
                                                                                        pvid=directory_service,
                                                                                        rowkey=directory_service)
    assert add_domain_account_success, f'Failed to set add account permission in the domain {result}'
    logger.info(f"add account permission set successfully in the Domain.")
    request, add_account_success = ResourceManager.add_account(core_session, account_name, data["Password"],
                                                               ismanaged=data["Ismanaged"], domainid=directory_service,
                                                               description=None)
    assert add_account_success, f'Failed to set unmanaged account in the domain {request}'
    logger.info(f"unmanaged account set successfully in the Domain.")
    account_list.append(request)
    result = ResourceManager.del_account(core_session, request)
    assert result, f'failed to delete account with response {result}'
    logger.info(f"unmanaged account deleted successfully in the Domain.")

