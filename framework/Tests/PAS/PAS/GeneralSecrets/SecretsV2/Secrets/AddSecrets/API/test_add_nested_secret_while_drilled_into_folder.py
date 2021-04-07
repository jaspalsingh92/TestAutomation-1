import pytest
import logging
from Shared.API.secret import create_folder, create_text_secret_within_folder
from Shared.endpoint_manager import EndPoints
from Utils.guid import guid

logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi
def test_add_nested_secret_while_drilled_into_folder(core_session, create_secret_folder, pas_general_secrets,
                                                     cleanup_secrets_and_folders):
    """test method to add a secret into nested folder"""
    secrets_list = cleanup_secrets_and_folders[0]
    secret_folder_details = create_secret_folder
    folder_id = secret_folder_details['ID']
    params = pas_general_secrets
    prefix = guid()
    secret_folder_success, secret_folder_parameters, secret_folder_id = create_folder(core_session,

                                                                                      prefix + params['name'],
                                                                                      params['description'],
                                                                                      parent=folder_id)
    logger.info(f'Nested Folder created successfully:{secret_folder_success} & details are:{secret_folder_parameters}')
    assert secret_folder_success is True, f'Failed to create Nested folder :{secret_folder_id}'
    nested_folder_id = secret_folder_id
    logger.info(
        f'Creating secrets in Nested Folder : {secret_folder_parameters}')
    added_text_secret_success, added_text_secret_result = create_text_secret_within_folder(
        core_session, prefix + params['secret_name'], params['secret_text'], params['secret_description'],
        nested_folder_id)
    logger.info(f'Secret Created successfully: {added_text_secret_success}')
    assert added_text_secret_success, f'Unable to create secret {added_text_secret_result}'
    secret_delete_result = core_session.post(EndPoints.SECRET_DELETE, {'ID': added_text_secret_result}).json()
    logger.info(f'Added Secret deleted successfully: {secrets_list} & success:{secret_delete_result}')
    delete_nested_folder = core_session.post(EndPoints.SECRET_FOLDER_DELETE, {'ID': nested_folder_id}).json()
    logger.info(f'Added Nested Folder deleted successfully: {delete_nested_folder} {delete_nested_folder["success"]}')
    assert delete_nested_folder['success'], f'Unable to delete nested folder:{delete_nested_folder["success"]}'
