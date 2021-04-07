import pytest
import logging
from Shared.API.infrastructure import ResourceManager
from Shared.API.policy import PolicyManager

logger = logging.getLogger("test")


@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi
def test_update_account_policy(core_session, pas_windows_setup):
    """
    TC:C2168 Update account policy.
    :param core_session: Returns a API session.
    :param pas_windows_setup: Returns a fixture.
    """
    # Creating a system and account.
    system_id, account_id, sys_info, connector_id, user_password = pas_windows_setup()

    # verify account checkout
    result, success = ResourceManager.get_account_information(core_session, account_id)
    assert result['Workflow']['WorkflowEnabled'] is False, f"account workflow is enabled:{account_id}"

    profile_id = []
    profiles = PolicyManager.get_auth_profiles(core_session)
    for profile in profiles:
        if profile['Row']['Name'] == 'Default New Device Login Profile':
            profile_id.append(profile['Row']['Uuid'])
    # assign policy profile
    update_acc_res, update_acc_success = ResourceManager.update_account(core_session, account_id, sys_info[4],
                                                                        system_id,
                                                                        policy_id=profile_id[0])

    assert update_acc_success, \
        f"failed to update account policy profile  {account_id}, result is: {update_acc_res}"
    logger.info('account updated for policy profile')
    # Get account details
    result = ResourceManager.get_account_challenges(core_session, account_id)
    assert result['Result']['PasswordCheckoutDefaultProfile'] == profile_id[0], \
        f" account policy profile is mismatch: {account_id}"
    logger.info(f'get account information details successfully: {result}')
