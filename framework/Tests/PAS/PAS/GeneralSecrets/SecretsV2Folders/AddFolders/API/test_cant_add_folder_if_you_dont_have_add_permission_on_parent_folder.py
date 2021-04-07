import logging
import pytest
from Shared.API.secret import create_folder, set_member_permissions_to_folder, give_user_permissions_to_folder
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_cant_add_folder_if_you_dont_have_add_permission_on_parent_folder(core_session,
                                                                          create_secret_folder,
                                                                          pas_general_secrets,
                                                                          users_and_roles):
    """
        test method to not able to add a child Folder inside a Parent Folder
        when ADD permissions are not enabled for the Parent Folder
    :param core_session: Authenticated Centrify Session
    :param create_secret_folder: Fixture to create a folder & yields folder related details
    :param pas_general_secrets:  Fixture to read secret data from yaml file
    :param users_and_roles: Fixture to create a random user with PAS Power Rights

    """
    secret_folder_details = create_secret_folder
    folder_id = secret_folder_details['ID']
    folder_params = pas_general_secrets

    # API to get new session for User A
    pas_power_user_session = users_and_roles.get_session_for_user('Privileged Access Service Power User')
    assert pas_power_user_session.auth_details is not None, 'Failed to Login with PAS Power User'
    user_name = pas_power_user_session.auth_details['User']
    user_id = pas_power_user_session.auth_details['UserId']
    logger.info(f'User with PAS Power User Rights login successfully: user_Name: {user_name}')

    # Api to give user permissions to folder
    user_permissions_result = give_user_permissions_to_folder(core_session, user_name, user_id, folder_id,
                                                              'View')
    assert user_permissions_result, f'Not Able to set user permissions to folder{user_permissions_result}'
    logger.info(f'User Permissions to folder: {user_permissions_result}')

    # Api to give member permissions to folder
    member_perm_result, member_perm_success = set_member_permissions_to_folder(core_session,
                                                                               user_name,
                                                                               'View,Grant',
                                                                               user_id,
                                                                               folder_id)
    assert member_perm_success, f'Not Able to set member permissions to Folder{member_perm_result["Result"]}'
    logger.info(f'Member permissions to folder:{member_perm_result}')

    folder_prefix = guid()
    # Creating ChildFolder for PAS Power User
    folder_success, folder_parameters, child_folder_id = create_folder(pas_power_user_session,
                                                                       folder_prefix + folder_params['name'],
                                                                       folder_params['description'],
                                                                       parent=folder_id)
    assert folder_success is False, \
        f'Added subfolder without ADD permissions for the folder:{child_folder_id}'
    logger.info(f'Add Folder without ADD permissions: {folder_success}{folder_parameters}')
