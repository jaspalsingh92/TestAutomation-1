import pytest
import logging
from Shared.API.infrastructure import ResourceManager
from Shared.API.redrock import RedrockController

logger = logging.getLogger("test")

lock_tenant = True


@pytest.mark.api
@pytest.mark.pas
def test_system_level_password_checkout_no(core_session, pas_windows_setup, users_and_roles,
                                           update_tenant_multiple_checkouts):
    """
    C1549 : System level password checkout set to 'No'
    :param core_session: Authenticated Centrify Session
    :param pas_windows_setup: Added and return Windows system and Account associated to it.
    :param users_and_roles: Gets user and role on demand.
    """
    system_id, account_id, sys_info, connector_id, user_password = pas_windows_setup()
    user_session = users_and_roles.get_session_for_user("Privileged Access Service Administrator")
    pas_admin = user_session.__dict__['auth_details']
    # Setting 'Allow multiple password checkouts for this system' policy to 'No' on Advanced tab
    result, success = ResourceManager.update_system(core_session, system_id,
                                                    sys_info[0], sys_info[1], sys_info[2], allowmultiplecheckouts=False)
    assert success, f"'Allow multiple password checkouts' policy not set to 'No' for System : {system_id}. API " \
                    f"response result: {result}. "
    logger.info(f"'Allow multiple password checkouts' policy set to 'No' for System : {system_id}")
    # Setting 'Allow multiple password checkouts' policy to Uncheck on Global Security Setting page
    result, success = update_tenant_multiple_checkouts(core_session, False)
    assert success, f"Not able to disable 'Allow multiple password checkouts' policy on " \
                    f"Global Security Setting page. API response result: {result}. "
    logger.info(f"'Allow multiple password checkouts' policy Unchecked on Global Security Setting page")
    # Assigning 'Checkout' permission to user for Account.
    account_result, account_success = ResourceManager.assign_account_permissions(core_session, 'Naked',
                                                                                 pas_admin['User'],
                                                                                 pas_admin['UserId'], 'User',
                                                                                 account_id)
    assert account_success, f"Assign Checkout permission to account : {account_id} failed. " \
                            f"API response result: {account_result}."
    logger.info(f"'Checkout' permission given to user: {pas_admin['User']} for Account:{account_id}.")

    # Checkout account while logged in as Cloud Admin
    admin_checkout_result, admin_checkout_success = ResourceManager.check_out_password(core_session, 1, account_id)
    assert admin_checkout_result['Password'] == user_password, f"Not able to checkout Account : {account_id}. API " \
                                                               f"response result: {admin_checkout_result}. "
    logger.info(f"Account Checkout successful for Account :{account_id}.")

    # Checkout account while logged in as Privileged Access Service Administrator
    user_checkout_result, user_checkout_success = ResourceManager.check_out_password(user_session, 1, account_id)
    assert not user_checkout_success, f"Checkout Account successful : {account_id} : " \
                                      f"API response result: {user_checkout_result}"
    logger.info(f"Not able to checkout Account  : {account_id}")
    activity = RedrockController.get_account_activity(user_session, account_id)[0]['Detail']
    assert 'Multiple checkouts not allowed' in activity, f"Checkout Failed activity not found for " \
                                                         f"account : {account_id}. API response result: {activity} "
    logger.info(f"Checkout Failed activity found in Activity for account : {account_id}")
