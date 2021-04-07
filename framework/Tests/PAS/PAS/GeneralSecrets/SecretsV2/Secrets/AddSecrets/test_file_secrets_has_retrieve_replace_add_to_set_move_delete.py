import pytest
import logging
from Shared.API.secret import get_file_type_secret_contents
from Shared.UI.Centrify.SubSelectors.state import RestCallComplete

logger = logging.getLogger('test')


@pytest.mark.ui
@pytest.mark.pas
@pytest.mark.pasapi_ui
@pytest.mark.bhavna
def test_file_secrets_has_retrieve_replace_add_to_set_move_delete(core_session, added_secrets_file, core_admin_ui):

    """
    test method to check right click options available for file type secret

    :param core_session: Authenticated Centrify Session
    :param added_secrets_file: Fixture to add file type secrets
    :param core_admin_ui: Fixture to launch a browser session & yields it
    """
    added_secret_id = added_secrets_file
    # Getting details of file type secret added
    secret_result, secret_success, secret_date = get_file_type_secret_contents(core_session, added_secret_id)
    assert secret_success, f'Failed to get file type secret contents{secret_result}'
    logger.info(f'file type secret contents:{secret_result}')

    file_type_secret_name = secret_result['SecretName']
    ui = core_admin_ui
    ui.navigate('Resources', 'Secrets')
    ui.expect(RestCallComplete(), 'expected to for rest call to complete to validate UI state, but it did not.')
    ui.search(file_type_secret_name)

    list_to_be_verified = ['Retrieve', 'Replace', 'Add To Set', 'Move', 'Delete']
    # method to verify list of elements at right click
    ui.check_actions(list_to_be_verified, file_type_secret_name)
