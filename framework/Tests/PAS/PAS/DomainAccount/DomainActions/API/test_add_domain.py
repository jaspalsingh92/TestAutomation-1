import pytest
from Shared.API.infrastructure import ResourceManager
from Shared.API.core import CoreManager
from Shared.API.redrock import RedrockController
import logging

logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.bhavna
def test_create_domain(create_domain):
    """
              Steps for this scenario using API:
                1) Add new Domain
                    System configuration received through test_pas_bat_domain.yaml stored in config/tests/PAS/PAS_BAT
           """
    domain_id = create_domain
    assert domain_id, f'failed to create domain with response {domain_id}'


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.bhavna
def test_create_domain_account(core_session, create_domain, domain_config_data):
    """
          Steps for this scenario using API:
            1) Add new Domain
            2) Add new Domain Accounts
                   System configuration received through test_pas_bat_domain.yaml stored in config/tests/PAS/PAS_BAT
       """
    domain_id = create_domain
    conf = domain_config_data
    data = conf['pas_scenario1_new_accounts'][0]
    new_account_id, add_account_success = ResourceManager.add_account(core_session, data['User_name'],
                                                                      data['Password'],
                                                                      domainid=domain_id,
                                                                      description="This domain should be "
                                                                                  "removed by test automation.")

    assert add_account_success, f"Failed to add Domain account: {data['User_name']}"
    logger.info(f"domain account added successfully: {new_account_id}")
    result = ResourceManager.del_account(core_session, new_account_id)
    assert result, f'failed to delete account with response {result}'


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.bhavna
def test_add_a_duplicate_domain(core_session, domain_config_data):
    """
                 Add a duplicate Domain using API

       """
    conf = domain_config_data
    name = conf['pas_bat_scenario1_infrastructure_data'][0]
    domain_name = name['Domain_name2']
    if domain_name in name:
        domain_id = RedrockController.get_domain_id_by_name(core_session,
                                                            domain_name)  # Check whether domain exist or not
        assert domain_id, f'Domain name {domain_name} does not exist'
    logger.info(f"Cannot add duplicate as Domain name {domain_name} already exist.")


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.bhavna
def test_delete_domain(core_session, domain_config_data):
    """

                 Delete Domain

       """
    conf = domain_config_data
    name = conf['pas_bat_scenario1_infrastructure_data'][0]
    domain_name = name['Domain_name2']
    if domain_name in name.values():
        domain_id = RedrockController.get_domain_id_by_name(core_session, domain_name)
        del_domain = ResourceManager.del_domain(core_session, domain_id)
        assert del_domain, f'Failed to delete domain {domain_id}'
        logger.info(f"Domain deleted successfully {domain_id}")
    else:
        logger.info(f"Domain Name {domain_name} does not exist!")


@pytest.mark.api
@pytest.mark.pas_failed
@pytest.mark.bhavna
def test_set_admin_account_ad_service(core_session, domain_config_data, cleanup_domains_with_admin):
    """
                      Steps for this scenario using API:
                        1)Get the domain that needs to be added administrative account of Active Directory
                        2)Set the administrative account of Active Directory
              """
    domains_list1 = cleanup_domains_with_admin
    conf = domain_config_data
    name = conf['pas_bat_scenario1_infrastructure_data'][0]
    domain_name = name['Domain_name2']
    domain_list = [domain_name]
    data = conf['pas_scenario1_new_accounts'][1]
    user = conf['pas_scenario1_administrative_accounts'][0]
    ad_user = user['Administrative_account3']

    # Set Administrative account
    directory_services = CoreManager.get_directory_services(core_session)
    logger.info(f" Successfully get all the Domain Directory Services. {directory_services}")

    # Get the Active Domain Directory Service
    for directory_service in directory_services.json()['Result']['Results']:
        if directory_service['Row']['Name'] == name['Domain_name4']:
            directory_service = directory_service['Row']['directoryServiceUuid']
            break

    result, add_admin_account_success, message = ResourceManager.set_administrative_account(
        core_session,
        domain_list,
        password=data['Password'],
        user=ad_user,
        directoryservices=directory_service)
    assert add_admin_account_success, f'Failed to set administrative account of Active Directory {message}'
    logger.info(f"Administrative account for Active Directory set successfully in the Domain{result}.")
    for domain_names in domain_list:
        domains_list1.append(domain_names)
