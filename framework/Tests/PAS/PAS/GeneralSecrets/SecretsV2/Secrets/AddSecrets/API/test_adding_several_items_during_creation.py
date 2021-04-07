import pytest
import logging
from Shared.API.secret import set_users_effective_permissions, \
    update_file_type_secret, get_file_type_secret_contents, update_secret
from Shared.API.policy import PolicyManager
from Utils.assets import get_asset_path
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_adding_several_items_during_creation(core_session,
                                              added_secrets_file,
                                              added_secrets,
                                              users_and_roles,
                                              pas_general_secrets,
                                              clean_up_policy):
    secret_prefix = guid()
    secrets_params = pas_general_secrets
    added_secret_id = added_secrets_file
    added_text_secret_id, added_text_secret_name = added_secrets
    application_management_user = users_and_roles.get_user('Privileged Access Service Power User')
    user_name = application_management_user.get_login_name()
    user_id = application_management_user.get_id()

    # setting permissions for User A
    set_permission_result, set_permission_success = set_users_effective_permissions(core_session,
                                                                                    user_name,
                                                                                    'View,Grant',
                                                                                    user_id,
                                                                                    added_secret_id)
    assert set_permission_success, f'Failed to set permission: {set_permission_result}'
    logger.info(f'Setting permission:{set_permission_result}{set_permission_success}')

    # creating new policy
    policy_result = PolicyManager.create_new_auth_profile(core_session,
                                                          secret_prefix + secrets_params['policy_name'],
                                                          ["UP", None], None, "30")
    assert policy_result is not None, f'Failed to create policy:{policy_result}'
    logger.info(f' Creating new policy:{policy_result}')
    clean_up_policy.append(policy_result)

    # Getting details of file type secrets
    get_secret_details, get_secret_success, get_secret_created_date = get_file_type_secret_contents(core_session,
                                                                                                    added_secret_id)
    assert get_secret_success, f'Failed to get the file type secret contents:{get_secret_success}'
    logger.info(f'Secret created details: {get_secret_details}')
    secrete_file = {'Type': '',
                    'SecretFilePassword': 'pass1',
                    'SecretFilePath': '',
                    'SecretFileSize': '',
                    'SecretName': get_secret_details['SecretName'],
                    'ID': added_secret_id,
                    'DataVaultDefaultProfile': ''
                    }
    local_secret_path = get_asset_path('secret_upload.txt')

    # Assigning policy to file type secrets
    policy_assigned = update_file_type_secret(core_session, added_secret_id, secrete_file, local_secret_path,
                                              policy_result)
    assert policy_assigned['success'], f'Failed to assign policy to secret: {policy_assigned["Result"]["ID"]}'
    logger.info(f'Policy assigned to secret : {policy_assigned}')

    # Removing policy to file type secrets
    policy_assigned = update_file_type_secret(core_session, added_secret_id, secrete_file, local_secret_path)
    assert policy_assigned['success'], f'Failed to assign policy to secret: {policy_assigned["Result"]["ID"]}'
    logger.info(f'Policy assigned to secret : {policy_assigned}')

    # Setting permissions for text type secrets
    set_permission_result, set_permission_success = set_users_effective_permissions(core_session, user_name,
                                                                                    'View,Grant', user_id,
                                                                                    added_text_secret_id[0])
    assert set_permission_success, f'Failed to set permission: {set_permission_result}'
    logger.info(f'Setting permission:{set_permission_result}{set_permission_success}')

    # Applying Policy
    policy_assigned = update_secret(core_session,
                                    added_text_secret_id[0],
                                    added_text_secret_name,
                                    policy_id=policy_result)
    assert policy_assigned['success'], f'Failed to assign policy to secret: {policy_assigned["Result"]["ID"]}'
    logger.info(f' Policy assigned to text type secret: {policy_assigned}')

    # Removing policy
    policy_assigned = update_secret(core_session,
                                    added_text_secret_id[0],
                                    added_text_secret_name)
    assert policy_assigned['success'], f'Failed to assign policy to secret: {policy_assigned["Result"]["ID"]}'
    logger.info(f' Policy assigned to text type secret: {policy_assigned}')
