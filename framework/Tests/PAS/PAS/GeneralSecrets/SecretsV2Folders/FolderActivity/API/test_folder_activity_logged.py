import pytest
import logging
from Shared.API.secret import give_user_permissions_to_folder, get_folder_activity

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_folder_activity_logged(core_session, create_secret_folder, users_and_roles):
    """
    C3067: test method to Folder activity logged
        1) Create a secret folder, verify you can logged the activity of the folder added
        2) Add folder permissions for user A As 'View', Verify you can logged the activity of the permissions added
        3) Similarly Update permissions several times, verify you can logged all the activity of the permissions updated
    :param core_session: Authenticated Centrify Session
    :param create_secret_folder: Fixture to create secret folder & yields folder details
    :param users_and_roles: Fixture to create a random user with PAS Power rights
    """
    secret_folder_details = create_secret_folder
    folder_id = secret_folder_details['ID']

    # API to get new session for User A
    pas_power_user_session = users_and_roles.get_session_for_user('Privileged Access Service User')
    assert pas_power_user_session.auth_details, 'Failed to Login with PAS User'
    user_name = pas_power_user_session.auth_details['User']
    user_id = pas_power_user_session.auth_details['UserId']
    logger.info(f'User with PAS User Rights login successfully: user_Name:{user_name}')

    # Api to give user permissions to parent folder(View)
    user_permissions_alpha = give_user_permissions_to_folder(core_session,
                                                             user_name,
                                                             user_id,
                                                             folder_id,
                                                             'View')
    assert user_permissions_alpha['success'], \
        f'Not Able to set user permissions to folder, API response result:{user_permissions_alpha["Result"]}'
    logger.info(f'User Permissions to folder: {user_permissions_alpha}')

    # Api to give user permissions to parent folder
    user_permissions_alpha = give_user_permissions_to_folder(core_session,
                                                             user_name,
                                                             user_id,
                                                             folder_id,
                                                             None)
    assert user_permissions_alpha['success'], \
        f'Not Able to set user permissions to folder, API response result:{user_permissions_alpha["Result"]}'
    logger.info(f'User Permissions to folder: {user_permissions_alpha}')

    # Api to give user permissions to parent folder
    user_permissions_alpha = give_user_permissions_to_folder(core_session,
                                                             user_name,
                                                             user_id,
                                                             folder_id,
                                                             'View,Edit')
    assert user_permissions_alpha['success'], \
        f'Not Able to set user permissions to folder, API response result:{user_permissions_alpha["Result"]}'
    logger.info(f'User Permissions to folder: {user_permissions_alpha}')

    # Getting activity of the folder(updating folder permissions multiple times)
    activity_rows = get_folder_activity(core_session, folder_id)
    verify_create_activity = 'added a folder'
    verify_folder_permissions_view_edit = 'to have "View , Edit" permissions'
    verify_folder_permissions_view = 'to have "View" permissions on'
    verify_folder_permissions_none = 'to have "None" permissions on'
    assert verify_create_activity in activity_rows[3]['Detail'], \
        f'Failed to verify the activity, API response result::{activity_rows}'
    assert verify_folder_permissions_view in activity_rows[2]['Detail'], \
        f'Failed to verify the activity, API response result::{activity_rows}'
    assert verify_folder_permissions_none in activity_rows[1]['Detail'], \
        f'Failed to verify the activity, API response result::{activity_rows}'
    assert verify_folder_permissions_view_edit in activity_rows[0]['Detail'], \
        f'Failed to verify the activity:{activity_rows}'
    logger.info(f'Replace activity found for secret, API response result: {activity_rows}')
