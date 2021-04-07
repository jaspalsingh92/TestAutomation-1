import pytest
import logging
from Shared.API.secret import move_secret
from Shared.API.users import UserManager

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_move_secret(core_session, added_secrets, create_secret_folder):
    """
                C3072: Move secret
    :param core_session:  Authenticated Centrify Session
    :param added_secrets: Fixture to create text type secret & yield secret id, secret_name
    :param create_secret_folder: Fixture to create secret folder & yields folder related details
     """
    added_text_secret_id, added_text_secret_name = added_secrets
    secret_folder_details = create_secret_folder
    folder_id = secret_folder_details['ID']

    # Moving secret into Folder
    result_move = move_secret(core_session, added_text_secret_id[0], folder_id)
    assert result_move['success'], \
        f'Failed to move the secret into Folder,API response result:{result_move["Message"]}'
    logger.info(f'Successfully moved the secret into folder: {result_move["Result"]}')

    # Api to retrieve the activity of the secret
    rows_result = UserManager.get_secret_activity(core_session, added_text_secret_id[0])
    assert rows_result, \
        f'Failed to fetch Secret updated details & activity fetched,API response result:{rows_result}'
    logger.info(f'Activity list:{rows_result}')
    moved_secret_status = False
    for rows in rows_result:
        if ' moved the secret' in rows['Detail']:
            moved_secret_status = True
    assert moved_secret_status, \
        f'Failed to get activity related to move secrets,API response result:{moved_secret_status}'
