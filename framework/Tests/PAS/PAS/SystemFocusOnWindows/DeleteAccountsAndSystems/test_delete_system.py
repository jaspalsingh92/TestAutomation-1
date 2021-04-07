import logging
import pytest
from Shared.API.redrock import RedrockController
from Shared.UI.Centrify.SubSelectors.grids import GridRowByGuid
from Shared.UI.Centrify.selectors import TextField

logger = logging.getLogger("test")


@pytest.mark.api_ui
@pytest.mark.pas
@pytest.mark.pasapi_ui
@pytest.mark.bhavna
def test_system_delete(pas_setup, core_admin_ui, core_session):
    """C2571 Delete systems
            Steps:
                Pre: Create system with 1 manage account hand
                1. Try to delete system
                    -Assert Failure
                2.check on the SecretName
                   -Assert Failure
        """

    ui = core_admin_ui
    # Step 1: create a system along with on account
    added_system_id, account_id, sys_info = pas_setup
    logger.info(f"System: {sys_info[0]} successfully added with UUID: {added_system_id} and account: {sys_info[4]} "
                f"with UUID: {account_id} associated with it.")
    ui.navigate('Resources', 'Systems')
    ui.search(sys_info[0])
    ui.right_click_action(GridRowByGuid(added_system_id), 'Delete')
    ui.switch_context('System Delete')
    email_id = ui._searchAndExpect(TextField('SecretName'), "Not able to get the data from textbox")
    get_email_id = email_id.get_value_from_attribute('value')
    ui.remove_context()
    ui.button('Delete')

    # Step 2: Fetch the all secrets from data vault and compare
    query = 'Select * FROM DataVault'
    rows = RedrockController.get_result_rows(RedrockController.redrock_query(core_session, query))
    delete = []
    for row in rows:
        if row['SecretName'].find(get_email_id) == -1:
            delete.append(row['ParentPath'])
        else:
            logger.info(f"no data found:{delete}")
    assert 'Bulk Delete' in delete, "User not deleted system and there is no data"
    logger.info(f'Successfully deleted a system and generated bulk delete secret')
