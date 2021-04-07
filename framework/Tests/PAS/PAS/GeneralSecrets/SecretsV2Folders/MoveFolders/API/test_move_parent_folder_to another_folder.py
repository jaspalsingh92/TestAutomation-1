import pytest
import logging
from Shared.API.secret import move_folder, get_secrets_and_folders_in_folders

logger = logging.getLogger('test')


@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_move_top_level_folder_into_another_folder(core_session,
                                                   create_secret_inside_folder,
                                                   create_folder_inside_folder,
                                                   cleanup_secrets_and_folders):
    """
        C284025: test method to Move parent folder into another folder
             1) Move one folder into another folder & Verify move is successfully including secret
    :param core_session: Authenticated Centrify Session
    :param create_secret_inside_folder: Fixture to create secret inside Folder & yields folder & secret related details
    :param create_folder_inside_folder: Fixture to create nested Folder & yields folder & sub folder related details
    :param cleanup_secrets_and_folders: Fixture to cleanup the secrets & folders created.

    """
    folder_id_list, folder_name, secret_list = create_secret_inside_folder
    parent_folder_info, nested_folder_info, nested_folder_id = create_folder_inside_folder
    folder_list = cleanup_secrets_and_folders[1]

    # Move root Folder to another root Folder.
    logger.info(f'Moving Folder {folder_name} into Folder:{parent_folder_info}')
    result_move = move_folder(core_session, folder_id_list[1], nested_folder_id)
    assert result_move['success'], \
        f'Not Able to move Folder into another Folder, API response result: {result_move["Result"]}'
    logger.info(f'Moved Folder {folder_id_list[1]} into another Folder:{nested_folder_id} successfully')
    folder_list.insert(0, folder_list.pop(1))

    # Getting moved folder name inside folder or nested folder to verify.
    moved_folder = get_secrets_and_folders_in_folders(core_session, nested_folder_id)
    moved_folder_name = moved_folder["Result"]["Results"][0]["Row"]["Name"]
    assert moved_folder_name == folder_name, f'Failed to get the moved folder{moved_folder_name} inside the folder'
    logger.info(f'Moved folder {moved_folder_name} get successfully inside the folder')
