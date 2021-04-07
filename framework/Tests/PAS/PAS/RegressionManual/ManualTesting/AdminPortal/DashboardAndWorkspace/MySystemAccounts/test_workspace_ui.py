import pytest
import logging
from Shared.UI.Centrify.selectors import Span

logger = logging.getLogger('test')


@pytest.mark.ui
@pytest.mark.bhavna
@pytest.mark.pasui
def test_workspace_ui_check(core_admin_ui):
    """
    Test case: C2058
    :param core_admin_ui: Authenticated Centrify Ui session
    """
    # list of Grid titles in workspace page, can be modified if more grids added of anything removed, test execution will remain safe
    workspace_grid = ['My Favorites', 'My Password Checkouts', 'My System Accounts', 'My Active Sessions',
                      'My Expiring Checkouts', 'My Total Checkouts', 'My Total Sessions', 'Recent Systems']

    # list of grid column names, can add more grid columns in future, test execution will remain same.
    columns = {"my_system_accounts": ['Target', 'User Name', 'Credential Type'], }
    ui = core_admin_ui
    ui.navigate(('Workspace', 'My Favorites'))
    for grid in workspace_grid:
        ui.expect(Span(grid), f'No grid found for {grid}')
        logger.info(f"Grid found for {grid}")
    for column_header, column_name in columns.items():
        for headers in column_name:
            ui.expect(Span(headers), f'No {headers} column found in {column_header}.')
            logger.info(f"{headers} column found in {column_header}.")
