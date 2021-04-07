import pytest
import logging
from Shared.API.secret import get_folder, create_folder
from Utils.guid import guid

logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.parametrize("separator", ['/', '\\', 'multiple'])
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi
def test_create_folders_with_multiple_levels_using_slashes(core_session,
                                                           pas_general_secrets,
                                                           cleanup_secrets_and_folders,
                                                           separator):
    """
        C3025:test method to add nested secret with  multiple levels (Engineering QA Devdog)
                1) forward slashes
                2) back slashes
                 3) both forward and back slashes
    :param core_session:  Authenticated Centrify Session
    :param pas_general_secrets:  Fixture to read secret data from yaml file
    :param cleanup_secrets_and_folders:  Fixture to cleanup the secrets & folder created
    :param separator: Parameterize the test against multiple inputs
    """
    folder_list = cleanup_secrets_and_folders[1]
    folder_params = pas_general_secrets
    prefix = guid()
    if separator == 'multiple':
        folder_name = prefix + folder_params['folder_name_with_multiple_slashes']
    else:
        folder_name = prefix + "Engineering" + separator + "QA" + separator + "Devdog"
    success, folder_details, folder_id = create_folder(core_session, folder_name, folder_params['description'])
    assert success, f'Failed to create folders with slashes:{folder_id}'
    logger.info(f'Creating folders with  slashes:{folder_details} ')
    folder_list.append(folder_id)

    # Getting details of Nested Folder
    result_folder = get_folder(core_session, folder_id)
    nested_folder_id = result_folder["Result"]["Results"][0]["Row"]["Parent"]
    assert nested_folder_id, f'Failed to get nested folder id:{nested_folder_id}'
    logger.info(f'Nested Folder details: {result_folder}')
    folder_list.append(nested_folder_id)

    # Getting details of Parent Folder
    parent_folder = get_folder(core_session, nested_folder_id)
    parent_folder_id = parent_folder["Result"]["Results"][0]["Row"]["Parent"]
    assert parent_folder_id, f'Failed to get parent folder id:{parent_folder_id}'
    logger.info(f'Parent Folder details: {parent_folder}')
    folder_list.append(parent_folder_id)
