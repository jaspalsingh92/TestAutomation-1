import pytest
import logging

from Shared.UI.Centrify.SubSelectors.grids import GridRowByGuid
from Shared.UI.Centrify.SubSelectors.navigation import ActiveMainContentArea
from Shared.UI.Centrify.selectors import Header, Anchor

logger = logging.getLogger('test')


@pytest.mark.pas
@pytest.mark.ui
@pytest.mark.bhavna
def test_check_help_page(add_database_with_account, core_admin_ui):
    """
    Test case: C1162
    :param core_session: Centrify authenticated session
    :param add_database_with_account: fixture to create database with account as optional
    :param core_admin_ui: Centrify admin ui session
    """
    db_name, db_id, db_account_id, db_data, database_cleaner_list, account_cleaner_list = \
        add_database_with_account(db_class='oracle', add_account=False)

    ui = core_admin_ui
    ui.navigate('Resources', 'Databases')
    ui.search(db_name)
    ui.click_row(GridRowByGuid(db_id))
    ui.tab('Settings')
    ui.switch_context(ActiveMainContentArea())
    ui.expect(Anchor(button_text='Learn more'), expectation_message="Learn more Link to click").try_click()
    logger.info('Located "Learn More" span and clicked on it.')
    ui.wait_for_tab_with_name('Changing database settings')
    ui.switch_context(ActiveMainContentArea())
    ui.expect(Header('Changing database settings'), 'Expected to find the header with title '
                                                    '"Changing database settings"')
    logger.info('Changing database settings help page pop up')

    ui.switch_first_tab()
    ui.tab('Accounts')
    ui.switch_context(ActiveMainContentArea())
    ui.expect(Anchor(button_text='Learn more'), expectation_message="Learn more Link to click").try_click()
    logger.info('Located "Learn More" span and clicked on it.')
    ui.wait_for_tab_with_name('Adding database accounts')
    ui.switch_context(ActiveMainContentArea())
    ui.expect(Header('Adding database accounts'), 'Expected to find the header with title '
                                                  '"Adding database accounts"')
    logger.info('Adding database accounts help page pop up')

    ui.switch_first_tab()
    ui.tab('Activity')
    ui.switch_context(ActiveMainContentArea())
    ui.expect(Anchor(button_text='Learn more'), expectation_message="Learn more Link to click").try_click()
    logger.info('Located "Learn More" span and clicked on it.')
    ui.wait_for_tab_with_name('Viewing activity for a database')
    ui.switch_context(ActiveMainContentArea())
    ui.expect(Header('Viewing activity for a database'), 'Expected to find the header with title '
                                                         '"Viewing activity for a database"')
    logger.info('Viewing activity for a database help page pop up')

    ui.switch_first_tab()
    ui.tab('Permissions')
    ui.switch_context(ActiveMainContentArea())
    ui.expect(Anchor(button_text='Learn more'), expectation_message="Learn more Link to click").try_click()
    logger.info('Located "Learn More" span and clicked on it.')
    ui.wait_for_tab_with_name('Setting database-specific permissions')
    ui.switch_context(ActiveMainContentArea())
    ui.expect(Header('Setting database-specific permissions'), 'Expected to find the header with title '
                                                               '"Setting database-specific permissions"')
    logger.info('Setting database-specific permissions help page pop up')
