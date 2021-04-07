import pytest
import logging
from Shared.UI.Centrify.SubSelectors.grids import GridRowByGuid
from Shared.UI.Centrify.SubSelectors.navigation import ActiveMainContentArea
from Shared.UI.Centrify.selectors import Div, PageWithTitle, HoverToolTip, HoverCkeckboxToolTip

logger = logging.getLogger("test")


@pytest.mark.ui
@pytest.mark.pas_failed
@pytest.mark.bhavna
def test_help_page_and_tip_message_check(core_admin_ui, add_single_system):
    """
    C1546 : Help page and tip message check
    :param core_admin_ui: Authenticated Centrify Browser Session
    :param add_single_system: Add system and return system details.
    """
    ui = core_admin_ui
    added_system_id, sys_info = add_single_system
    ui.navigate('Resources', 'Systems')
    ui.search(sys_info[0])
    ui.click_row(GridRowByGuid(added_system_id))
    # Navigate Policy page
    ui.tab('Policy')
    ui.switch_context(ActiveMainContentArea())
    ui.button('Learn more')
    ui.wait_for_tab_with_name("Setting system‑specific policies", max_seconds_to_wait=10)
    assert ui.check_exists(PageWithTitle("Setting system‑specific policies")), "Setting system‑specific policies, " \
                                                                               "page not found. "
    logger.info("Clicking on 'Learn More' button launched 'Setting system‑specific policies' tab successfully")
    ui.switch_first_tab()
    ui.mouse_hover_element(HoverToolTip("Allow access from a public"))
    assert ui.check_exists(Div("Specifies whether remote connections")), "Could not able to find the tool tip value " \
                                                                         "for Allow access from a public network "
    logger.info("'Specifies whether remote connections' tool tip message found")
    ui.mouse_hover_element(HoverToolTip("Checkout lifetime"))
    assert ui.check_exists(Div("Specifies the number of minutes")), "Could not able to find the tool tip value for " \
                                                                    "Checkout lifetime "
    logger.info("'Specifies the number of minutes' tool tip message found")
    # Navigate Advanced page
    ui.tab('Advanced')
    ui.switch_context(ActiveMainContentArea())
    ui.button('Learn more')
    ui.wait_for_tab_with_name("Setting system‑specific advanced options", max_seconds_to_wait=10)
    assert ui.check_exists(PageWithTitle("Setting system‑specific advanced options")), "Setting system‑specific " \
                                                                                       "advanced options, " \
                                                                                       "page not found "
    logger.info("Clicking on 'Learn More' button launched 'Setting system‑specific advanced options' tab successfully")
    ui.switch_first_tab()

    ui.mouse_hover_element(HoverToolTip("Allow multiple password"))
    assert ui.check_exists(Div("Specifies whether multiple users")), "Could not able to find the tool tip value for " \
                                                                     "Multiple password checkouts"
    logger.info("'Specifies whether multiple users' tool tip message found")

    ui.mouse_hover_element(HoverToolTip("password history cleanup"))
    assert ui.check_exists(Div("Specifies whether retired passwords"), 30), "Could not able to find the tool tip " \
                                                                            "value for Password History Cleanup"
    logger.info("'Specifies whether retired passwords' tool tip message found")

    ui.mouse_hover_element(HoverToolTip("Enable password rotation"))
    assert ui.check_exists(Div("Specifies whether managed password")), "Could not able to find the tool tip value " \
                                                                       "for Password rotation after checkin "
    logger.info("'Specifies whether managed password' tool tip message found")
    ui.mouse_hover_element(HoverToolTip("Enable periodic password"))
    assert ui.check_exists(Div("Specifies whether managed password")), "Could not able to find the tool tip value " \
                                                                       "for Periodic password rotation "
    logger.info("'Specifies whether managed password' tool tip message found")
    ui.mouse_hover_element(HoverToolTip("Minimum Password Age"))
    assert ui.check_exists(Div("Minimum amount of days old")), "Could not able to find the tool tip value for " \
                                                               "Minimum Password Age "
    logger.info("'Minimum amount of days old' tool tip message found")
    ui.navigate('Settings', 'Resources', 'Security', 'Security Settings', False)
    ui.switch_context(ActiveMainContentArea())
    ui.button('Learn more')
    ui.wait_for_tab_with_name("Setting global security options", 20)
    assert ui.check_exists(PageWithTitle("Setting global security options"), 20), "Setting global security options, " \
                                                                                  "page not found. "
    logger.info("Clicking on 'Learn More' button launched 'Setting global security options' tab successfully")
    ui.switch_first_tab()

    ui.mouse_hover_element(HoverCkeckboxToolTip("Enable periodic password history cleanup"))
    assert ui.check_exists(Div("Specifies whether retired passwords"), 20), "Could not able to find the tool tip " \
                                                                            "value for Password history cleanup "
    logger.info("'Specifies whether retired passwords' tool tip message found")

    ui.mouse_hover_element(HoverCkeckboxToolTip("password rotation after checkin"))
    assert ui.check_exists(Div("password should be rotated after it's checked"), 20), "Could not able to find the " \
                                                                                      "tool tip value for Password " \
                                                                                      "rotation after checkin "
    logger.info("'Password should be rotated after it's checked' tool tip message found")

    ui.mouse_hover_element(HoverCkeckboxToolTip("password rotation at specified interval"))
    assert ui.check_exists(Div("password should be rotated periodically"), 20), "Could not able to find the tool " \
                                                                                "tip value for Password rotation at " \
                                                                                "specified interval "
    logger.info("'Password should be rotated periodically' tool tip message found")

    ui.mouse_hover_element(HoverToolTip("password checkout lifetime"))
    assert ui.check_exists(Div("Specifies the number of minutes"), 20), "Could not able to find the tool tip value " \
                                                                        "for Default account password checkout " \
                                                                        "lifetime "
    logger.info("'Specifies the number of minutes' tool tip message found")

    ui.mouse_hover_element(HoverToolTip("Minimum Password Age"))
    assert ui.check_exists(Div("Minimum amount of days old"), 20), "Could not able to find the tool tip value for " \
                                                                   "Minimum Password Age "
    logger.info("'Minimum amount of days old' tool tip message found")

    ui.mouse_hover_element(HoverToolTip("SSH Gateway"))
    assert ui.check_exists(Div("message to users at SSH session login"), 20), "Could not able to find the tool tip " \
                                                                              "value for SSH Gateway Banner "
    logger.info("'Message to users at SSH session login' tool tip message found")

    ui.mouse_hover_element(HoverCkeckboxToolTip("requests for password checkouts"))
    assert ui.check_exists(Div("allows users to request permanent access"), 20), "Could not able to find the tool " \
                                                                                 "tip value for Requests for " \
                                                                                 "password checkouts "
    logger.info("'When enabled, allows users to request permanent access passwords' tool tip message found")

    ui.mouse_hover_element(HoverCkeckboxToolTip("requests for login"))
    assert ui.check_exists(Div("allows users to request permanent login access"), 20), "Could not able to find the " \
                                                                                       "tool tip value for Requests " \
                                                                                       "for login "
    logger.info("'allows users to request permanent login access' tool tip message found")

    ui.mouse_hover_element(HoverCkeckboxToolTip("Allow multiple password checkouts"))
    assert ui.check_exists(Div("Specifies whether multiple users can"), 20), "Could not able to find the tool tip " \
                                                                             "value for Allow multiple password " \
                                                                             "checkouts "
    logger.info("'Specifies whether multiple users can' tool tip message found")

    ui.mouse_hover_element(HoverCkeckboxToolTip("Allow access from"))
    assert ui.check_exists(Div("Specifies whether remote connections"), 20), "Could not able to find the tool tip " \
                                                                             "value for Allow access from a public" \
                                                                             " network "
    logger.info("'Specifies whether remote connections' tool tip message found")
