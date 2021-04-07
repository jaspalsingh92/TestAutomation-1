import pytest
import logging
from Shared.API.sets import SetsManager
from Shared.API.users import UserManager

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_add_a_new_top_level_stand_alone_folder(core_session,
                                                create_secret_folder,
                                                pas_general_secrets):

    """
         Test method to create a Folder &
        verifying the  rights of the folder created
    :param core_session: Authenticated Centrify Session
    :param create_secret_folder: Fixture to create a folder & yields folder related details
    :param pas_general_secrets: Fixture to read secret data from yaml file

    """
    secret_folder_details = create_secret_folder
    folder_id = secret_folder_details['ID']

    # Getting the Id of the user.
    user_details = core_session.__dict__
    user_id = user_details['auth_details']['UserId']

    # Refreshing the page.
    refresh_result = UserManager.refresh_token(core_session, user_id)
    assert refresh_result["success"], f"Failed to reload:API response result:{refresh_result}"

    # Getting permissions of the folder created
    permissions = SetsManager.get_collection_rights(core_session, folder_id)
    verify_permissions = 'View, Edit, Delete, Grant, Add'
    assert verify_permissions == permissions["Result"], \
        f'Failed to verify permissions for the folder{permissions["Result"]}'
    logger.info(f'Permissions of the folder created: {permissions}')
