import logging
import pytest
from Shared.API.secret import create_folder, get_users_effective_folder_permissions
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.bhavna
def test_sysadmin_by_default_has_grant_view_edit_and_delete_on_everyone_secret_or_folder(core_session,
                                                                                         pas_general_secrets,
                                                                                         cleanup_secrets_and_folders,
                                                                                         users_and_roles):
    """
        C283794: Sysadmin by default has Grant, View, Edit and Delete on everyone's secret/folder

    :param core_session: Authenticated Centrify Session
    :param pas_general_secrets:  Fixture to read secret data from yaml file
    :param cleanup_secrets_and_folders: Fixture to cleanup the secrets & folder created
    :param users_and_roles: Fixture to create a random user with PAS Power Rights

    """
    folder_params = pas_general_secrets
    folders_list = cleanup_secrets_and_folders[1]

    # API to get new session for User A
    pas_power_user_session = users_and_roles.get_session_for_user('Privileged Access Service Power User')
    assert pas_power_user_session.auth_details, 'Failed to Login with PAS Power User'

    folder_prefix = guid()
    # Creating Folder for Non-Admin User
    folder_success, folder_parameters, folder_id = create_folder(pas_power_user_session,
                                                                 folder_prefix + folder_params['name'],
                                                                 folder_params['description'])
    folders_list.append(folder_id)
    assert folder_success, f'Failed to Add Folder with Non-Admin user:{folder_id}'
    logger.info(f'Adding Folder with Non-Admin user : {folder_success}{folder_parameters}')

    permissions = get_users_effective_folder_permissions(pas_power_user_session, folder_id)
    verify_permissions = ['View', 'Edit', 'Delete', 'Grant', 'Add']
    assert permissions == verify_permissions, f'Failed to verify sys_admin permissions:{permissions}'
    logger.info(f'Sys_admin Permissions for the Folder added:{permissions}')
