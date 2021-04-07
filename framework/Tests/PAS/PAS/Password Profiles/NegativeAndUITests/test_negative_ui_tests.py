import pytest
import logging
from Shared.API.infrastructure import ResourceManager
from Shared.UI.Centrify.SubSelectors.forms import InvalidInputAlertWithStrings
from Shared.UI.Centrify.SubSelectors.grids import GridCell
from Shared.UI.Centrify.SubSelectors.modals import ConfirmModal, ErrorModal, Modal
from Shared.UI.Centrify.SubSelectors.navigation import ActiveMainContentArea
from Shared.UI.Centrify.selectors import Div, Anchor, Span
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.ui
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi_ui
def test_create_existing_password_complexity_profile(core_session, core_admin_ui, create_basic_pass_profile):
    """
       Test case: C1652
        :param core_session: Centrify session
        :param core_admin_ui: Creates random user and login in browser.
        :param create_basic_pass_profile: Created a basic password complexity profile.
        """
    ui = core_admin_ui
    ui.navigate("Settings", "Resources", "Password Profiles")
    profile = create_basic_pass_profile(core_session, 1, 8)[0]
    cps_prof_id = profile[0]['_RowKey']
    profile_name_cps = profile[0]['Name']
    ui = core_admin_ui
    ui.navigate("Settings", "Resources", "Password Profiles")
    ui.launch_modal("Add", modal_title="Password Complexity Profile")
    profile_description = " AddNewProfile_Test"
    ui.input("Name", profile_name_cps)
    ui.input("Description", profile_description)
    ui.input("MinimumPasswordLength", 12)
    ui.input("MaximumPasswordLength", 24)
    ui.check("ConsecutiveCharRepeatAllowed")
    ui.check("undefined")
    ui.input("MaximumCharOccurrenceCount", 3)
    ui.check("undefined")
    ui.check("undefined")
    ui.input("MinimumAlphabeticCharacterCount", 2)
    ui.input("MinimumNonAlphabeticCharacterCount", 2)
    ui.button("Save")
    ui.expect(Div("already exists."), "Profile is already exists")
    logger.info(f"Password complexity profile {profile_name_cps} with id {cps_prof_id} already exists")


@pytest.mark.ui
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi_ui
def test_adding_default_profile_name(core_admin_ui):
    """
        Test case: C1653
        :param core_admin_ui: Centrify admin Ui session
        """
    ui = core_admin_ui
    ui.navigate("Settings", "Resources", "Password Profiles")
    ui.launch_modal("Add", modal_title="Password Complexity Profile")
    ui.input("Name", "--")
    ui.button("Save")
    ui.expect(Div("Invalid arguments passed to the server."), "Profile throws error with invalid arguments.")
    logger.info("Invalid arguments passed to the server error message appeared with default profile name '--'")


@pytest.mark.ui
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi_ui
def test_check_min_max_hint_messages(core_admin_ui):
    """
        Test case: C1654
        :param core_admin_ui: Centrify admin Ui session
        """
    ui = core_admin_ui
    ui.navigate("Settings", "Resources", "Password Profiles")
    ui.launch_modal("Add", modal_title="Password Complexity Profile")
    profile_name = f'testprofilename{guid()}'
    profile_description = "Test Description"
    ui.input("Name", profile_name)
    ui.input("Description", profile_description)
    ui.input("MinimumPasswordLength", 24)
    ui.input("MaximumPasswordLength", 12)
    ui.check("ConsecutiveCharRepeatAllowed")
    ui.check("undefined")
    ui.input("MaximumCharOccurrenceCount", 3)
    ui.check("undefined")
    ui.check("undefined")
    ui.input("MinimumAlphabeticCharacterCount", 2)
    ui.input("MinimumNonAlphabeticCharacterCount", 2)
    ui.button("Save")
    expected_password_length_error = "Maximum password length should not be less than minimum password length."
    ui.expect_value(Div("Maximum password length should not be less than minimum password length."), value='value',
                    expected_value=expected_password_length_error,
                    wrong_value_message="Maximum password length error popup not appeared", text=True)
    ui.expect(Anchor(button_text="Close"), "Error popup appears").try_click(
        expected_selector=Span("Password Complexity Profile"))

    # Checking Minimum Password Length field with Minimum and Maximum values.

    ui.input("MinimumPasswordLength", 3)
    min_pass_error = ui.check_tooltip_error("The minimum value for this field is 4")
    assert min_pass_error, "Error tooltip not appeared"
    logger.info("Hint message appeared as 'The minimum value for this field is 4'")

    ui.input("MinimumPasswordLength", 129)
    min_pass_error_len = ui.check_tooltip_error("The maximum value for this field is 128")
    assert min_pass_error_len, "Error tooltip not appeared"
    logger.info("Hint message appeared as 'The maximum value for this field is 128'")

    ui.input("MinimumPasswordLength", 4567)
    min_pass_error_len_max = ui.check_tooltip_error(
        "The maximum length for this field is 3</li><li>The maximum value for this field is 128")
    assert min_pass_error_len_max, "Error tooltip not appeared"
    logger.info(
        "Hint message appeared as 'The maximum length for this field is 3</li><li>The maximum value for this field is 128'")
    ui.input("MinimumPasswordLength", 33)

    # Checking Maximum Password Length field with Minimum and Maximum values.

    ui.input("MaximumPasswordLength", 3)
    max_pass_error = ui.check_tooltip_error("The minimum value for this field is 8")
    assert max_pass_error, "Error tooltip not appeared"
    logger.info("Hint message appeared as 'The minimum value for this field is 8'")

    ui.input("MaximumPasswordLength", 129)
    max_pass_error_len = ui.check_tooltip_error("The maximum value for this field is 128")
    assert max_pass_error_len, "Error tooltip not appeared"
    logger.info("Hint message appeared as 'The maximum value for this field is 128'")

    ui.input("MaximumPasswordLength", 4567)
    max_pass_error_len_max = ui.check_tooltip_error(
        "The maximum length for this field is 3</li><li>The maximum value for this field is 128")
    assert max_pass_error_len_max, "Error tooltip not appeared"
    logger.info(
        "Hint message appeared as 'The maximum length for this field is 3</li><li>The maximum value for this field is 128'")
    ui.input("MaximumPasswordLength", 45)

    # Checking Special Characters with Valid and Invalid values

    ui.input("SpecialCharSet", r"!#$%&()*+,-./:;<=>?@[\]^_{|}~")
    ui.input("SpecialCharSet", "`")
    special_char_error = ui.check_tooltip_error(
        r"Special characters are limited to the following: !#$%&()*+,-./:;<=>?@[\]^_{|}~ and characters cannot be repeated")
    assert special_char_error, "Error tooltip not appeared"
    logger.info(
        r"Hint message appeared as 'Special characters are limited to the following: {!#$%&()*+,-./:;<=>?@[\]^_{|}~} and characters cannot be repeated'")

    ui.input("SpecialCharSet", r"!#$%&()*+,-./:;<=>?@[\]^_{|}~!#")
    special_char_repeate_error = ui.check_tooltip_error(
        r"Special characters are limited to the following: !#$%&()*+,-./:;<=>?@[\]^_{|}~ and characters cannot be repeated")
    assert special_char_repeate_error, "Error tooltip not appeared"
    logger.info(
        r"Hint message appeared for repeate as 'Special characters are limited to the following: {!#$%&()*+,-./:;<=>?@[\]^_{|}~} and characters cannot be repeated'")
    ui.input("SpecialCharSet", r"!#$%&()*+,-./:;<=>?@[\]^_{|}~")

    # Checking Minimum number of Alpha characters count

    ui.input("MinimumAlphabeticCharacterCount", 0)
    min_alpha_char = ui.check_tooltip_error("The minimum value for this field is 1")
    assert min_alpha_char, "Error tooltip not appeared"
    logger.info("Hint message appeared as 'The minimum value for this field is 1'")

    ui.input("MinimumAlphabeticCharacterCount", 129)
    min_alpha_char_len = ui.check_tooltip_error("The maximum value for this field is 128")
    assert min_alpha_char_len, "Error tooltip not appeared"
    logger.info("Hint message appeared as 'The maximum value for this field is 128'")

    ui.input("MinimumAlphabeticCharacterCount", 1294)
    min_alpha_char_len_max = ui.check_tooltip_error(
        "The maximum length for this field is 3</li><li>The maximum value for this field is 128")
    assert min_alpha_char_len_max, "Error tooltip not appeared"
    logger.info(
        "Hint message appeared as 'The maximum length for this field is 3</li><li>The maximum value for this field is 128'")
    ui.input("MinimumAlphabeticCharacterCount", 12)

    # Checking Minimum number of non Alpha characters count values

    ui.input("MinimumNonAlphabeticCharacterCount", 0)
    min_non_alpha_char = ui.check_tooltip_error("The minimum value for this field is 1")
    assert min_non_alpha_char, "Error tooltip not appeared"
    logger.info("Hint message appeared as 'The minimum value for this field is 1'")

    ui.input("MinimumNonAlphabeticCharacterCount", 129)
    min_non_alpha_char_len = ui.check_tooltip_error("The maximum value for this field is 128")
    assert min_non_alpha_char_len, "Error tooltip not appeared"
    logger.info("Hint message appeared as 'The maximum value for this field is 128'")

    ui.input("MinimumNonAlphabeticCharacterCount", 1294)
    min_non_alpha_char_len_max = ui.check_tooltip_error(
        "The maximum length for this field is 3</li><li>The maximum value for this field is 128")
    assert min_non_alpha_char_len_max, "Error tooltip not appeared"
    logger.info("Hint message appeared as 'The maximum value for this field is 128'")

    ui.input("MinimumNonAlphabeticCharacterCount", 12)

    # Checking Maximum Character Occurrence Count values

    ui.input("MaximumCharOccurrenceCount", 0)
    max_char_occurence = ui.check_tooltip_error("The minimum value for this field is 1")
    assert max_char_occurence, "Error tooltip not appeared"
    logger.info("Hint message appeared as 'The minimum value for this field is 1'")

    ui.input("MaximumCharOccurrenceCount", 129)
    max_char_occurence_len = ui.check_tooltip_error("The maximum value for this field is 128")
    assert max_char_occurence_len, "Error tooltip not appeared"
    logger.info("Hint message appeared as 'The maximum value for this field is 128'")

    ui.input("MaximumCharOccurrenceCount", 1294)
    max_char_occurence_len_max = ui.check_tooltip_error(
        "The maximum length for this field is 3</li><li>The maximum value for this field is 128")
    assert max_char_occurence_len_max, "Error tooltip not appeared"
    logger.info(
        "Hint message appeared as 'The maximum length for this field is 3</li><li>The maximum value for this field is 128'")
    ui.input("MaximumCharOccurrenceCount", 12)


@pytest.mark.ui
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi_ui
def test_check_profile_name_special_char(core_admin_ui):
    """
        Test case: C1655
        :param core_admin_ui: Centrify admin Ui session
        """
    ui = core_admin_ui
    ui.navigate("Settings", "Resources", "Password Profiles")
    ui.launch_modal("Add", modal_title="Password Complexity Profile")

    # Checking profile name input with spaces.
    ui.input("Name", " ")
    ui.expect(InvalidInputAlertWithStrings(
        "'&#' and inputs behind '<' are not allowed and the message cannot contain spaces only."), "Error message")
    logger.info(
        "Hint message appeared as :'&#' and inputs behind '<' not allowed and the message cannot contain spaces only")

    # Checking profile name input with '&#'.
    ui.input("Name", "&#")
    ui.expect(InvalidInputAlertWithStrings(
        "'&#' and inputs behind '<' are not allowed and the message cannot contain spaces only."),
        "Error input popup message")
    logger.info(
        "Hint message appeared as :'&#' and inputs behind '<' not allowed and the message cannot contain spaces only")

    # Checking profile name input with '<alert>ok</alert>'.
    ui.input("Name", "<alert>ok</alert>")
    ui.expect(InvalidInputAlertWithStrings(
        "'&#' and inputs behind '<' are not allowed and the message cannot contain spaces only."),
        "Error input popup message")
    logger.info(
        "Hint message appeared as :'&#' and inputs behind '<' not allowed and the message cannot contain spaces only")

    # Checking profile name input with "\_%\_ etc".
    profile_name = r"\_%\_ etc"
    ui.input("Name", profile_name)
    ui.button("Save")
    ui.expect(GridCell(profile_name, data_content=True), expectation_message="Expecting newly created profile")
    logger.info(f"Password complexity profile {profile_name} Saved successfully")
    ui.wait_for_tab_with_name("Password Profiles")
    ui.right_click_action(GridCell(profile_name, data_content=True), 'Delete')
    ui.switch_context(ConfirmModal())
    ui.close_modal(button_text='Yes')
    logger.info(f"Password complexity profile {profile_name} deleted successfully")


@pytest.mark.ui
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi_ui
def test_check_validity_of_field(core_admin_ui):
    """
        Test case: C1656
        :param core_admin_ui: Centrify admin Ui session
        """
    ui = core_admin_ui
    ui.navigate("Settings", "Resources", "Password Profiles")
    ui.launch_modal("Add", modal_title="Password Complexity Profile")

    # Checking profile with miniumum password length 6 and maximum password length 53.
    profile_name = f'testprofilename{guid()}'
    profile_description = "Test Description"
    ui.input("Name", profile_name)
    ui.input("Description", profile_description)
    ui.input("MinimumPasswordLength", 6)
    ui.input("MaximumPasswordLength", 53)
    ui.check("undefined")
    ui.input("SpecialCharSet", "!")
    ui.input("MinimumAlphabeticCharacterCount", 51)
    ui.input("MaximumCharOccurrenceCount", 1)
    ui.button("Save")
    ui.expect(Div(
        "Min number of alpha characters should not exceed 50, when the value of 'Restrict number of character occurrences' is 1."),
        "Profile throws error message")
    logger.info(
        f"Password complexity profile {profile_name} thrown error with 'Restrict number of character occurrences' is 1'")
    ui.switch_context(ErrorModal())
    ui.close_modal("Close")

    # Checking profile with Minimum alphabetic character count and minimum non alphabetic character count as 10
    ui.input("MinimumAlphabeticCharacterCount", "")
    ui.input("MinimumNonAlphabeticCharacterCount", 10)
    ui.button("Save")
    ui.expect(Div(
        "Min number of non-alpha characters should not exceed 9, when the value of 'Restrict number of character occurrences' is 1."),
        "Profile throws error message")
    logger.info(f"Password complexity profile {profile_name} thrown error as expected")
    ui.switch_context(ErrorModal())
    ui.close_modal("Close")

    # Checking profile with Minimum alphabetic character count as 44 and minimum non alphabetic charecter count as 9
    ui.input("MinimumAlphabeticCharacterCount", "44")
    ui.input("MinimumNonAlphabeticCharacterCount", 9)
    ui.input("MaximumPasswordLength", 44)
    ui.button("Save")
    ui.expect(Div("Maximum password length should be at least 53 characters."), "Profile throws error message")
    ui.switch_context(ErrorModal())
    ui.close_modal("Close")
    logger.info(f"Password complexity profile {profile_name} thrown error as expected")

    # Checking profile with Minimum alphabetic character count and minimum non alphabetic charecter count as 55 and maximum password length as 52
    ui.input("MinimumAlphabeticCharacterCount", "")
    ui.input("MinimumNonAlphabeticCharacterCount", 55)
    ui.input("MaximumPasswordLength", 52)
    ui.button("Save")
    ui.expect(Div("Min number of non-alpha characters should not exceed 52."), "Profile throws error message")
    logger.info(f"Password complexity profile {profile_name} thrown error as expected")

    # Checking profile with Minimum alphabetic character count as 55 and minimum non alphabetic charecter count
    ui.input("MinimumAlphabeticCharacterCount", "55")
    ui.input("MinimumNonAlphabeticCharacterCount", "")
    ui.button("Save")
    ui.expect(Div("Min number of non-alpha characters should not exceed 52."), "Profile throws error message")
    ui.switch_context(ErrorModal())
    ui.close_modal("Close")
    logger.info(f"Password complexity profile {profile_name} thrown error as expected")

    # Checking profile with Minimum alphabetic character count as 49 and maximum password length
    ui.input("MaximumPasswordLength", 49)
    ui.input("MinimumAlphabeticCharacterCount", 49)
    ui.check("AtLeastOneDigit")
    ui.uncheck("AtLeastOneSpecial")
    ui.button("Save")
    ui.expect(Div("Maximum password length should be at least 50 characters."), "Profile throws error message")
    ui.switch_context(ErrorModal())
    ui.close_modal("Close")
    logger.info(f"Password complexity profile {profile_name} thrown error as expected")

    # Checking profile with Minimum alphabetic character count and minimum non alphabetic charecter count as 9 and maximum password length as 9
    ui.input("MaximumPasswordLength", 9)
    ui.uncheck("AtLeastOneDigit")
    ui.input("MinimumAlphabeticCharacterCount", "")
    ui.input("MinimumNonAlphabeticCharacterCount", 9)
    ui.button("Save")
    ui.expect(Div("Maximum password length should be at least 11 characters."), "Profile throws error message")
    ui.switch_context(ErrorModal())
    ui.close_modal("Close")
    logger.info(f"Password complexity profile {profile_name} thrown error as expected")

    # Checking profile with Minimum alphabetic character count as 50 and minimum non alphabetic charecter count as 9 and maximum password length as 120 and minimum password length as 60
    ui.input("MaximumPasswordLength", 120)
    ui.input("MinimumPasswordLength", 60)
    ui.input("MaximumCharOccurrenceCount", 1)
    ui.input("MinimumAlphabeticCharacterCount", 50)
    ui.input("MinimumNonAlphabeticCharacterCount", 9)
    ui.button("Save")
    ui.expect(Div(
        "Minimum password length should be at most 59 characters, when the value of 'Restrict number of character occurrences' is 1"),
        "Profile throws error message")
    ui.switch_context(ErrorModal())
    ui.close_modal("Close")
    logger.info(f"Password complexity profile {profile_name} thrown error as expected")


@pytest.mark.ui
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi_ui
def test_delete_used_profile(core_session, core_admin_ui, pas_setup, create_basic_pass_profile):
    """
        Test case: C1657
        :param core_admin_ui: Centrify admin Ui session
        :param pas_setup: Creates System and Account
        :param create_basic_pass_profile: Created a basic password complexity profile.
        """

    System_id, account_id, sys_info = pas_setup
    system_name = sys_info[0]
    FQDN = sys_info[1]
    computer_class = sys_info[2]

    # Creating a basic password profile
    profile = create_basic_pass_profile(core_session, 1)[0]
    cps_prof_id = profile[0]['_RowKey']
    profile_name_cps = profile[0]['Name']

    # updating system to add created password profile
    result, success = ResourceManager.update_system(core_session, System_id, system_name, FQDN,
                                                    computer_class, passwordprofileid=cps_prof_id)
    assert success, f'Failed to update system {result}'
    logger.info(f'System successfully updated with result: {result}')
    ui = core_admin_ui
    ui.navigate("Settings", "Resources", "Password Profiles")
    ui.search(profile_name_cps)

    # Deleting the password profile which is assigned to a system.
    ui.right_click_action(GridCell(profile_name_cps, data_content=True), 'Delete')
    ui.expect(Div('You are about to delete 1 Password Generation Profile. Are you sure you want to continue?'),
              "Delete warning popup appears")
    logger.info("Delete warning popup appears.")
    ui.switch_context(ConfirmModal())
    ui.close_modal(button_text='Yes')
    ui.expect(Div(f"The password profile cannot be deleted because it is being used by System '{system_name}'."),
              "Profile delete error popup")
    logger.info(f"Password complexity profile {profile_name_cps} not deleted")

    # Removing password profile from the system for the clean up/deleting password profile.
    result, success = ResourceManager.update_system(core_session, System_id, system_name, FQDN,
                                                    computer_class)
    assert success, f'Failed to update system {result}'
    logger.info("Removed the profile assigned to system to clean up/delete the profile.")


@pytest.mark.ui
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi_ui
def test_delete_multiple_used_profile(core_session, core_admin_ui, create_resources, create_basic_pass_profile):
    """
        Test case: C1659
        :param core_session: Returns API session
        :param core_admin_ui: Centrify admin Ui session
        :param create_resources: Creates System and Account
        :param create_basic_pass_profile: Created a basic password complexity profile.
        """
    # Creating one password complexity profile
    profile = create_basic_pass_profile(core_session, 1)[0]
    cps_prof_id = profile[0]['_RowKey']
    profile_name_cps = profile[0]['Name']
    systems_info = []

    # Creating two windows systems
    resources = create_resources(core_session, 2, "Windows")
    for res in resources:
        systems_info.append(res['ID'])
        systems_info.append(res['Name'])

        # Updating windows system with password complexity profile.
        result, success = ResourceManager.update_system(core_session, res['ID'], res['Name'], res['FQDN'],
                                                        res['ComputerClass'], passwordprofileid=cps_prof_id)
        assert success, f'Failed to update system {result}'
        logger.info(f'System successfully updated with result: {result}')

    ui = core_admin_ui
    ui.navigate("Settings", "Resources", "Password Profiles")
    ui.search(profile_name_cps)

    # Deleting the password profile which is assigned to a system.
    ui.right_click_action(GridCell(profile_name_cps, data_content=True), 'Delete')
    ui.expect(Div('You are about to delete 1 Password Generation Profile. Are you sure you want to continue?'),
              "Delete warning popup appears")
    logger.info("Delete warning popup appears.")
    ui.switch_context(ConfirmModal())
    ui.close_modal(button_text='Yes')

    # Delete warning message appears
    ui.expect(Div(f"The password profile cannot be deleted because it is being used by System 'automation_test_system"),
              "Profile delete error popup")
    logger.info(f"Password complexity profile {profile_name_cps} not deleted")


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.bhavna
def test_delete_profile_global_profile_mapping(core_session, create_basic_pass_profile):
    """
            Test case: C1658
            :param core_session: Returns API session
            :param create_basic_pass_profile: Created a basic password complexity profile.
            """

    # Creating one password complexity profile
    profile = create_basic_pass_profile(core_session, 1)[0]
    cps_prof_id = profile[0]['_RowKey']
    profile_name_cps = profile[0]['Name']

    # Updating the 'Unix' Type with new Password Complexity profile
    result, success = ResourceManager.update_global_pass_profile_mapping(core_session, "Unix", cps_prof_id)
    assert success, f"failed to update global password profile mapping {result}"
    logger.info(f"Password complexity profile {profile_name_cps} not deleted")

    # Fetching the global password profile mapping.
    result, success = ResourceManager.get_global_pass_profile_mapping(core_session)
    profile_name = []
    for row in result:
        if row['_RowKey'] == cps_prof_id:
            profile_name.append(row['Name'])
    assert profile_name_cps == profile_name[
        0], f"profile name is not updated with the Type of global profile mapping {result}"

    resp = ResourceManager.delete_password_profile(core_session, cps_prof_id)
    assert resp is False, f"Password complexity profile {profile_name_cps} deleted"
    logger.info(f"Password complexity profile {profile_name_cps} not deleted")


@pytest.mark.api_ui
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi_ui
def test_clear_password_complexity_profile_description(core_session, core_admin_ui, create_basic_pass_profile):
    """ Test case C1661
        :param core_session: Centrify session
        :param core_admin_ui: Creates random user and login in browser.
        :param create_basic_pass_profile: Created a basic password complexity profile.
        """

    # Creating a basic password profile
    profile = create_basic_pass_profile(core_session, 1)[0]
    cps_prof_id = profile[0]['_RowKey']
    profile_name_cps = profile[0]['Name']
    ui = core_admin_ui
    ui.navigate("Settings", "Resources", "Password Profiles")
    ui.search(profile_name_cps)

    # Modify the password profile of description
    ui.right_click_action(GridCell(profile_name_cps, data_content=True), 'Modify Profile')
    ui.switch_context(Modal("Password Complexity Profile"))
    ui.input("Description", " ")
    ui.close_modal("Save")

    # Getting all the profiles and checking for the updated profile
    all_profiles, success = ResourceManager.get_profiles(core_session, type="All", rr_format=True)
    complex_password_profile = []
    for row in all_profiles['Results']:
        if row['Row']['Name'] == profile_name_cps:
            complex_password_profile.append(row['Row']['Description'])

    # checking the description of the profile saved successfully after clearing the description field.
    assert complex_password_profile[0] == '', \
        f"Profile with id {cps_prof_id} not saved successfully with description{success}"
    logger.info(f"Updated description of profile {profile_name_cps} successfully with {complex_password_profile[0]}")


@pytest.mark.api_ui
@pytest.mark.pas1
@pytest.mark.bhavna
@pytest.mark.pasapi_ui
def test_unsaved_global_profile_mapping(core_session, core_admin_ui, create_basic_pass_profile):
    """     Test case: C1660
            :param core_session: Creates core session
            :param core_admin_ui: Creates random user and login in browser.
            :param create_basic_pass_profile: Created a basic password complexity profile.
            """

    profile = create_basic_pass_profile(core_session, 1)[0]
    cps_prof_id = profile[0]['_RowKey']
    profile_name_cps = profile[0]['Name']

    # Getting the global password profile mapping profiles
    result, success = ResourceManager.get_global_pass_profile_mapping(core_session)
    profile_name = []
    for row in result:
        if row['TargetTypeDisplayName'] == "Unix System":
            profile_name.append(row['Name'])

    # UI navigating to Security Settings and updating the 'Unix' Type global password profile.
    ui = core_admin_ui
    ui.navigate("Settings", "Resources", "Security", "Security Settings")
    ui.expect(GridCell(profile_name[0]), "Unix type password profile not editable.").try_click(Div("Security Settings"))
    ui.switch_context(ActiveMainContentArea())
    ui.select_option('Name', profile_name_cps)
    ui.switch_context(ConfirmModal())
    ui.button('Continue')
    ui.expect(Span("Password Profiles"), "Clicking Password Profiles").try_click(Div("Security Settings"))
    assert ui.check_exists(Div('Unsaved Changes')), "Fail, as 'Confirmation Modal' i.e. 'Unsaved Changes dialog' " \
                                                    "didn't pop up even after clicking another tab."
    logger.info("'Unsaved Changes dialog' popped up after clicking another tab without saving the new profile")

    # Clicking 'Yes' button on 'Unsaved Changes' dialog box and expecting new profile to be saved.
    ui.switch_context(ConfirmModal())
    ui.close_modal("Yes")

    # Getting all the global password profile mappings.
    result, success = ResourceManager.get_global_pass_profile_mapping(core_session)
    for res in result:
        if res['Name'] == profile_name_cps:
            assert res['TargetType'] == 'Unix', f"Failed to update profile with id {cps_prof_id} Unix Type {result}"
    logger.info("Updated the new profile to the 'Unix' Type")


@pytest.mark.api_ui
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi_ui
def test_apply_profile_not_exist(core_session, pas_setup, create_basic_pass_profile, core_admin_ui):
    """
        Test case: C1657
        :param core_session: Centrify session.
        :param core_admin_ui: Centrify admin Ui session
        :param pas_setup: Creates System and Account
        :param create_basic_pass_profile: Created a basic password complexity profile.
        """
    # Creating windows system.
    System_id, account_id, sys_info = pas_setup
    system_name = sys_info[0]
    fqdn = sys_info[1]
    logger.info(f"Created windows system {system_name} with fqdn {fqdn}")

    # Creating a basic password profile
    profile = create_basic_pass_profile(core_session, 1)[0]
    cps_prof_id = profile[0]['_RowKey']
    profile_name_cps = profile[0]['Name']
    logger.info(f"Created password profile {profile_name_cps} with id {cps_prof_id}")

    # ui starts from here.
    ui = core_admin_ui
    ui.navigate('Resources', 'Systems')
    ui.search(system_name)
    ui.click_row(system_name)
    ui.tab('Advanced')
    ui.select_option("PasswordProfileID", profile_name_cps)
    ui.switch_context(ConfirmModal())
    ui.close_modal('Continue')
    ResourceManager.delete_password_profile(core_session, cps_prof_id)
    ui.button("Save")
    ui.expect(Div("Password profile is not found."),
              f"'password profile {profile_name_cps} already deleted' error popup not appeared")
    logger.info(f"password profile {profile_name_cps} with id {cps_prof_id} deleted")
