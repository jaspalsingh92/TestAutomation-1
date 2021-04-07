import logging
import pytest
from Shared.API.policy import PolicyManager
from Shared.API.secret import update_folder, \
    get_secret, get_folder, create_text_secret, retrieve_secret_contents, retrieve_secret_contents_with_mfa
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_retrieve_mfa_on_closest_parent_should_override_mfa(
        core_session,
        pas_general_secrets,
        cleanup_secrets_and_folders,
        clean_up_policy):
    """
        C283926: MFA on closest parent should override MFA on higher levels
             1) Create a multilevel folder "Folder/Subfolder/secretName"
             2) Assign different MFA to parent(Folder) & Nested Folder(Subfolder)
             3) Verify secretName inherits challenge of subfolder

    :param core_session:  Authenticated Centrify Session
    :param pas_general_secrets:  Fixture to read secret data from yaml file
    :param cleanup_secrets_and_folders:  Fixture to cleanup the secrets & folder created
    :param clean_up_policy:  Fixture to cleanup the policy created
    """
    folder_list = cleanup_secrets_and_folders[1]
    secrets_list = cleanup_secrets_and_folders[0]
    folder_params = pas_general_secrets
    suffix = guid()
    secret_name = folder_params['folder_name_with_frwdslashes'] + suffix
    user_name = core_session.auth_details['User']

    # creating multilevel folder "Folder/Subfolder/secretName"
    added_secret_success, details, secret_id = create_text_secret(
        core_session,
        secret_name,
        folder_params['secret_text'])
    assert added_secret_success, "Added Multilevel folder Failed,API response result: {secret_id} "
    logger.info(f'Added Multilevel folder info: {details, secret_id}')
    secrets_list.append(secret_id)

    # Getting details of the secret
    found_secret = get_secret(core_session, secret_id)
    assert found_secret['success'], \
        f'Failed to get the details of the secret, API response result:{found_secret["Message"]}'
    logger.info(f'Getting details of the secret: {found_secret}')
    nested_folder_id = found_secret['Result']['FolderId']
    nested_folder_path = found_secret['Result']['ParentPath']
    parent_folder_list = nested_folder_path.split('\\')
    parent_folder_name = parent_folder_list[0]

    # Getting details of Parent Folder
    parent_folder = get_folder(core_session, nested_folder_id)
    parent_folder_id = parent_folder["Result"]["Results"][0]["Row"]["Parent"]
    nested_folder_name = parent_folder["Result"]["Results"][0]["Row"]["SecretName"]
    logger.info(f'Parent Folder details: {parent_folder}')

    if folder_list != []:
        folder_list[0] = nested_folder_id
        folder_list[1] = parent_folder_id
    else:
        folder_list.append(nested_folder_id)
        folder_list.append(parent_folder_id)

    challenges = ["UP", ""]
    challenges_v2 = ["UP,EMAIL", ""]
    # Creating new policy with Password
    policy_result = PolicyManager.create_new_auth_profile(core_session, folder_params['policy_name'] + suffix,
                                                          challenges, 0, 0)
    assert policy_result, f'Failed to create policy, API response result:{policy_result}'
    logger.info(f' Creating new policy:{policy_result}')
    clean_up_policy.append(policy_result)

    # Creating new policy with Password & Email
    policy_result_email = PolicyManager.create_new_auth_profile(core_session,
                                                                folder_params['policy_name'] + "V2" + suffix,
                                                                challenges_v2, 0, 0)
    assert policy_result_email, f'Failed to create another policy, API response result:{policy_result_email}'
    logger.info(f' Creating another policy:{policy_result_email}')
    clean_up_policy.append(policy_result_email)

    # Applying MFA on Nested Folder
    result = update_folder(core_session, nested_folder_id,
                           nested_folder_name,
                           nested_folder_name,
                           description=folder_params['mfa_folder_description'],
                           policy_id=policy_result)
    assert result['success'], f'Failed to apply MFA on Nested folder, API response result: {result["Message"]} '
    logger.info(f'MFA Applied on Nested Folder: {result}')

    # Applying MFA on Parent Folder
    result = update_folder(core_session, parent_folder_id,
                           parent_folder_name,
                           parent_folder_name,
                           description=folder_params['mfa_folder_description'],
                           policy_id=policy_result_email)
    assert result['success'], f'Failed to apply MFA on parent folder, API response result: {result["Message"]} '
    logger.info(f'MFA Applied on Parent Folder: {result}')

    # Move Secret with Mfa Authentication
    retrieve_success, retrieve_result = retrieve_secret_contents(core_session, secret_id)

    # StartChallenge MFA Authentication
    session, mechanism = core_session.start_mfa_authentication(user_name, retrieve_result['ChallengeId'])

    # AdvanceAuthentication MFA to Password
    advance_auth_result = core_session.advance_authentication(answer=core_session.user.user_input.password,
                                                              session_id=session, mechanism_id=mechanism)
    mfa_result = advance_auth_result.json()
    assert advance_auth_result, f'Password Authentication Failed, API response result:{mfa_result["success"]}'
    logger.info(f'Successfully applied password authentication with closest parent: {mfa_result}')

    # After Authenticating of MFA move secret with challenge password
    retrieve_secret_success, retrieve_secret_result = retrieve_secret_contents_with_mfa(
        core_session, secret_id, ChallengeStateId=retrieve_result['ChallengeId'])
    assert retrieve_secret_success, f'Failed to retrieve secret with closest parent challenge: {retrieve_secret_result}'
    logger.info(f'Successfully retrieved secret with closest parent challenge: {retrieve_secret_result}')

    # Removing MFA on Nested Folder
    result = update_folder(core_session, nested_folder_id,
                           nested_folder_name,
                           nested_folder_name,
                           description=folder_params['mfa_folder_description'])
    assert result['success'], f'Failed to remove MFA on Nested folder, API response result: {result["Message"]} '
    logger.info(f'MFA removed on Nested Folder: {result}')

    # Removing MFA on Parent Folder
    result = update_folder(core_session, parent_folder_id,
                           parent_folder_name,
                           parent_folder_name,
                           description=folder_params['mfa_folder_description'])
    assert result['success'], f'Failed to remove MFA on parent folder, API response result: {result["Message"]} '
    logger.info(f'MFA removed on Parent Folder: {result}')
