import pytest
import logging
from Shared.UI.Centrify.selectors import Div, HoverToolTip
from Shared.UI.Centrify.selectors import GridRowByGuid

logger = logging.getLogger("test")


@pytest.mark.ui
@pytest.mark.pas
@pytest.mark.pas_ui
@pytest.mark.bhavna
def test_check_accounts_checkout_lifetime_description(core_admin_ui, add_single_system):
    """
    C2099 : Check the account's checkout lifetime's description
    :param core_admin_ui:
    :param add_single_system:
    """
    ui = core_admin_ui
    added_system_id, sys_info = add_single_system
    ui.navigate('Resources', 'Systems')
    ui.search(sys_info[0])
    ui.click_row(GridRowByGuid(added_system_id))
    # Navigate Policy page
    ui.tab('Policy')
    ui.mouse_hover_element(HoverToolTip("Checkout lifetime"))
    assert ui.check_exists(Div("Specifies the number of minutes")), f"Could not be able to find the tool tip value " \
                                                                    f"Checkout lifetime"
