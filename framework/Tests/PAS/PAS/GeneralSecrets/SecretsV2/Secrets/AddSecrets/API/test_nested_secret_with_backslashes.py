import pytest
import logging
from Shared.API.secret import get_secret_contents, get_folder
from Shared.endpoint_manager import EndPoints
from Shared.API.users import UserManager
from Utils.guid import guid

logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi
def test_nested_secret_with_backslashes(core_session,
                                        pas_general_secrets,
                                        cleanup_secrets_and_folders):
    """test method to add nested secret with '\\' """
    secrets_list = cleanup_secrets_and_folders[0]
    folder_list = cleanup_secrets_and_folders[1]
    secrets_params = pas_general_secrets
    secret_prefix = guid()
    secret_parameters = {
        'SecretName': secret_prefix + secrets_params['nested_secret_backslashes'],
        'SecretText': secrets_params['secret_text'],
        'Type': 'Text',
        'Description': secrets_params['secret_description'],
        'FolderId': ''}
    logger.info(
        f'Creating nested secrets : { secrets_params["nested_secret_backslashes"]}')
    """Api to create nested secret with backslashes"""
    secret_result = core_session.post(EndPoints.SECRET_ADD, secret_parameters).json()
    logger.info(f'Secret Created successfully:{secret_result}{secret_result["success"]}')
    assert secret_result['success'], f'Not able to create secret with {secret_result}'
    secret_id = secret_result["Result"]

    """Api to get secret activity"""
    secret_activity = UserManager.get_secret_activity(core_session, secret_id)
    logger.info(
        f'Secret Created activity:{secret_activity} ')
    str1 = 'added a secret "Topsecret" of type "Text"'
    assert str1 in secret_activity[0]['Detail'], "Failed to assert"

    """Api to get text type secret details"""
    get_secret_details, get_secret_success, get_secret_created_date, get_secret_text = get_secret_contents(core_session,
                                                                                                           secret_id)
    logger.info(f'Secret created details: {get_secret_details}')
    child_folder = get_secret_details['FolderId']
    parent_path = get_secret_details['ParentPath']
    parent_folder_name = parent_path.split('\\')
    parent_folder_sliced = parent_folder_name[0]
    parent_id = get_folder(core_session, parent_folder_sliced)
    logger.info(f'parent folder id::{parent_id["Result"]["Results"][0]["Row"]["ID"]}')
    secrets_list.append(secret_id)
    folder_list.append(child_folder)
    folder_list.append(parent_id['Result']['Results'][0]['Row']['ID'])
    logger.info(f'Added folder deleted successfully : {folder_list}')
    logger.info(f'Added Secret deleted successfully : {secrets_list}')
