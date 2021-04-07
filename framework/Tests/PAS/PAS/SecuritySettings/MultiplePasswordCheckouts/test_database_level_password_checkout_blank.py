import pytest
import logging
from Shared.API.infrastructure import ResourceManager

logger = logging.getLogger("test")
lock_tenant = True


@pytest.mark.pas
@pytest.mark.api
@pytest.mark.workflow
def test_database_level_password_checkout_blank(core_session, create_databases_with_accounts,
                                                users_and_roles, update_tenant_multiple_checkouts):
    """
    C1552 : Database Level password checkout set to 'default'.
    :param core_session: Authenticated Centrify Session.
    :param create_databases_with_accounts: Added and return Database and Account associated to it.
    :param users_and_roles: Gets user and role on demand.
    """
    database = create_databases_with_accounts(core_session, 1, 1)[0]
    user_session = users_and_roles.get_session_for_user("Privileged Access Service Administrator")
    pas_admin = user_session.__dict__['auth_details']

    # Setting 'Allow multiple password checkouts' policy to enable on Global Security Setting page
    result, success = update_tenant_multiple_checkouts(core_session, True)
    assert success, f"Not able to enable 'Allow multiple password checkouts' policy on Global Security Setting page. " \
                    f"API response result: {result}."
    logger.info(f"'Allow multiple password checkouts' policy Enabled on Global Security Setting page")
    # Assigning 'Checkout' permission to user for account.
    account_result, account_success = ResourceManager.assign_account_permissions(core_session, 'Naked',
                                                                                 pas_admin['User'],
                                                                                 pas_admin['UserId'], 'User',
                                                                                 database['Accounts'][0]['ID'])
    assert account_success, f"Assign Checkout permission to account : {database['Accounts'][0]['ID']} " \
                            f"failed. API response result: {account_result}. "
    logger.info(f"'Checkout' permission given to user: {pas_admin['User']} for "
                f"Account:{database['Accounts'][0]['ID']}.")

    # Checkout account while logged in as Cloud Admin
    admin_checkout_result, admin_checkout_success = ResourceManager.check_out_password(core_session, 1,
                                                                                       database['Accounts'][0]['ID'])
    assert admin_checkout_success, f"Not able to checkout Account : {database['Accounts'][0]['ID']}. API response " \
                                   f"result: {admin_checkout_result}. "
    logger.info(f"Account Checkout successful for Account :{database['Accounts'][0]['ID']}.")

    # Checkout account while logged in as Privileged Access Service Administrator
    user_checkout_result, user_checkout_success = ResourceManager.check_out_password(user_session, 1,
                                                                                     database['Accounts'][0]['ID'])
    assert user_checkout_success, f"Not able to checkout Account : {database['Accounts'][0]['ID']}. API response " \
                                  f"result: {user_checkout_result}. "
    logger.info(f"Account Checkout successful for Account :{database['Accounts'][0]['ID']}.")
