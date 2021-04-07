import pytest
import logging
from Shared.API.infrastructure import ResourceManager
from Shared.API.redrock import RedrockController
from Shared.API.users import UserManager
from Utils.guid import guid

logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_add_account_without_configuration_proxy_account(core_session, pas_config):
    """
    TC:C2212 Add account without configuration proxy account.
    :param core_session: Returns a API session.
    :param pas_config: Read yaml data.

    """
    # Adding a system  without proxy.
    payload_data = pas_config['Windows_infrastructure_data']
    system_name = f'{payload_data["system_name"]}{guid()}'
    added_system_id, system_success_status = ResourceManager.add_system(core_session, system_name,
                                                                        payload_data['FQDN'],
                                                                        payload_data['system_class'],
                                                                        payload_data['session_type'],
                                                                        payload_data['description'])
    assert system_success_status, f'Adding system failed returned status {system_success_status}'
    logger.info(f'Successfully created system:{added_system_id}')
    # Validating that no proxy account has added to the system.
    system_details = RedrockController.get_computer_with_ID(core_session, added_system_id)
    assert system_details['ProxyUser'] is None, \
        f'Expect proxy account none in computer info but found one: {system_details} '
    logger.info("Successfully do not found 'Use proxy account' in  on pop-up box.")


@pytest.mark.api
@pytest.mark.pas_broken
@pytest.mark.bhavna
def test_checkout_lifetime_to_blank(core_session, pas_windows_setup):
    """
    TC:C2213 Set the Checkout lifetime to blank.
    :param core_session: Returns a API session.
    :param pas_windows_setup: Returns a fixture

    """
    # Getting the Id of the user.
    user_details = core_session.__dict__
    user_id = user_details['auth_details']['UserId']

    # Adding a system with account.
    system_id, account_id, sys_info, connector_id, user_password = pas_windows_setup()

    # Setting the lifetime checkout to 15 min.
    checkout_lifetime = 15
    updated_account_result, update_account_success = \
        ResourceManager.update_account(core_session,
                                       account_id,
                                       sys_info[4],
                                       host=system_id,
                                       ismanaged=False,
                                       default_checkout_time=checkout_lifetime)

    assert update_account_success, f"Failed to add default checkout time: API response result:{updated_account_result}"
    logger.info(f'Successfully added default checkout time: {updated_account_result}"')

    # Checking the lifetime checkout value.
    account_info_result, account_info_success = ResourceManager.get_account_information(core_session,
                                                                                        account_id)
    account_checkout_lifetime = account_info_result['VaultAccount']['Row']['DefaultCheckoutTime']

    assert account_checkout_lifetime == checkout_lifetime, f'Failed to found default checkout time in account info: ' \
                                                           f'API response ' \
                                                           f'result:{account_info_result} '
    logger.info(f"Successfully Found check out time in account info: {account_checkout_lifetime}")

    # Setting the lifetime checkout to blank.
    updated_account_result, update_account_success = ResourceManager.update_account(core_session,
                                                                                    account_id,
                                                                                    sys_info[4],
                                                                                    host=system_id,
                                                                                    ismanaged=False,
                                                                                    default_checkout_time=None
                                                                                    )
    assert update_account_success, f"Failed to update default checkout time to blank: " \
                                   f"API response result:{updated_account_result} "
    logger.info(f'Successfully updated default checkout time to blank:{updated_account_result}. ')

    # Checking the lifetime checkout value.
    account_info_result, account_info_success = ResourceManager.get_account_information(core_session,
                                                                                        account_id)

    updated_account_checkout_lifetime = account_info_result['VaultAccount']['Row']

    assert 'DefaultCheckoutTime' not in updated_account_checkout_lifetime, "DefaultCheckoutTime is present"

    logger.info(f"'DefaultCheckoutTime' is not present in account info: {updated_account_checkout_lifetime}")

    # Refreshing the page.
    refresh_result = UserManager.refresh_token(core_session, user_id)
    assert refresh_result["success"], f"Failed to reload:API response result:{refresh_result}"

    # Checking the lifetime value after refresh.
    modified_account_info_result, modified_account_info_success = ResourceManager. \
        get_account_information(core_session, account_id)

    modified_account_checkout_lifetime = modified_account_info_result['VaultAccount']['Row']
    assert 'DefaultCheckoutTime' not in modified_account_checkout_lifetime, "DefaultCheckoutTime is present"

    logger.info(f"'DefaultCheckoutTime' is not present in account info: {updated_account_checkout_lifetime}")
