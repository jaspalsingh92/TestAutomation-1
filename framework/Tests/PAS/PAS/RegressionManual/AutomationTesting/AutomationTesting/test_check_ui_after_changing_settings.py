import pytest
import logging
from Shared.API.infrastructure import ResourceManager

logger = logging.getLogger('test')


@pytest.mark.pasapi
@pytest.mark.pas
@pytest.mark.bhavna
def test_check_ui_after_changing_setting(core_session, users_and_roles, create_resources):
    """
    Test case: C2199  Check UI after changing settings
    :param core_session: Authenticated centrify session
    :param core_admin_ui: Authenticated Centrify browser session
    :param users_and_roles Gets user and role on demand.

    """
    # adding Systems for test execution
    sys_info = create_resources(core_session, 1, 'Windows')
    sys_name = sys_info[0]['Name']
    sys_id = sys_info[0]['ID']

    # Cloud user session with "Privileged Access Service Administrator"
    cloud_user_session = users_and_roles.get_session_for_user('Privileged Access Service Administrator')
    cloud_user = cloud_user_session.auth_details['User']
    user_id = cloud_user_session.auth_details['UserId']

    # Assigning permissions to system excluding "View" Permission
    result, status = ResourceManager.assign_system_permissions(core_session, "View", cloud_user, user_id,
                                                               pvid=sys_id)
    assert status, f'failed to assign rights of system to user {cloud_user}'
    logger.info(f'successfully assigned rights to user {cloud_user} excluding "View" permission')

    # Get list of permission
    get_sys_result, get_sys_success = ResourceManager.get_system_permissions(cloud_user_session, sys_id)
    assert get_sys_success, f"Getting System Permissions Failed for resource {sys_name} with user {cloud_user}"
    user_permission = ""
    for user in get_sys_result:
        if user['Principal'] == cloud_user:
            user_permission = user['Rights']
            break
    assert user_permission == "View", f"Rights Did not match user {cloud_user} it was assigned to"
    logger.info(f"Update permission are saved successfully in the system {user_permission}")
