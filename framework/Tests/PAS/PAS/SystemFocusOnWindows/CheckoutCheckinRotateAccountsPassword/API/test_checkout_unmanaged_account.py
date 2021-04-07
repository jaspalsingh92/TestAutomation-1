import pytest
import logging
from Shared.API.infrastructure import ResourceManager

logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.pas
def test_checkout_un_managed_account(core_session, pas_windows_setup, pas_config):
    """
    Test case:C2552 Checkout password for an un managed account
    :param core_session: Returns a API session.
    :param  pas_windows_setup:  Returns a fixture.
    :param pas_config: fixture for fetching up the value from yaml.

    """
    # Creating a system and account.
    system_id, account_id, sys_info, connector_id, user_password = pas_windows_setup()

    # Checking out the password and validating the password.
    password_checkout_result, password_checkout_success = ResourceManager.check_out_password(core_session, 1,
                                                                                             accountid=account_id)
    assert password_checkout_result['Password'] == user_password, \
        f"password checkout Failed. API response result: {password_checkout_result}"
    logger.info(f"password successfully checkout Account password: {password_checkout_result['COID']}")


@pytest.mark.api
@pytest.mark.pas
def test_check_in_password_un_managed_account(core_session, pas_windows_setup, pas_config):
    """
    Test case: C2553 Check in password for the un managed account
    :param core_session:  Returns a API session.
    :param pas_windows_setup: Returns a fixture.
    :param pas_config: fixture for fetching up the value from yaml.

    """

    # Creating a system and account.
    system_id, account_id, sys_info, connector_id, user_password = pas_windows_setup()

    # Checking out the password and validating the password.
    password_checkout_result, password_checkout_success = ResourceManager.check_out_password(core_session, 1,
                                                                                             accountid=account_id)

    assert password_checkout_result['Password'] == user_password, \
        f"password checkout Failed. API response result: {password_checkout_result}"
    logger.info(f"password successfully checkout Account password: {password_checkout_result['COID']}")

    # Checking in password.
    password_check_in_result, password_check_in_success = ResourceManager.check_in_password(
        core_session, coid=password_checkout_result['COID'])
    assert password_check_in_success, f"password check-in Failed. API response result: {password_check_in_result}"
    logger.info(f"password successfully check in for account: {password_check_in_result}")

    # Checking the activity.
    username = core_session.get_user().get_login_name()
    result_activity = ResourceManager.get_system_activity(core_session, system_id)
    assert f'{username} checked in local account "{sys_info[4]}" password for system "{sys_info[0]}"' \
           f'({sys_info[1]})' in result_activity[0]['Detail'], \
        "Fail to check in password:API response result: {password_check_in_result} "
    logger.info(f"account activity list:{result_activity}")
