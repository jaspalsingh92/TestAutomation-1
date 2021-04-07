import pytest
import logging
from Shared.API.secret import get_secret_contents, create_text_secret_within_folder

logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi
def test_create_text_type_secret_within_folder(
        core_session,
        create_secret_folder,
        pas_general_secrets,
        cleanup_secrets_and_folders):

    """
    test method to add text type secret in a folder
    """
    secrets_list = cleanup_secrets_and_folders[0]
    secret_folder_details = create_secret_folder
    folder_id = secret_folder_details['ID']
    secrets_params = pas_general_secrets
    logger.info(
        f'Creating secrets in folder with folder name : {secret_folder_details["Name"]}')
    added_text_secret_success, added_text_secret_result = create_text_secret_within_folder(
        core_session,
        secrets_params['secret_name'],
        secrets_params['secret_text'],
        secrets_params['secret_description'],
        folder_id)
    assert added_text_secret_success, f"Unable to create secret{added_text_secret_result}"
    logger.info(f'Secret Created successfully: {added_text_secret_success}')

    get_secret_details, get_secret_success, get_secret_created_date, get_secret_text = get_secret_contents(
        core_session,
        added_text_secret_result)
    logger.info(f'Secret created details: {get_secret_details}')

    assert get_secret_details["FolderId"] == folder_id, f'secret within folder {folder_id} doesnt exist'
    logger.info(f'secret inside folder with id:{get_secret_details["FolderId"]} verified successfully')
    secrets_list.append(added_text_secret_result)
    logger.info(f'Added Secret deleted successfully: {secrets_list}')
