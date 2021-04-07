import pytest
import logging
from Shared.UI.Centrify.SubSelectors.grids import GridRowByGuid
from Shared.UI.Centrify.SubSelectors.navigation import RenderedTab

logger = logging.getLogger("test")


@pytest.mark.api_ui
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi_ui
def test_check_account_actions(core_session, users_and_roles, pas_windows_setup):
    """
    TC:C2214 Check account's Actions.
    :param:core_session: Returns Authenticated Centrify session.
    :param users_and_roles: Fixture to manage roles and user.
    :param pas_windows_setup: Return a fixture.
    """

    # Creating a system and account.
    system_id, account_id, sys_info, connector_id, user_password = pas_windows_setup()

    # UI session with 'Privileged Access Service Power User' rights.
    ui = users_and_roles.get_ui_as_user("Privileged Access Service Administrator")

    # UI Launch
    ui.navigate('Resources', 'Systems')
    ui.search(sys_info[0])
    ui.click_row(GridRowByGuid(system_id))
    ui.switch_context(RenderedTab('Accounts'))
    ui.check_actions(['Add To Set', 'Verify Credential'], sys_info[4])
    logger.info('Successfully show accounts menu rather than system menu.')
