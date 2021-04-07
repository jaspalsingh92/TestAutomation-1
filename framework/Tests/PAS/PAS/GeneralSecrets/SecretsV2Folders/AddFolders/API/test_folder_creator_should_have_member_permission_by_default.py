import pytest
import logging
from Shared.API.secret import get_users_effective_folder_permissions

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_folder_creator_should_have_member_permission_by_default(core_session,
                                                                 create_secret_folder,
                                                                 pas_general_secrets):
    """
        C3029:test method to create a Folder & verify
        Folder should have default Member Permissions i.e View', 'Edit', 'Delete', 'Grant'
    :param core_session: Authenticated Centrify Session
    :param create_secret_folder: Fixture to create a folder & yields folder related details
    :param pas_general_secrets: Fixture to read secret data from yaml file

    """
    secret_folder_details = create_secret_folder
    folder_id = secret_folder_details['ID']

    # Getting permissions of the folder created
    permissions = get_users_effective_folder_permissions(core_session, folder_id)

    verify_permissions = ['View', 'Edit', 'Delete', 'Grant', 'Add']
    assert verify_permissions == permissions, f'Failed to verify permissions for the folder{permissions}'
    logger.info(f'Permissions of the folder created: {permissions}')
