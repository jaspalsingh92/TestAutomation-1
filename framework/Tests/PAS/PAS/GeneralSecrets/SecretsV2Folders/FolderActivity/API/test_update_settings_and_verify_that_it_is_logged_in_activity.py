import pytest
import logging
from Shared.API.secret import get_folder_activity, update_folder
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_update_settings_and_verify_that_it_is_logged_in_activity(core_session,
                                                                  create_secret_folder,
                                                                  users_and_roles,
                                                                  pas_general_secrets):
    """
            C3070 : Update Settings and verify that it’s logged in activity
    :param core_session: Authenticated Centrify Session
    :param create_secret_folder: Fixture to create secret folder & yields folder details
    :param users_and_roles: Fixture to create a random user with PAS Power rights
    :param pas_general_secrets: Fixture to read secrets related data from yaml
    """
    secrets_params = pas_general_secrets
    suffix = guid()
    secret_folder_details = create_secret_folder
    folder_id = secret_folder_details['ID']
    folder_name = secret_folder_details['Name']

    # Updating settings of the Folder(Applying MFA)
    result = update_folder(core_session,
                           folder_id,
                           folder_name,
                           secrets_params['mfa_folder_name_update'] + suffix,
                           description=secrets_params['mfa_folder_description'])
    assert result['success'], f'Not Able to update settings of the folder, API response result: {result["Message"]} '
    logger.info(f'Updating settings of the folder: {result}')

    # Getting activity of the folder updated
    activity_rows = get_folder_activity(core_session, folder_id)
    verify_folder_update = 'updated the folder'
    assert verify_folder_update in activity_rows[0]['Detail'], \
        f'Failed to verify the activity, API response result::{activity_rows}'
    logger.info(f'Update activity for folder, API response result: {activity_rows}')
