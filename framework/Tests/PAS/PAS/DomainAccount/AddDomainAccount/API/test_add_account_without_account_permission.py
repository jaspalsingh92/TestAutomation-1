from Shared.API.infrastructure import ResourceManager
import logging
import pytest

logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_add_account_without_add_account_permission(core_session, domain_config_data, create_domain, cleanup_accounts):
    """
      TC:- C1325  Add account without Add Account permission
          Steps for this scenario using API:
            1) Add Domain Accounts without Add Account Permission
                   System configuration received through test_pas_bat_domain.yaml stored in config/tests/PAS/PAS_BAT
       """
    user_details = core_session.__dict__
    domain_id = create_domain
    account_list = cleanup_accounts[0]
    assert domain_id, f'failed to create domain with response {domain_id}'
    conf = domain_config_data
    data = conf['pas_scenario1_new_accounts'][0]
    permissions = "Grant,View,Edit,Delete"
    result, add_domain_account_success = ResourceManager.set_domain_account_permissions(core_session, permissions,
                                                                                        user_details["auth_details"]["User"],
                                                                                        user_details["auth_details"]["UserId"],
                                                                                        pvid=domain_id)
    assert add_domain_account_success, f'Failed to set add account permission in the domain {result}'
    logger.info(f"add account permission set successfully in the Domain.")
    new_account_id, add_account_success = ResourceManager.add_account(core_session, data['User_name'],
                                                                      data['Password'],
                                                                      domainid=domain_id)

    assert add_account_success is False, (f"Successfully added domain account: {data['User_name']}")
    account_list.append(new_account_id)
    logger.info(f"Failed to add Account in the Domain, Add Account permission for this domain is required: {new_account_id}")
