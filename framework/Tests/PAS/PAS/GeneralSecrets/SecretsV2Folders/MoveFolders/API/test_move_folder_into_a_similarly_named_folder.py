import pytest
import logging
from Shared.API.secret import move_folder, create_folder
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_move_folder_into_a_similarly_named_folder(core_session,
                                                   pas_general_secrets,
                                                   cleanup_secrets_and_folders):
    """
        C3042: test method to create folders B1,B11,B1.1 at same level
        1) Move Folder B1 to B11 & verify move is successful.
        2) Move Folder B1 to B1.1 & verify move is successful.

    :param core_session: Authenticated Centrify Session
    :param pas_general_secrets: Fixture to read secrets related data from yaml file
    :param cleanup_secrets_and_folders: Fixture to cleanup the secrets & folders created.
    """
    params = pas_general_secrets
    prefix = guid()
    folder_list = cleanup_secrets_and_folders[1]

    # Creating folder B1
    folder_success, folder_parameters, folder_id = create_folder(
        core_session,
        prefix + params['folder_name_move'],
        params['description'])
    assert folder_success, f'Failed to create a folder with b1:{folder_parameters["Message"]}'
    logger.info(f' Folder b1 created successfully: {folder_success} & details are {folder_parameters}')
    folder_list.insert(0, folder_id)

    # Creating folder B11
    new_folder_success, new_folder_parameters, new_folder_id = create_folder(
        core_session,
        prefix + params['folder_name_move_simi'],
        params['description'])
    assert new_folder_success, f'Failed to create a folder with b11:{new_folder_id}'
    logger.info(f' New Folder b11 created successfully: {new_folder_success} & details are {new_folder_parameters}')
    folder_list.insert(1, new_folder_id)

    # Creating folder B1.1
    success, parameters, id_folder = create_folder(
        core_session,
        prefix + params['folder_name_move_similar'],
        params['description'])
    assert success, f'Failed to create a folder with b1.1 {parameters["Message"]}'
    logger.info(f' Folder b1.1 created successfully: {success} & details are {parameters}')
    # As the cleanup is not working accordingly due to multiple moves so ids are
    # inserted like this
    folder_list.insert(2, id_folder)

    # Moving Folder B1 into B11
    result_move = move_folder(core_session, folder_id, new_folder_id)
    assert result_move['success'], f'Not Able to Move Folder B1 into B11: {result_move["Result"]}'
    logger.info(f'Moving Folder into Sub Folder:{result_move["Message"]}')

    # Moving Folder B1 into  B1.1
    result_move = move_folder(core_session, folder_id, id_folder)
    assert result_move['success'], f'Not Able to  Move Folder B1 into  B1.1: {result_move["Result"]}'
    logger.info(f'Moving Folder into Sub Folder:{result_move["Message"]}')
