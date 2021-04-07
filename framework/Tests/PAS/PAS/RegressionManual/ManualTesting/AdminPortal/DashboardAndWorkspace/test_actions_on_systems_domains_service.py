import pytest
import logging
from Shared.UI.Centrify.selectors import Div

logger = logging.getLogger("test")


@pytest.mark.api_ui
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi_ui
def test_actions_on_systems_domains_service(core_session, pas_windows_setup, core_admin_ui):
    """
    TC: C2055 Check action on Systems/Accounts/Domains/Services.
    :param core_session: Authenticated Centrify session.
    :param pas_windows_setup: Returning a fixture.
    :param core_admin_ui: Authenticated Centrify  UI session.
    """

    # Creating a system and account.
    system_id, account_id, sys_info, connector_id, user_password = pas_windows_setup()

    # UI Launch.
    ui = core_admin_ui
    ui.navigate('Resources', 'Systems')
    ui.search(sys_info[0])
    ui.right_click(Div(sys_info[0]))
    expected_last_actions_value = 'Delete'
    system_list_action = False
    counter = 0
    while system_list_action is False:
        if counter is not 30:
            list_action_element = ui.get_list_of_right_click_element_values('Login')
            if expected_last_actions_value in list_action_element:
                system_list_action = True
                logger.info('expected_last_actions_value is in the list_action_element')
                break
        counter = + 1
    actual_last_action_element = list_action_element.pop()
    assert actual_last_action_element == expected_last_actions_value, f"Delete is not the last element in Actions list"
    logger.info(f'Delete is  the last element in Actions list: "{actual_last_action_element}."')
