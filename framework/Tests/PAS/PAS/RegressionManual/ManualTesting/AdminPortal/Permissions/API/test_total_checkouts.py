import pytest
import logging
from Shared.API.infrastructure import ResourceManager

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi
def test_check_number_of_total_checkout(core_session, pas_setup, users_and_roles):
    """
    Test case: C286364
    :param core_session: Authenticated Centrify session
    :param users_and_roles: Fixture to manage roles and user
    """
    system_id, account_id, sys_info = pas_setup

    # Cloud user session with "Privileged Access Service Administrator"
    cloud_user_session = users_and_roles.get_session_for_user('Privileged Access Service Administrator')
    user_name = cloud_user_session.auth_details['User']
    user_id = cloud_user_session.auth_details['UserId']

    # Assigning system view permission
    result, status = ResourceManager.assign_system_permissions(core_session, "View", user_name, user_id,
                                                               pvid=system_id)
    assert status, f"Failed to assign system permissions return result is {result}"
    logger.info(f'View rights assigned to user {user_name} for system {sys_info[0]}')

    # Assigning cloud user view and checkout permission for account
    account_rights = "View,Naked"
    acc_result, acc_status = ResourceManager.assign_account_permissions(core_session, account_rights,
                                                                        user_name, user_id,
                                                                        pvid=account_id)
    assert acc_status, f"failed to assign account permission, returned result is {acc_result}"
    logger.info(f'successfully assigned {account_rights} permission for account {sys_info[4]} of '
                f'{sys_info[0]} to user {user_name}')

    # Checkout password using cloud user
    result, success = ResourceManager.check_out_password(cloud_user_session, 1, account_id)
    assert success, f"cloud user: {user_name} failed to checkout account {sys_info[4]}."
    logger.info(f"Cloud user: {user_name} successfully checked out account {sys_info[4]} of system {sys_info[0]}.")

    # retrieving my total checkout value from workspace
    checkout_count = ResourceManager.get_my_total_checkout(cloud_user_session, user_id)
    assert checkout_count > 0, f'failed to retrieve total checkout value as it never updated. returned count is ' \
                               f'{checkout_count}'
    logger.info(f'My total Checkout field is updated by {checkout_count}')
