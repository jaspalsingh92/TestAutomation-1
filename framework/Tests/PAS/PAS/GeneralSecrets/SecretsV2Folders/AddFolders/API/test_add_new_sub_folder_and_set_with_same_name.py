import logging
import pytest
from Shared.API.secret import create_folder
from Utils.guid import guid
from Shared.API.sets import SetsManager

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_add_new_sub_folder_and_set_with_same_name(core_session,
                                                   set_cleaner,
                                                   create_secret_folder,
                                                   pas_general_secrets,
                                                   cleanup_secrets_and_folders):
    """
         test method to add a set with same name as Sub Folder

    :param core_session: Authenticated Centrify Session
    :param set_cleaner: Fixture to cleanup the sets created
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
    assert folder_success, f'Failed to add sub folder:{folder_parameters["Result"]}'
    logger.info(f'Folder added successfully: {folder_success}')
    folders_list.insert(0, sub_folder_id)

    success, set_id = SetsManager.create_manual_collection(core_session,
                                                           folder_prefix + folder_params['name'],
                                                           'DataVault')

    assert success is True, f'Failed to create manual set with same name as Sub Folder {set_id}'
    logger.info(f'creating manual set:{success} with setid as: {set_id}')
    set_cleaner.append(set_id)
    logger.info(f'Added set deleted successfully:{set_cleaner}')

    # Getting permissions of the set created
    permissions = SetsManager.get_collection_rights(core_session, set_id)

    verify_permissions = 'View, Edit, Delete, Grant'
    assert verify_permissions == permissions["Result"], \
        f'Failed to verify permissions for the set:{permissions["Result"]}'
    logger.info(f'Permissions of the set created: {permissions}')
