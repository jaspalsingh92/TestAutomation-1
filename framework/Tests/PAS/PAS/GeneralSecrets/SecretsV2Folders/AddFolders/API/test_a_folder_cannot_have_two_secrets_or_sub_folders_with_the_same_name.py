import logging
import pytest
from Shared.API.secret import get_secret_contents, create_text_secret, create_folder, get_folder
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_a_folder_cannot_have_two_secrets_or_sub_folders_with_the_same_name(core_session,
                                                                            pas_general_secrets,
                                                                            cleanup_secrets_and_folders):

    """
        C3027:test method to
        1) add secrets with same name within same folder should fail
        2) add sub folder with same name in same path should fail
        3) add sub folder with same name (caps) in same path should fail

    :param core_session: Authenticated Centrify Session
    :param pas_general_secrets:  Fixture to read secret data from yaml file
    :param cleanup_secrets_and_folders: Fixture to cleanup the secrets & folder created
    """
    params = pas_general_secrets
    secrets_list = cleanup_secrets_and_folders[0]
    folders_list = cleanup_secrets_and_folders[1]
    prefix = guid()

    # Creating secret inside folder
    added_secret_success, details, added_secret_id = create_text_secret(core_session,
                                                                        prefix + params['nested_secret_name'],
                                                                        params['secret_text'])
    assert added_secret_success, f"Adding Secret inside folder Failed:{added_secret_id}"
    logger.info(f'Adding Secret inside folder: {added_secret_success, details, added_secret_id}')
    secrets_list.append(added_secret_id)

    # Getting id of Parent Folder
    get_secret_details, get_secret_success, get_secret_created_date, get_secret_text = get_secret_contents(
        core_session,
        added_secret_id)
    folder_id = get_secret_details['FolderId']
    folders_list.append(folder_id)

    # Adding secret with same name(caps) in same path should fail
    added_secret_success, details, added_secret_id = create_text_secret(core_session,
                                                                        prefix + params['nested_secret_name_in_caps'],
                                                                        params['secret_text'])
    assert added_secret_success is False, f"Adding same Secret(with caps) successful:{added_secret_id}"
    logger.info(f'Should not add same(caps) secrets: {added_secret_success, details, added_secret_id}')

    # Creating Sub folder
    success, folder_details, nested_folder_id = create_folder(core_session,
                                                              prefix + params['sub_folder_name'],
                                                              params['description'])
    assert success, f'Failed to add sub folder:{folder_details["Message"]}'
    logger.info(f'Should able to create sub folder:{success}{folder_details} ')
    nested_folder_name = folder_details['Name']
    folders_list.append(nested_folder_id)

    # Getting details of parent folder
    parent_folder = get_folder(core_session, nested_folder_id)
    parent_folder_id = parent_folder["Result"]["Results"][0]["Row"]["Parent"]
    assert parent_folder_id, f'Failed to get parent folder id:{parent_folder_id}'
    logger.info(f'Parent Folder details: {parent_folder}')
    folders_list.append(parent_folder_id)

    # Adding Sub folder with same name in same path should fail
    success, folder_details, nested_folder_id = create_folder(core_session,
                                                              nested_folder_name,
                                                              params['description'])
    assert success is False, f'Same sub folder is added successfully:{folder_details["Message"]}'
    logger.info(f'Should not add same sub folder:{success}')

    # Adding Sub folder with same name(caps) in same path should fail
    success, folder_details, nested_folder_id = create_folder(core_session,
                                                              prefix + params['sub_folder_name_in_caps'],
                                                              params['description'])
    assert success is False, f'Same sub folder with caps is added successfully:{folder_details["Message"]}'
    logger.info(f'Should not add same sub folder with caps:{success} ')
