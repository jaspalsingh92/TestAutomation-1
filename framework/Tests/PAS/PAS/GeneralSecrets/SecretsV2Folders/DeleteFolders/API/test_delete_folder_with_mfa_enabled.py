import logging
import pytest
from Utils.guid import guid
from Shared.API.policy import PolicyManager
from Shared.API.secret import del_folder, update_folder, del_folder_mfa

logger = logging.getLogger('test')


@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_delete_folder_with_mfa_enabled(core_session, create_secret_folder, pas_general_secrets, clean_up_policy,
                                        cleanup_secrets_and_folders):
    """
            C284042: Delete folder that has an MFA enabled
    :param core_session: Authenticated Centrify Session.
    :param create_secret_folder: Fixture to create  folder & yields folder related details
    :param pas_general_secrets: Fixture to read secrets related data from yaml file
    :param clean_up_policy: Fixture to clean up the policy created
    :param cleanup_secrets_and_folders: Fixture to cleanup the secrets & folders created
    """
    secret_folder_details = create_secret_folder
    folder_id = secret_folder_details['ID']
    folder_name = secret_folder_details['Name']
    params = pas_general_secrets
    suffix = guid()
    challenges1 = ["UP", ""]
    user_name = core_session.auth_details['User']
    folders_list = cleanup_secrets_and_folders[1]

    # creating a new Authentication profile for folder
    policy_result = PolicyManager.create_new_auth_profile(core_session,
                                                          params['policy_name'] + suffix, challenges1, 0, 0)
    assert policy_result, f'Failed to create policy, API response result:{policy_result}'
    logger.info(f' Creating new policy:{policy_result}')
    clean_up_policy.append(policy_result)

    # Updating the Folder(Applying MFA)
    result = update_folder(core_session,
                           folder_id,
                           folder_name,
                           folder_name,
                           description=params['mfa_folder_description'],
                           policy_id=policy_result)
    assert result['success'], f' Failed to apply MFA on folder, API response result: {result["Message"]} '
    logger.info(f'MFA Applied on Folder: {result}')

    # Delete folder with Mfa Authentication
    del_result = del_folder(core_session, folder_id)

    # StartChallenge MFA Authentication
    session, mechanism = core_session.start_mfa_authentication(user_name, del_result['Result']['ChallengeId'])

    # AdvanceAuthentication MFA to Password
    result = core_session.advance_authentication(answer=core_session.user.user_input.password, session_id=session,
                                                 mechanism_id=mechanism)
    assert result, "Password Authentication Failed"

    # After Authentication of MFA delete folder
    del_secret_result = del_folder_mfa(core_session, folder_id,
                                       ChallengeStateId=del_result['Result']['ChallengeId'])
    assert del_secret_result['success'], f'Failed to delete folder with mfa, API response result: {del_secret_result}'
    logger.info(f'Successfully deleted folder with MFA & get challenged: {del_secret_result}')
    folders_list.remove(folder_id)
