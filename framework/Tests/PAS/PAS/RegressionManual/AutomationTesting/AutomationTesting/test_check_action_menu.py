import pytest
import logging
from Shared.API.infrastructure import ResourceManager
from Shared.UI.Centrify.SubSelectors.grids import GridRowByGuid, GridRowCheckbox
from Shared.UI.Centrify.SubSelectors.navigation import RenderedTab

logger = logging.getLogger("test")


@pytest.mark.api_ui
@pytest.mark.pas
@pytest.mark.pasapi_ui
@pytest.mark.bhavna
def test_check_action_menu(core_session, pas_windows_setup, users_and_roles):
    """
    TC:C2172 Check Actions menu.
    :param core_session: Returns a API session.
    :param pas_windows_setup: Returns a fixture.
    :param users_and_roles: Returns Authenticated Centrify UI session  with limited rights.
    """

    # Creating a system and account.
    system_id, account_id, sys_info, connector_id, user_password = pas_windows_setup()

    # Getting the limited user session with limited rights " Privilege Service Power User right."
    ui = users_and_roles.get_ui_as_user("Privileged Access Service Power User")
    limited_user = ui.get_user()

    # Assigning "Login" permission for system to limited user.
    assign_system_perm_res, assign_system_perm_success = \
        ResourceManager.assign_account_permissions(core_session, "Login",
                                                   limited_user.get_login_name(),
                                                   limited_user.get_id(),
                                                   'User',
                                                   account_id)

    assert assign_system_perm_success, f"Failed to assign 'Edit' permissions to " \
                                       f"user for the  system: API response result: {assign_system_perm_res}."
    logger.info(f"Successfully assign 'Edit' permissions to user for the system:{assign_system_perm_res}.")

    # UI Launch.
    ui.navigate('Resources', 'Systems')
    ui.search(sys_info[0])
    ui.click_row(GridRowByGuid(system_id))
    ui.check_row_by_guid(account_id)
    ui.switch_context(RenderedTab("Accounts"))
    expected_actions = ['Login', 'Add To Set', 'Verify Credential']
    ui.check_actions(expected_actions, sys_info[4])
    logger.info('Successfully found "Actions" menu in Accounts page.')
    ui.expect(GridRowCheckbox(sys_info[4], True), "Not checking the row").try_click()
    logger.info('Successfully uncheck the account row.')
    ui.right_click(GridRowByGuid(account_id))
    Flag = False
    counter = 0
    while Flag:
        list_action_elements = ui.get_list_of_right_click_element_values('Login')
        if 'Verify Credential' in list_action_elements:
            Flag = True
            break
        counter += 1
        if counter == 10:
            break
        assert expected_actions == list_action_elements, f"Expected actions elements are not found in the list"
    logger.info('Successfully found the elements same as in "Actions" menu in Accounts page.')
