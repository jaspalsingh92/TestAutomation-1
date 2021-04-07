import pytest
import logging
from Shared.API.infrastructure import ResourceManager

logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi
def test_delete_system_before_delete_its_account(core_session, pas_windows_setup, users_and_roles):
    """
    TC:C2219 Delete a system before deleting its accounts.
    :param core_session: Returns a API session.
    :param pas_windows_setup: Returns a fixture.
    :param users_and_roles: Fixture to manage roles and user.

    """
    # Creating a system and account.
    system_id, account_id, sys_info, connector_id, user_password = pas_windows_setup()

    # Cloud user session with "Privileged Access Service User".
    cloud_user_session = users_and_roles.get_session_for_user('Privileged Access Service User')
    user_name = cloud_user_session.auth_details['User']
    user_id = cloud_user_session.auth_details['UserId']

    # Assigning system "View,Edit,Delete" permission.
    assign_system_result, assign_system_success = ResourceManager.assign_system_permissions(core_session,
                                                                                            "View,Edit,Delete",
                                                                                            user_name,
                                                                                            user_id,
                                                                                            'User',
                                                                                            system_id)
    assert assign_system_success, f"Failed to assign system permissions: API response result: {assign_system_result}"
    logger.info(f'Successfully assigned "View,Edit,Delete" permission to user:{assign_system_result}.')

    # Trying to delete system whose account is not deleted.
    del_system_result, del_system_success = ResourceManager.del_system(cloud_user_session, system_id)
    assert del_system_success is False, f'System is deleted:API response result:{del_system_result}'
    logger.info(f'Failed to delete system whose account is not deleted:{del_system_result}')

    # Checking the system Activity.
    sys_activity = ResourceManager.get_system_activity(cloud_user_session, system_id)
    assert f'{user_name} failed to delete system "{sys_info[0]}"({sys_info[1]}). ' \
           f'Reason: System has active accounts' in sys_activity[0]['Detail'], \
        f'"Failed to  get the expected activity:API response result:{sys_activity}'

    logger.info(f'Successfully Found the expected activity:{sys_activity}')
