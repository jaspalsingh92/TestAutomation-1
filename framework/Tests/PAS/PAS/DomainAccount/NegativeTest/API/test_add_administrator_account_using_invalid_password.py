from Shared.API.infrastructure import ResourceManager
from Shared.API.core import CoreManager
from Utils.guid import guid
import logging
import pytest

logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.bhavna
def test_set_administrative_account_using_invalid_password(core_session, domain_config_data):
    """
        TC#: C282306
          Steps for this scenario using API:
            1) Set Administrative Account from Active Directory with invalid credentials(Invalid Password)
                   System configuration received through test_pas_bat_domain.yaml stored in config/tests/PAS/PAS_BAT
       """
    conf = domain_config_data
    name = conf['pas_bat_scenario1_infrastructure_data'][0]
    domain_name = [name['Domain_name2']]
    data = conf['pas_scenario1_new_accounts'][0]
    user_details = conf['pas_scenario1_administrative_accounts'][0]
    admin_account = user_details['Administrative_account3']
    directory_services = CoreManager.get_directory_services(core_session)
    logger.info(f" Successfully get all the Domain Directory Services.")

    # Get the Active Domain Directory Service
    for directory_service in directory_services.json()['Result']['Results']:
        if directory_service['Row']['Name'] == name['Domain_name4']:
            directory_service = directory_service['Row']['directoryServiceUuid']
            break

    result, add_admin_account_success, message = ResourceManager.set_administrative_account(
                                                core_session,
                                                domain_name,
                                                password=data['Password'] + guid(),
                                                user=admin_account,
                                                directoryservices=directory_service)

    assert add_admin_account_success is False, f"Failed to add Administrative account in the domain :{result}"
    logger.info(f"Failed to set Administrative Account: {message}")
