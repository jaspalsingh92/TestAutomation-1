import pytest
import logging
from Shared.API.secret import create_folder, get_folder, get_secrets_and_folders_in_folders,\
    give_user_permissions_to_folder

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_add_single_folder_then_append_multilevel_folder_to_it(core_session,
                                                               pas_general_secrets,
                                                               cleanup_secrets_and_folders,
                                                               users_and_roles,
                                                               create_secret_folder):
    """
        C3051: test method to Add single folder then append multilevel folder to it
        1) create multilevel folder dogs/labradors/yellow inside a parent folder
       2) Login as Admin, set folder permissions "View,Delete" for parent folder
       3) Login as pas user
       4) verify pas user can view all folders i.e. "animals/dogs/labradors/yellow"

    :param core_session: Authenticated Centrify session
    :param pas_general_secrets: Fixture to read secrets related data from yaml file
    :param cleanup_secrets_and_folders: Fixture to cleanup the secrets & folders created
    :param users_and_roles: Fixture to create random user with PAS User Rights
    :param create_secret_folder: Fixture to create folder & yields folder details

    """
    params = pas_general_secrets
    folders_list = cleanup_secrets_and_folders[1]
    folder_parameters = create_secret_folder
    parent_folder_id = folder_parameters['ID']

    # creating multilevel folder dogs/labradors/yellow
    child_folder_success, child_folder_parameters, child_folder_id = create_folder(
        core_session,
        params['folder_multiple_level'],
        params['description'],
        parent=parent_folder_id)
    assert child_folder_success, f'Failed to create multilevel folder, API response result: {child_folder_id}'
    logger.info(f'Multilevel Folder created successfully, details are: {child_folder_parameters}')

    # Getting details of Folder Labradors
    labradors_folder = get_folder(core_session, child_folder_id)
    logger.info(f'labradors folder details:{labradors_folder}')
    labradors_folder_id = labradors_folder['Result']['Results'][0]['Row']['Parent']

    # Getting id of Folder Dogs
    dogs_folder = get_folder(core_session, labradors_folder_id)
    logger.info(f'Dogs folder details:{dogs_folder}')
    dogs_folder_id = dogs_folder['Result']['Results'][0]['Row']['Parent']

    # API to get new session for User A
    pas_power_user_session = users_and_roles.get_session_for_user('Privileged Access Service User')
    assert pas_power_user_session.auth_details, 'Failed to Login with PAS User'
    user_name = pas_power_user_session.auth_details['User']
    user_id = pas_power_user_session.auth_details['UserId']
    logger.info(f'User with PAS User Rights login successfully: user_Name:{user_name}')

    # Api to give user permissions to parent folder
    user_permissions_alpha = give_user_permissions_to_folder(core_session,
                                                             user_name,
                                                             user_id,
                                                             parent_folder_id,
                                                             'View, Delete')
    assert user_permissions_alpha['success'], \
        f'Not Able to set user permissions to folder, API response result:{user_permissions_alpha["Result"]}'
    logger.info(f'User Permissions to folder: {user_permissions_alpha}')

    # Getting id of Folder Dog
    dog_folder = get_secrets_and_folders_in_folders(pas_power_user_session, parent_folder_id)
    logger.info(f'Details of Dog Folder Retrieved with pas user:{dog_folder}')
    dog_id = dog_folder["Result"]["Results"][0]["Entities"][0]["Key"]
    assert dog_id == dogs_folder_id, f' Failed to view dog folder with pas user, API response result:' \
                                     f'{dog_folder["success"]} & {dog_folder["Result"]}'

    # Getting id of parent folder
    labradors_folder = get_secrets_and_folders_in_folders(pas_power_user_session, dog_id)
    logger.info(f'Details of labradors Folder Retrieved with pas user:{labradors_folder}')
    labradors_id = labradors_folder["Result"]["Results"][0]["Entities"][0]["Key"]
    assert labradors_id == labradors_folder_id, f' Failed to view labradors folder with pas user, API response result:' \
                                                f'{labradors_folder["success"]} & {labradors_folder["Result"]}'

    # Getting id of parent folder
    yellow_folder = get_secrets_and_folders_in_folders(pas_power_user_session, labradors_id)
    logger.info(f'Details of yellow Folder Retrieved with pas user:{yellow_folder}')
    yellow_id = yellow_folder["Result"]["Results"][0]["Entities"][0]["Key"]
    assert \
        yellow_id == child_folder_id, f' Failed to view yellow folder with pas user, API response result:' \
                                      f'{yellow_folder["success"]} & {yellow_folder["Result"]}'

    # cleanup of folders accordingly
    folders_list.insert(0, child_folder_id)
    folders_list.insert(1, labradors_folder_id)
    folders_list.insert(2, dogs_folder_id)
