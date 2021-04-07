import pytest
import logging
from Shared.API.infrastructure import ResourceManager
from Shared.UI.Centrify.selectors import Modal, ConfirmModal, InfoModal, Div
from Shared.data_manipulation import DataManipulation
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.api_ui
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi_ui
def test_ui_check_bulk_delete_account_scheduled(core_session, core_admin_ui, list_of_created_systems):
    """
    Test case: C3088
               :param core_session: Returns API session
               :param core_admin_ui: Centrify admin Ui session
               :param list_of_created_systems: creating a empty list of created systems.
               """
    account_name_prefix = f'account_test{guid()}'

    # adding multiple systems with accounts
    result = ResourceManager.add_multiple_systems_with_accounts(core_session, 1, 2, list_of_created_systems,
                                                                user_prefix=account_name_prefix)

    # arranging the results in the lists
    all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values([result])
    ui = core_admin_ui
    ui.navigate('Resources', 'Accounts')
    account_names = []
    for account in all_accounts:
        # getting the account information
        query_result, query_success = ResourceManager.get_account_information(core_session, account)
        account_names.append(query_result['VaultAccount']['Row']['User'])

    ui.search(account_name_prefix)
    ui.action('Delete accounts', account_names)
    ui.switch_context(Modal('Bulk Account Delete'))
    ui.uncheck("SaveSecret")
    ui.button('Delete')
    ui.switch_context(ConfirmModal())
    ui.button('Yes')
    ui.switch_context(InfoModal())
    ui.expect(
        Div("A delete operation has been scheduled. You will receive an e-mail when the operation has been completed."),
        "Expecting a info popup for delete schedule")
    logger.info("Popup with delete operation has been scheduled appeared")
    ui.button('Close')
    result, success = ResourceManager.del_multiple_systems(core_session, all_systems)
    assert success is True, 'Delete systems job failed when expected success'
    logger.info(f"Delete systems job executed successfully {result}")
