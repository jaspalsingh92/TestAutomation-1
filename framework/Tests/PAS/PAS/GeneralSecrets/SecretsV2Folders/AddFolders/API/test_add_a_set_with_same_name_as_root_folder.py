import logging
import pytest
from Shared.API.sets import SetsManager

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_add_a_set_with_same_name_as_root_folder(core_session,
                                                 set_cleaner,
                                                 create_secret_folder,
                                                 pas_general_secrets,
                                                 cleanup_secrets_and_folders):
    """
         C3023:test method to add a set with same name as Root Folder

    :param core_session: Authenticated Centrify Session
    :param set_cleaner: Fixture to cleanup the sets created
    :param create_secret_folder: Fixture to create a folder & yields folder related details
    :param pas_general_secrets: Fixture to read secret data from yaml file
    :param cleanup_secrets_and_folders: Fixture to cleanup the secrets & folder created

    """
    secret_folder_details = create_secret_folder
    folder_name = secret_folder_details['Name']

    # Creating set with same name as root folder
    success, set_id = SetsManager.create_manual_collection(core_session,
                                                           folder_name,
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
