import pytest
import logging
from Shared.UI.Centrify.selectors import Modal, Button, Div

logger = logging.getLogger('test')


@pytest.mark.api_ui
@pytest.mark.pas
@pytest.mark.pasui
@pytest.mark.bhavna
def test_check_behaviour_of_check_out_password(pas_setup, core_admin_ui, pas_config):
    """
        Test case: C2190 Check the behavior of checkout password
        :param core_admin_ui: Authenticated Centrify Session.
        :param  pas_setup: Returns a fixture.
        :param  pas_config: Config file to get data from the yaml.
        """
    system_id, account_id, sys_info = pas_setup
    ui = core_admin_ui
    conf = pas_config
    expected_checkout_password = conf['Windows_infrastructure_data']['password']
    ui.navigate('Resources', 'Accounts')
    ui.search(sys_info[0])
    account_name = sys_info[4]
    ui.action('Checkout', account_name)
    ui.switch_context(Modal(account_name))
    ui.check_exists(Button("Show Password"))
    logger.info("password button shows successfully")
    ui.check_exists(Button("Copy Password"))
    logger.info("Copy clip button shows successfully")
    ui.button('Show Password')
    ui.expect(Div(expected_checkout_password), "Failed to get the expected password", time_to_wait=30)
    logger.info("Successfully shows password")
