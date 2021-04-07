import time

import pytest
import logging

from Shared.API.infrastructure import ResourceManager
from Shared.API.redrock import RedrockController
from Shared.API.sets import SetsManager
from Shared.UI.Centrify.selectors import Modal, GridCell, NoTitleModal, InfoModal
from Shared.data_manipulation import DataManipulation
from Utils.guid import guid

pytestmark = [pytest.mark.ui, pytest.mark.cps, pytest.mark.bulk_system_unenroll]

logger = logging.getLogger('test')


@pytest.mark.api_ui
@pytest.mark.pas
def test_bulk_system_unenrolls_manually_from_set(core_session, core_admin_ui, create_manual_set,
                                                 test_four_virtual_aapm_agents):
    agents, server_prefix = test_four_virtual_aapm_agents
    agent_ids, server_ids, names_of_servers = _setup_agents(core_session, agents)
    # Make sure aapm is enabled
    _wait_for_systems_validation(core_session, agent_ids, True)

    # enable paswdRecon on first system and last system
    result = RedrockController.get_system(core_session, server_ids[0])
    assert len(result) != 0
    system = result[0]["Row"]
    ResourceManager.update_system(core_session, server_ids[0], system["Name"], system["FQDN"],
                                  system["ComputerClass"],
                                  allowautomaticlocalaccountmaintenance=True)

    result = RedrockController.get_system(core_session, server_ids[3])
    assert len(result) != 0
    system = result[0]["Row"]
    ResourceManager.update_system(core_session, server_ids[3], system["Name"], system["FQDN"],
                                  system["ComputerClass"],
                                  allowautomaticlocalaccountmaintenance=True)

    # Non-ui stuff, create a custom set, and all the new systems to that set.
    manual_set = create_manual_set(core_session, "Server")
    update_success, update_result = SetsManager.update_members_collection(core_session, 'add', server_ids, 'Server',
                                                                          manual_set['ID'])
    assert update_success, f"Failed to add resources {server_ids} to Set {manual_set['Name']}"

    ui = core_admin_ui
    ui.navigate('Resources', 'Systems')
    ui.search(server_prefix)

    ui.set_action(manual_set['Name'], "Unenroll Systems")

    ui.switch_context(Modal('Bulk System Unenroll'))
    ui.button('Unenroll')
    ui.switch_context(NoTitleModal())
    ui.button('Close')

    _wait_for_systems_validation(core_session, agent_ids[1:3], False)
    _validate_aapm_agent_details(core_session, agent_ids[:1], True)
    _validate_aapm_agent_details(core_session, agent_ids[3:], True)

    # Now lets re-enroll and enable aapm on 1 and 2 systems and run the unenroll operation
    # with SkipIfAgentReconciliationEnabled unchecked
    # Expected: Both systems should successfully unenroll

    _setup_agents(core_session, agents)

    # Make sure aapm is enabled on all systems
    _validate_aapm_agent_details(core_session, agent_ids, True)

    ui = core_admin_ui
    ui.navigate('Resources', 'Systems')
    ui.search(server_prefix)

    ui.set_action(manual_set['Name'], "Unenroll Systems")

    ui.switch_context(Modal('Bulk System Unenroll'))
    ui.uncheck("SkipIfAgentReconciliationEnabled")
    ui.button('Unenroll')
    ui.switch_context(NoTitleModal())
    ui.button('Close')

    # Make sure aapm is disabled on both systems
    _wait_for_systems_validation(core_session, agent_ids, False)


@pytest.mark.api_ui
@pytest.mark.pas
def test_bulk_system_unenrolls_manually(core_session, core_ui, test_four_virtual_aapm_agents):
    agents, server_prefix = test_four_virtual_aapm_agents
    agent_ids, server_ids, names_of_servers = _setup_agents(core_session, agents)

    # Make sure aapm is enabled
    _validate_aapm_agent_details(core_session, agent_ids, True)

    # enable paswdRecon on first and last system
    result = RedrockController.get_system(core_session, server_ids[0])
    system = result[0]["Row"]
    ResourceManager.update_system(core_session, server_ids[0], system["Name"], system["FQDN"],
                                  system["ComputerClass"],
                                  allowautomaticlocalaccountmaintenance=True)

    result = RedrockController.get_system(core_session, server_ids[3])
    assert len(result) != 0
    system = result[0]["Row"]
    ResourceManager.update_system(core_session, server_ids[3], system["Name"], system["FQDN"],
                                  system["ComputerClass"],
                                  allowautomaticlocalaccountmaintenance=True)

    ui = core_ui
    ui.navigate('Resources', 'Systems')
    ui.search(server_prefix)

    for name in names_of_servers:
        assert ui.check_exists(GridCell(name)), "Missing server from view " + name

    ui.action('Unenroll Systems', names_of_servers)
    core_ui.switch_context(Modal('Bulk System Unenroll'))
    core_ui.button('Unenroll')
    core_ui.switch_context(InfoModal())
    core_ui.button('Close')

    _wait_for_systems_validation(core_session, agent_ids[1:3], False)
    _validate_aapm_agent_details(core_session, agent_ids[:1], True)
    _validate_aapm_agent_details(core_session, agent_ids[3:], True)

    # Now lets re-enroll and enable aapm on 1 and 2 systems and run the unenroll operation
    # with SkipIfAgentReconciliationEnabled unchecked
    # Expected: Both systems should successfully unenroll

    _setup_agents(core_session, agents)

    # Make sure aapm is enabled on all systems
    _validate_aapm_agent_details(core_session, agent_ids, True)

    ui = core_ui
    ui.navigate('Resources', 'Systems')
    ui.search(server_prefix)

    for name in names_of_servers:
        assert ui.check_exists(GridCell(name)), "Missing server from view " + name

    ui.action('Unenroll Systems', names_of_servers)
    core_ui.switch_context(Modal('Bulk System Unenroll'))
    core_ui.uncheck("SkipIfAgentReconciliationEnabled")
    core_ui.button('Unenroll')
    core_ui.switch_context(InfoModal())
    core_ui.button('Close')

    _wait_for_systems_validation(core_session, agent_ids, False)


@pytest.mark.api_ui
@pytest.mark.pas
@pytest.mark.parametrize('right_data', [("Privileged Access Service Power User", ['Add To Set']),
                                        ("System Administrator",
                                         ['Add To Set', 'Provision Local Administrative Accounts',
                                          'Unenroll Systems', 'Delete Systems'])])
def test_bulk_system_unenroll_does_not_appear_as_pas_power_user(core_session, right_data, users_and_roles,
                                                                test_four_virtual_aapm_agents):
    agents, server_prefix = test_four_virtual_aapm_agents
    _, _, names_of_servers = _setup_agents(core_session, agents)

    logger.info(f'Testing prefix: {server_prefix} names: {names_of_servers}')
    ui = None
    try:
        ui = users_and_roles.get_ui_as_user(right_data[0])
        ui.navigate('Resources', 'Systems')
        ui.search(server_prefix)

        for name in names_of_servers:
            assert ui.check_exists(GridCell(name)), "Missing server from view " + name

        ui.check_actions(right_data[1], names_of_servers)
    except Exception as e:
        logger.info("Taking screenshot of failed state.")
        raise e
    finally:
        if ui is not None:
            ui.browser.screen_cap('test_bulk_system_unenroll_does_not_appear_as_pas_power_user')
            ui.browser.exit()


@pytest.mark.api_ui
@pytest.mark.pas
def test_bulk_system_unenrolls_manually_single_system(core_session, core_ui, test_virtual_aapm_agent):
    agent, server_prefix = test_virtual_aapm_agent
    agent.enroll(core_session, True)
    result = RedrockController.get_system(core_session, agent.computerUuid)
    assert len(result) != 0
    system = result[0]["Row"]
    logger.info(agent.agentProfileId)
    logger.info(agent.resourceName)

    # Make sure agent has aapm feature
    _validate_aapm_agent_details(core_session, [agent.agentProfileId], True)

    ui = core_ui
    ui.navigate('Resources', 'Systems')
    ui.search(server_prefix)

    assert ui.check_exists(GridCell(agent.resourceName)), "Missing server from view " + agent.resourceName

    ui.action('Unenroll', agent.resourceName)
    core_ui.switch_context(Modal('System Unenroll'))

    core_ui.button('Unenroll')

    logger.info(agent.agentProfileId)
    logger.info(agent.resourceName)
    # Test Unenroll should be successful and feature appm should be disabled
    assert _wait_for_systems_validation(core_session, [agent.agentProfileId], False)

    ui = core_ui
    ui.navigate('Resources', 'Systems')
    ui.search(server_prefix)

    assert ui.check_exists(GridCell(agent.resourceName)), "Missing server from view " + agent.resourceName

    agent.enroll(core_session, True)
    ResourceManager.update_system(core_session, agent.computerUuid, system["Name"], system["FQDN"],
                                  system["ComputerClass"],
                                  allowautomaticlocalaccountmaintenance=True)
    _validate_aapm_agent_details(core_session, [agent.agentProfileId], True)

    ui.action('Unenroll', agent.resourceName)
    core_ui.switch_context(Modal('System Unenroll'))
    core_ui.uncheck("SkipIfAgentReconciliationEnabled")

    core_ui.button('Unenroll')

    # Test Unenroll should be successful and feature appm should be disabled
    assert _wait_for_systems_validation(core_session, [agent.agentProfileId], False)


@pytest.mark.api_ui
@pytest.mark.pas
def test_single_system_no_agent_enrolled(clean_bulk_delete_systems_and_accounts, core_session, core_ui,
                                         list_of_created_systems):
    server_prefix, names_of_servers, server_ids = _make_one_server_get_name(core_session, list_of_created_systems)

    ui = core_ui
    ui.navigate('Resources', 'Systems')
    ui.search(server_prefix)

    for name in names_of_servers:
        assert ui.check_exists(GridCell(name)), "Missing server from view " + name

    # Make sure unenroll operation is not available
    ui.check_actions(['Login', 'Select/Request Account', 'Enter Account', 'System',
                      'Add To Set', 'Test connection', 'Delete'], names_of_servers)


def _make_one_server_get_name(session, mutable_list, ssh=False):
    server_prefix = "bsd_tst_sys" + "-" + str(ResourceManager.time_mark_in_hours()) + "-" + guid()
    if ssh:
        batch1 = ResourceManager.add_multiple_ssh_systems_with_accounts(session, 1, 2, mutable_list,
                                                                        system_prefix=server_prefix)
    else:
        batch1 = ResourceManager.add_multiple_systems_with_accounts(session, 1, 2, mutable_list,
                                                                    system_prefix=server_prefix)
    all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values([batch1])
    names_of_servers = list(ResourceManager.get_multi_added_system_ids(session, all_systems).keys())
    return server_prefix, names_of_servers, batch1.keys()


def _setup_agents(session, agents):
    for agent in agents:
        agent.enroll(session, True)

    all_agent_ids = [agent.agentProfileId for agent in agents]
    all_server_ids = [agent.computerUuid for agent in agents]
    all_server_names = [agent.resourceName for agent in agents]

    return all_agent_ids, all_server_ids, all_server_names


def _validate_aapm_agent_details(session, agent_ids, expected):
    query = RedrockController.get_query_for_ids('centrifyclients', agent_ids, columns='ResourceID, FeatureAAPM')
    results = RedrockController.get_result_rows(
        RedrockController.redrock_query(session, query))

    logger.info(results)
    # make sure num of systems match
    assert len(results) == len(agent_ids)

    for row in results:
        assert row["FeatureAAPM"] is expected


def _wait_for_systems_validation(session, agent_ids, expected, intervals_to_wait=600, delay=1):
    while intervals_to_wait > 0:
        query = RedrockController.get_query_for_ids('centrifyclients', agent_ids, columns='ResourceID, FeatureAAPM')
        results = RedrockController.get_result_rows(
            RedrockController.redrock_query(session, query))

        logger.info(results)
        # make sure num of systems match
        assert len(results) == len(agent_ids)

        row = results[0]
        if row["FeatureAAPM"] is expected:
            return True
        if delay > 0:
            time.sleep(delay)

        intervals_to_wait = intervals_to_wait - 1

    return False
