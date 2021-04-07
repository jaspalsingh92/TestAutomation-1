import pytest
import logging
from Shared.UI.Centrify.SubSelectors.modals import WarningModal
from Shared.UI.Centrify.selectors import GridRow
from Shared.API.infrastructure import ResourceManager
from Shared.UI.Centrify.selectors import Div

logger = logging.getLogger('test')


@pytest.mark.ui
@pytest.mark.pas
@pytest.mark.pas_ui
@pytest.mark.bhavna
def test_check_save_advanced_without_set_value(core_session, core_admin_ui):
    """
    C1578 : Check save advanced without set value
    :param core_session: Authenticated Centrify Session.
    :param core_admin_ui: Authenticated Centrify Browser Session.
    :return:
    """
    # Navigating to Advanced tab
    domain_details = ResourceManager.get_domains(core_session)
    core_admin_ui.navigate('Resources', 'Domains')
    core_admin_ui.click_row(GridRow(domain_details[0][0]['DomainName']))
    core_admin_ui.tab('Advanced')
    logger.info("Navigated to Resource -> Domain -> Advanced tab")
    expected_alert_message = "Please correct the errors in your form before submitting."
    core_admin_ui.select_option("AllowPasswordRotation", "Yes")
    logger.info("Changed 'Enable periodic password rotation' field to Yes")
    core_admin_ui.button('Save')
    core_admin_ui.switch_context(WarningModal())
    assert core_admin_ui.check_exists((Div(expected_alert_message))), f"pop up warning message for periodic password " \
                                                                      f"rotation is not " \
                                                                      f"same as : {expected_alert_message}"
    logger.info("Correct pop up warning message displayed for Periodic Password Rotation. ")
    core_admin_ui.close_modal('Close')
    core_admin_ui.select_option("AllowPasswordRotation", "--")
    logger.info("Changed 'Enable periodic password rotation' field to default")
    core_admin_ui.tab('Accounts')
    core_admin_ui.tab('Advanced')
    core_admin_ui.select_option("AllowPasswordHistoryCleanUp", "Yes")
    logger.info("Changed 'Enable periodic password history cleanup' field to Yes")
    core_admin_ui.button('Save')
    expected_alert_message = "Please correct the errors in your form before submitting."
    core_admin_ui.switch_context(WarningModal())
    assert core_admin_ui.check_exists((Div(expected_alert_message))), \
        f"Pop up warning message for periodic password history cleanup is not same as : {expected_alert_message}"
    logger.info("Correct pop up warning message displayed for Periodic Password History Cleanup. ")
    core_admin_ui.close_modal('Close')
