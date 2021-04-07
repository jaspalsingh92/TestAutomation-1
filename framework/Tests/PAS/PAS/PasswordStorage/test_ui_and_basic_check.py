import pytest
import logging
from Shared.API.discovery import Discovery
from Shared.API.infrastructure import ResourceManager
from Shared.API.jobs import JobManager
from Shared.API.redrock import RedrockController
from Shared.UI.Centrify.SubSelectors.grids import GridRowByGuid
from Shared.UI.Centrify.SubSelectors.modals import ErrorModal
from Shared.UI.Centrify.SubSelectors.navigation import RenderedTab, ActiveMainContentArea
from Shared.UI.Centrify.selectors import Anchor, Span, Div, Label, Button, PageWithTitle
from Shared.data_manipulation import DataManipulation
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.ui
@pytest.mark.pas
@pytest.mark.bhavna
def test_ui_check_job_details_page(core_session, core_admin_ui, list_of_created_systems):
    """
         Test case: C1674
               :param core_session: Returns API session
               :param core_admin_ui: Centrify admin Ui session
               :param list_of_created_systems: returns the empty systems list.
               """

    account_name_prefix = f'account_test{guid()}'

    # adding multiple systems with accounts
    result = ResourceManager.add_multiple_systems_with_accounts(core_session, 1, 1, list_of_created_systems,
                                                                user_prefix=account_name_prefix)

    # arranging the results in the lists
    all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values([result])

    # Deleting systems for creating bulk delete scheduled report
    result_acc, success_acc = ResourceManager.del_multiple_accounts(core_session, all_accounts)
    assert success_acc, f"Api did not complete successfully for bulk account delete MSG:{result_acc}"

    # Deleting accounts for creating bulk delete scheduled report
    result, success = ResourceManager.del_multiple_systems(core_session, all_systems)
    assert success, f'Delete systems job failed when expected success'
    logger.info(f"Delete systems job executed successfully {result}")

    # Going to password storage page and click on migration job status link.
    ui = core_admin_ui
    ui.navigate("Settings", "Resources", "Password Storage", check_rendered_tab=False)
    ui.expect(Anchor("View Migration Job Status and Reports "), "Clicking migration job status").try_click(
        Span(text="Type"))
    ui.switch_to_newest_tab()
    ui._waitUntilSettled()
    ui.click_row(GridRowByGuid(result))
    ui.expect(Span("Details"), "Clicking migration job status").try_click(Div("Job Details"))
    ui.expect_value(Div(result), value=None, expected_value=result,
                    wrong_value_message="expected id value is not matched in the report",
                    text=True)
    logger.info("Id value in the Job description appeared correctly")


@pytest.mark.ui
@pytest.mark.pas
@pytest.mark.bhavna
def test_ui_check_job_details_page_values(core_session, core_admin_ui, list_of_created_systems):
    """
         Test case: C1670
               :param core_session: Returns API session
               :param core_admin_ui: Centrify admin Ui session
               :param list_of_created_systems: returns the empty systems list.
               """
    account_name_prefix = f'account_test{guid()}'

    # adding multiple systems with accounts
    result = ResourceManager.add_multiple_systems_with_accounts(core_session, 1, 1, list_of_created_systems,
                                                                user_prefix=account_name_prefix)

    # arranging the results in the lists
    all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values([result])

    # Deleting systems for creating bulk delete scheduled report
    result_acc, success_acc = ResourceManager.del_multiple_accounts(core_session, all_accounts)
    assert success_acc, f"Api did not complete successfully for bulk account delete MSG:{result_acc}"

    # Deleting accounts for creating bulk delete scheduled report
    result_sys, success = ResourceManager.del_multiple_systems(core_session, all_systems)
    assert success, f'Delete systems job failed when expected success'
    logger.info(f"Delete systems job executed successfully {result_sys}")

    # Going to password storage page and click on migration job status link.
    ui = core_admin_ui
    ui.navigate("Settings", "Resources", "Password Storage", check_rendered_tab=False)
    ui.expect(Anchor("View Migration Job Status and Reports "), "Clicking migration job status").try_click()
    ui.switch_to_newest_tab()
    ui._waitUntilSettled()
    ui.click_row(GridRowByGuid(result_sys))
    ui.expect(Span("Details"), "Clicking migration job status").try_click(Div("Job Details"))

    # Checking the Job Id of system.
    ui.expect_value(Div(result_sys), value=None, expected_value=result_sys,
                    wrong_value_message="expected id value is not matched in the report",
                    text=True)
    logger.info("Id value in the Job description appeared correctly")

    # List of the Expected text from Job Details
    list_of_text = ['Job Information', 'Type', 'ID', 'Description', 'Submitted', 'Started', 'Completed',
                    'Retry Count', 'Items Synced', 'Items Failed']

    # Getting the Job history
    job_history = JobManager.get_job_history(core_session)

    # Validating the Job history expected title appeared correctly on UI.
    for label in list_of_text:
        ui.expect_value(Label(label), value=None, expected_value=label,
                        wrong_value_message=f"expected {label} value is not matched in the report",
                        text=True)
        logger.info(f"expected {label} value is matched in the report")
    delete_scheduled_job = []
    check_text = []
    if job_history[1]['JobName'] == 'BulkSystemDelete':
        account_bulk_delete_schedule_id = job_history[0]['ID']
        System_bulk_delete_schedule_id = job_history[1]['ID']
        System_jobdescription = job_history[1]['JobDescription']
        System_jobName = job_history[1]['JobName']
        check_text.append(System_bulk_delete_schedule_id)
        check_text.append(System_jobdescription)
        check_text.append(System_jobName)
        check_text.append(account_bulk_delete_schedule_id)
        delete_scheduled_job.append(System_bulk_delete_schedule_id)
    ui.switch_context(RenderedTab("Job Details"))

    # Validating the Job history results from API appeared correctly on UI.
    for text in check_text:
        ui.expect_value(Div(text), value=None, expected_value=text,
                        wrong_value_message=f"expected {text} value is not matched in the report",
                        text=True)
        logger.info(f"expected {text} value is matched in the report")

    # Deleting the Scheduled jobs of Bulk System's and Account's
    for delete in delete_scheduled_job:
        result_account_delete, success, response = Discovery.delete_job_history(core_session, delete)
        assert success, f"Failed to delete Job history profile {result_account_delete}"
        logger.info(f"delete Job history profile with id {delete} successful {success}")


@pytest.mark.ui
@pytest.mark.pas
@pytest.mark.bhavna
def test_system_password_rotation(core_session, pas_setup, core_admin_ui):
    """
    Test Case ID: C1671
    :param core_session: Returns API session
    :param pas_setup: Creates System and Account
    :param core_admin_ui: Authenticates Centrify UI session
    """
    # Creating windows system.
    system_id, account_id, sys_info = pas_setup
    system_name = sys_info[0]

    # Navigating to System and enabling the "All Password Rotation" option with valid and invalid values.
    ui = core_admin_ui
    ui.navigate('Resources', 'Systems')
    ui.search(system_name)
    ui.click_row(GridRowByGuid(system_id))
    ui.tab('Advanced')
    ui.switch_context(RenderedTab("Advanced"))
    ui.select_option("AllowPasswordRotation", "Yes")
    expected_password_rotation_duration = 1
    ui.input("PasswordRotateDuration", expected_password_rotation_duration)
    ui.expect(Button("Save"), "Save button should enabled")
    logger.info("Save button enabled")
    ui.save()
    logger.info("Valid value 1 is accepted and saved successfully")

    # Checking the value is saved and reflected with the system's settings.
    system_list = RedrockController.get_computers(core_session)
    discovered_system = []
    for system in system_list:
        if system['Name'] == sys_info[0]:
            discovered_system.append(system['ID'])
            discovered_system.append(system['PasswordRotateDuration'])
    actual_password_rotation_duration = discovered_system[1]
    assert expected_password_rotation_duration == actual_password_rotation_duration, f"password rotation duration count {expected_password_rotation_duration} not matched with actual count {actual_password_rotation_duration}"
    logger.info(
        f"Password rotation duration of the system {system_name} with id {system_id} saved with count {actual_password_rotation_duration} ")

    # Changing the value of password rotation duration with invalid value 0.
    ui.tab('Advanced')
    ui.switch_context(RenderedTab("Advanced"))
    ui.select_option("AllowPasswordRotation", "Yes")
    ui.input("PasswordRotateDuration", 0)
    ui.save()
    ui.switch_context(ErrorModal())
    ui.expect(Div("Please correct the errors in your form before submitting."), " Error pop up should appear")
    logger.info("Invalid value 0 is not accepted and thrown error popup successfully")


@pytest.mark.ui
@pytest.mark.pas
@pytest.mark.bhavna
def test_password_storage_page(core_admin_ui):
    """
            Test Case ID: C1669
            :param core_admin_ui: Authenticates Centrify UI session
            """

    # Navigating to the Password Storage page and checking the UI.
    ui = core_admin_ui
    ui.navigate("Settings", "Resources", "Password Storage", check_rendered_tab=False)
    ui.expect(Label("Select the location where system passwords should be stored"),
              "Expected the 'Select the location' label to be appeared")
    logger.info("'Select the location where system passwords should be stored' appeared successfully")

    #  Checking the 'Centrify Privileged Access Service' label
    ui.expect(Label("Centrify Privileged Access Service"),
              "Expected the 'Centrify Privileged Access Service' label to be appeared")
    logger.info("'Centrify Privileged Access Service' appeared successfully")

    #  Checking the 'SafeNet KeySecure appliance' label
    ui.expect(Label("SafeNet KeySecure appliance"), "Expected the 'SafeNet KeySecure appliance' label to be appeared")
    logger.info("'SafeNet KeySecure appliance' appeared successfully")

    #  Checking the 'Migrate Passwords' button
    ui.expect(Span("Migrate Passwords"), "Expected 'Migrate Passwords' button to be appeared")
    logger.info("'Migrate Passwords' button appeared successfully")


@pytest.mark.pas
@pytest.mark.ui
@pytest.mark.bhavna
def test_check_safenet(core_admin_ui):
    """
     Test Case ID: C1729
    :param core_admin_ui: Authenticates Centrify UI session
    """

    # Navigating to the Password Storage page and checking the tooptip and help pages.
    ui = core_admin_ui
    ui.navigate("Settings", "Resources", "Password Storage", check_rendered_tab=False)

    # Clicking the help tooltip at the begin of the page.
    ui.expect(Span(text="?"),
              'tooltip ? to be enabled').try_click(Span(text="Migrate Passwords"))
    ui.switch_to_newest_tab()
    ui.expect(PageWithTitle("Configuring password storage"),
              "Expecting a new page with title 'Configuring password storage'")
    logger.info("Title with the page 'Configuring password storage' loaded successfully'")
    ui.switch_to_main_window()
    ui.switch_context(ActiveMainContentArea())

    # Clicking the Learn more link in the password storage page.
    ui.expect(Anchor(button_text="Learn more"), "expecting a link named 'Learn more'").try_click(
        Span(text="Migrate Passwords"))
    ui.switch_to_newest_tab()
    ui.expect(PageWithTitle("Configuring password storage"),
              "Expecting a new page with title 'Configuring password storage'")
    logger.info("Title with the page 'Configuring password storage' loaded successfully'")
    ui.switch_to_main_window()

    ui.navigate("Settings", "Resources", ("SafeNet KeySecure Configuration", "SafeNet KeySecure Configuration"))

    # Clicking the Learn more link in the SafeNet KeySecure Configuration page.
    ui.expect(Anchor(button_text="Learn more"), "expecting a link named 'Learn more'").try_click(
        Div(text="SafeNet KeySecure Configuration"))
    ui.switch_to_newest_tab()
    ui.expect(PageWithTitle("Configuring communication with SafeNet KeySecure"),
              "Expecting a new page with title 'Configuring communication with SafeNet KeySecure'")
    logger.info("Title with the page 'Configuring communication with SafeNet KeySecure' loaded successfully'")


@pytest.mark.ui
@pytest.mark.pas
@pytest.mark.bhavna
def test_system_password_rotation_switch_page(core_session, pas_setup, core_admin_ui):
    """
    Test Case ID: C1672
    :param core_session: Returns API session
    :param pas_setup: Creates System and Account
    :param core_admin_ui: Authenticates Centrify UI session
    """
    # Creating windows system.
    system_id, account_id, sys_info = pas_setup
    system_name = sys_info[0]

    # Navigating to System and enabling the "password rotation duration" option with valid values.
    ui = core_admin_ui
    ui.navigate('Resources', 'Systems')
    ui.search(system_name)
    ui.click_row(GridRowByGuid(system_id))
    ui.tab('Advanced')
    ui.switch_context(RenderedTab("Advanced"))
    ui.select_option("AllowPasswordRotation", "Yes")
    expected_password_rotation_duration = 5
    ui.input("PasswordRotateDuration", expected_password_rotation_duration)
    ui.save()
    ui.navigate('Resources', 'Domains')

    # Leaving the page and coming back to the System's page as per the test case.
    ui.navigate('Resources', 'Systems')
    system_list = RedrockController.get_computers(core_session)
    discovered_system = []
    for system in system_list:
        if system['Name'] == sys_info[0]:
            discovered_system.append(system['ID'])
            discovered_system.append(system['PasswordRotateDuration'])
    assert expected_password_rotation_duration == discovered_system[1], f"password rotation duration count {expected_password_rotation_duration} not matched with actual count {discovered_system[1]}"
    logger.info(
        f"Password rotation duration of the system {system_name} with id {system_id} saved with count {discovered_system[1]}")
