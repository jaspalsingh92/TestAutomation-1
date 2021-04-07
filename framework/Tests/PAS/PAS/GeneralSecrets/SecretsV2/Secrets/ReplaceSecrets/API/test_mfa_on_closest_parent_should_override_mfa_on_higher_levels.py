import logging
import pytest
from Shared.API.policy import PolicyManager
from Shared.API.secret import update_secret, update_folder, get_secret, get_folder, create_text_secret, \
    get_secret_contents
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_mfa_on_closest_parent_should_override_mfa_on_higher_levels(

        core_session,
        pas_general_secrets,
        cleanup_secrets_and_folders,
        clean_up_policy,
        core_session_unauthorized):
    """
         C2982: MFA on closest parent should override MFA on higher levels
             1) Create a multilevel folder "Folder/Subfolder/secretName"
             2) Assign different MFA to parent(Folder) & Nested Folder(Subfolder)
             3) Verify secretName inherits challenge of subfolder

    :param core_session:  Authenticated Centrify Session
    :param pas_general_secrets:  Fixture to read secret data from yaml file
    :param cleanup_secrets_and_folders:  Fixture to cleanup the secrets & folder created
    :param clean_up_policy:  Fixture to cleanup the policy created
    :param core_session_unauthorized:  Fixture to start authentication MFA
    """
    folder_list = cleanup_secrets_and_folders[1]
    secrets_list = cleanup_secrets_and_folders[0]
    folder_params = pas_general_secrets
    suffix = guid()
    folder_name = folder_params['folder_name_with_frwdslashes'] + suffix

    # creating multilevel folder "Folder/Subfolder/secretName"
    added_secret_success, details, secret_id = create_text_secret(
        core_session,
        folder_name,
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
    assert result['success'], f'Not Able to apply MFA on Nested folder, API response result: {result["Message"]} '
    logger.info(f'MFA Applied on Nested Folder: {result}')

    # Applying MFA on Parent Folder
    result = update_folder(core_session, parent_folder_id,
                           parent_folder_name,
                           parent_folder_name,
                           description=folder_params['mfa_folder_description'],
                           policy_id=policy_result_email)
    assert result['success'], f'Not Able to apply MFA on parent folder, API response result: {result["Message"]} '
    logger.info(f'MFA Applied on Parent Folder: {result}')

    user = core_session.get_user()
    user_name = user.get_login_name()
    password = user.get_password()

    # MFA Authentication starts on the secret to be replaced
    mfa_authentication = core_session_unauthorized.start_authentication(user_name)
    result = mfa_authentication.json()['Result']
    success = mfa_authentication.json()['success']
    assert success, f'Failed to start MFA Authentication on the secret to be replaced, API response result:{result}'
    challenge_value = result['Challenges'][0]['Mechanisms'][0]['Name']
    assert challenge_value == 'UP', f'Challenge "Password" is not set, API response result:{result}'
    logger.info(f'MFA Authentication applies for closest parent,Password Only:{mfa_authentication.json()}')

    # Advance MFA Authentication starts on the secret to be replaced
    up_result = core_session_unauthorized.advance_authentication(password, challenge_index=0, mechanism_name='UP')
    mfa_result = up_result.json()
    assert mfa_result['success'], f'Failed to respond to challenge, API response result:{mfa_result["Result"]}'
    logger.info(f'MFA applies for closest parent,popups before secret gets replaced: {mfa_result}')

    # Replacing the text of the secret
    result = update_secret(core_session,
                           secret_id,
                           folder_params['mfa_secret_name_update'] + suffix,
                           secret_text=folder_params['secret_text_replaced']
                           )
    assert result['success'], f'Not Able to replace the text of the secret, API response result:{result["Message"]} '
    logger.info(f'Secret gets replaced: {result}')

    # Removing MFA from Nested folder
    result = update_folder(core_session, nested_folder_id,
                           nested_folder_name,
                           nested_folder_name,
                           description=folder_params['mfa_folder_description'])
    assert result['success'], f'Not Able to remove mfa from folder, API response result:: {result["Message"]} '
    logger.info(f'Removing mfa from folder: {result}')

    # Removing MFA from Parent folder
    result = update_folder(core_session, parent_folder_id,
                           parent_folder_name,
                           parent_folder_name,
                           description=folder_params['mfa_folder_description'])
    assert result['success'], f'Not Able to remove mfa from folder, API response result:: {result["Message"]} '
    logger.info(f'Removing mfa from folder: {result}')

    # Getting details of the Secret Replaced
    get_secret_details, get_secret_success, get_secret_created_date, get_secret_text = get_secret_contents(
        core_session,
        secret_id)
    assert get_secret_text == folder_params['secret_text_replaced'], \
        f'Failed to replace the secret, API response result: {get_secret_success}'
    logger.info(f'Details of the secret Replaced: {get_secret_details}')
