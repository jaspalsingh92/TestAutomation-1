import pytest
import logging
from Shared.UI.Centrify.selectors import Div
from Utils.guid import guid

logger = logging.getLogger("test")


@pytest.mark.ui
@pytest.mark.pas
@pytest.mark.pasui
@pytest.mark.bhavna
def test_add_unreachable_sys_hostname_as_dns(core_admin_ui):
    """
    TC:C2165 Add an unreachable system which hostname as DNS Name/IP Address.
    :param core_admin_ui: Return a browser session.
    """

    # Launch UI.
    ui = core_admin_ui
    ui.navigate('Resources', 'Systems')
    ui.launch_modal('Add System')

    # Trying to create system with unreachable DNS/IP Address.
    system_name = f'test_system{guid()}'
    ui.input('Name', system_name)
    ui.select_option('SystemProfileId', 'Windows')
    system_ip = f'fqdn{guid()}'
    ui.input('FQDN', system_ip)
    ui.step('Next >')
    ui.step('Next >')
    ui.step('Next >')
    ui.step('Finish')
    ui.expect(Div('Verification failed.'), 'Failed to find the error text.')
    logger.info('Successfully find the error text.')
