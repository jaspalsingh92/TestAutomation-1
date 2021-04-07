from Shared.API.infrastructure import ResourceManager
import logging
import pytest

logger = logging.getLogger("test")


@pytest.mark.pasapi
@pytest.mark.bhavna
@pytest.mark.pas
def test_modify_password_profile(core_session, create_basic_pass_profile):
    """
    Test Case ID: C281492
    Test Case: Modify Password Complex Profile
    :param core_session: Authenticates API session.
    :param create_basic_pass_profile: Creates a Password Profile
    """
    profile = create_basic_pass_profile(core_session, 1)[0]
    profile_name_cps = profile[0]['Name']
    cps_prof_id = profile[0]['_RowKey']
    cps_prof_result, cps_prof_success = ResourceManager.get_password_profile_by_id(core_session, cps_prof_id)
    assert cps_prof_success, f"Failed to create Profile due to {cps_prof_result}"
    logger.info(f'System successfully updated with result: {cps_prof_result}')

    update_cps_prof_success = ResourceManager.update_password_profile(core_session, cps_prof_id, profile_name_cps,
                                                                      13, 26, one_lwr_case=False, one_upp_case=False,
                                                                      one_digit=False, consecutive_chars=False,
                                                                      one_special_char=False,
                                                                      max_alphabetic_char=5, min_alphabetic_char=5)

    assert update_cps_prof_success, f"Getting Password Profile Failed for Profile {cps_prof_id} for core user"
    logger.info(f'Profile {profile_name_cps} successfully updated')
    cps_prof_result, cps_prof_success = ResourceManager.get_password_profile_by_id(core_session, cps_prof_id)
    assert cps_prof_success, f"Getting Password Profile Failed for Profile {cps_prof_id} for core user"
    logger.info(f"Getting Password Profile successfully {cps_prof_id}")
    assert cps_prof_result['MinimumPasswordLength'] == 13, \
        f"Getting Min Password for Profile {cps_prof_id} for core user did not match lens"
    logger.info("Successfully updated minimum password length as 13")
    assert cps_prof_result['MaximumPasswordLength'] == 26, \
        f"Getting Min Password for Profile {cps_prof_id} for core user did not match lens"
    logger.info("Successfully updated minimum password length as 26")
    assert cps_prof_result['AtLeastOneLowercase'] is False, \
        f"Getting Min Password for Profile {cps_prof_id} for core user did not match lens"
    logger.info("Updated At Least One Lower Case successfully as False")
    assert cps_prof_result['AtLeastOneUppercase'] is False, \
        f"Getting Min Password for Profile {cps_prof_id} for core user did not match lens"
    logger.info("Updated At Least One Upper Case successfully as False")
    assert cps_prof_result['AtLeastOneDigit'] is False, \
        f"Getting Min Password for Profile {cps_prof_id} for core user did not match lens"
    logger.info("Updated At Least One Digit successfully as False")
    assert cps_prof_result['ConsecutiveCharRepeatAllowed'] is False, \
        f"Getting Min Password for Profile {cps_prof_id} for core user did not match lens"
    logger.info("Updated Consecutive Char Repeat Allowed successfully as False")
    assert cps_prof_result['AtLeastOneSpecial'] is False, \
        f"Getting Min Password for Profile {cps_prof_id} for core user did not match lens"
    logger.info("Updated At Least One Special Character successfully as False")
    assert cps_prof_result['MinimumAlphabeticCharacterCount'] == 5, \
        f"Getting Min Password for Profile {cps_prof_id} for core user did not match lens"
    logger.info("Updated Minimum Alphabetic Character Count successfully as False")
