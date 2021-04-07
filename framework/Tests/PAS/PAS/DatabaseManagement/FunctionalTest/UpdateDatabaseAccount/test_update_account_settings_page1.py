import pytest
import logging
from Shared.UI.Centrify.SubSelectors.forms import TextArea
from Shared.UI.Centrify.SubSelectors.grids import GridRowByGuid

logger = logging.getLogger('test')


@pytest.mark.api_ui
@pytest.mark.pas
@pytest.mark.pasapi_ui
@pytest.mark.bhavna
def test_update_account_settings_page1(core_session, add_database_with_account, core_admin_ui):
    """
    Test case: C1093 - Update Account Settings page 1
    :param core_session: Authenticated centrify session
    :param add_database_with_account: fixture to create database with account
    :param core_admin_ui: Authenticated centrify ui session
    """
    db_name, db_id, db_account_id, db_data, database_cleaner_list, sql_account_cleaner_list = \
        add_database_with_account(db_class='sql', add_account=True)
    test_description = f'test description of account {db_data["db_account"]} for database {db_name}'

    ui = core_admin_ui
    ui.navigate('Resources', 'Databases')
    ui.search(db_name)
    ui.click_row(GridRowByGuid(db_id))
    ui.tab('Accounts')
    ui.click_row(GridRowByGuid(db_account_id))
    ui.tab('Settings')
    ui.input(name='Description', value=test_description)
    ui.save()
    logger.info('Settings form saved successfully')
    ui.tab('Permissions')
    ui.tab('Settings')
    ui.expect(TextArea(name='Description', contains=test_description), f'failed to update description on settings page '
                                                                       f'for account {db_data["db_account"]} '
                                                                       f'of database {db_name}')
    logger.info(f'Account {db_data["db_account"]} description updated successfully.')
