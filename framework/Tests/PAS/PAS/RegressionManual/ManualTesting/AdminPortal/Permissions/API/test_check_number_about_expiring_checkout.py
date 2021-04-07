import pytest
import logging
from Shared.API.infrastructure import ResourceManager
from Shared.API.redrock import RedrockController

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi
def test_check_number_about_expiring_checkout(core_session, pas_windows_setup, users_and_roles):
    """
    Test case:C2116 Check numbers about expiring checkouts.
    :param core_session: Authenticated centrify session.
    :param users_and_roles: Fixture to manage roles and user.
    :param pas_windows_setup: Fixture for creating system and accounts.
    """
    # Adding a system with account.
    system_id, account_id, sys_info, connector_id, user_password = pas_windows_setup()

    # Cloud user session with "Privileged Access Service Administrator"
    cloud_user_session = users_and_roles.get_session_for_user('Privileged Access Service Administrator')
    user_name = cloud_user_session.auth_details['User']
    user_id = cloud_user_session.auth_details['UserId']

    # Assigning system "View" permission
    assign_system_result, assign_system_success = ResourceManager.assign_system_permissions(core_session,
                                                                                            "View",
                                                                                            user_name,
                                                                                            user_id,
                                                                                            'User',
                                                                                            system_id)
    assert assign_system_success, f"Failed to assign system permissions: API response result: {assign_system_result}"
    logger.info(f'Successfully assigned "View" permission to user:{assign_system_result}.')

    # Assigning cloud user "Checkout" permission for account.
    assign_account_result, assign_account_success = ResourceManager.assign_account_permissions(core_session,
                                                                                               "Naked",
                                                                                               user_name,
                                                                                               user_id,
                                                                                               'User',
                                                                                               account_id)
    assert assign_account_success, f"Failed to assign account permissions: API response result: {assign_account_result}"
    logger.info(f'Successfully assigned "Checkout" permission to user:{assign_system_result}.')

    # Setting the system lifetime checkout to 15 min.
    updated_system_result, update_system_success = ResourceManager.update_system(core_session,
                                                                                 system_id,
                                                                                 sys_info[0],
                                                                                 fqdn=sys_info[1],
                                                                                 computerclass=sys_info[2],
                                                                                 defaultcheckouttime=15)
    assert update_system_success, f"Failed to add default checkout time: API response result:{updated_system_result}"
    logger.info(f'Successfully added default checkout time: {updated_system_result}.')

    # Checkout account by cloud user
    checkout_result, checkout_success = ResourceManager.check_out_password(cloud_user_session,
                                                                           1,
                                                                           account_id)
    assert checkout_success, f"Checkout Account successful:{sys_info[4]}:API response result:{checkout_result}"
    logger.info(f'Successfully checkout account:{checkout_result}.')

    # Checking the count of "MY Expiring Checkout" in workspace and expecting to be greater than equal to 1.
    expire_checkout_count = RedrockController.get_expire_checkout_count_from_workspace(cloud_user_session, user_id)
    assert expire_checkout_count[0]['Count'] > 0, f"Failed to find expire checkout count:" \
                                                  f"API response result:{updated_system_result} "
    logger.info(f'Successfully found expire checkout in workspace:{expire_checkout_count}')
