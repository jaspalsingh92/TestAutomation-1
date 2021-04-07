import logging
import pytest
from Shared.API.secret import create_text_secret, get_secrets_and_folders_in_folders, get_secret_contents, get_folder
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_create_folder_as_part_of_a_new_secret(core_session, cleanup_secrets_and_folders, pas_general_secrets):

    """
           test method to create a folder with ADD Secret API
           with secret name as "Folder/Subfolder/secretName" & verify
           Folder, Subfolder & Secrets are created properly.

       :param core_session: Authenticated Centrify Session
       :param cleanup_secrets_and_folders: Fixture to cleanup the secrets & folder created
       :param pas_general_secrets:  Fixture to read secret data from yaml file

    """

    secrets_data = pas_general_secrets
    secrets_list = cleanup_secrets_and_folders[0]
    folders_list = cleanup_secrets_and_folders[1]
    prefix = guid()
    added_secret_success, details, added_secret_id = create_text_secret(
        core_session,
        prefix + secrets_data['folder_name_with_frwdslashes'],
        secrets_data['secret_text'])
    assert added_secret_success, "Added Secret Failed "
    logger.info(f'Added secrets info: {added_secret_success, details, added_secret_id}')
    secrets_list.append(added_secret_id)

    # Getting contents & details of secrets added
    get_secret_details, get_secret_success, get_secret_created_date, get_secret_text = get_secret_contents(
        core_session,
        added_secret_id)
    child_id = get_secret_details['FolderId']
    logger.info(f'child id :{child_id}')
    parent_path = get_secret_details['ParentPath']
    parent_folder_name = parent_path.split('\\')
    parent_folder_sliced = parent_folder_name[0]

    # Getting id of parent folder
    parent_folder = get_folder(core_session, parent_folder_sliced)
    parent_folder_id = parent_folder["Result"]["Results"][0]["Row"]["ID"]
    assert parent_folder_id, f'Failed to retrieve super parent id :{parent_folder_id}'
    logger.info(f'Super parent folder id:{parent_folder_id}')

    # Getting id of nested folder
    nested_folder = get_secrets_and_folders_in_folders(core_session, parent_folder_id)
    nested_folder_id = nested_folder["Result"]["Results"][0]["Row"]["ID"]
    assert nested_folder_id, 'Failed to retrieve nested folder id'
    logger.info(f'Nested Folder id:{nested_folder}')

    folders_list.append(nested_folder_id)
    folders_list.append(parent_folder_id)
    logger.info(f'Added Secret deleted successfully: {secrets_list}')
    logger.info(f'Added Folders deleted successfully: {folders_list}')
