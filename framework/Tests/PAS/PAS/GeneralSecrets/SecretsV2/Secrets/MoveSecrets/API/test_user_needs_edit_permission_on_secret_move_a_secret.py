import logging
import pytest
from Shared.API.secret import set_users_effective_permissions, move_secret, create_folder
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_user_needs_edit_permission_on_secret_move_a_secret(core_session,
                                                            users_and_roles,
                                                            added_secrets,
                                                            added_secrets_file,
                                                            pas_general_secrets,
                                                            cleanup_secrets_and_folders):
    """
    test method to set permissions to secret for User A(With Edit/Without Edit) &
    then to check Secret is movable to folder(Should movable/Not able to move)
    :param core_session: Authenticated centrify session
    :param users_and_roles: Fixture to create new user with specified roles
    :param added_secrets: Fixture to add text type secret & yields secret id, secret name
    :param added_secrets_file: Fixture to add file type secret & yields secret id
    :param pas_general_secrets: Fixture to read secrets data from yaml file
    :param cleanup_secrets_and_folders: Fixture to cleanup the secrets & folders created.
    """

    added_text_secret_id, added_text_secret_name = added_secrets
    added_secret_id = added_secrets_file
    folder_params = pas_general_secrets
    prefix = guid()
    folder_list = cleanup_secrets_and_folders[1]
    pas_power_user = users_and_roles.get_user('Privileged Access Service Power User')
    user_name = pas_power_user.get_login_name()
    user_id = pas_power_user.get_id()

    # API to get new session for User A
    pas_power_user_session = users_and_roles.get_session_for_user('Privileged Access Service Power User')
    assert pas_power_user_session.auth_details, 'Failed to Login with PAS Power User'
    logger.info(f'User with PAS Power User Rights login successfully :user_Name: {user_name}'
                f' & Password: {pas_power_user.get_password()} ')

    # Api to create secret folder
    secret_folder_success, secret_folder_parameters, secret_folder_id = create_folder(pas_power_user_session,
                                                                                      prefix + folder_params['name'],
                                                                                      folder_params['description'])
    folder_list.append(secret_folder_id)

    # Api to set permissions to secret (without Edit)
    text_type_secret_result, text_type_secret_success = set_users_effective_permissions(core_session,
                                                                                        user_name,
                                                                                        'View,Grant',
                                                                                        user_id,
                                                                                        added_text_secret_id[0])
    assert text_type_secret_success, f'Failed to set permissions for text type secret:{text_type_secret_result}'
    logger.info(f'Setting permissions for text type secret: {text_type_secret_success}')

    # Api to move secret without Edit permissions
    result_move = move_secret(pas_power_user_session, added_text_secret_id[0], secret_folder_id)
    assert result_move['success'] is False, f'Able to move the secret without edit permissions{result_move["Result"]}'
    logger.info(f'Moving secret without edit permissions:{result_move["Message"]}')

    # Api to set Edit permissions to secret
    text_type_secret_result, text_type_secret_success = set_users_effective_permissions(core_session,
                                                                                        user_name,
                                                                                        'View,Grant,Edit',
                                                                                        user_id,
                                                                                        added_secret_id)
    assert text_type_secret_success, f'Failed to set permissions for file type secret:{text_type_secret_result}'
    logger.info(f'Setting permissions for file type secret: : {text_type_secret_success}')

    # Api to move secret with Edit permissions
    result_move = move_secret(pas_power_user_session, added_secret_id, secret_folder_id)
    assert result_move['success'], f'Not Able to move the secret with edit permissions{result_move["Result"]}'
    logger.info(f'Moving secret with edit permissions:{result_move}')
