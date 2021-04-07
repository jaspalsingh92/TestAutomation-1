import logging
import pytest
import copy
from Shared.UI.Centrify.selectors import Span, Div, TreeExpander, select_radio_button
from Shared.UI.Centrify.selectors import Button

logger = logging.getLogger('test')


@pytest.mark.ui
@pytest.mark.bhavna
@pytest.mark.pas_skip("Not applicable because we need empty tenant [no connector is existed]")
def test_trigger_no_systems_discovered_state(core_ui, pas_ad_discovery_config):
    """
    C3187 : Trigger "No Systems Discovered" state.
    :param core_session: Authenticated Centrify Session
    :param core_ui: Authenticated Centrify Browser Session
    """
    config_data = pas_ad_discovery_config
    test_data = copy.deepcopy(config_data)
    domain_name = test_data['domains'][0]['Name']
    organizational_unit = test_data['ad_profile_data'][0]['organization_unit'][0]
    ui = core_ui
    ui.user_menu('Getting Started')
    ui.step('Next')
    if ui.check_exists(Span("Centrify Connector")):
        ui.step('Next')
    expand_domain = ui.expect(TreeExpander(domain_name), "Expand tree option not available for mentioned Domain")
    expand_domain.try_click()
    ui.expect(select_radio_button(organizational_unit), "Not able to select Organizational Unit").try_click()
    ui.step('Next')
    assert ui.check_exists(Div("No Systems Discovered")), f"System Discovered in selected Organizational Unit"
    assert ui.check_exists(Div("We did not discover any systems within")), f"Failed to open 'We did not discover any " \
                                                                           f"systems within the selected domain...' " \
                                                                           f"page "
    assert ui.check_exists(Button("Choose Domain")), f"'Choose Domain' button not exist on modal page"
    assert ui.check_exists(Button("Next")), f"'Next' button not exist on modal page"
    assert ui.check_exists(Button("Cancel")), f"'Cancel' button not exist on modal page"
