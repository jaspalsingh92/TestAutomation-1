import pytest
import logging
from Shared.UI.Centrify.SubSelectors.forms import DisabledCheckbox, DisabledTextBox, ReadOnlyTextField
from Shared.UI.Centrify.SubSelectors.grids import GridRowByGuid
from Shared.UI.Centrify.SubSelectors.navigation import ActiveMainContentArea

logger = logging.getLogger("test")


@pytest.mark.ui
@pytest.mark.pas
def test_check_ui_for_privilege_service_power_user_right(add_single_system, users_and_roles):
    """
    C1545 : UI Check for Privilege Service Power User right
    :param users_and_roles: Gets user and role on demand.
    :param add_single_system: Add system and return system details.
    """
    ui = users_and_roles.get_ui_as_user("Privileged Access Service Power User")
    added_system_id, sys_info = add_single_system
    ui.navigate('Resources', 'Systems')
    ui.search(sys_info[0])
    ui.click_row(GridRowByGuid(added_system_id))

    # Navigate Policy page
    ui.tab('Policy')
    assert ui.expect(DisabledTextBox("DefaultCheckoutTime"), 'Drop down Element "DefaultCheckoutTime" is not disabled')
    logger.info("'DefaultCheckoutTime' Element in Policy page are gray out")
    assert ui.expect(DisabledTextBox("AllowRemote"), 'Drop down Element "AllowRemote" is not disabled')
    logger.info("'AllowRemote' Element in Policy page are gray out")

    # Navigate Global Settings page
    ui.navigate('Settings', 'Resources', 'Security', 'Security Settings', False)
    ui.switch_context(ActiveMainContentArea())
    assert ui.expect(DisabledCheckbox("AllowRemote"), 'Check box Element "AllowRemote" is not disabled')
    logger.info("Allow Remote check box is grey out in Global Security Setting Page")
    assert ui.expect(DisabledCheckbox("AllowMultipleCheckouts"), 'Check box Element "AllowMultipleCheckouts" '
                                                                 'is not disabled')
    logger.info("Allow Multiple Checkouts check box is grey out in Global Security Setting Page")
    assert ui.expect(DisabledCheckbox("AllowPermanentCheckoutWorkflow"), 'Check box Element '
                                                                         '"AllowPermanentCheckoutWorkflow" '
                                                                         'is not disabled')
    logger.info("Allow Permanent Checkout Workflow check box is grey out in Global Security Setting Page")
    assert ui.expect(DisabledCheckbox("AllowPermanentLoginWorkflow"), 'Check box Element "AllowPermanentLoginWorkflow"'
                                                                      ' is not disabled')
    logger.info("Allow Permanent Login Workflow check box is grey out in Global Security Setting Page")
    assert ui.expect(DisabledCheckbox("AllowPasswordHistoryCleanUp"), 'Check box Element "AllowPasswordHistoryCleanUp"'
                                                                      ' is not disabled')
    logger.info("Allow Password History CleanUp check box is grey out in Global Security Setting Page")
    assert ui.expect(DisabledCheckbox("AllowPasswordRotation"), 'Check box Element "AllowPasswordRotation"'
                                                                ' is not disabled')
    logger.info("Allow Password Rotation check box is grey out in Global Security Setting Page")
    assert ui.expect(DisabledCheckbox("AllowPasswordRotationAfterCheckin"), 'Check box Element '
                                                                            '"AllowPasswordRotationAfterCheckin" '
                                                                            'is not disabled')
    logger.info("Allow Password  Rotation After Checkin check box is grey out in Global Security Setting Page")
    assert ui.expect(DisabledCheckbox("SSHGatewayCustomBannerEnabled"), 'Check box Element '
                                                                        '"SSHGatewayCustomBannerEnabled" '
                                                                        'is not disabled')
    logger.info("SSH Gateway Custom Banner Enabled check box is grey out in Global Security Setting Page")
    assert ui.expect(DisabledTextBox("DefaultCheckoutTime"), 'Text box Element "DefaultCheckoutTime" is not disabled')
    logger.info("Default Checkout Time text box is grey out in Global Security Setting Page")
    assert ui.expect(ReadOnlyTextField("PasswordHistoryCleanUpDuration"), 'Text Field Element '
                                                                          '"PasswordHistoryCleanUpDuration" '
                                                                          'is not disabled')
    logger.info("Password History CleanUp Duration Text Field is grey out in Global Security Setting Page")
    assert ui.expect(DisabledTextBox("PasswordRotateDuration"), 'Text box Element "PasswordRotateDuration" '
                                                                'is not disabled')
    logger.info("Password Rotate Duration text box is grey out in Global Security Setting Page")
    assert ui.expect(ReadOnlyTextField("MinimumPasswordAge"), 'Text field Element "MinimumPasswordAge" is '
                                                              'not disabled')
    logger.info("Minimum Password Age text field is grey out in Global Security Setting Page")
