import pytest
import logging

from Shared.UI.Centrify.SubSelectors.navigation import ActiveMainContentArea
from Shared.UI.Centrify.selectors import LoadingMask, Getallsystem

logger = logging.getLogger("test")


@pytest.mark.ui
@pytest.mark.bhavna
@pytest.mark.pas
def test_check_systems_page(core_admin_ui):
    """
    Test Case ID: C2092
    Check systems page
    Test Case is to check systems page should not load after re-visiting.
    :param core_admin_ui: Authenticates Centrify UI session.
    """
    ui = core_admin_ui
    ui.navigate('Resources', 'Systems')
    ui.navigate('Resources', 'Domains')
    ui.navigate('Resources', 'Systems', check_rendered_tab=False)
    ui.switch_context(ActiveMainContentArea())
    systems = ui._searchAndExpectMany(Getallsystem(),
                                      "systems are not found")
    no_of_systems = [value.text for value in systems]
    assert len(no_of_systems) > 0, 'system page is not loading properly'
    logger.info("system page is loading and user able see all system without loading.")
