import pytest
import logging
from Shared.API.redrock import RedrockController
from Shared.API.infrastructure import ResourceManager
from Utils.config_loader import Configs

logger = logging.getLogger("test")


@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_check_ui_on_subnet_mapping_page(core_session, cleanup_system_subnet_mapping):
    """
    TC:C2197 Check UI on Subnet Mappings page.
        1) Login Admin Portal as cloud admin
        2) Add System subnet mapping by calling API add_system_subnet_mapping
        3) Checking through UI for assertion

    :param core_session: Authenticated Centrify session.
    :param core_admin_ui: Authenticated Centrify browser session.
    :param: cleanup_system_subnet_mapping: cleanup for created system subnet.
    """
    subnet = Configs.get_environment_node('update_discovery_profile',
                                          'automation_main')['port_scan_scope']['subnet_mask']
    subnet_list = cleanup_system_subnet_mapping

    # Adding System Subnet Mapping.
    result, success, message = ResourceManager.add_system_subnet_mapping(core_session, subnet, chooseConnector="on")
    system_subnet_id = result['ID']
    assert success, f'Failed to add System subnet mapping with API response: {message}'
    subnet_list.append(system_subnet_id)
    logger.info(f"System subnet mapping added successfully, {system_subnet_id}")

    # Checking on ui for assertion
    query = "select * from ProxyGroup"
    results = RedrockController.get_result_rows(RedrockController.redrock_query(core_session, query))
    assert results[0]['Subnet'] == subnet, \
        f'Failed to see the detail of System Subnet Mapping with API response: {message}'
