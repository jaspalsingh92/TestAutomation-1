import pytest
import logging
from Shared.API.secret import get_secret_contents, get_folder, get_secrets_and_folders_in_folders
from Shared.endpoint_manager import EndPoints
from Utils.guid import guid

logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi
def test_add_duplicate_names_with_different_folder_names(core_session,
                                                         cleanup_secrets_and_folders,
                                                         pas_general_secrets):
    """test method to add duplicate names with different subfolder names using forwardslashes """
    secrets_list = cleanup_secrets_and_folders[0]
    folder_list = cleanup_secrets_and_folders[1]
    secrets_params = pas_general_secrets
    secret_prefix = guid()
    secret_parameters = {
        'SecretName': secret_prefix + secrets_params['nested_secret_name_new'],
        'SecretText': secrets_params['secret_text'],
        'Type': 'Text',
        'Description': secrets_params['secret_description'],
        'FolderId': ''
    }
    """Api to add  secret """
    secret_added_result = core_session.post(EndPoints.SECRET_ADD, secret_parameters).json()
    assert secret_added_result['success'], f'Not able to create secret with {secret_added_result["Result"]}'
    logger.info(f'Secret Created successfully: {secret_added_result["success"]}{secret_added_result["Result"]}')
    secrets_list.append(secret_added_result["Result"])

    get_secret_details, get_secret_success, get_secret_created_date, get_secret_text = get_secret_contents(
                                                                    core_session,
                                                                    secret_added_result["Result"])
    child_id = get_secret_details['FolderId']
    logger.info(f'child id :{child_id}')
    parent_path = get_secret_details['ParentPath']
    parent_folder_name = parent_path.split('\\')
    parent_folder_sliced = parent_folder_name[0]
    secret_parameters = {
        'SecretName': parent_folder_sliced + secrets_params['nested_secret_name_new_duplicate'],
        'SecretText': secrets_params['secret_text'],
        'Type': 'Text',
        'Description': secrets_params['secret_description'],
        'FolderId': ''
    }

    """Api to add duplicate secret """
    duplicate_secret_added_result = core_session.post(EndPoints.SECRET_ADD, secret_parameters).json()
    assert duplicate_secret_added_result["success"], \
        f'Adding Duplicate Secret Failed:{duplicate_secret_added_result["Result"]}'
    logger.info(f'Duplicate Secret Created successfully: {duplicate_secret_added_result["success"]}'
                f'{duplicate_secret_added_result["Result"]}')
    secrets_list.append(duplicate_secret_added_result["Result"])

    """Api to get id of parent folder """
    parent_folder = get_folder(core_session, parent_folder_sliced)
    parent_folder_id = parent_folder["Result"]["Results"][0]["Row"]["ID"]
    assert parent_folder_id is not None, f'Failed to retrieve super parent id :{parent_folder_id}'
    logger.info(f'Super parent folder id:{parent_folder_id}')

    """Api to nested folder details"""
    nested_folder = get_secrets_and_folders_in_folders(core_session, parent_folder["Result"]["Results"][0]["Row"]["ID"])
    nested_folder_id = nested_folder["Result"]["Results"][0]["Row"]["ID"]
    assert nested_folder_id is not None, f'Failed to retrieve nested folder id'
    logger.info(f'Nested Folder id:{nested_folder_id}')

    """Api to get child folder details"""
    child_folder = get_secrets_and_folders_in_folders(core_session, nested_folder["Result"]["Results"][0]["Row"]["ID"])
    child_folder_id = child_folder["Result"]["Results"][0]["Row"]["ID"]
    assert child_folder_id is not None, f'Failed to retrieve child folder id'
    logger.info(f'child Folder id:{child_folder_id}')

    folder_list.append(child_id)
    folder_list.append(child_folder_id)
    folder_list.append(nested_folder_id)
    folder_list.append(parent_folder_id)
    logger.info(f'Secret deleted successfully:{secrets_list}')
    logger.info(f'Folder deleted successfully:{folder_list}')
