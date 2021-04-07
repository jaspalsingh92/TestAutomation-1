import logging
import pytest
from Shared.API.secret import create_folder
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_add_a_sub_folder_with_add_permission_on_the_parent_folder(core_session,
                                                                   create_secret_folder,
                                                                   pas_general_secrets,
                                                                   cleanup_secrets_and_folders):
    """
         test method to add a Sub Folder inside a Parent Folder
        when ADD permissions are  enabled for the Parent Folder
    :param core_session: Authenticated Centrify Session
    :param create_secret_folder: Fixture to create a folder & yields folder related details
    :param pas_general_secrets: Fixture to read secret data from yaml file
    :param cleanup_secrets_and_folders: Fixture to cleanup the secrets & folder created

    """
    secret_folder_details = create_secret_folder
    folder_id = secret_folder_details['ID']
    folder_params = pas_general_secrets
    folders_list = cleanup_secrets_and_folders[1]

    folder_prefix = guid()
    folder_success, folder_parameters, sub_folder_id = create_folder(core_session,
                                                                     folder_prefix + folder_params['name'],
                                                                     folder_params['description'],
                                                                     parent=folder_id)
    assert folder_success, \
        f'Failed to add another folder means No ADD permissions for the folder:{folder_parameters["Result"]}'
    logger.info(f'Folder added successfully: {folder_success}')
    folders_list.insert(0, sub_folder_id)
