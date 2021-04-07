import logging
import pytest
from Shared.API.secret import create_folder, create_text_secret_within_folder, move_secret
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_ok_to_move_secret_to_root_level(core_session,
                                         create_secret_folder,
                                         pas_general_secrets,
                                         cleanup_secrets_and_folders):
    """
            test method to move child secret into root folder
                        should work
    :param core_session: Authenticated Centrify Session.
    :param create_secret_folder: Fixture to create secret folder & yields folder_id
    :param pas_general_secrets: Fixture to read secrets related data from yaml file
    :param cleanup_secrets_and_folders: Fixture to clean up secrets & folders
    """
    secrets_list = cleanup_secrets_and_folders[0]
    folders_list = cleanup_secrets_and_folders[1]
    secret_folder_details = create_secret_folder
    root_folder_id = secret_folder_details['ID']
    prefix = guid()
    params = pas_general_secrets

    # Creating nested folder inside root folder
    nested_folder_success, nested_folder_parameters, nested_folder_id = create_folder(
        core_session,
        prefix + params['name'], params['description'],
        parent=root_folder_id)
    assert nested_folder_success, f'Failed to create a folder:{nested_folder_id} '
    logger.info(f' Folder created successfully: {nested_folder_success} & details are:{nested_folder_parameters}')
    folders_list.insert(0, nested_folder_id)

    # Creating a secret inside nested folder
    added_secret_success, added_secret_result = create_text_secret_within_folder(
        core_session,
        params['secret_name'],
        params['secret_text'],
        params['secret_description'],
        nested_folder_id)
    assert added_secret_success, f"Unable to create secret{added_secret_result}"
    logger.info(f'Secret Created successfully: {added_secret_success}')
    secrets_list.append(added_secret_result)

    # Moving secret into root Folder
    result_move = move_secret(core_session, added_secret_result, root_folder_id)
    assert result_move['success'], f'Not Able to move the secret into Root Folder: {result_move["Result"]}'
    logger.info(f'Able to move the secret into root folder :{result_move["Message"]}')
