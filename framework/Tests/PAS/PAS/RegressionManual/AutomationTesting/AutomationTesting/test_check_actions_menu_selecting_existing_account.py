import pytest
import logging
from Shared.API.infrastructure import ResourceManager
from Shared.UI.Centrify.SubSelectors.grids import GridRowByGuid
from Shared.UI.Centrify.SubSelectors.navigation import RenderedTab

logger = logging.getLogger("test")


@pytest.mark.api_ui
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi_ui
def test_check_action_menu_selecting_existing_account(core_session, pas_windows_setup, users_and_roles):
    """
    TC:C2173 Check Actions menu after selecting an existing account.
    :param core_session: Returns a API session.
    :param pas_windows_setup: Returns a fixture.
    :param:users_and_roles:Fixture to manage roles and user.
    """

    # Creating a system and account.
    system_id, account_id, sys_info, connector_id, user_password = pas_windows_setup()

    # Cloud user session with "'Privileged Access Service Power User'".
    cloud_user_session = users_and_roles.get_session_for_user('Privileged Access Service Power User')
    user_name = cloud_user_session.auth_details['User']
    user_id = cloud_user_session.auth_details['UserId']

    # UI session with 'Privileged Access Service Power User' rights.
    ui = users_and_roles.get_ui_as_user('Privileged Access Service Power User')

    # Assigning system "Edit" permission.
    assign_system_result, assign_system_success = ResourceManager.assign_system_permissions(core_session,
                                                                                            "Edit",
                                                                                            user_name,
                                                                                            user_id,
                                                                                            'User',
                                                                                            system_id)
    assert assign_system_success, f"Failed to assign system permissions: API response result: {assign_system_result}"
    logger.info(f'Successfully assigned "Edit" permission to user:{assign_system_result}.')

    # UI Launch.
    ui.navigate('Resources', 'Systems')
    ui.search(sys_info[0])
    ui.click_row(GridRowByGuid(system_id))
    ui.switch_context(RenderedTab("Accounts"))
    ui.check_row(sys_info[4])
    assert ui.button_exists('Actions'), "Failed to find 'Actions'menu button in Accounts page."
    logger.info('Successfully found "Actions" menu in Accounts page. ')
