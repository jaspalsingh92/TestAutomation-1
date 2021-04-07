import pytest
import logging
from Shared.API.redrock import RedrockController
from Shared.API.secret import set_users_effective_permissions, get_secret_contents, update_secret
from Shared.API.sets import SetsManager
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_needs_edit_permission_to_replace_contents(core_session,
                                                   users_and_roles,
                                                   added_secrets_file,
                                                   added_secrets,
                                                   pas_general_secrets):
    """
        C283887: User needs edit permission on the secret to replace the contents.
    :param core_session: Authenticated Centrify Session
    :param users_and_roles: Fixture to create New user with PAS Power User & PAS User Rights
    :param added_secrets_file: Fixture to create file type secret
    :param added_secrets: Fixture to create text type secret
    :param pas_general_secrets: Fixture to read secret data from yaml file
    """
    secrets_params = pas_general_secrets
    added_file_secret_id = added_secrets_file
    added_text_secret_id, added_text_secret_name = added_secrets
    suffix = guid()

    # API to get new session for User A
    pas_power_user_session = users_and_roles.get_session_for_user('Privileged Access Service Power User')
    assert pas_power_user_session.auth_details, 'Failed to Login with PAS Power User'
    user_name = pas_power_user_session.auth_details['User']
    user_id = pas_power_user_session.auth_details['UserId']
    logger.info(f'User with PAS Power User Rights login successfully: user_Name:{user_name}')

    # setting user permissions for file_type_secret"""
    file_type_secret_result, file_type_secret_success = set_users_effective_permissions(core_session,
                                                                                        user_name,
                                                                                        'View,Grant',
                                                                                        user_id,
                                                                                        added_file_secret_id)
    assert file_type_secret_success, f'setting permissions for file type secret failed: {file_type_secret_result}'
    logger.info(f'setting permissions for file type secret: {file_type_secret_success}')

    # setting user permissions for file_type_secret"""
    text_type_secret_result, text_type_secret_success = set_users_effective_permissions(core_session,
                                                                                        user_name,
                                                                                        'View,Grant,Edit',
                                                                                        user_id,
                                                                                        added_text_secret_id[0])
    assert text_type_secret_success, f'setting permissions for text type secret:{text_type_secret_result}'
    logger.info(f'setting permissions for text type secret: : {text_type_secret_success}')

    # Replacing the content of the secret
    secret_updated = update_secret(pas_power_user_session,
                                   added_text_secret_id[0],
                                   secrets_params['mfa_secret_name_update'] + suffix,
                                   description=secrets_params['mfa_secret_description'],
                                   secret_text=secrets_params['secret_text_updated'] + suffix)
    assert secret_updated['success'], f'Failed to update secret: {secret_updated["Result"]["ID"]}'
    logger.info(f' Successfully updated text type secret: {secret_updated}')

    # Verifying replaced secret
    get_secret_details, get_secret_success, get_secret_created_date, get_secret_text = get_secret_contents(
        core_session, added_text_secret_id[0])
    logger.info(f'Secret Updated details: {get_secret_details}')
    replaced_content = get_secret_details['SecretText']
    assert secrets_params['secret_text_updated'] in replaced_content,  \
        f'Failed to replace the secrets:{replaced_content}'
    secret_name = get_secret_details['SecretName']

    # creating set manually
    success, set_id = SetsManager.create_manual_collection(pas_power_user_session, secrets_params['set_name'] + suffix,
                                                           'DataVault')
    assert success, f'Failed to create manual set: {set_id}'
    logger.info(f'creating manual set:{success} with setid as: {set_id}')

    # Adding set to secret
    added_to_set_success, added_to_set_result = SetsManager.update_members_collection(pas_power_user_session,
                                                                                      'add',
                                                                                      [added_text_secret_id[0]],
                                                                                      "DataVault", set_id)
    assert added_to_set_success, f'Failed to add secret to set: {added_to_set_result}'
    logger.info(f'Adding secret to set: {added_to_set_success}')

    # Redrock query to fetch "Add to set" related details
    get_set_info = RedrockController.verify_set_secret(pas_power_user_session, set_id, added_text_secret_id[0])
    logger.info(f'{get_set_info}')
    assert get_set_info[0]["Row"]["SecretName"] == secret_name, f' Failed to get "ADD to Set" inside "Actions"'
    logger.info(f'Verifiying secret name {get_set_info[0]["Row"]["SecretName"]} in '
                f'set with ID {get_set_info[0]["Row"]["CollectionID"]} ')
