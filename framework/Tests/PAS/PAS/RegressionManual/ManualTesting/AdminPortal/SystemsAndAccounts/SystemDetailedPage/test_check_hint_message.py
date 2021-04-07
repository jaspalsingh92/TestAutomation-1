from Shared.UI.Centrify.selectors import DarkTooltip, GridRowByGuid, TooltipSystemSettings
import pytest
import logging

logger = logging.getLogger("test")


@pytest.mark.ui
@pytest.mark.bhavna
def test_check_hint_message(core_admin_ui, pas_setup, pas_config):
    """
    Test Case ID: C2095
    :param core_admin_ui: Authenticates Centrify Ui session.
    :param pas_setup: Creates Windows System and Account.
    """

    system_id, account_id, sys_info = pas_setup
    system_name = sys_info[0]
    ui = core_admin_ui
    ui.navigate('Resources', 'Systems')
    ui.search(system_name)
    ui.click_row(GridRowByGuid(system_id))
    ui.tab('Settings')
    proxy_account_text = "Use a proxy account to manage this system."
    hover_mouse = ui.expect(TooltipSystemSettings(proxy_account_text),
                            expectation_message='Expected to find Tooltip but it '
                                                'did not')
    hover_mouse.mouse_hover()
    tooltip_expected_text = "The proxy account must be either a member of the local administration group or the" \
                            " 'Remote Management Users' group (who has access to PowerShell through WinRM). If the" \
                            " system is joined to a zone, the proxy account must also have the right 'PowerShell " \
                            "remote access is allowed' (from Access Manager)."

    ui.inner_text_of_element(DarkTooltip(), expectation_message=tooltip_expected_text,
                             warning_message='Failed to find the tooltip message')
    logger.info(f'Tooltip icon contains:{tooltip_expected_text}')
