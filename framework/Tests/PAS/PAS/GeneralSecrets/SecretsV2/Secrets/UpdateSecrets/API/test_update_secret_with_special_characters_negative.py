import logging
import pytest
from Shared.API.secret import update_secret
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_update_secret_with_special_characters_negative(core_session, added_secrets, pas_general_secrets):
    """
    test method to update the secret with special characters
    :param core_session: Authenticated Centrify session
    :param added_secrets: Fixture to create text type secret & yield secret id, secret_name
    :param pas_general_secrets: Fixture to read secret data from yaml file
    """
    added_text_secret_id, added_text_secret_name = added_secrets
    secrets_params = pas_general_secrets
    prefix = guid()

    # Api to update the secret name with special characters(backslashes)"""
    result = update_secret(core_session, added_text_secret_id, prefix + secrets_params['invalid_name_with_backslashes'])
    assert result['success'] is False, f'Able to update with invalid name {result["Result"]} '
    logger.info(f'Unable to update with invalid name:  {result["success"]} & {result["Exception"]}')

    # Api to update the secret name with special characters(forwardslashes)"""
    result = update_secret(core_session, added_text_secret_id,
                           prefix + secrets_params['invalid_name_with_forwdslashes'])
    assert result['success'] is False, f'Able to update with invalid name {result["Result"]} '
    logger.info(f'Unable to update with invalid name:  {result["success"]} & {result["Exception"]}')

    # Api to update the secret name with special characters(specialcharacters)"""
    result = update_secret(core_session, added_text_secret_id,
                           prefix + secrets_params['invalid_name_with_special_chars'])
    assert result['success'] is False, f'Able to update with invalid name {result["Result"]} '
    logger.info(f'Unable to update with invalid name:  {result["success"]} & {result["Exception"]}')
