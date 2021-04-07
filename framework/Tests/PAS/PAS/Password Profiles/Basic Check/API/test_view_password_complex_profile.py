from Shared.API.infrastructure import ResourceManager
import logging
import pytest

logger = logging.getLogger("test")


@pytest.mark.pasapi
@pytest.mark.bhavna
@pytest.mark.pas
def test_view_password_profile(core_session):
    """
    Test Case ID: C281493
    Test Case: View Password Complex Profile
    :param core_session: Authenticates API session.
    """
    all_profiles_result, all_profiles_success = ResourceManager.get_profiles(core_session, type='Default',
                                                                             rr_format=True)
    assert all_profiles_success, f"Failed to get profiles list {all_profiles_result}"
    logger.info(f"Successfully get the list of all the profiles {all_profiles_result}")

    # Cisco IOS Profile
    builtin_profile_id = []
    cisco_profile = 'Cisco IOS Profile'
    for row in all_profiles_result['Results']:
        if row['Row']['Name'] == cisco_profile:
            builtin_profile_id.append(row['Row']['ID'])
    cps_prof_result, cps_prof_success = ResourceManager.get_password_profile_by_id(core_session,
                                                                                   builtin_profile_id[0])
    assert cps_prof_result['MinimumPasswordLength'] == 12, \
        f"Getting Min Password for Profile {cisco_profile} did not match"
    logger.info("Minimum password length is 12")
    assert cps_prof_result['MaximumPasswordLength'] == 25, \
        f"Getting Min Password for Profile {cisco_profile} did not match"
    logger.info("Minimum password length is 25")
    assert cps_prof_result['AtLeastOneLowercase'] is True, \
        f"AtLeastOneLowercase value is False"
    logger.info("AtLeastOneLowercase value is True")
    assert cps_prof_result['AtLeastOneUppercase'] is True, \
        f"AtLeastOneUppercase is False"
    logger.info("AtLeastOneUppercase is True")
    assert cps_prof_result['AtLeastOneDigit'] is True, \
        f"AtLeastOneDigit is False"
    logger.info("AtLeastOneDigit is True")
    assert cps_prof_result['AtLeastOneSpecial'] is True, \
        f"AtLeastOneSpecial is False"
    logger.info("AtLeastOneSpecial is True")
    assert cps_prof_result['ConsecutiveCharRepeatAllowed'] is True, \
        f"ConsecutiveCharRepeatAllowed is False"
    logger.info("ConsecutiveCharRepeatAllowed is not selected")

    # Built-in profile should not update
    update_cps_prof_success = ResourceManager.update_password_profile(core_session, builtin_profile_id[0],
                                                                      cisco_profile,
                                                                      13, 26, one_lwr_case=True, one_upp_case=True,
                                                                      one_digit=False, consecutive_chars=False,
                                                                      one_special_char=False,
                                                                      max_alphabetic_char=5, min_alphabetic_char=5)
    assert update_cps_prof_success is False, "Builtin Profile updated"
    logger.info(f'Builtin profile {cisco_profile} failed to update which is expected')

    # Domain Profile
    builtin_profile_id = []
    domain_profile = 'Domain Profile'
    for row in all_profiles_result['Results']:
        if row['Row']['Name'] == domain_profile:
            builtin_profile_id.append(row['Row']['ID'])

    cps_prof_result, cps_prof_success = ResourceManager.get_password_profile_by_id(core_session,
                                                                                   builtin_profile_id[0])
    assert cps_prof_result['MinimumPasswordLength'] == 12, \
        f"Getting Min Password for Profile {domain_profile} did not match"
    logger.info("Minimum password length is 12")
    assert cps_prof_result['MaximumPasswordLength'] == 32, \
        f"Getting Min Password for Profile {domain_profile} did not match"
    logger.info("Minimum password length is 25")
    assert cps_prof_result['AtLeastOneLowercase'] is True, \
        f"AtLeastOneLowercase value is False"
    logger.info("AtLeastOneLowercase value is True")
    assert cps_prof_result['AtLeastOneUppercase'] is True, \
        f"AtLeastOneUppercase is False"
    logger.info("AtLeastOneUppercase is True")
    assert cps_prof_result['AtLeastOneDigit'] is True, \
        f"AtLeastOneDigit is False"
    logger.info("AtLeastOneDigit is True")
    assert cps_prof_result['AtLeastOneSpecial'] is True, \
        f"AtLeastOneSpecial is False"
    logger.info("AtLeastOneSpecial is True")
    assert cps_prof_result['ConsecutiveCharRepeatAllowed'] is True, \
        f"ConsecutiveCharRepeatAllowed is False"
    logger.info("ConsecutiveCharRepeatAllowed is not selected")

    # Built-in profile should not update
    update_cps_prof_success = ResourceManager.update_password_profile(core_session, builtin_profile_id[0],
                                                                      domain_profile,
                                                                      13, 26, one_lwr_case=True, one_upp_case=True,
                                                                      one_digit=False, consecutive_chars=False,
                                                                      one_special_char=False,
                                                                      max_alphabetic_char=5, min_alphabetic_char=5)
    assert update_cps_prof_success is False, "Builtin Profile updated"
    logger.info(f'Builtin profile {domain_profile} failed to update which is expected')

    # Oracle Database Profile
    builtin_profile_id = []
    database_profile = 'Oracle Database Profile'
    for row in all_profiles_result['Results']:
        if row['Row']['Name'] == database_profile:
            builtin_profile_id.append(row['Row']['ID'])

    cps_prof_result, cps_prof_success = ResourceManager.get_password_profile_by_id(core_session,
                                                                                   builtin_profile_id[0])
    assert cps_prof_result['MinimumPasswordLength'] == 12, \
        f"Getting Min Password for Profile {database_profile} did not match"
    logger.info("Minimum password length is 12")
    assert cps_prof_result['MaximumPasswordLength'] == 30, \
        f"Getting Min Password for Profile {database_profile} did not match"
    logger.info("Minimum password length is 25")
    assert cps_prof_result['AtLeastOneLowercase'] is True, \
        f"AtLeastOneLowercase value is False"
    logger.info("AtLeastOneLowercase value is True")
    assert cps_prof_result['AtLeastOneUppercase'] is True, \
        f"AtLeastOneUppercase is False"
    logger.info("AtLeastOneUppercase is True")
    assert cps_prof_result['AtLeastOneDigit'] is True, \
        f"AtLeastOneDigit is False"
    logger.info("AtLeastOneDigit is True")
    assert cps_prof_result['AtLeastOneSpecial'] is True, \
        f"AtLeastOneSpecial is False"
    logger.info("AtLeastOneSpecial is True")
    assert cps_prof_result['ConsecutiveCharRepeatAllowed'] is True, \
        f"ConsecutiveCharRepeatAllowed is False"
    logger.info("ConsecutiveCharRepeatAllowed is not selected")

    # Built-in profile should not update
    update_cps_prof_success = ResourceManager.update_password_profile(core_session, builtin_profile_id[0],
                                                                      database_profile,
                                                                      13, 26, one_lwr_case=True, one_upp_case=True,
                                                                      one_digit=False, consecutive_chars=False,
                                                                      one_special_char=False,
                                                                      max_alphabetic_char=5, min_alphabetic_char=5)
    assert update_cps_prof_success is False, "Builtin Profile updated"
    logger.info(f'Builtin profile {database_profile} failed to update which is expected')

    # Unix Profile
    builtin_profile_id = []
    unix_profile = 'Unix Profile'
    for row in all_profiles_result['Results']:
        if row['Row']['Name'] == unix_profile:
            builtin_profile_id.append(row['Row']['ID'])

    cps_prof_result, cps_prof_success = ResourceManager.get_password_profile_by_id(core_session,
                                                                                   builtin_profile_id[0])
    assert cps_prof_result['MinimumPasswordLength'] == 12, \
        f"Getting Min Password for Profile {unix_profile} did not match"
    logger.info("Minimum password length is 12")
    assert cps_prof_result['MaximumPasswordLength'] == 32, \
        f"Getting Min Password for Profile {unix_profile} did not match"
    logger.info("Minimum password length is 25")
    assert cps_prof_result['AtLeastOneLowercase'] is True, \
        f"AtLeastOneLowercase value is False"
    logger.info("AtLeastOneLowercase value is True")
    assert cps_prof_result['AtLeastOneUppercase'] is True, \
        f"AtLeastOneUppercase is False"
    logger.info("AtLeastOneUppercase is True")
    assert cps_prof_result['AtLeastOneDigit'] is True, \
        f"AtLeastOneDigit is False"
    logger.info("AtLeastOneDigit is True")
    assert cps_prof_result['AtLeastOneSpecial'] is True, \
        f"AtLeastOneSpecial is False"
    logger.info("AtLeastOneSpecial is True")
    assert cps_prof_result['ConsecutiveCharRepeatAllowed'] is True, \
        f"ConsecutiveCharRepeatAllowed is False"
    logger.info("ConsecutiveCharRepeatAllowed is not selected")

    # Built-in profile should not update
    update_cps_prof_success = ResourceManager.update_password_profile(core_session, builtin_profile_id[0],
                                                                      unix_profile,
                                                                      13, 26, one_lwr_case=True, one_upp_case=True,
                                                                      one_digit=False, consecutive_chars=False,
                                                                      one_special_char=False,
                                                                      max_alphabetic_char=5, min_alphabetic_char=5)

    assert update_cps_prof_success is False, "Builtin Profile updated"
    logger.info(f'Builtin profile {unix_profile} failed to update which is expected')

    # Windows Profile
    builtin_profile_id = []
    windows_profile = 'Windows Profile'
    for row in all_profiles_result['Results']:
        if row['Row']['Name'] == windows_profile:
            builtin_profile_id.append(row['Row']['ID'])

    cps_prof_result, cps_prof_success = ResourceManager.get_password_profile_by_id(core_session,
                                                                                   builtin_profile_id[0])
    assert cps_prof_result['MinimumPasswordLength'] == 12, \
        f"Getting Min Password for Profile {windows_profile} did not match"
    logger.info("Minimum password length is 12")
    assert cps_prof_result['MaximumPasswordLength'] == 32, \
        f"Getting Min Password for Profile {windows_profile} did not match"
    logger.info("Minimum password length is 25")
    assert cps_prof_result['AtLeastOneLowercase'] is True, \
        f"AtLeastOneLowercase value is False"
    logger.info("AtLeastOneLowercase value is True")
    assert cps_prof_result['AtLeastOneUppercase'] is True, \
        f"AtLeastOneUppercase is False"
    logger.info("AtLeastOneUppercase is True")
    assert cps_prof_result['AtLeastOneDigit'] is True, \
        f"AtLeastOneDigit is False"
    logger.info("AtLeastOneDigit is True")
    assert cps_prof_result['AtLeastOneSpecial'] is True, \
        f"AtLeastOneSpecial is False"
    logger.info("AtLeastOneSpecial is True")
    assert cps_prof_result['ConsecutiveCharRepeatAllowed'] is True, \
        f"ConsecutiveCharRepeatAllowed is False"
    logger.info("ConsecutiveCharRepeatAllowed is not selected")

    # Built-in profile should not update
    update_cps_prof_success = ResourceManager.update_password_profile(core_session, builtin_profile_id[0],
                                                                      unix_profile,
                                                                      13, 26, one_lwr_case=True, one_upp_case=True,
                                                                      one_digit=False, consecutive_chars=False,
                                                                      one_special_char=False,
                                                                      max_alphabetic_char=5, min_alphabetic_char=5)

    assert update_cps_prof_success is False, "Builtin Profile updated"
    logger.info(f'Builtin profile {windows_profile} failed to update which is expected')

    # IBM i Profile
    builtin_profile_id = []
    ibm_i_profile = 'IBM i Profile'
    for row in all_profiles_result['Results']:
        if row['Row']['Name'] == ibm_i_profile:
            builtin_profile_id.append(row['Row']['ID'])

    cps_prof_result, cps_prof_success = ResourceManager.get_password_profile_by_id(core_session,
                                                                                   builtin_profile_id[0])
    assert cps_prof_result['MinimumPasswordLength'] == 8, \
        f"Getting Min Password for Profile {ibm_i_profile} did not match"
    logger.info("Minimum password length is 12")
    assert cps_prof_result['MaximumPasswordLength'] == 10, \
        f"Getting Min Password for Profile {ibm_i_profile} did not match"
    logger.info("Minimum password length is 25")
    assert cps_prof_result['AtLeastOneLowercase'] is True, \
        f"AtLeastOneLowercase value is False"
    logger.info("AtLeastOneLowercase value is True")
    assert cps_prof_result['AtLeastOneUppercase'] is True, \
        f"AtLeastOneUppercase is False"
    logger.info("AtLeastOneUppercase is True")
    assert cps_prof_result['AtLeastOneDigit'] is True, \
        f"AtLeastOneDigit is False"
    logger.info("AtLeastOneDigit is True")
    assert cps_prof_result['AtLeastOneSpecial'] is True, \
        f"AtLeastOneSpecial is False"
    logger.info("AtLeastOneSpecial is True")
    assert cps_prof_result['ConsecutiveCharRepeatAllowed'] is False, \
        f"ConsecutiveCharRepeatAllowed is True"
    logger.info("ConsecutiveCharRepeatAllowed is selected")

    # Built-in profile should not update
    update_cps_prof_success = ResourceManager.update_password_profile(core_session, builtin_profile_id[0],
                                                                      ibm_i_profile,
                                                                      13, 26, one_lwr_case=True, one_upp_case=True,
                                                                      one_digit=False, consecutive_chars=False,
                                                                      one_special_char=False,
                                                                      max_alphabetic_char=5, min_alphabetic_char=5)

    assert update_cps_prof_success is False, "Builtin Profile updated"
    logger.info(f'Builtin profile {ibm_i_profile} failed to update which is expected')

    # HP NonStop Profile
    builtin_profile_id = []
    hp_profile = 'HP NonStop Profile'
    for row in all_profiles_result['Results']:
        if row['Row']['Name'] == hp_profile:
            builtin_profile_id.append(row['Row']['ID'])

    cps_prof_result, cps_prof_success = ResourceManager.get_password_profile_by_id(core_session,
                                                                                   builtin_profile_id[0])
    assert cps_prof_result['MinimumPasswordLength'] == 8, \
        f"Getting Min Password for Profile {hp_profile} did not match"
    logger.info("Minimum password length is 12")
    assert cps_prof_result['MaximumPasswordLength'] == 8, \
        f"Getting Min Password for Profile {hp_profile} did not match"
    logger.info("Minimum password length is 25")
    assert cps_prof_result['AtLeastOneLowercase'] is True, \
        f"AtLeastOneLowercase value is False"
    logger.info("AtLeastOneLowercase value is True")
    assert cps_prof_result['AtLeastOneUppercase'] is True, \
        f"AtLeastOneUppercase is False"
    logger.info("AtLeastOneUppercase is True")
    assert cps_prof_result['AtLeastOneDigit'] is True, \
        f"AtLeastOneDigit is False"
    logger.info("AtLeastOneDigit is True")
    assert cps_prof_result['AtLeastOneSpecial'] is True, \
        f"AtLeastOneSpecial is False"
    logger.info("AtLeastOneSpecial is True")
    assert cps_prof_result['ConsecutiveCharRepeatAllowed'] is True, \
        f"ConsecutiveCharRepeatAllowed is False"
    logger.info("ConsecutiveCharRepeatAllowed is not selected")

    # Built-in profile should not update
    update_cps_prof_success = ResourceManager.update_password_profile(core_session, builtin_profile_id[0],
                                                                      hp_profile,
                                                                      13, 26, one_lwr_case=True, one_upp_case=True,
                                                                      one_digit=False, consecutive_chars=False,
                                                                      one_special_char=False,
                                                                      max_alphabetic_char=5, min_alphabetic_char=5)

    assert update_cps_prof_success is False, "Builtin Profile updated"
    logger.info(f'Builtin profile {hp_profile} failed to update which is expected')

    # SQL Server Profile
    builtin_profile_id = []
    sql_profile = 'SQL Server Profile'
    for row in all_profiles_result['Results']:
        if row['Row']['Name'] == sql_profile:
            builtin_profile_id.append(row['Row']['ID'])

    cps_prof_result, cps_prof_success = ResourceManager.get_password_profile_by_id(core_session,
                                                                                   builtin_profile_id[0])
    assert cps_prof_result['MinimumPasswordLength'] == 12, \
        f"Getting Min Password for Profile {sql_profile} did not match"
    logger.info("Minimum password length is 12")
    assert cps_prof_result['MaximumPasswordLength'] == 32, \
        f"Getting Min Password for Profile {sql_profile} did not match"
    logger.info("Minimum password length is 25")
    assert cps_prof_result['AtLeastOneLowercase'] is True, \
        f"AtLeastOneLowercase value is False"
    logger.info("AtLeastOneLowercase value is True")
    assert cps_prof_result['AtLeastOneUppercase'] is True, \
        f"AtLeastOneUppercase is False"
    logger.info("AtLeastOneUppercase is True")
    assert cps_prof_result['AtLeastOneDigit'] is True, \
        f"AtLeastOneDigit is False"
    logger.info("AtLeastOneDigit is True")
    assert cps_prof_result['AtLeastOneSpecial'] is True, \
        f"AtLeastOneSpecial is False"
    logger.info("AtLeastOneSpecial is True")
    assert cps_prof_result['ConsecutiveCharRepeatAllowed'] is True, \
        f"ConsecutiveCharRepeatAllowed is False"
    logger.info("ConsecutiveCharRepeatAllowed is not selected")

    # Built-in profile should not update
    update_cps_prof_success = ResourceManager.update_password_profile(core_session, builtin_profile_id[0],
                                                                      sql_profile,
                                                                      13, 26, one_lwr_case=True, one_upp_case=True,
                                                                      one_digit=False, consecutive_chars=False,
                                                                      one_special_char=False,
                                                                      max_alphabetic_char=5, min_alphabetic_char=5)
    assert update_cps_prof_success is False, "Builtin Profile updated"
    logger.info(f'Builtin profile {sql_profile} failed to update which is expected')

    # VMware VMkernel Profile
    builtin_profile_id = []
    vm_ware_profile = 'VMware VMkernel Profile'
    for row in all_profiles_result['Results']:
        if row['Row']['Name'] == vm_ware_profile:
            builtin_profile_id.append(row['Row']['ID'])

    cps_prof_result, cps_prof_success = ResourceManager.get_password_profile_by_id(core_session,
                                                                                   builtin_profile_id[0])
    assert cps_prof_result['MinimumPasswordLength'] == 12, \
        f"Getting Min Password for Profile {vm_ware_profile} did not match"
    logger.info("Minimum password length is 12")
    assert cps_prof_result['MaximumPasswordLength'] == 39, \
        f"Getting Min Password for Profile {vm_ware_profile} did not match"
    logger.info("Minimum password length is 25")
    assert cps_prof_result['AtLeastOneLowercase'] is True, \
        f"AtLeastOneLowercase value is False"
    logger.info("AtLeastOneLowercase value is True")
    assert cps_prof_result['AtLeastOneUppercase'] is True, \
        f"AtLeastOneUppercase is False"
    logger.info("AtLeastOneUppercase is True")
    assert cps_prof_result['AtLeastOneDigit'] is True, \
        f"AtLeastOneDigit is False"
    logger.info("AtLeastOneDigit is True")
    assert cps_prof_result['AtLeastOneSpecial'] is True, \
        f"AtLeastOneSpecial is False"
    logger.info("AtLeastOneSpecial is True")
    assert cps_prof_result['ConsecutiveCharRepeatAllowed'] is True, \
        f"ConsecutiveCharRepeatAllowed is False"
    logger.info("ConsecutiveCharRepeatAllowed is not selected")

    # Built-in profile should not update
    update_cps_prof_success = ResourceManager.update_password_profile(core_session, builtin_profile_id[0],
                                                                      vm_ware_profile,
                                                                      13, 26, one_lwr_case=True, one_upp_case=True,
                                                                      one_digit=False, consecutive_chars=False,
                                                                      one_special_char=False,
                                                                      max_alphabetic_char=5, min_alphabetic_char=5)
    assert update_cps_prof_success is False, "Builtin Profile updated"
    logger.info(f'Builtin profile {vm_ware_profile} failed to update which is expected')

    # SAP ASE Profile
    builtin_profile_id = []
    sap_profile = 'SAP ASE Profile'
    for row in all_profiles_result['Results']:
        if row['Row']['Name'] == sap_profile:
            builtin_profile_id.append(row['Row']['ID'])

    cps_prof_result, cps_prof_success = ResourceManager.get_password_profile_by_id(core_session,
                                                                                   builtin_profile_id[0])
    assert cps_prof_result['MinimumPasswordLength'] == 12, \
        f"Getting Min Password for Profile {sap_profile} did not match"
    logger.info("Minimum password length is 12")
    assert cps_prof_result['MaximumPasswordLength'] == 30, \
        f"Getting Min Password for Profile {sap_profile} did not match"
    logger.info("Minimum password length is 25")
    assert cps_prof_result['AtLeastOneLowercase'] is True, \
        f"AtLeastOneLowercase value is False"
    logger.info("AtLeastOneLowercase value is True")
    assert cps_prof_result['AtLeastOneUppercase'] is True, \
        f"AtLeastOneUppercase is False"
    logger.info("AtLeastOneUppercase is True")
    assert cps_prof_result['AtLeastOneDigit'] is True, \
        f"AtLeastOneDigit is False"
    logger.info("AtLeastOneDigit is True")
    assert cps_prof_result['AtLeastOneSpecial'] is True, \
        f"AtLeastOneSpecial is False"
    logger.info("AtLeastOneSpecial is True")
    assert cps_prof_result['ConsecutiveCharRepeatAllowed'] is True, \
        f"ConsecutiveCharRepeatAllowed is False"
    logger.info("ConsecutiveCharRepeatAllowed is not selected")

    # Built-in profile should not update
    update_cps_prof_success = ResourceManager.update_password_profile(core_session, builtin_profile_id[0],
                                                                      sap_profile,
                                                                      13, 26, one_lwr_case=True, one_upp_case=True,
                                                                      one_digit=False, consecutive_chars=False,
                                                                      one_special_char=False,
                                                                      max_alphabetic_char=5, min_alphabetic_char=5)
    assert update_cps_prof_success is False, "Builtin Profile updated"
    logger.info(f'Builtin profile {sap_profile} failed to update which is expected')

    # Palo Alto Networks PAN-OS Profile
    builtin_profile_id = []
    palo_profile = 'Palo Alto Networks PAN-OS Profile'
    for row in all_profiles_result['Results']:
        if row['Row']['Name'] == palo_profile:
            builtin_profile_id.append(row['Row']['ID'])

    cps_prof_result, cps_prof_success = ResourceManager.get_password_profile_by_id(core_session,
                                                                                   builtin_profile_id[0])
    assert cps_prof_result['MinimumPasswordLength'] == 12, \
        f"Getting Min Password for Profile {palo_profile} did not match"
    logger.info("Minimum password length is 12")
    assert cps_prof_result['MaximumPasswordLength'] == 31, \
        f"Getting Min Password for Profile {palo_profile} did not match"
    logger.info("Minimum password length is 25")
    assert cps_prof_result['AtLeastOneLowercase'] is True, \
        f"AtLeastOneLowercase value is False"
    logger.info("AtLeastOneLowercase value is True")
    assert cps_prof_result['AtLeastOneUppercase'] is True, \
        f"AtLeastOneUppercase is False"
    logger.info("AtLeastOneUppercase is True")
    assert cps_prof_result['AtLeastOneDigit'] is True, \
        f"AtLeastOneDigit is False"
    logger.info("AtLeastOneDigit is True")
    assert cps_prof_result['AtLeastOneSpecial'] is True, \
        f"AtLeastOneSpecial is False"
    logger.info("AtLeastOneSpecial is True")
    assert cps_prof_result['ConsecutiveCharRepeatAllowed'] is True, \
        f"ConsecutiveCharRepeatAllowed is False"
    logger.info("ConsecutiveCharRepeatAllowed is not selected")

    # Built-in profile should not update
    update_cps_prof_success = ResourceManager.update_password_profile(core_session, builtin_profile_id[0],
                                                                      palo_profile,
                                                                      13, 26, one_lwr_case=True, one_upp_case=True,
                                                                      one_digit=False, consecutive_chars=False,
                                                                      one_special_char=False,
                                                                      max_alphabetic_char=5, min_alphabetic_char=5)
    assert update_cps_prof_success is False, "Builtin Profile updated"
    logger.info(f'Builtin profile {palo_profile} failed to update which is expected')

    # Check Point Gaia Profile
    builtin_profile_id = []
    check_point_gaia_profile = 'Check Point Gaia Profile'
    for row in all_profiles_result['Results']:
        if row['Row']['Name'] == check_point_gaia_profile:
            builtin_profile_id.append(row['Row']['ID'])

    cps_prof_result, cps_prof_success = ResourceManager.get_password_profile_by_id(core_session,
                                                                                   builtin_profile_id[0])
    assert cps_prof_result['MinimumPasswordLength'] == 12, \
        f"Getting Min Password for Profile {check_point_gaia_profile} did not match"
    logger.info("Minimum password length is 12")
    assert cps_prof_result['MaximumPasswordLength'] == 32, \
        f"Getting Min Password for Profile {check_point_gaia_profile} did not match"
    logger.info("Minimum password length is 25")
    assert cps_prof_result['AtLeastOneLowercase'] is True, \
        f"AtLeastOneLowercase value is False"
    logger.info("AtLeastOneLowercase value is True")
    assert cps_prof_result['AtLeastOneUppercase'] is True, \
        f"AtLeastOneUppercase is False"
    logger.info("AtLeastOneUppercase is True")
    assert cps_prof_result['AtLeastOneDigit'] is True, \
        f"AtLeastOneDigit is False"
    logger.info("AtLeastOneDigit is True")
    assert cps_prof_result['AtLeastOneSpecial'] is True, \
        f"AtLeastOneSpecial is False"
    logger.info("AtLeastOneSpecial is True")
    assert cps_prof_result['ConsecutiveCharRepeatAllowed'] is False, \
        f"ConsecutiveCharRepeatAllowed is True"
    logger.info("ConsecutiveCharRepeatAllowed is selected")

    # Built-in profile should not update
    update_cps_prof_success = ResourceManager.update_password_profile(core_session, builtin_profile_id[0],
                                                                      check_point_gaia_profile,
                                                                      13, 26, one_lwr_case=True, one_upp_case=True,
                                                                      one_digit=False, consecutive_chars=False,
                                                                      one_special_char=False,
                                                                      max_alphabetic_char=5, min_alphabetic_char=5)
    assert update_cps_prof_success is False, "Builtin Profile updated"
    logger.info(f'Builtin profile {check_point_gaia_profile} failed to update which is expected')

    # F5 Networks BIG-IP Profile
    builtin_profile_id = []
    f5_networks_profile = 'F5 Networks BIG-IP Profile'
    for row in all_profiles_result['Results']:
        if row['Row']['Name'] == f5_networks_profile:
            builtin_profile_id.append(row['Row']['ID'])

    cps_prof_result, cps_prof_success = ResourceManager.get_password_profile_by_id(core_session,
                                                                                   builtin_profile_id[0])
    assert cps_prof_result['MinimumPasswordLength'] == 12, \
        f"Getting Min Password for Profile {f5_networks_profile} did not match"
    logger.info("Minimum password length is 12")
    assert cps_prof_result['MaximumPasswordLength'] == 31, \
        f"Getting Min Password for Profile {f5_networks_profile} did not match"
    logger.info("Minimum password length is 25")
    assert cps_prof_result['AtLeastOneLowercase'] is True, \
        f"AtLeastOneLowercase value is False"
    logger.info("AtLeastOneLowercase value is True")
    assert cps_prof_result['AtLeastOneUppercase'] is True, \
        f"AtLeastOneUppercase is False"
    logger.info("AtLeastOneUppercase is True")
    assert cps_prof_result['AtLeastOneDigit'] is True, \
        f"AtLeastOneDigit is False"
    logger.info("AtLeastOneDigit is True")
    assert cps_prof_result['AtLeastOneSpecial'] is True, \
        f"AtLeastOneSpecial is False"
    logger.info("AtLeastOneSpecial is True")
    assert cps_prof_result['ConsecutiveCharRepeatAllowed'] is True, \
        f"ConsecutiveCharRepeatAllowed is False"
    logger.info("ConsecutiveCharRepeatAllowed is not selected")

    # Built-in profile should not update
    update_cps_prof_success = ResourceManager.update_password_profile(core_session, builtin_profile_id[0],
                                                                      f5_networks_profile,
                                                                      13, 26, one_lwr_case=True, one_upp_case=True,
                                                                      one_digit=False, consecutive_chars=False,
                                                                      one_special_char=False,
                                                                      max_alphabetic_char=5, min_alphabetic_char=5)
    assert update_cps_prof_success is False, "Builtin Profile updated"
    logger.info(f'Builtin profile {f5_networks_profile} failed to update which is expected')

    # Juniper Junos Profile
    builtin_profile_id = []
    juniper_profile = 'Juniper Junos Profile'
    for row in all_profiles_result['Results']:
        if row['Row']['Name'] == juniper_profile:
            builtin_profile_id.append(row['Row']['ID'])

    cps_prof_result, cps_prof_success = ResourceManager.get_password_profile_by_id(core_session,
                                                                                   builtin_profile_id[0])
    assert cps_prof_result['MinimumPasswordLength'] == 12, \
        f"Getting Min Password for Profile {juniper_profile} did not match"
    logger.info("Minimum password length is 12")
    assert cps_prof_result['MaximumPasswordLength'] == 20, \
        f"Getting Min Password for Profile {juniper_profile} did not match"
    logger.info("Minimum password length is 25")
    assert cps_prof_result['AtLeastOneLowercase'] is True, \
        f"AtLeastOneLowercase value is False"
    logger.info("AtLeastOneLowercase value is True")
    assert cps_prof_result['AtLeastOneUppercase'] is True, \
        f"AtLeastOneUppercase is False"
    logger.info("AtLeastOneUppercase is True")
    assert cps_prof_result['AtLeastOneDigit'] is True, \
        f"AtLeastOneDigit is False"
    logger.info("AtLeastOneDigit is True")
    assert cps_prof_result['AtLeastOneSpecial'] is True, \
        f"AtLeastOneSpecial is False"
    logger.info("AtLeastOneSpecial is True")
    assert cps_prof_result['ConsecutiveCharRepeatAllowed'] is True, \
        f"ConsecutiveCharRepeatAllowed is False"
    logger.info("ConsecutiveCharRepeatAllowed is not selected")

    # Built-in profile should not update
    update_cps_prof_success = ResourceManager.update_password_profile(core_session, builtin_profile_id[0],
                                                                      juniper_profile,
                                                                      13, 26, one_lwr_case=True, one_upp_case=True,
                                                                      one_digit=False, consecutive_chars=False,
                                                                      one_special_char=False,
                                                                      max_alphabetic_char=5, min_alphabetic_char=5)
    assert update_cps_prof_success is False, "Builtin Profile updated"
    logger.info(f'Builtin profile {juniper_profile} failed to update which is expected')

    # Cisco AsyncOS Profile
    builtin_profile_id = []
    cisco_asyncos_profile = 'Cisco AsyncOS Profile'
    for row in all_profiles_result['Results']:
        if row['Row']['Name'] == cisco_asyncos_profile:
            builtin_profile_id.append(row['Row']['ID'])

    cps_prof_result, cps_prof_success = ResourceManager.get_password_profile_by_id(core_session,
                                                                                   builtin_profile_id[0])
    assert cps_prof_result['MinimumPasswordLength'] == 12, \
        f"Getting Min Password for Profile {cisco_asyncos_profile} did not match"
    logger.info("Minimum password length is 12")
    assert cps_prof_result['MaximumPasswordLength'] == 32, \
        f"Getting Min Password for Profile {cisco_asyncos_profile} did not match"
    logger.info("Minimum password length is 25")
    assert cps_prof_result['AtLeastOneLowercase'] is True, \
        f"AtLeastOneLowercase value is False"
    logger.info("AtLeastOneLowercase value is True")
    assert cps_prof_result['AtLeastOneUppercase'] is True, \
        f"AtLeastOneUppercase is False"
    logger.info("AtLeastOneUppercase is True")
    assert cps_prof_result['AtLeastOneDigit'] is True, \
        f"AtLeastOneDigit is False"
    logger.info("AtLeastOneDigit is True")
    assert cps_prof_result['AtLeastOneSpecial'] is True, \
        f"AtLeastOneSpecial is False"
    logger.info("AtLeastOneSpecial is True")
    assert cps_prof_result['ConsecutiveCharRepeatAllowed'] is True, \
        f"ConsecutiveCharRepeatAllowed is False"
    logger.info("ConsecutiveCharRepeatAllowed is not selected")

    # Built-in profile should not update
    update_cps_prof_success = ResourceManager.update_password_profile(core_session, builtin_profile_id[0],
                                                                      cisco_asyncos_profile,
                                                                      13, 26, one_lwr_case=True, one_upp_case=True,
                                                                      one_digit=False, consecutive_chars=False,
                                                                      one_special_char=False,
                                                                      max_alphabetic_char=5, min_alphabetic_char=5)
    assert update_cps_prof_success is False, "Builtin Profile updated"
    logger.info(f'Builtin profile {cisco_asyncos_profile} failed to update which is expected')

    # Cisco NX-OS Profile
    builtin_profile_id = []
    cisco_nxos_profile = 'Cisco NX-OS Profile'
    for row in all_profiles_result['Results']:
        if row['Row']['Name'] == cisco_nxos_profile:
            builtin_profile_id.append(row['Row']['ID'])

    cps_prof_result, cps_prof_success = ResourceManager.get_password_profile_by_id(core_session,
                                                                                   builtin_profile_id[0])
    assert cps_prof_result['MinimumPasswordLength'] == 12, \
        f"Getting Min Password for Profile {cisco_nxos_profile} did not match"
    logger.info("Minimum password length is 12")
    assert cps_prof_result['MaximumPasswordLength'] == 32, \
        f"Getting Min Password for Profile {cisco_nxos_profile} did not match"
    logger.info("Minimum password length is 25")
    assert cps_prof_result['AtLeastOneLowercase'] is True, \
        f"AtLeastOneLowercase value is False"
    logger.info("AtLeastOneLowercase value is True")
    assert cps_prof_result['AtLeastOneUppercase'] is True, \
        f"AtLeastOneUppercase is False"
    logger.info("AtLeastOneUppercase is True")
    assert cps_prof_result['AtLeastOneDigit'] is True, \
        f"AtLeastOneDigit is False"
    logger.info("AtLeastOneDigit is True")
    assert cps_prof_result['AtLeastOneSpecial'] is True, \
        f"AtLeastOneSpecial is False"
    logger.info("AtLeastOneSpecial is True")
    assert cps_prof_result['ConsecutiveCharRepeatAllowed'] is True, \
        f"ConsecutiveCharRepeatAllowed is False"
    logger.info("ConsecutiveCharRepeatAllowed is not selected")

    # Built-in profile should not update
    update_cps_prof_success = ResourceManager.update_password_profile(core_session, builtin_profile_id[0],
                                                                      cisco_nxos_profile,
                                                                      13, 26, one_lwr_case=True, one_upp_case=True,
                                                                      one_digit=False, consecutive_chars=False,
                                                                      one_special_char=False,
                                                                      max_alphabetic_char=5, min_alphabetic_char=5)
    assert update_cps_prof_success is False, "Builtin Profile updated"
    logger.info(f'Builtin profile {cisco_nxos_profile} failed to update which is expected')
