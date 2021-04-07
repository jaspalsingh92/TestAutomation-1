import logging
import pytest

from Shared.API.sets import SetsManager
from Shared.UI.Centrify.SubSelectors.navigation import ActiveMainContentArea
from Shared.UI.Centrify.SubSelectors.sets import SetRow
from Shared.UI.Centrify.selectors import Button, HiddenButton
from Utils.guid import guid

logger = logging.getLogger("test")

pytestmark = [pytest.mark.pas, pytest.mark.ui, pytest.mark.sysadminsetoption]


@pytest.mark.parametrize('user_rights', ['Privileged Access Service Administrator'], indirect=True)
def test_set_visibility_of_non_admin_set_from_ui(cds_session, set_cleaner, core_ui):

    non_admin_session, api_user = cds_session
    ui = core_ui

    set_name = f"test_visibility_{guid()}"

    success, set_id = SetsManager.create_manual_collection(non_admin_session, set_name, 'Server', object_ids=None)
    assert success is True, f'Failed to create manual set {set_id}'
    set_cleaner.append(set_id)

    ui.navigate('Resources', 'Systems')

    # this will ensure that the set container is visible and updated

    ui.expect(SetRow("All Systems"), "All systems set should be visible")
    ui.missing(SetRow(set_name), f"{set_name} should not be visible")
    assert ui.check_exists(Button("Show All Sets")), "Show All Sets link should be visible"
    assert not ui.check_exists(Button("Show My Sets"), time_to_wait=0), "Show My Sets button should be hidden"

    ui.button("Show All Sets")

    ui.expect_disappear(SetRow(set_name), f'{set_name} did not disappear when it should have')
    assert ui.check_exists(Button("Show My Sets"), 10), "Show My Sets button should be visible"

    ui.button("Show My Sets")

    assert ui.check_exists(Button("Show All Sets"), 10), "Show All Sets button should be visible"
    ui.missing(SetRow(set_name), f"{set_name} should not be visible")

    # ensure button does not erroneously appear

    ui.navigate('Access', 'Users')
    show_all_button = Button("Show All Sets").inside(ActiveMainContentArea())
    show_my_button = Button("Show My Sets").inside(ActiveMainContentArea())
    ui.missing(show_all_button, f'Show All Sets Button should not be present on users tab')
    ui.missing(show_my_button, f'Show My Sets Button should not be present on users tab')


def test_show_all_not_visible_for_non_sys_admin_in_ui(core_pas_admin_ui):
    ui = core_pas_admin_ui
    ui.navigate('Resources', 'Systems')
    ui.expect(SetRow("All Systems"), "All systems set should be visible")
    assert not ui.check_exists(Button("Show My Sets"), time_to_wait=0), "Show My Sets button should be hidden"
    ui.hidden(Button("Show All Sets"), "Show all sets button should be hidden")
