import logging
import pytest
from Shared.endpoint_manager import EndPoints

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.bhavna
def test_getting_started_wizard_ui_check(core_session, domain_config_data):
    """
    C3179 : Getting Started Wizard UI check.
    :param core_session: Authenticated Centrify Session
    :param domain_config_data: To get the domain names from >> test_pas_bat_domain
    """
    domain = domain_config_data
    domain_list = domain['pas_bat_scenario1_infrastructure_data']
    # Get the discover systems from getting started
    request = core_session.apirequest(EndPoints.GETTING_STARTED)
    discover_systems = []
    for domains in request.json()['Result']:
        discover_systems.append(domains['Name'])
    # Connector should be up and running and all the domains are discovered
    assert discover_systems == [domain_list[0]['Domain_name2'],
                                domain_list[0]['Domain_name3'], domain_list[0]['Domain_name1']], \
        f'Connector is not configure and domains are not discovered in getting started wizard {discover_systems}'
    logger.info(f"Successfully discovered all the domains {discover_systems}")
