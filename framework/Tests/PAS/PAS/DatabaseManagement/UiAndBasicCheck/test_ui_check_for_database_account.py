import pytest
import logging
from Shared.UI.Centrify.SubSelectors.grids import GridRowByGuid
from Shared.UI.Centrify.selectors import Label, Span

logger = logging.getLogger('test')


@pytest.mark.api_ui
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_database_account_ui_check(core_session, create_databases_with_accounts, core_admin_ui):
    """
    Test case: C1074
    :param core_session: Authenticated Centrify session
    :param create_databases_with_accounts: fixture to create database with account
    """
    database = create_databases_with_accounts(core_session, databasecount=1, accountcount=1)
    db_name, db_id, db_account, db_account_id = \
        database[0]['Name'], database[0]['ID'], database[0]['Accounts'][0]['User'], database[0]['Accounts'][0]['ID']

    ui = core_admin_ui
    ui.navigate('Resources', 'Databases')
    ui.search(db_name)
    ui.click_row(GridRowByGuid(db_id))
    ui.tab('Accounts')
    ui.expect(GridRowByGuid(db_account_id), f'No database account {db_account} found in database {db_name}')
    ui.click_row(GridRowByGuid(db_account_id))
    ui.tab('Settings')
    assert ui.check_exists(Label('Use a proxy account')) is False, '"Use proxy account" checkbox label is available ' \
                                                                   'in Database account settings page'
    logger.info('No "Use proxy account" checkbox label')
    ui.user_menu('Reload Rights')
    ui.tab('Permissions')
    assert ui.check_exists(Span(text='Login')) is False, f'Login column available in Database account permissions page.'
    logger.info('No "Login" column is available in database account permissions page.')
    assert ui.check_exists(
        Span(text='Portal Login')) is False, f'Login column available in Database account permissions page.'
    logger.info('No "Portal Login" column is available in database account permissions page.')
