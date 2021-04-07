import logging
import pytest
from Shared.UI.Centrify.selectors import Div, Anchor, Header

logger = logging.getLogger('test')


@pytest.mark.pas
@pytest.mark.ui
@pytest.mark.bhavna
def test_learn_more_help_check_for_secrets(core_admin_ui, added_secrets):
    """
     C2940: test method to login with cloud admin & click on Secrets
    1) Settings tab, click "Learn more", check pop-up help page should display
    2) Policy tab, click "Learn more", check pop-up help page should display
    3) Activity tab, click "Learn more", check pop-up help page should display
    4) Permissions tab, click "Learn more", check pop-up help page should display

    :param core_admin_ui: Fixture to launch the browser with cloud admin
    :param added_secrets: Fixture to add text type secrets & yields secret related details

    """
    added_text_secret_id, added_text_secret_name = added_secrets
    ui = core_admin_ui
    ui.navigate('Resources', 'Secrets')
    ui.search(added_text_secret_name)
    ui.expect(Div(added_text_secret_name),
              expectation_message='Expecting to find {added_text_secret_name} but did not ').try_click()

    link_selector = Anchor(button_text='Learn more')
    link_clicked = ui.expect(link_selector, expectation_message="Learn more Link to click")
    link_clicked.try_click()
    ui.switch_to_pop_up_window()
    permissions_pop_up = ui.check_exists(Header('Setting secret, folder, and set permissions'))
    assert permissions_pop_up, f'Failed to verify the {permissions_pop_up}'
    logger.info(f'Permissions pop up loading successful:{permissions_pop_up}')
    ui.close_browser()
    ui.switch_to_main_window()

    ui.tab('Settings')
    link_selector = Anchor(button_text='Learn more')
    link_clicked = ui.expect(link_selector, expectation_message="Learn more Link to click")
    link_clicked.try_click()
    ui.switch_to_newest_tab()
    settings_pop_up = ui.check_exists(Header('Viewing and changing settings'))
    assert settings_pop_up, f'Failed to verify the {settings_pop_up}'
    logger.info(f'Settings pop up loading Successful:{settings_pop_up}')
    ui.close_browser()
    ui.switch_to_main_window()

    ui.tab('Policy')
    link_selector = Anchor(button_text='Learn more')
    link_clicked = ui.expect(link_selector, expectation_message="Learn more Link to click")
    link_clicked.try_click()
    ui.switch_to_newest_tab()
    policy_pop_up = ui.check_exists(Header('Setting access challenge policies'))
    assert policy_pop_up, f'Failed to verify the {policy_pop_up}'
    logger.info(f'Policy pop up loading Successful:{policy_pop_up}')
    ui.close_browser()
    ui.switch_to_main_window()

    ui.tab('Activity')
    link_selector = Anchor(button_text='Learn more')
    link_clicked = ui.expect(link_selector, expectation_message="Learn more Link to click")
    link_clicked.try_click()
    ui.switch_to_newest_tab()
    activity_pop_up = ui.check_exists(Header('Viewing activity for a secret or folder'))
    assert activity_pop_up, f'Failed to verify the {activity_pop_up}'
    logger.info(f'Activity pop up loading Successful:{activity_pop_up}')
    ui.close_browser()
    ui.switch_to_main_window()
