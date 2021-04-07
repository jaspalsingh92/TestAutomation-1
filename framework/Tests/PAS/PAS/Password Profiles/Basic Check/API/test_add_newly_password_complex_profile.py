from Shared.API.infrastructure import ResourceManager
from Utils.guid import guid
import logging
import pytest

logger = logging.getLogger("test")


@pytest.mark.pasapi
@pytest.mark.bhavna
@pytest.mark.pas
def test_add_password_profile(core_session, cleanup_password_profile):
    """
    Test Case ID: C281491
    Test Case: Add newly Password Complex Profile
    :param core_session: Authenticates API session
    :param cleanup_password_profile: Deletes the created password profile
    """
    profile_name_cps = f'Profile {guid()}'
    profile_create_result, profile_create_success = ResourceManager.add_password_profile(core_session,
                                                                                         profile_name_cps,
                                                                                         min_pwd_len=12, max_pwd_len=24)
    assert profile_create_success, f"Profile: {profile_name_cps} failed to create due to {profile_create_result}"
    logger.info(f"Profile {profile_name_cps} successfully created and result is {profile_create_result}")
    all_profiles_result, all_profiles_success = ResourceManager.get_profiles(core_session, type='All', rr_format=True)
    assert all_profiles_success, f"Failed to get profiles list {all_profiles_result}"
    logger.info(f"Successfully get the list of all the profiles {all_profiles_result}")
    cloned_builtin_profile_id = []
    for row in all_profiles_result['Results']:
        if row['Row']['Name'] == profile_name_cps:
            cloned_builtin_profile_id.append(row['Row']['ID'])
    profile_list = cleanup_password_profile
    profile_list.append(cloned_builtin_profile_id[0])
