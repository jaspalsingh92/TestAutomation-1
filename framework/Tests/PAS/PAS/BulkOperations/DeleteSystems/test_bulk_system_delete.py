import pytest
import logging
from Shared.API.infrastructure import ResourceManager
from Shared.API.redrock import RedrockController
from Shared.UI.Centrify.selectors import Modal, GridCell, NoTitleModal, ConfirmModal, InfoModal
from Shared.data_manipulation import DataManipulation
from Utils.guid import guid

pytestmark = [pytest.mark.ui, pytest.mark.cps, pytest.mark.bulk_system_delete]

logger = logging.getLogger('test')


@pytest.mark.api_ui
@pytest.mark.pas
def test_bulk_system_deletes_manually(clean_bulk_delete_systems_and_accounts, core_session, core_ui, list_of_created_systems):
    server_prefix, names_of_servers, server_ids = _make_two_servers_get_names(core_session, list_of_created_systems)

    ui = core_ui
    ui.navigate('Resources', 'Systems')
    ui.search(server_prefix)

    for name in names_of_servers:
        assert ui.check_exists(GridCell(name)), "Missing server from view " + name

    ui.action('Delete Systems', names_of_servers)
    core_ui.switch_context(Modal('Bulk System Delete'))
    core_ui.button('Delete')
    core_ui.switch_context(InfoModal())
    core_ui.button('Close')

    ResourceManager.wait_for_systems_to_delete_or_timeout(core_session, server_ids)

    assert len(ResourceManager.get_multi_added_account_ids(core_session, server_ids)) == 0, "All added accounts not removed"
    assert len(ResourceManager.get_multi_added_system_ids(core_session, server_ids)) == 0, "All added systems not removed"


@pytest.mark.api_ui
@pytest.mark.pas
@pytest.mark.parametrize('right_data', [("Privileged Access Service Power User", ['Add To Set']), ("System Administrator", ['Add To Set', 'Provision Local Administrative Accounts', 'Unenroll Systems', 'Delete Systems'])])
def test_bulk_system_does_not_appear_as_pas_power_user(clean_bulk_delete_systems_and_accounts, core_session, list_of_created_systems, users_and_roles, right_data):
    server_prefix, names_of_servers, server_ids = _make_two_servers_get_names(core_session, list_of_created_systems)

    logger.info(f'Testing prefix: {server_prefix} names: {names_of_servers} ids: {server_ids}')
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
            ui.browser.screen_cap('test_bulk_system_does_not_appear_as_pas_power_user')
            ui.browser.exit()


@pytest.mark.api_ui
@pytest.mark.pas
def test_bulk_system_deletes_manually_single_system_and_secret(clean_bulk_delete_systems_and_accounts, core_session, core_ui, list_of_created_systems, secret_cleaner):
    server_prefix, names_of_servers, server_ids = _make_one_server_get_name(core_session, list_of_created_systems)

    ui = core_ui
    ui.navigate('Resources', 'Systems')
    ui.search(server_prefix)

    for name in names_of_servers:
        assert ui.check_exists(GridCell(name)), "Missing server from view " + name

    ui.action('Delete', names_of_servers)
    core_ui.switch_context(Modal('System Delete'))

    secret_name = "secret_e2e_name_" + guid()
    core_ui.input("SecretName", secret_name)

    core_ui.button('Delete')

    ResourceManager.wait_for_systems_to_delete_or_timeout(core_session, server_ids)
    assert len(ResourceManager.get_multi_added_account_ids(core_session, server_ids)) == 0, "All added accounts not removed"
    assert len(ResourceManager.get_multi_added_system_ids(core_session, server_ids)) == 0, "All added systems not removed"

    ResourceManager.wait_for_secret_to_exist_or_timeout(core_session, secret_name)

    secret_id = RedrockController.get_secret_id_by_name(core_session, secret_name)
    assert secret_id is not None, "Secret not found"
    secret_cleaner.append(secret_id)


@pytest.mark.api_ui
@pytest.mark.pas
def test_bulk_system_delete_no_secret_manually(clean_bulk_delete_systems_and_accounts, core_session, core_ui, list_of_created_systems, secret_cleaner):
    server_prefix, names_of_servers, server_ids = _make_two_servers_get_names(core_session, list_of_created_systems)

    ui = core_ui
    ui.navigate('Resources', 'Systems')
    ui.search(server_prefix)

    for name in names_of_servers:
        assert ui.check_exists(GridCell(name)), "Server not found in grid " + name

    ui.action('Delete Systems', names_of_servers)
    core_ui.switch_context(Modal('Bulk System Delete'))

    core_ui.uncheck("SaveSecret")
    core_ui.button('Delete')

    core_ui.switch_context(ConfirmModal())
    core_ui.button('Yes')

    core_ui.switch_context(NoTitleModal())
    core_ui.button('Close')

    ResourceManager.wait_for_systems_to_delete_or_timeout(core_session, server_ids)

    assert len(ResourceManager.get_multi_added_account_ids(core_session, server_ids)) == 0, "All added accounts not removed"
    assert len(ResourceManager.get_multi_added_system_ids(core_session, server_ids)) == 0, "All added systems not removed"


@pytest.mark.api_ui
@pytest.mark.pas
def test_bulk_system_deletes_mixed_ssh_systems(clean_bulk_delete_systems_and_accounts, core_session, core_ui, list_of_created_systems, secret_cleaner):
    server_prefix, names_of_servers, server_ids = _make_two_servers_get_names(core_session, list_of_created_systems, ssh=True)

    ui = core_ui
    ui.navigate('Resources', 'Systems')
    ui.search(server_prefix)

    for name in names_of_servers:
        assert ui.check_exists(GridCell(name)), "Missing server from view " + name

    ui.action('Delete Systems', names_of_servers)
    core_ui.switch_context(Modal('Bulk System Delete'))
    core_ui.button('Delete')
    core_ui.switch_context(InfoModal())
    core_ui.button('Close')

    ResourceManager.wait_for_systems_to_delete_or_timeout(core_session, server_ids)

    assert len(ResourceManager.get_multi_added_account_ids(core_session, server_ids)) == 0, "All added accounts not removed"
    assert len(ResourceManager.get_multi_added_system_ids(core_session, server_ids)) == 0, "All added systems not removed"


@pytest.mark.api_ui
@pytest.mark.pas
def test_bulk_system_deletes_manually_from_set(clean_bulk_delete_systems_and_accounts, core_session, core_ui, list_of_created_systems):
    server_prefix, names_of_servers, server_ids = _make_two_servers_get_names(core_session, list_of_created_systems)

    ui = core_ui
    ui.navigate('Resources', 'Systems')
    ui.search(server_prefix)

    not_favorite_stars = ui.browser.get_list_of_elements_by_css_selector("img.server-is-not-favorite")
    assert len(not_favorite_stars) == 2, "Expected two favorite stars to be found, but other number returned"

    for star in not_favorite_stars:
        star.click()  # favorite server

    core_ui.set_action("Favorites", "Delete Systems")

    core_ui.switch_context(Modal('Bulk System Delete'))
    core_ui.button('Delete')

    core_ui.switch_context(NoTitleModal())
    core_ui.button('Close')

    ResourceManager.wait_for_systems_to_delete_or_timeout(core_session, server_ids)

    assert len(ResourceManager.get_multi_added_account_ids(core_session, server_ids)) == 0, "All added accounts not removed"
    assert len(ResourceManager.get_multi_added_system_ids(core_session, server_ids)) == 0, "All added systems not removed"


def _make_two_servers_get_names(session, mutable_list, ssh=False):
    server_prefix = "bsd_tst_sys" + "-" + str(ResourceManager.time_mark_in_hours()) + "-" + guid()
    if ssh:
        batch1 = ResourceManager.add_multiple_ssh_systems_with_accounts(session, 1, 1, mutable_list, system_prefix=f'{server_prefix}-ssh')
        batch2 = ResourceManager.add_multiple_systems_with_accounts(session, 1, 1, mutable_list, system_prefix=f'{server_prefix}-password')
        all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values([batch1, batch2])
    else:
        batch1 = ResourceManager.add_multiple_systems_with_accounts(session, 2, 2, mutable_list, system_prefix=server_prefix)
        all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values([batch1])
    names_of_servers = list(ResourceManager.get_multi_added_system_ids(session, all_systems).keys())
    return server_prefix, names_of_servers, batch1.keys()


def _make_one_server_get_name(session, mutable_list, ssh=False):
    server_prefix = "bsd_tst_sys" + "-" + str(ResourceManager.time_mark_in_hours()) + "-" + guid()
    if ssh:
        batch1 = ResourceManager.add_multiple_ssh_systems_with_accounts(session, 1, 2, mutable_list, system_prefix=server_prefix)
    else:
        batch1 = ResourceManager.add_multiple_systems_with_accounts(session, 1, 2, mutable_list, system_prefix=server_prefix)
    all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values([batch1])
    names_of_servers = list(ResourceManager.get_multi_added_system_ids(session, all_systems).keys())
    return server_prefix, names_of_servers, batch1.keys()
