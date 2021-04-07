import logging
import pytest

logger = logging.getLogger("test")


@pytest.mark.pasapi
@pytest.mark.bhavna
@pytest.mark.pas
def test_clone_password_complex_profile(core_session, create_basic_pass_profile, create_clone_windows_pass_profile,
                                        create_clone_custom_pass_profile):
    """
    Test Case ID: C281494
    Test Case: Clone Password Complex Profile
    :param core_session: Authenticates API session
    :param create_basic_pass_profile: Creates a basic password complexity profile
    :param create_clone_windows_pass_profile: Creates cloned windows password profile
    :param create_clone_custom_pass_profile: Creates cloned custom password profile
    """

    profile = create_basic_pass_profile(core_session, 1)[0]
    profile_name_cps = profile[0]['Name']
    custom_profile_name_clone = f"{profile_name_cps} (Cloned)"

    # Creating custom profile clone
    create_clone_custom_profile = create_clone_custom_pass_profile(core_session,
                                                                   name=custom_profile_name_clone)

    cloned_profiles = create_clone_custom_profile[0]
    assert cloned_profiles[0]['Name'] == custom_profile_name_clone, f"Failed to clone custom password profile"
    logger.info("Cloned custom Password profile successfully")

    # Creating builtin cloned Windows profile clone
    clone_windows_profile_name = "Windows Profile (Cloned)"
    profile_clone = create_clone_windows_pass_profile(core_session)
    cloned_profiles_windows = profile_clone[0]
    assert cloned_profiles_windows[0]['Name'] == clone_windows_profile_name, f"Failed to clone builtin password profile"
    logger.info("Cloned builtin Password profile successfully")
