import pytest
import logging
from Shared.API.infrastructure import ResourceManager
from Shared.UI.Centrify.selectors import Modal, Div, Label
from Shared.data_manipulation import DataManipulation
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.api_ui
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi_ui
def test_ui_check_bulk_delete_account_caution(core_session, core_admin_ui, list_of_created_systems):
    """
         Test case: C3086
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
    ui.expect(Label("Save password to secret"), "Expected to see the label of save the password")
    ui.expect(Div("Deleting an account means we will no longer know the password."
                  " Saving deleted account passwords to a secret is recommended until you are sure they are "
                  "no longer needed."),
              "Expected to see the Caution message.")
    result, success = ResourceManager.del_multiple_systems(core_session, all_systems)
    assert success is True, f'Delete systems job failed when expected success'
    logger.info(f"Delete systems job executed successfully {result}")
    result_acc, success_acc = ResourceManager.del_multiple_accounts(core_session, all_accounts)
    assert success_acc, f"Api did not complete successfully for bulk account delete MSG:{result_acc}"
