import pytest
import logging
from Shared.API.infrastructure import ResourceManager
from Shared.UI.Centrify.SubSelectors.forms import ComboBoxValue, CheckedCheckbox, \
    ComboboxWithNameStartsWith, ReadOnlyTextField
from Shared.UI.Centrify.SubSelectors.grids import SortedAscendingOrderElement
from Shared.UI.Centrify.SubSelectors.navigation import RenderedTab
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.ui
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi_ui
def test_check_password_profile_in_order(core_session, pas_windows_setup, core_admin_ui):
    """
    Test case: C1629
    :param core_session: Centrify session
    :param pas_windows_setup: Creating windows system.
    :param core_admin_ui: Centrify admin Ui session
    """
    ui = core_admin_ui
    system_id, account_id, sys_info, connector_id, user_password = pas_windows_setup()
    ui.navigate("Settings", "Resources", "Password Profiles")
    expected_category_list = ['All Profiles', 'Built-In Profiles', 'Custom Profiles']
    actual_category_list = ui.get_select_option_list(ComboBoxValue("All Profiles"))
    # Checking the profile types list.
    assert expected_category_list == actual_category_list, "Profiles are not listed in Categories"
    ui.expect(SortedAscendingOrderElement("Name"), "Element is not in Accending order")
    logger.info("Name element is in Accending order")
    ui.navigate('Resources', 'Systems')
    ui.search(sys_info[0])
    ui.click_row(sys_info[0])
    ui.tab('Advanced')
    expected_category_list = ['--', 'Windows Profile', '- Add New Profile -']
    actual_category_list = ui.get_select_option_list("PasswordProfileID")
    # Checking the password complexity profile for windows.
    if expected_category_list in actual_category_list:
        assert actual_category_list, "Profiles are not listed in Categories"
    logger.info(f"Password complexity profiles for the system{sys_info[0]} are {actual_category_list}")


# TODO UI needs to give tests a better selector as current name is "undefined". Change here after UI updated.
@pytest.mark.api_ui
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi_ui
def test_add_newly_password_complex_profile(core_session, core_admin_ui):
    """
        Test case: C1630
        :param core_session: Centrify session
        :param core_admin_ui: Centrify admin Ui session
        """
    ui = core_admin_ui
    ui.navigate("Settings", "Resources", "Password Profiles")
    ui.launch_modal("Add", modal_title="Password Complexity Profile")
    profile_name = f'testprofilename{guid()}'
    profile_description = "Test Description"
    ui.input("Name", profile_name)
    ui.input("Description", profile_description)
    ui.input("MinimumPasswordLength", 12)
    ui.input("MaximumPasswordLength", 32)
    check_atleast_one_digit_repeat = ui.check_exists(CheckedCheckbox("AtLeastOneDigit"))
    # checking At least One Digit in the password profile option exists in ui.
    assert check_atleast_one_digit_repeat, "Expecting checkbox for atLeast one digit repeat not appeared"
    logger.info("Atleast one digit option showed")
    ui.check("ConsecutiveCharRepeatAllowed")
    ui.check("undefined")
    ui.input("MaximumCharOccurrenceCount", 3)
    ui.check("undefined")
    ui.check("undefined")
    ui.input("MinimumAlphabeticCharacterCount", 2)
    ui.input("MinimumNonAlphabeticCharacterCount", 2)
    ui.close_modal("Save")
    # Getting all the profiles in password complexity profile.
    all_profiles, a = ResourceManager.get_profiles(core_session, type="All", rr_format=True)
    cloned_builtin_profile_id = []
    for row in all_profiles['Results']:
        if row['Row']['Name'] == profile_name:
            cloned_builtin_profile_id.append(row['Row']['ProfileType'])
    assert row['Row']['ProfileType'] == "UserDefined", f"Profile created successfully with id " \
                                                       f"{cloned_builtin_profile_id}"
    logger.info(f"Created profile_name {profile_name} successfully with {cloned_builtin_profile_id}")


@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi_ui
def test_modify_existing_password_complex_profiles(core_session, create_basic_pass_profile):
    """
        Test case: C1631
        :param core_session: Centrify session
        :param create_basic_pass_profile: Created a basic password complexity profile.
        """
    profile = create_basic_pass_profile(core_session, 1, 8)[0]
    cps_prof_id = profile[0]['_RowKey']
    profile_name_cps = profile[0]['Name']
    # Getting the password profile by id
    cps_prof_result, cps_prof_succcess = ResourceManager.get_password_profile_by_id(core_session, cps_prof_id)
    assert cps_prof_succcess, f"Getting Password Profile Failed for Profile {cps_prof_id} for core user"
    logger.info(f"Password profile created successfully with {cps_prof_result}")
    # updates the exiting password profile.
    update_cps_prof_success = ResourceManager.update_password_profile(core_session, cps_prof_id, profile_name_cps,
                                                                      min_pwd_len=13, max_pwd_len=26,
                                                                      special_char_set="!#$%&()*",
                                                                      min_alphabetic_char=5, max_alphabetic_char=5)
    assert update_cps_prof_success, f"Getting Password Profile Failed for Profile {cps_prof_id} for core user"
    # Getting the password profile by id
    cps_prof_result, cps_prof_succcess = ResourceManager.get_password_profile_by_id(core_session, cps_prof_id)
    assert cps_prof_succcess, f"Getting Password Profile Failed for Profile {cps_prof_id} for core user"
    expected_profile_update_values = [13, 26, '!#$%&()*', 5, 5]
    actual_profile_update_values = [cps_prof_result['MinimumPasswordLength'], cps_prof_result['MaximumPasswordLength'],
                                    cps_prof_result['SpecialCharSet'],
                                    cps_prof_result['MinimumAlphabeticCharacterCount'],
                                    cps_prof_result['MinimumNonAlphabeticCharacterCount']]
    # Checking the password complexity profile field's value.
    assert expected_profile_update_values == actual_profile_update_values, f"Getting Password profile update values " \
                                                                           f"for Profile {cps_prof_id} for core user " \
                                                                           f"did not match values " \
                                                                           f"{actual_profile_update_values}"
    logger.info(f"Password profile updated successfully with {cps_prof_result}")


@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi_ui
def test_view_builtin_password_complex_profile(core_session, core_admin_ui):
    """
        Test case: C1632
        :param core_session: Centrify session
        :param core_admin_ui: Centrify admin Ui session
        """
    ui = core_admin_ui
    ui.navigate("Settings", "Resources", "Password Profiles")
    ResourceManager.get_profiles(core_session, type="Default", rr_format=True)
    ui.select_option(name=ComboboxWithNameStartsWith("jsutil-datacombo"), item_name="Built-In Profiles")
    ui.action("View Profile", "Windows")

    # Viewing the Built-in windows profile Checking Minimum password Length, Maximum password Length,
    # Minium Alphabetic Character Count, Minimum NonAlphabetic Character Count
    ui.expect(ReadOnlyTextField('Name'), "Name is not editable")
    ui.expect(ReadOnlyTextField('MinimumPasswordLength'), "Minimum Password Length is not editable")
    ui.expect(ReadOnlyTextField('MaximumPasswordLength'), "Maximum Password Length is not editable")
    ui.expect(ReadOnlyTextField('MinimumAlphabeticCharacterCount'),
              "Minimum Alphabetic Character Count is not editable")
    ui.expect(ReadOnlyTextField('MinimumNonAlphabeticCharacterCount'),
              "Minimum Non Alphabetic Character Count is not editable")
    ui.close_modal("Close", modal_title="Password Complexity Profile")
    logger.info("Password profile for windows is not editable as expected")
    ui.switch_context(RenderedTab("Password Profiles"))

    # viewing the Database built-in profile. Checking Minimum password Length, Maximum password Length,
    # Minium Alphabetic Character Count, Minimum NonAlphabetic Character Count
    ui.action("View Profile", "Default profile for Oracle Database services")
    ui.expect(ReadOnlyTextField('Name'), "Name is not editable")

    ui.expect(ReadOnlyTextField('MinimumPasswordLength'), "Minimum Password Length is not editable")
    ui.expect(ReadOnlyTextField('MaximumPasswordLength'), "Maximum Password Length is not editable")
    ui.expect(ReadOnlyTextField('MinimumAlphabeticCharacterCount'),
              "Minimum Alphabetic Character Count is not editable")
    ui.expect(ReadOnlyTextField('MinimumNonAlphabeticCharacterCount'),
              "Minimum Non Alphabetic Character Count is not editable")
    ui.close_modal("Close", modal_title="Password Complexity Profile")
    logger.info("Password profile for windows is not editable as expected")
    ui.switch_context(RenderedTab("Password Profiles"))

    # viewing the Active directory built-in profile. Checking Minimum password Length, Maximum password Length,
    # Minium Alphabetic Character Count, Minimum NonAlphabetic Character Count, Read Only Text Field
    ui.action("View Profile", "Default profile for Active Directory domains")
    ui.expect(ReadOnlyTextField('Name'), "Name is not editable")
    ui.expect(ReadOnlyTextField('MinimumPasswordLength'), "Minimum Password Length is not editable")
    ui.expect(ReadOnlyTextField('MaximumPasswordLength'), "Maximum Password Length is not editable")
    ui.expect(ReadOnlyTextField('MinimumAlphabeticCharacterCount'),
              "Minimum Alphabetic Character Count is not editable")
    ui.expect(ReadOnlyTextField('MinimumNonAlphabeticCharacterCount'),
              "Minimum Non Alphabetic Character Count is not editable")
    ui.close_modal("Close", modal_title="Password Complexity Profile")
    logger.info("Password profile for domains is not editable as expected")


@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi_ui
def test_clone_password_complex_profiles(core_session, core_admin_ui, create_basic_pass_profile,
                                         create_clone_windows_pass_profile, create_clone_custom_pass_profile):
    """ :param : C1633
        :param core_session: Centrify session
        :param core_admin_ui: Creates random user and login in browser.
        :param create_basic_pass_profile: Created a basic password complexity profile.
        :param create_clone_windows_pass_profile: Creates windows password profile
        :param create_clone_custom_pass_profile: Creates custom password profile.
        """
    ui = core_admin_ui
    current_tenant_id = core_session.__dict__["tenant_id"]
    ui.navigate("Settings", "Resources", "Password Profiles")
    profile = create_basic_pass_profile(core_session, 1, 8)[0]
    cps_prof_id = profile[0]['_RowKey']
    profile_name_cps = profile[0]['Name']
    custom_profile_name_clone = f"{profile_name_cps} (Cloned)"
    cps_prof_result, cps_prof_succcess = ResourceManager.get_password_profile_by_id(core_session, cps_prof_id)
    assert cps_prof_succcess, f"Getting Password Profile Failed for Profile {cps_prof_id} for core user"
    # Checking the cloned password complexity profile exists after cloned.
    logger.info(f"Password profile created successfully with {cps_prof_result}")
    profile_clone = create_clone_windows_pass_profile(core_session)
    cloned_profiles_windows = list(profile_clone[0])
    cloned_builtin_profile_id = cloned_profiles_windows[0]['_RowKey']
    assert cloned_builtin_profile_id is not None, f"Cloned built-in password profile created successfully with id " \
                                                  f"{cloned_builtin_profile_id}"
    logger.info(
        f"Cloned built-in password profile created successfully {cloned_profiles_windows} with id "
        f"{cloned_builtin_profile_id}")
    # Checking the cloned password complexity profile exists after cloned.
    create_clone_custom_profile = create_clone_custom_pass_profile(core_session,
                                                                   name=custom_profile_name_clone,
                                                                   tenant_id=current_tenant_id)

    cloned_profiles = list(create_clone_custom_profile[0])
    cloned_profile_id = cloned_profiles[0]['_RowKey']
    assert cloned_profile_id is not None, f"Cloned password profile created successfully with id {cloned_profile_id}"
    logger.info(f"Cloned Password profile created successfully {cloned_profiles} with id {cloned_profile_id}")


@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi_ui
def test_delete_password_complex_profile(core_session, core_admin_ui, create_basic_pass_profile):
    """
        Test case: C1634
        :param core_session: Centrify session
        :param core_admin_ui: Creates random user and login in browser.
        :param create_basic_pass_profile: Created a basic password complexity profile.
        """
    ui = core_admin_ui
    ui.navigate("Settings", "Resources", "Password Profiles")
    profile = create_basic_pass_profile(core_session, 1, 8)[0]
    cps_prof_id = profile[0]['_RowKey']
    profile_name_cps = profile[0]['Name']
    cps_prof_result, cps_prof_succcess = ResourceManager.get_password_profile_by_id(core_session, cps_prof_id)
    # Checking the created custom password complexity profile.
    assert cps_prof_succcess, f"Getting Password Profile Failed for Profile {cps_prof_id} for core user"
    logger.info(f"Password profile created successfully with {cps_prof_result}")
    profile_delete = ResourceManager.delete_password_profile(core_session, cps_prof_id)
    # Deleting the custom password complexity profile.
    assert profile_delete, f"Password complexity profile {profile_name_cps} not deleted"
    logger.info(f"Password complexity profile {profile_name_cps} deleted successfully")
