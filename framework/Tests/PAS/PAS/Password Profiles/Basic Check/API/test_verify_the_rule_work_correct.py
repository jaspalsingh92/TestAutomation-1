from Shared.API.infrastructure import ResourceManager
import logging
import pytest
import re

logger = logging.getLogger("test")


@pytest.mark.pasapi
@pytest.mark.bhavna
@pytest.mark.pas
def test_verify_rule_work_correct(core_session, create_basic_pass_profile, cleanup_accounts,
                                  pas_setup, remote_users_qty1,
                                  cleanup_password_profile):
    """
    TC C281497: Verify the rule(Min number of alpha characters) work correct
    :param core_session: Authenticates API session
    :param create_basic_pass_profile: Creates a password profile
    :param pas_setup: Creates system and account
    :param remote_users_qty1: Creates account in target system
    :param cleanup_password_profile: Deletes password profile
    :param cleanup_accounts: Deletes account
    """

    accounts_list = cleanup_accounts[0]

    added_system_id, account_id, sys_info = pas_setup
    logger.info(f"System: {sys_info[0]} successfully added with UUID: {added_system_id} and account: {sys_info[4]} "
                f"with UUID: {account_id} associated with it.")
    profile_list = cleanup_password_profile

    # Adding user in target machine
    add_user_in_target_system = remote_users_qty1
    user_password = "Hello123"

    # Adding account in portal
    acc_result, acc_success = ResourceManager.add_account(core_session, add_user_in_target_system[0],
                                                          password=user_password, host=added_system_id,
                                                          ismanaged=True)
    assert acc_success, f"Failed  to add account: {acc_result}"
    logger.info("Successfully added account in system")

    # Cleanup Account
    accounts_list.append(acc_result)

    # Creating Password Profile
    profile = create_basic_pass_profile(core_session, 1)[0]
    profile_name_cps = profile[0]['Name']
    cps_prof_id = profile[0]['_RowKey']

    # Deleting Password Profile
    profile_list.append(cps_prof_id)

    cps_prof_result, cps_prof_success = ResourceManager.get_password_profile_by_id(core_session, cps_prof_id)
    assert cps_prof_success, f"Failed to create Profile due to {cps_prof_result}"
    logger.info(f'System successfully updated with result: {cps_prof_result}')

    # Updating Password Profile
    update_cps_prof_success = ResourceManager.update_password_profile(core_session, cps_prof_id, profile_name_cps,
                                                                      30, 55, one_lwr_case=False, one_upp_case=False,
                                                                      one_digit=False, consecutive_chars=False,
                                                                      one_special_char=False,
                                                                      min_alphabetic_char=50,
                                                                      max_alphabetic_char=5)
    assert update_cps_prof_success, f"Getting Password Profile Failed for Profile {cps_prof_id} for core user"
    logger.info(f'Profile {profile_name_cps} successfully updated')

    cps_prof_result, cps_prof_success = ResourceManager.get_password_profile_by_id(core_session, cps_prof_id)
    assert cps_prof_success, f"Getting Password Profile Failed for Profile {cps_prof_id} for core user"

    assert cps_prof_result['MinimumPasswordLength'] == 30, \
        f"Getting Min Password length for Profile {cps_prof_id} is {cps_prof_result['MinimumPasswordLength']} " \
        f"instead of 30"
    logger.info("Successfully updated minimum password length as 30")
    assert cps_prof_result['MaximumPasswordLength'] == 55, \
        f"Getting Min Password length for Profile {cps_prof_id} is {cps_prof_result['MaximumPasswordLength']} " \
        f"instead of 55"
    logger.info("Successfully updated minimum password length as 50")
    assert cps_prof_result['MinimumAlphabeticCharacterCount'] == 50, \
        f"Getting Min Password length for Profile {cps_prof_id} is " \
        f"{cps_prof_result['MinimumAlphabeticCharacterCount']} instead of 50"
    logger.info("Updated Minimum Alphabetic Character Count successfully")
    update_result, update_success = ResourceManager.update_system(core_session, added_system_id, sys_info[0],
                                                                  sys_info[1],
                                                                  sys_info[2],
                                                                  passwordprofileid=cps_prof_id)
    assert update_success, f"Failed to update system sue to {update_result}"
    logger.info(f"Successfully update system {sys_info[0]}")

    # Rotate Password
    rotate_password_result, rotate_password_success = ResourceManager.rotate_password(core_session, acc_result)
    assert rotate_password_success, f"Failed to rotate password due to {rotate_password_result}"
    logger.info("Rotate password successfully")

    # Checkout Password
    check_out_password_result, check_out_password_success = ResourceManager.check_out_password(core_session, lifetime=1,
                                                                                               accountid=acc_result)
    assert check_out_password_success, f"Failed to checkout password due to {check_out_password_result}"
    logger.info("Password checkout successfully")

    # Getting password value after checkout
    co_password_value = check_out_password_result['Password']

    # Finding all alpha characters after checkout password
    split_co_password = re.findall(r"[^\W\d_]+|\d+", co_password_value)
    get_alpha_characters = ''.join([char for char in split_co_password if not char.isdigit()])
    assert len(get_alpha_characters) >= 50, "Length of Minimum Alphabetic Character Count is less than 50"
    logger.info("Minimum Alphabetic Character Count is greater than or equal to 50")

    # Removing Password Profile from system so that profile can be deleted
    update_result, update_success = ResourceManager.update_system(core_session, added_system_id, sys_info[0],
                                                                  sys_info[1],
                                                                  sys_info[2],
                                                                  passwordprofileid=None)
    assert update_success, f"Failed to remove password profile from system {sys_info[0]}"
    logger.info(f"Successfully removed password profile from system {sys_info[0]}")
