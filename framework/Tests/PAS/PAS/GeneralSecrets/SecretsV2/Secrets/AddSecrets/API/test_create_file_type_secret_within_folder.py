import pytest
import logging
from Shared.API.secret import create_file_type_secret_within_folder, get_file_type_secret_contents
from Utils.assets import get_asset_path
from Utils.guid import guid

logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi
def test_create_file_type_secret_within_folder(core_session,
                                               create_secret_folder, pas_general_secrets, cleanup_secrets_and_folders):
    """
        test method to add text type secret in a folder
     """
    secrets_list = cleanup_secrets_and_folders[0]
    secret_folder_details = create_secret_folder
    folder_id = secret_folder_details['ID']
    secret_prefix = guid()
    secrets_params = pas_general_secrets
    secrets_file = \
        {'SecretName': '',
         'FolderId': '',
         'SecretFilePath': '',
         'SecretFilePassword': '',
         'SecretFileSize': '',
         'Description': '',
         'Type': "File",
         'updateChallenges': False}
    local_secret_path = get_asset_path('secret_upload.txt')
    secret_created = create_file_type_secret_within_folder(core_session,
                                                           secrets_file,
                                                           secret_prefix + secrets_params['secret_name'],
                                                           folder_id,
                                                           local_secret_path,
                                                           secrets_params['secret_password'],
                                                           secrets_params['secret_description'])

    assert secret_created["success"], \
        f'Not Able to create secret {secret_created["Result"]} with in folder {folder_id}'
    logger.info(f'Secret created within folder successfully: {secret_created["success"]} '
                f'and secret id {secret_created["Result"]}')

    get_secret_details, get_secret_success, get_secret_created_date = get_file_type_secret_contents(
        core_session,
        secret_created["Result"])
    logger.info(f'Secret created details: {get_secret_details}')

    assert get_secret_details["FolderId"] == folder_id, f'secret within folder {folder_id} doesnt exist'
    logger.info(f'secret inside folder with id: {get_secret_details["FolderId"]} verified successfully')
    secrets_list.append(secret_created["Result"])
    logger.info(f'Added Secret deleted successfully: {secrets_list}')
