import pytest
import logging
from Utils.guid import guid
from Shared.API.secret import create_folder, create_text_secret_within_folder, get_folder

logger = logging.getLogger('test')


@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi
@pytest.mark.parametrize("administrative_right", ['Privileged Access Service Power User',
                                                  'Privileged Access Service Administrator',
                                                  'Privileged Access Service User'])
def test_create_secret_folder_with_valid_parameters(users_and_roles,
                                                    pas_general_secrets,
                                                    administrative_right,
                                                    cleanup_secrets_and_folders):
    """
        TC ID's :- C283804
        Creates a secret inside folder,by each of the user privilege rights.

        :param users_and_roles: Fixture to create New user with PAS Power Rights
        :param pas_general_secrets: Fixture to read secret data from yaml file.
        :param cleanup_secrets_and_folders: Fixture to clean up secrets & folders
        :param administrative_right: Assign users to different rights
        """
    session = users_and_roles.get_session_for_user(administrative_right)

    secrets_params = pas_general_secrets
    secrets_list = cleanup_secrets_and_folders[0]
    folder_list = cleanup_secrets_and_folders[1]
    folder_params = pas_general_secrets
    folder_name = "my_new_folder" + guid()

    # Creating a folder
    success, folder_details, folder_id = create_folder(session, folder_name, folder_params['description'])
    assert success, f'Failed to create folders:{folder_id}'
    logger.info(f'Creating folders successfully:{folder_details} ')
    folder_list.append(folder_id)

    # creating a secret inside the folder.
    added_text_secret_success, added_text_secret_result = create_text_secret_within_folder(
        session,
        secrets_params['secret_name'],
        secrets_params['secret_text'],
        secrets_params['secret_description'],
        folder_id)
    assert added_text_secret_success, f"Unable to create secret{added_text_secret_result}"
    logger.info(f'Secret Created successfully: {added_text_secret_success}')
    secrets_list.append(added_text_secret_result)

    # Call get folder API to verify folder is created or not.
    parent_folder = get_folder(session, folder_id)
    parent_folder_name = parent_folder["Result"]["Results"][0]["Row"]["Name"]
    assert parent_folder_name == folder_details['Name'], f'Failed to verify the folder name:{parent_folder}'
    logger.info(f'Folders Verified successfully. :{parent_folder_name}')
