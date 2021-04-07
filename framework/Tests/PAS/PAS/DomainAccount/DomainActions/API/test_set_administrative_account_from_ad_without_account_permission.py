from Shared.API.infrastructure import ResourceManager
from Shared.API.core import CoreManager
from Shared.API.redrock import RedrockController
import logging
import pytest

logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.bhavna
def test_set_admin_account_from_ad_without_add_account_permission(core_session, domain_config_data):
    """
        Test case: C282307
        Steps for this scenario using API:
            1) Set Administrative Account from Active Directory without Add Account Permission
                   System configuration received through test_pas_bat_domain.yaml stored in config/tests/PAS/PAS_BAT
               :param core_session: Returns API session
               :param domain_config_data: Fixtures for getting domain data from yaml.

       """
    conf = domain_config_data
    name = conf['pas_bat_scenario1_infrastructure_data'][0]
    domain_name = name['Domain_name2']
    domain_list = [domain_name]
    data = conf['pas_scenario1_new_accounts'][0]
    user = conf['pas_scenario1_administrative_accounts'][0]
    ad_user = user['Administrative_account1']
    user_data = core_session.get_user()
    username = user_data.get_login_name()
    user_id = user_data.get_id()

    # Get the domain Id from domain section
    script = f'Select ID from VaultDomain where Name = "{domain_name}"'
    request = RedrockController.redrock_query(core_session, script)
    child_directory_service = request[0]['Row']['ID']

    # Get the Directory Services
    directory_services = CoreManager.get_directory_services(core_session)
    logger.info(f" Successfully get all the Domain Directory Services.")

    # Get the Active Domain Directory Service
    for directory_service in directory_services.json()['Result']['Results']:
        if directory_service['Row']['Name'] == name['Domain_name4']:
            directory_service = directory_service['Row']['directoryServiceUuid']
            break

    # set permission
    permissions = "Grant,View,Edit,Delete,UnlockAccount"
    result, add_domain_account_success = ResourceManager.set_domain_account_permissions(core_session, permissions,
                                                                                        username,
                                                                                        user_id,
                                                                                        id=child_directory_service,
                                                                                        pvid=child_directory_service,
                                                                                        rowkey=child_directory_service)
    assert add_domain_account_success, f'Failed to set permission in the domain {result}'
    logger.info(f" Permission set successfully in the Domain.")

    result, add_admin_account_success, message = ResourceManager.set_administrative_account(
                                                    core_session, domain_list,
                                                    password=data['Password'],
                                                    user=ad_user,
                                                    directoryservices=directory_service)

    assert add_admin_account_success is False, (
        f"Successfully set Administrative account from Active Directory: {message}")
    logger.info(f"Failed to set Administrative Account, {message}")
