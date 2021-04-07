import pytest
from Shared.API.infrastructure import ResourceManager
from Shared.API.redrock import RedrockController
from Shared.API.sets import SetsManager
from Shared.UI.Centrify.selectors import Modal, GridCell, NoTitleModal, ConfirmModal, \
    InfoModal, Component, ComponentWithText, RestCallInitiated, \
    RestCallComplete, FavoriteStar, FavoritedStar, GridRowByGuid
from Shared.data_manipulation import DataManipulation
from Utils.guid import guid

pytestmark = [pytest.mark.ui, pytest.mark.cps, pytest.mark.bulk_account_delete]


@pytest.mark.api_ui
@pytest.mark.pas
def test_bulk_account_delete_one_account_at_a_time(clean_bulk_delete_systems_and_accounts, core_session,
                                                   list_of_created_systems):
    server_prefix, account_prefix, all_systems, all_accounts, all_account_names = _make_four_accounts_get_names \
        (core_session, list_of_created_systems, ssh=False)

    for i in all_accounts:
        ResourceManager.del_account(core_session, i)
    ResourceManager.wait_for_accounts_to_delete_or_timeout(core_session, all_systems, all_accounts)

    assert len(
        ResourceManager.get_multi_added_account_ids(core_session, all_systems)) == 0, "All added accounts not removed"
    assert len(ResourceManager.get_multi_added_system_ids(core_session,
                                                          all_systems)) == 1, "Wrong number of added systems remain"


@pytest.mark.ui
@pytest.mark.pas_skip
def test_bulk_account_delete_uncertain_password(clean_bulk_delete_systems_and_accounts, core_session, core_admin_ui,
                                                list_of_created_systems, cleanup_accounts):
    accounts_list, roles_list, users_list, coid_list = cleanup_accounts
    server_prefix, account_prefix, all_systems, all_accounts, all_accounts_names = \
        _make_four_uncertain_accounts_get_names(
            core_session, accounts_list, list_of_created_systems)
    ui = core_admin_ui

    ui.navigate('Resources', 'Accounts')
    ui.search(server_prefix)

    uncertain_account = all_accounts_names[0]
    ui.check_exists(GridCell(uncertain_account)), f"Account name {uncertain_account} not found in grid"

    ui.action('Delete', uncertain_account)

    # Uncertain accounts should follow the old flow where the user can choose to view two different passwords,
    # only one of which is correct.
    view_password_modal = Modal(f'Delete Account: {uncertain_account}')
    ui.switch_context(view_password_modal)

    proposed_container = Component('propsedContainer')
    expected_container = Component('currentContainer')

    ui.button('Show Password', [RestCallInitiated(), proposed_container])

    ui.expect(proposed_container, f'Failed to find container which has expected password when in uncertain state')

    ui.switch_context(proposed_container)

    proposedPassword = ComponentWithText('passwordPlainText', 'PendingSecret')

    ui.button('Show Password', [RestCallInitiated(), proposedPassword])
    ui.expect(proposedPassword,
              f'Failed to find expected PendingSecret password proposedPassword {proposedPassword.locator}')

    ui.switch_context(expected_container)
    expectedPassword = ComponentWithText('passwordPlainText', 'CurrentSecret')
    ui.button('Show Password', [RestCallInitiated(), expectedPassword])
    ui.expect(expectedPassword, f'Failed to find expected CurrentSecret password')

    ui.switch_context(view_password_modal)
    ui.button('Close')


@pytest.mark.api_ui
@pytest.mark.pas
def test_bulk_account_deletes_with_ui_no_secret(clean_bulk_delete_systems_and_accounts, core_session, core_admin_ui,
                                                list_of_created_systems):
    server_prefix, account_prefix, all_systems, all_accounts, all_account_names = _make_four_accounts_get_names(
        core_session, list_of_created_systems, ssh=True)

    ui = core_admin_ui
    ui.navigate('Resources', 'Accounts')
    ui.search(server_prefix)

    for name in all_account_names:
        assert ui.check_exists(GridCell(name)), f"Account name {name} not found in grid"

    ui.action('Delete accounts', all_account_names)
    ui.switch_context(Modal('Bulk Account Delete'))
    ui.uncheck("SaveSecret")
    ui.button('Delete')
    ui.switch_context(ConfirmModal())
    ui.button('Yes')
    ui.switch_context(InfoModal())
    ui.button('Close')

    ResourceManager.wait_for_accounts_to_delete_or_timeout(core_session, all_systems, all_accounts)

    assert len(
        ResourceManager.get_multi_added_account_ids(core_session, all_systems)) == 0, "All added accounts not removed"
    assert len(ResourceManager.get_multi_added_system_ids(core_session,
                                                          all_systems)) == 2, "Wrong number of added systems remain"


@pytest.mark.api_ui
@pytest.mark.pas
def test_bulk_account_stores_secret_when_deleting_using_ui(clean_bulk_delete_systems_and_accounts, core_session,
                                                           core_admin_ui, list_of_created_systems, secret_cleaner):
    server_prefix, account_prefix, all_systems, all_accounts, all_account_names = _make_four_accounts_get_names(
        core_session, list_of_created_systems, ssh=True)

    ui = core_admin_ui
    ui.navigate('Resources', 'Accounts')
    ui.search(server_prefix)

    for name in all_account_names:
        assert ui.check_exists(GridCell(name)), f"Account not found in grid with name {name}"

    delete_names, keep_names = DataManipulation.shuffle_and_split_into_two_lists(all_account_names)

    action_name = 'Delete accounts'
    modal_name = 'Bulk Account Delete'
    if len(delete_names) == 1:
        action_name = 'Delete'
        modal_name = 'Delete'

    ui.action(action_name, delete_names)
    ui.switch_context(Modal(modal_name))

    secret_name = "secret_e2e_name_" + guid() + "_" + guid()
    ui.input("SecretName", secret_name)

    ui.button('Delete')

    ui.switch_context(NoTitleModal())
    ui.button('Close')

    ResourceManager.wait_for_secret_to_exist_or_timeout(core_session, secret_name)

    secret_id = RedrockController.get_secret_id_by_name(core_session, secret_name)
    assert secret_id is not None, "Failed to create secret!"
    secret_cleaner.append(secret_id)

    assert len(ResourceManager.get_multi_added_account_ids(core_session, all_systems)) == len(
        keep_names), "Wrong number of remaining systems found"


@pytest.mark.api_ui
@pytest.mark.pas
def test_account_system_deletes_from_ui_using_set(clean_bulk_delete_systems_and_accounts, core_session, core_admin_ui,
                                                  list_of_created_systems):
    server_prefix, account_prefix, all_systems, all_accounts, all_account_names = _make_four_accounts_get_names(
        core_session, list_of_created_systems, ssh=True)
    ui = core_admin_ui
    ui.navigate('Resources', 'Accounts')
    ui.search(server_prefix)

    favorite_stars = ui.browser.get_list_of_elements_by_css_selector("img.server-is-not-favorite")
    assert len(favorite_stars) == 4, "Expected 4 favorite stars to exist but wrong number found"

    for account_id in all_accounts:
        notFavoriteStar = FavoriteStar().inside(GridRowByGuid(account_id))
        favoritedStar = FavoritedStar().inside(GridRowByGuid(account_id))
        star = ui._searchAndExpect(notFavoriteStar, f'Failed to find unselected favorite star for {account_id} account')
        star.try_click((RestCallInitiated(), favoritedStar))  # favorite account
        ui._searchAndExpect(favoritedStar, f'Expected {account_id} not-favorite start to turn to favorited.')

    ui.expect(RestCallComplete(), f'Expected rest call to favorite account to have completed.')

    ui.set_action("Favorite Accounts", "Delete accounts")

    ui.switch_context(Modal('Bulk Account Delete'))
    ui.button('Delete')

    ui.switch_context(NoTitleModal())
    ui.button('Close')

    ResourceManager.wait_for_accounts_to_delete_or_timeout(core_session, all_systems, all_accounts)

    assert len(
        ResourceManager.get_multi_added_account_ids(core_session, all_systems)) == 0, "All added accounts not removed"


def _make_four_accounts_get_names(session, mutable_list, ssh=False):
    server_prefix = "bsd_tst_sys" + "-" + str(ResourceManager.time_mark_in_hours()) + "-" + guid()
    account_prefix = "ta_"
    if ssh:
        batch = ResourceManager.add_multiple_systems_with_accounts(session, 1, 3, mutable_list,
                                                                   system_prefix=f'{server_prefix}_password',
                                                                   user_prefix=f'{account_prefix}_password')
        batch2 = ResourceManager.add_multiple_ssh_systems_with_accounts(session, 1, 1, mutable_list,
                                                                        system_prefix=f'{server_prefix}_ssh',
                                                                        user_prefix=f'{account_prefix}_ssh')
        all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values([batch, batch2])
    else:
        batch = ResourceManager.add_multiple_systems_with_accounts(session, 1, 4, mutable_list,
                                                                   system_prefix=server_prefix,
                                                                   user_prefix=account_prefix)
        all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values([batch])
    all_account_names = ResourceManager.get_multi_added_account_names(session, all_systems)
    return server_prefix, account_prefix, all_systems, all_accounts, all_account_names


def _make_four_uncertain_accounts_get_names(session, accounts_list, mutable_list):
    server_prefix, account_prefix, all_systems, all_accounts, all_account_names = _make_four_accounts_get_names \
        (session, mutable_list)
    for account_id in all_accounts:
        result, success, response = ResourceManager.make_account_uncertain(session, account_id)
        assert success is True, f'Failed to make account uncertain {response}'
        # need to add uncertain accounts to account cleaner
        accounts_list.append(account_id)

    return server_prefix, account_prefix, all_systems, all_accounts, all_account_names


def test_bulk_account_by_api_set_correct_accounts(clean_bulk_delete_systems_and_accounts, core_session,
                                                  list_of_created_systems, core_admin_ui):
    batch = ResourceManager.add_multiple_systems_with_accounts(core_session, 2, 2, list_of_created_systems)

    all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values([batch])
    delete_ids, keep_ids = DataManipulation.shuffle_and_split_into_two_lists(all_accounts)

    some_set_name = "ApiSet" + guid()
    success, set_id = SetsManager.create_manual_collection(core_session, some_set_name, "VaultAccount", None)
    assert success, "Did not create collection"

    SetsManager.update_members_collection(core_session, 'add', list(delete_ids), 'VaultAccount', set_id)

    filters = SetsManager.get_object_collection_and_filter_by_name(core_session, some_set_name, "VaultAccount")[
        'Filters']

    result, success = ResourceManager.del_multiple_accounts_by_query(core_session, filters)
    assert success, "del_multiple_accounts_by_query failed " + result

    SetsManager.delete_collection(core_session, set_id)

    assert set(ResourceManager.get_multi_added_system_ids(core_session, all_systems).values()) == set(
        all_systems), "Wrong set of added systems found"
    assert set(ResourceManager.get_multi_added_account_ids(core_session, all_systems)) == set(
        keep_ids), "Wrong set of added accounts found"
