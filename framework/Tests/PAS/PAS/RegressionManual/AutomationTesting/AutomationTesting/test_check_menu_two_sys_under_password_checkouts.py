import pytest
import logging
from Shared.API.infrastructure import ResourceManager
from Shared.UI.Centrify.SubSelectors.navigation import RenderedTab
from Shared.data_manipulation import DataManipulation

logger = logging.getLogger("test")


@pytest.mark.api_ui
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi_ui
def test_check_menu_two_sys_under_password_checkouts(core_session, list_of_created_systems, core_admin_ui,
                                                     cleanup_resources, cleanup_accounts):
    """
       TC:C2174 Check menu when choosing two systems under My Password Checkouts.
       :param:core_session: Returns Authenticated Centrify session.
       :param:list_of_created_systems:Container for created system.
       :param:core_admin_ui: Returns browser session.
       :param:cleanup_resources: Cleans up system.
       :param:cleanup_accounts:Cleans up accounts.

    """
    system_list = cleanup_resources[0]
    accounts_list = cleanup_accounts[0]

    # Creating multiple system and accounts.
    batches = ResourceManager.add_multiple_systems_with_accounts(core_session, 2, 1, list_of_created_systems)
    all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values([batches])
    assert len(
        ResourceManager.get_multi_added_system_ids(core_session, all_systems)) == 2, f"Failed to create multiple " \
                                                                                     f"system with accounts: API " \
                                                                                     f"response result: {batches} "
    assert len(ResourceManager.get_multi_added_account_ids(core_session,
                                                           all_systems)) == 2, f"Failed to create multiple system " \
                                                                               f"with accounts: API response result: " \
                                                                               f"{batches} "
    logger.info(f'Successfully Created multiple system with accounts.:{batches}')

    # Appending the created system and accounts id for cleanup.
    for all_account in all_accounts:
        accounts_list.append(all_account)
    for all_system in all_systems:
        system_list.append(all_system)

    # Checking out password for the account created.
    accounts_password_checkout = []
    for account_id in all_accounts:
        result, status = ResourceManager.check_out_password(core_session, 1, account_id, 'test checkout account')
        accounts_password_checkout.append(result['COID'])
        assert status, f'Failed to checkout password: API response result: {result}'

    # Getting the account name.
    accounts_name = []
    for account_id in all_accounts:
        result, success = ResourceManager.get_account_information(core_session, account_id)
        accounts_name.append(result["VaultAccount"]["Row"]['User'])

    # Validating "No actions available" after selecting two accounts from My Password Checkout Title in workspace.
    ui = core_admin_ui
    ui.navigate(("Workspace", "My Password Checkouts"))
    ui.switch_context(RenderedTab('My Password Checkouts'))
    ui.check_actions_by_guid([], accounts_password_checkout)
    logger.info('Successfully found "No actions available." after password account checkout.')
