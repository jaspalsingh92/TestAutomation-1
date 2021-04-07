import pytest
import logging
from Shared.UI.Centrify.SubSelectors.grids import FavoriteStar, FavoritedStar

logger = logging.getLogger("test")


@pytest.mark.api_ui
@pytest.mark.pas
@pytest.mark.pasapi_ui
@pytest.mark.bhavna
def test_check_star_icon_after_filter(core_session, pas_windows_setup, core_admin_ui):
    """
    TC : C2160 Check star icon after doing filter.
    :param core_session: Authenticated centrify session.
    :param:core_admin_ui: Returns browser Session.
    :param pas_windows_setup: Fixture for creating system and accounts.
    """
    # Adding a system with account.
    system_id, account_id, sys_info, connector_id, user_password = pas_windows_setup()

    # Launch UI.
    ui = core_admin_ui
    ui.navigate('Resources', 'Systems')
    ui.search(sys_info[0])
    ui.expect(FavoriteStar(), 'Failed to find the star icon').try_click()
    ui.expect(FavoritedStar(), 'Failed to find the star icon')
    logger.info("Successfully star of the systems is light up after click.")
    ui.input('search-field-input', "Win")
    ui.expect(FavoritedStar(), 'Failed to find the star icon')
    logger.info("Successfully star of the systems is light up after partial input.")
    ui.navigate(('Workspace', 'My System Accounts'))
    ui.navigate('Resources', 'Systems')
    ui.search(sys_info[0])
    ui.input('search-field-input', "Win")
    ui.expect(FavoritedStar(), 'Failed to find the star icon')
    logger.info("Successfully star of the systems is light up after navigating to workspace and input in search field.")
