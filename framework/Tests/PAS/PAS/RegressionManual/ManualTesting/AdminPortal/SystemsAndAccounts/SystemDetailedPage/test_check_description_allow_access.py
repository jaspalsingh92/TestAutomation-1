from Shared.UI.Centrify.selectors import GridRowByGuid, Label, HoverToolTip, Div
import pytest
import logging

logger = logging.getLogger("test")


@pytest.mark.ui
@pytest.mark.pasapi_ui
@pytest.mark.bhavna
@pytest.mark.pas
def test_check_description_allow_access(core_admin_ui, add_single_system):
    """
    Test Case ID: C2094
    Test Case Description: Check description for Allow access from a public network
    :param core_admin_ui: Authenticates Centrify Ui session
    :param add_single_system: Creates a single system
    """

    system_id, system_info = add_single_system
    system_name = system_info[0]
    ui = core_admin_ui
    ui.navigate('Resources', 'Systems')
    ui.search(system_name)
    ui.click_row(GridRowByGuid(system_id))
    ui.tab('Policy')
    allow_access_description = "Allow access from a public network (web client only)"

    # Checking the 'allow_access_description' is present in Label tag
    assert ui.check_exists(Label(allow_access_description)), f'Text: {allow_access_description} is not present in page.'
    logger.info(f'Text: {allow_access_description} is present in page.')

    system_policy_tooltip = ui.expect(HoverToolTip(allow_access_description),
                                      expectation_message='Expected to find '
                                                          'System Policy Tooltip'
                                                          ' but it did not')
    system_policy_tooltip.mouse_hover()
    expected_text = 'Specifies whether remote connections are allowed from a public network for a selected system.'

    # Checking the 'expected_text' is present in Div tag
    ui.expect(Div(expected_text), expectation_message=f'expected to find Text: {expected_text}, but it did not.')
    logger.info(f'Expected Text: {expected_text} is present inside tooltip.')
