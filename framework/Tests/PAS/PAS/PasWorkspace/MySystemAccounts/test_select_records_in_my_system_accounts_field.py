import pytest
import logging
from Shared.API.infrastructure import ResourceManager
from Shared.API.users import UserManager
from Shared.UI.Centrify.SubSelectors.grids import GridRowByGuid


logger = logging.getLogger('test')


@pytest.mark.api_ui
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi_ui
def test_select_two_records_in_my_system_account_field(core_session, create_resources_with_accounts, core_admin_ui, cleanup_accounts):

    """
    Test case id : C14833
    :param core_session: Centrify session
    :param create_resources_with_accounts: fixture to create system with accounts
    :param core_admin_ui: Ui session
    :param cleanup_accounts: cleanup fixture for accounts after test completion
    """
    sys = create_resources_with_accounts(core_session, 1, 'Windows', 2)[0]
    acc = sys['Accounts']
    sys1 = acc[0]["User"]
    sys2 = acc[1]["User"]

    ui = core_admin_ui
    admin_user_uuid = UserManager.get_user_id(core_session, ui.user.centrify_user["Username"])

    rights = "View,Login,UserPortalLogin"
    for account in range(len(acc)):
        result, status = ResourceManager.assign_account_permissions(core_session, rights, ui.user.centrify_user["Username"],
                                                                    admin_user_uuid,
                                                                    pvid=acc[account]['ID'])
        assert status, f'failed to assign {rights} permission to cloud admin {ui.user.centrify_user["Username"]}. returned result is: {result}'
        logger.info(f'rights {rights} are provided to {ui.user.centrify_user["Username"]} for account {acc[account]["Name"]}')

    ui.user_menu('Reload Rights')
    ui.navigate(('Workspace', 'My System Accounts'))

    # Expecting to find both added systems in My System Account List in workspace
    ui.expect(GridRowByGuid(acc[0]["ID"]), f'Expected to find system {sys1} in My System Account but did not')
    ui.expect(GridRowByGuid(acc[1]["ID"]), f'Expected to find system {sys2} in My System Account but did not')
    ui.check_actions(['Rotate credentials', 'Manage Accounts', 'Add To Set'], [sys1, sys2])
    logger.info('Add To set option is available')
