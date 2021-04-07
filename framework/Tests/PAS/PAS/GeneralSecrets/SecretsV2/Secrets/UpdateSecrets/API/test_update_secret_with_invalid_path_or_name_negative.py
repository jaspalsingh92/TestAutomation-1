import logging
import pytest
from Shared.API.secret import update_secret
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_update_secret_with_invalid_path_or_name_negative(core_session, added_secrets, pas_general_secrets):
    """
    test method to update the secret with invalid path & invalid name
    :param core_session: Authenticated Centrify session
    :param added_secrets: Fixture to create text type secret & yield secret id, secret_name
    :param pas_general_secrets: Fixture to read secret data from yaml file
    """
    added_text_secret_id, added_text_secret_name = added_secrets
    secrets_params = pas_general_secrets
    prefix = guid()

    # Api to update the secret with invalid path
    result = update_secret(core_session, added_text_secret_id, prefix + secrets_params['nested_secret_backslashes'])
    assert result['success'] is False, f'Able to update with invalid path name { result["Result"]} '
    logger.info(f'Unable to update with invalid path name:{result["success"]} & {result["Exception"]} ')

    # Api to update the secret with invalid name
    result = update_secret(core_session, added_text_secret_id, prefix + secrets_params['invalid_name'])
    assert result['success'] is False, f'Able to update with invalid name {result["Result"]} '
    logger.info(f'Unable to update with invalid name:  {result["success"]} & {result["Exception"]}')
