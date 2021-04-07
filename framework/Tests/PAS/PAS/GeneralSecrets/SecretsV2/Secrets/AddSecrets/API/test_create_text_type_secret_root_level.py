import pytest
import logging
from Shared.API.secret import get_secret_contents, create_text_secret

logger = logging.getLogger("test")


@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi
def test_create_type_secret_at_root_level(
        core_session,
        create_secret_folder,
        pas_general_secrets,
        cleanup_secrets_and_folders):

    """
    TC ID's :- C283795
    test method to add text type secret at root level.
    """
    secrets_list = cleanup_secrets_and_folders[0]
    secret_details = create_secret_folder
    secrets_params = pas_general_secrets
    logger.info(
        f'Creating secrets with text type secret name : {secret_details["Name"]}')
    added_text_secret_success, added_text_secret_parameters, added_text_secret_result = create_text_secret(
        core_session,
        secrets_params['secret_name'],
        secrets_params['secret_text'],
        secrets_params['secret_description'])
    assert added_text_secret_success, f"Unable to create secret{added_text_secret_result}"
    logger.info(f'Secret Created at root level successfully: {added_text_secret_success}')

    get_secret_details, get_secret_success, get_secret_created_date, get_secret_text = get_secret_contents(
        core_session,
        added_text_secret_result)
    logger.info(f'Secret created details: {get_secret_details}')
    secrets_list.append(added_text_secret_result)
    logger.info(f'Added Secret deleted successfully: {secrets_list}')
