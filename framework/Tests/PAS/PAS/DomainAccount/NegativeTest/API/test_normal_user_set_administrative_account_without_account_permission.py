from Shared.API.infrastructure import ResourceManager
from Shared.API.redrock import RedrockController
from Shared.API.core import CoreManager
from Shared.API.users import UserManager
import logging
import pytest

logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.bhavna
def test_normal_user_save_admin_account_without_grant_permission(core_session, domain_config_data,
                                                                 get_admin_user_module):
    """   Tc#  C282246
                      Steps for this scenario using API:
                        1)Login Admin Portal as a Normal User
                        2)Call API to clear administrative account
                        3)Set Administrative account from active directory by calling set Administrative account API
              """
    conf = domain_config_data
    limited_sesh, limited_user = get_admin_user_module
    name = conf['pas_bat_scenario1_infrastructure_data'][0]
    domain_name = name["Domain_name2"]
    domain_list = [domain_name]
    data = conf['pas_scenario1_new_accounts'][0]
    user = conf['pas_scenario1_new_accounts'][1]
    admin_user = user['User_name']
    user_data = core_session.get_user()
    username = user_data.get_login_name()
    user_id = user_data.get_id()

    # Get the domain Id from domain section
    script = f'Select ID from VaultDomain where Name = "{domain_name}"'
    request = RedrockController.redrock_query(core_session, script)
    directory_service = request[0]['Row']['ID']

    permissions = "Edit"
    result, add_domain_account_success = ResourceManager.set_domain_account_permissions(core_session, permissions,
                                                                                        limited_user.get_login_name(),
                                                                                        limited_user.get_id(),
                                                                                        id=directory_service,
                                                                                        pvid=directory_service,
                                                                                        rowkey=directory_service)
    assert add_domain_account_success, f'Failed to set add account permission in the domain {result}'
    logger.info(f"add account permission set successfully in the Domain.")

    directory_services = CoreManager.get_directory_services(core_session)
    logger.info(f" Successfully get all the Domain Directory Services.")

    # Get the Active Domain Directory Service
    for child_directory_service in directory_services.json()['Result']['Results']:
        if child_directory_service['Row']['Name'] == name['Domain_name4']:
            child_directory_service = child_directory_service['Row']['directoryServiceUuid']
            break
    active_directory_service_child_domain, add_success = UserManager.directory_query_user(core_session, admin_user,
                                                                                          [child_directory_service])

    # set permission
    permissions = "Grant,View,Edit,Delete,UnlockAccount,AddAccount"
    result, add_domain_account_success = ResourceManager.set_domain_account_permissions(core_session, permissions,
                                                                                        username,
                                                                                        user_id,
                                                                                        id=directory_service,
                                                                                        pvid=directory_service,
                                                                                        rowkey=directory_service)
    assert add_domain_account_success, f'Failed to set permission in the domain {result}'
    logger.info(f" Permission set successfully in the Domain.")

    admin_account = active_directory_service_child_domain['SystemName']
    result, add_admin_account_success, message = ResourceManager.set_administrative_account(
                                                core_session,
                                                domain_list,
                                                password=data['Password'],
                                                user=admin_account,
                                                directoryservices=child_directory_service)
    assert add_admin_account_success, f'Failed to set administrative account of Active Directory: {message}'
    logger.info(f"Administrative account for Active Directory set successfully in the Domain.{result}")

    #  Clear Administrative account by Normal User in Admin Portal
    result, clear_admin_account_success, message = ResourceManager.set_administrative_account(get_admin_user_module[0],
                                                                                              domain_list)
    assert clear_admin_account_success, f'Failed to clear administrative account {message}'
    logger.info(f"Administrative account for Active Directory clear successfully in the Domain.{message}")

    # Normal User set an Administrative account
    result, add_admin_account_success, message = ResourceManager.set_administrative_account(
                                                get_admin_user_module[0],
                                                domain_list,
                                                password=data['Password'],
                                                user=admin_account,
                                                directoryservices=child_directory_service)
    assert add_admin_account_success is False, f'Successfully set administrative account. {result}'
    logger.info(f"Failed to set administrative account, {message}.")
