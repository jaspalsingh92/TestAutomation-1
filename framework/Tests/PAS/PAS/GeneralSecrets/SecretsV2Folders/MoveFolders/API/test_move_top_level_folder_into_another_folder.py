import pytest
import logging
from Shared.API.secret import move_folder, create_folder
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_move_top_level_folder_into_another_folder(core_session,
                                                   create_secret_inside_folder,
                                                   create_folder_inside_folder,
                                                   pas_general_secrets,
                                                   cleanup_secrets_and_folders):
    """
        C3035: test method to Move top level folder into another folder
             1) Move top level folder into another top level folder & Verify move is successful
             2) Move top level folder into a sub folder & Verify move is successful
    :param core_session: Authenticated Centrify Session
    :param create_secret_inside_folder: Fixture to create secret inside Folder & yields folder & secret related details
    :param create_folder_inside_folder: Fixture to create nested Folder & yields folder & sub folder related details
    :param pas_general_secrets: Fixture to read secrets related data from yaml file
    :param cleanup_secrets_and_folders: Fixture to cleanup the secrets & folders created.

    """
    folder_id_list, folder_name, secret_list = create_secret_inside_folder
    parent_folder_info, nested_folder_info, nested_folder_id = create_folder_inside_folder
    folder_params = pas_general_secrets
    folder_prefix = guid()
    folder_list = cleanup_secrets_and_folders[1]

    # Creating folder
    secret_folder_success, secret_folder_parameters, secret_folder_id = create_folder(
        core_session,
        folder_params['name'] + folder_prefix,
        folder_params['description'])
    assert secret_folder_success, f'Failed to create a folder, API response result:{secret_folder_id}'
    logger.info(f' Folder created successfully: {secret_folder_success} & details are {secret_folder_parameters}')
    folder_list.insert(2, secret_folder_id)

    # Moving Top Level Folder into another Sub Folder
    result_move = move_folder(core_session, folder_id_list[1], nested_folder_id)
    assert result_move['success'], \
        f'Not Able to move Folder into Sub Folder, API response result: {result_move["Result"]}'
    logger.info(f'Moving Folder into Sub Folder:{result_move["Message"]}')
    folder_list.insert(0, folder_list.pop(1))

    # Moving Top Level Folder into another Root Folder
    result_move = move_folder(core_session, secret_folder_id,  folder_id_list[3])
    assert result_move['success'], \
        f'Not Able to move Folder into Root Folder, API response result: {result_move["Result"]}'
    logger.info(f'Moving Folder into Root Folder:{result_move["Message"]}')
