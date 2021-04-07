import pytest
import logging
from Shared.API.secret import create_text_secret
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi
def test_add_to_set_during_secret_creation(
        core_session,
        create_set_manual,
        pas_general_secrets,
        cleanup_secrets_and_folders):

    """test method to add a set while creating a new secret"""

    secrets_params = pas_general_secrets
    prefix = guid()
    set_success, set_id = create_set_manual
    secrets_list = cleanup_secrets_and_folders[0]
    added_secret_success, added_secret_details, added_secret_id = create_text_secret(
        core_session,
        prefix + secrets_params['secret_name'],
        secrets_params['secret_text'], set_id)
    logger.info(f'Added secrets info {added_secret_success, added_secret_details, added_secret_id}')
    assert added_secret_success, "Adding Secret with set Failed "
    assert added_secret_details['SetID'] is not None, f"Secret with set  not Added successfully:{added_secret_success}"
    logger.info(f'secret added with set id:{added_secret_details["SetID"]}')
    secrets_list.append(added_secret_id)
    logger.info(f'Added Secret deleted successfully{secrets_list}')
