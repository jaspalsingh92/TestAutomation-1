import logging
import pytest
from Shared.API.secret import create_text_secret, get_secret_contents, get_folder
from Shared.API.users import UserManager
from Utils.guid import guid
logger = logging.getLogger('test')


@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_add_nested_secret(core_session, pas_general_secrets, cleanup_secrets_and_folders):
    """
            C283806: Can add nested secret
    :param core_session: Authenticated Centrify session
    :param pas_general_secrets: Fixture to read secrets data from yaml file
    :param cleanup_secrets_and_folders: Fixture to cleanup the secrets & folders created
    """
    params = pas_general_secrets
    folder_list = cleanup_secrets_and_folders[1]
    secrets_list = cleanup_secrets_and_folders[0]
    suffix = guid()

    # Creating nested secrets
    added_secret_success, details, added_secret_id = create_text_secret(core_session,
                                                                        params['nested_secret_name_new'] + suffix,
                                                                        params['secret_text'])
    assert added_secret_success, f"Added Secret Failed, API response result: {added_secret_id}"
    logger.info(f'Added secrets info: {details, added_secret_id}')
    folders_and_secret_name = details['SecretName']

    # Getting details of nested secrets
    get_secret_details, get_secret_success, get_secret_created_date, get_secret_text = get_secret_contents(
        core_session,
        added_secret_id)
    logger.info(f'Secret created details: {get_secret_details}')
    secret_name = get_secret_details['SecretName']
    child_folder_id = get_secret_details['FolderId']
    parent_path = get_secret_details['ParentPath']
    parent_folder_and_child_folder = parent_path.split('\\')
    parent_name = parent_folder_and_child_folder[0]
    child_folder_name = parent_folder_and_child_folder[1]

    # Getting added secret status
    secret_activity = UserManager.get_secret_activity(core_session, added_secret_id)
    logger.info(f'Secret Created activity:{secret_activity} ')
    added_secret_status = False
    for rows in secret_activity:
        if 'added a secret' in rows['Detail']:
            added_secret_status = True
    assert added_secret_status, f'Failed to add secret: {added_secret_status}'
    assert parent_name in folders_and_secret_name, f'Failed to verify parent folder name: {parent_name}'
    assert child_folder_name in folders_and_secret_name, f'Failed to verify child folder name: {child_folder_name}'
    assert secret_name in folders_and_secret_name, f'Failed to verify secret name: {secret_name}'

    # Getting details of the parent folder & child folder
    parent_id = get_folder(core_session, parent_name)
    logger.info(f'parent folder id::{parent_id["Result"]["Results"][0]["Row"]["ID"]}')
    secrets_list.append(added_secret_id)
    folder_list.append(child_folder_id)
    folder_list.append(parent_id['Result']['Results'][0]['Row']['ID'])
    logger.info(f'Added folder deleted successfully : {folder_list}')
    logger.info(f'Added Secret deleted successfully : {secrets_list}')
