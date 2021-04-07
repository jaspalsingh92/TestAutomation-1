import pytest
import logging
from Shared.UI.Centrify.SubSelectors.state import RestCallComplete
from Shared.UI.Centrify.selectors import LearnMore, GridRow

logger = logging.getLogger("test")


@pytest.mark.ui
@pytest.mark.pas
@pytest.mark.bhavna
def test_help_page_adding_active_directory_domain(domain_config_data, core_admin_ui):
    """
    Help page check for Adding active Directory domain accounts
    :return:
    """
    conf = domain_config_data
    name = conf['pas_bat_scenario1_infrastructure_data'][0]
    domain_name = name['Domain_name3']
    ui = core_admin_ui
    ui.navigate('Resources', 'Domains')
    ui.search(domain_name)
    ui.click_row(GridRow(domain_name))
    ui.tab('Accounts')
    ui.button('Learn more')
    ui.wait_for_tab_with_name("Adding Active Directory domain accounts")
    set_name = "To add a new account for a domain"
    learn_more_tab = ui.check_exists(LearnMore(set_name))
    assert learn_more_tab, f"Learn more' didn't open 'Adding Active Directory domain accounts accounts' page"
    logger.info('successfully open Adding Active Directory domain accounts accounts page in new tab')


@pytest.mark.ui
@pytest.mark.pas
@pytest.mark.bhavna
def test_help_page_check_domain_policies(domain_config_data, core_admin_ui):
    """
    Help page check for Domain policies, and Domain specific advance page by clicking learn more
    :return:
    """
    conf = domain_config_data
    name = conf['pas_bat_scenario1_infrastructure_data'][0]
    domain_name = name['Domain_name3']
    ui = core_admin_ui
    ui.navigate('Resources', 'Domains')
    ui.expect(RestCallComplete(), 'Expected rest call to complete that indicates UI is in stable state, but it did not')
    ui.search(domain_name)
    ui.click_row(GridRow(domain_name))
    ui.tab('Policy')
    ui.button('Learn more')
    ui.wait_for_tab_with_name("Setting domain-specific policies")
    set_name = "To set domain-specific policies"
    learn_more_tab = ui.check_exists(LearnMore(set_name))
    assert learn_more_tab,f"Learn more' did n't open 'Setting domain-specific policies' page"
    logger.info('successfully open Setting domain-specific policies page')
    ui.switch_first_tab()
    ui.tab("Advanced")
    ui.button('Learn more')
    ui.wait_for_tab_with_name("Setting domain-specific advanced options")
    set_name = "To set domain-specific advanced options"
    learn_more_tab = ui.check_exists(LearnMore(set_name))
    assert learn_more_tab, f"Learn more' did n't open 'Setting domain-specific advanced options' page"
    logger.info('successfully open Setting domain-specific advanced options page')

