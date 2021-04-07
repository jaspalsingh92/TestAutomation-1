import logging
import pytest
from Shared.API.secret import del_secret, give_user_permissions_to_folder, create_text_secret_within_folder, \
    set_member_permissions_to_folder
from Utils.guid import guid
logger = logging.getLogger('test')


@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_needs_retrieve_permission_to_secret(core_session,
                                             users_and_roles,
                                             create_secret_inside_folder,
                                             pas_general_secrets):
    """
            C283961: User needs Retrieve Secret permission to retrieve and delete secret
    :param core_session: Authenticated Centrify Session.
    :param users_and_roles: Fixture to create New user with PAS Power Rights
    :param create_secret_inside_folder: Fixture to create secret inside foledr & yield secrets & folders details.
    :param pas_general_secrets: Fixture to read secret data from yaml file.
    """
    folder_id_list, folder_name, secret_id = create_secret_inside_folder
    params = pas_general_secrets
    suffix = guid()

    # Getting new session for User A
    pas_power_user_session = users_and_roles.get_session_for_user('Privileged Access Service Power User')
    assert pas_power_user_session.auth_details, 'Failed to Login with PAS Power User'
    user_name = pas_power_user_session.auth_details['User']
    user_id = pas_power_user_session.auth_details['UserId']
    logger.info(f'User with PAS Power User Rights login successfully: user_Name:{user_name}')

    # Create text type secret within folder
    added_text_secret_success, added_text_secret_result = create_text_secret_within_folder(
        core_session,
        params['secret_name'] + suffix,
        params['secret_text'],
        params['secret_description'],
        folder_id_list[0])
    assert added_text_secret_success, f'Failed to create secret {added_text_secret_result}'
    logger.info(f'Secret Created successfully: {added_text_secret_success}')

    # Setting user permissions to folder
    user_permissions_result = give_user_permissions_to_folder(core_session,
                                                              user_name,
                                                              user_id,
                                                              folder_id_list[0],
                                                              'View')
    assert user_permissions_result, f'Failed to set user permissions to folder:{user_permissions_result}'
    logger.info(f'User Permissions to folder: {user_permissions_result}')

    # Setting member permissions(Delete, Retrieve) to folder
    member_perm_result, member_perm_success = set_member_permissions_to_folder(core_session,
                                                                               user_name,
                                                                               'View,Grant,Delete,Retrieve',
                                                                               user_id,
                                                                               folder_id_list[0])
    assert member_perm_success, f'Failed to set member permissions to Folder:{member_perm_result["Result"]}'
    logger.info(f'Member permissions to folder:{member_perm_result}')

    #  Deleting child secret should work
    del_success, del_result = del_secret(pas_power_user_session, added_text_secret_result)
    assert del_success, f'Failed to delete child secret: {del_result}'
    logger.info(f'Successfully deleted child secret: {del_success}{del_result}')

    # Setting member permissions(Delete) to folder
    member_perm_result, member_perm_success = set_member_permissions_to_folder(core_session,
                                                                               user_name,
                                                                               'View,Grant,Delete',
                                                                               user_id,
                                                                               folder_id_list[0])
    assert member_perm_success, f'Failed to set member permissions to Folder:{member_perm_result["Result"]}'
    logger.info(f'Member permissions to folder:{member_perm_result}')

    # Deleting child secret should work(without Retrieve)
    del_success, del_result = del_secret(pas_power_user_session, secret_id[0])
    assert del_success, f'Failed to delete child secret: {del_result}'
    logger.info(f'Successfully deleted child secret: {del_result}')
    secret_id.remove(secret_id[0])
