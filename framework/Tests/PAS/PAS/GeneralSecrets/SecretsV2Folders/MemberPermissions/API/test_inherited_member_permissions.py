import pytest
import logging
from Shared.API.sets import SetsManager
from Utils.guid import guid
from Shared.API.secret import give_user_permissions_to_folder, create_text_secret_within_folder, \
    set_member_permissions_to_folder, get_rows_acl

logger = logging.getLogger('test')


@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_inherited_member_permissions(core_session,
                                      create_secret_folder,
                                      pas_general_secrets,
                                      users_and_roles,
                                      cleanup_secrets_and_folders):

    """
          C284058: Inherited member permissions
    :param core_session: Authenticated Centrify session
    :param create_secret_folder: Fixture to create secret folder & yields folder details
    :param pas_general_secrets: Fixture to read secret data from yaml file
    :param users_and_roles:  Fixture to create New user with PAS Power User & PAS User Rights
    :param cleanup_secrets_and_folders: Fixture to clean-up the secrets & folders created.
    """
    secrets_list = cleanup_secrets_and_folders[0]
    secret_folder_details = create_secret_folder
    folder_id = secret_folder_details['ID']
    secret_params = pas_general_secrets
    suffix = guid()

    # Getting new session for User A
    pas_power_user_session = users_and_roles.get_session_for_user('Privileged Access Service Power User')
    assert pas_power_user_session.auth_details, 'Failed to Login with PAS Power User'
    user_name = pas_power_user_session.auth_details['User']
    user_id = pas_power_user_session.auth_details['UserId']
    logger.info(f'User with PAS Power User Rights login successfully: user_Name:{user_name}')

    # Setting user A permissions to folder
    user_permissions_result = give_user_permissions_to_folder(core_session,
                                                              user_name,
                                                              user_id,
                                                              folder_id,
                                                              'View, Add')
    assert user_permissions_result, f'Failed to set user permissions to folder:{user_permissions_result}'
    logger.info(f'User Permissions to folder: {user_permissions_result}')

    # Setting member permissions to folder
    member_perm_result, member_perm_success = set_member_permissions_to_folder(core_session,
                                                                               user_name,
                                                                               'View,Grant,Edit',
                                                                               user_id,
                                                                               folder_id)
    assert member_perm_success, f'Failed to set member permissions to Folder:{member_perm_result["Result"]}'
    logger.info(f'Member permissions to folder:{member_perm_result}')

    # Getting new session for User B
    pas_user_session = users_and_roles.get_session_for_user('Privileged Access Service User')
    assert pas_user_session.auth_details, 'Failed to Login with PAS Power User'
    user_name_pas = pas_user_session.auth_details['User']
    user_id_pas = pas_user_session.auth_details['UserId']
    logger.info(f'User with PAS User Rights login successfully: user_Name:{user_name}')

    # Setting user B permissions to folder
    user_permissions_result = give_user_permissions_to_folder(core_session,
                                                              user_name_pas,
                                                              user_id_pas,
                                                              folder_id,
                                                              'View, Add')
    assert user_permissions_result, f'Failed to set user permissions to folder:{user_permissions_result}'
    logger.info(f'User Permissions to folder: {user_permissions_result}')

    # Setting member permissions to folder
    member_perm_result, member_perm_success = set_member_permissions_to_folder(core_session,
                                                                               user_name_pas,
                                                                               'View,Grant,Edit',
                                                                               user_id_pas,
                                                                               folder_id)
    assert member_perm_success, f'Failed to set member permissions to Folder:{member_perm_result["Result"]}'
    logger.info(f'Member permissions to folder:{member_perm_result}')

    # Creating set for UserA
    success, set_id = SetsManager.create_manual_collection(pas_power_user_session,
                                                           secret_params['set_name'] + suffix,
                                                           'DataVault')
    logger.info(f'creating manual set:{success} with set id as: {set_id}')
    assert success, f'Failed to create manual set for User A: {set_id}'

    # Create text type secret within folder for User A
    added_text_secret_success, added_text_secret_result = create_text_secret_within_folder(
        pas_power_user_session,
        secret_params['secret_name'] + suffix,
        secret_params['secret_text'],
        secret_params['secret_description'],
        folder_id, set_id)
    assert added_text_secret_success, f'Failed to create secret for User A:{added_text_secret_result}'
    logger.info(f'Secret Created successfully: {added_text_secret_success}')

    # Verifying inherited permissions for User B
    get_permission_result = get_rows_acl(pas_power_user_session, added_text_secret_result)
    assert get_permission_result, f'Failed to inherit permissions for User B:{get_permission_result}'
    logger.info(f' Successfully inherited permissions for User B: {get_permission_result}')
    secrets_list.append(added_text_secret_result)
    rows_returned = get_permission_result['Result']
    for rows in rows_returned:
        if rows['PrincipalName'] == user_name_pas:
            assert rows['Inherited'], "Failed to verify the inherited permissions"
