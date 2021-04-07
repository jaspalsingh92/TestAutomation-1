import logging
import pytest
from Shared.API.secret import move_folder, get_folder_activity

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_move_folder_and_contents_to_another_folder_verify_activity(core_session,
                                                                    create_secret_inside_folder,
                                                                    create_folder_inside_folder,
                                                                    cleanup_secrets_and_folders):
    """
        C3068: test method to Move folder and contents to another folder verify activity
             1) Move top level folder into a nested folder
             2) Verify you can logged the activity of the folder moved
    :param core_session: Authenticated Centrify Session
    :param create_secret_inside_folder: Fixture to create secret inside Folder & yields folder & secret related details
    :param create_folder_inside_folder: Fixture to create nested Folder & yields folder & sub folder related details
    :param cleanup_secrets_and_folders: Fixture to cleanup the secrets & folders created.
    """
    folder_id_list, folder_name, secret_list = create_secret_inside_folder
    parent_folder_info, nested_folder_info, nested_folder_id = create_folder_inside_folder
    folder_list = cleanup_secrets_and_folders[1]
    logger.info(f'{folder_id_list}')

    # Moving Top Level Folder into another Sub Folder
    result_move = move_folder(core_session, folder_id_list[1], nested_folder_id)
    assert result_move['success'], \
        f'Not Able to move Folder into Sub Folder, API response result: {result_move["Result"]}'
    logger.info(f'Moving Folder into Sub Folder:{result_move["Message"]}')
    folder_list.insert(0, folder_list.pop(1))

    activity_rows = get_folder_activity(core_session, folder_id_list[0])
    verify_move_activity = 'moved the folder'
    assert verify_move_activity in activity_rows[0]['Detail'], f'Failed to verify the activity:{activity_rows}'
    logger.info(f'Replace activity found for secret {activity_rows}')
