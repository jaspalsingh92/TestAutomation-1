import logging
import pytest

from Shared.API.sets import SetsManager
from Utils.guid import guid
from Shared.API.server import ServerManager

logger = logging.getLogger("test")

pytestmark = [pytest.mark.pas, pytest.mark.pasapi, pytest.mark.sysadminsetoption]


@pytest.fixture(scope="function")
def _modifying_setting_mutex(lock_fixture):
    """
    Use this to ensure no other tests run at the same time which also modify the system_admin_value
    :param test_mutex_fixture:
    :return:
    """
    lock_fixture("admin_set_option", 300)
    yield


@pytest.mark.parametrize('user_rights', ['System Administrator'], indirect=True)
def test_option_all_system_admins_option_true(core_session, cds_session, set_cleaner, _modifying_setting_mutex):

    update_result, update_success = ServerManager.update_server_security_settings(core_session, all_system_admin_see_all_sets_created_by_sys_admin=True)
    assert update_success, f"Failed to update security Settings {update_result}"

    results, success = ServerManager.get_server_settings(core_session, key='policy')
    assert success, f"Failed to retrieve policy settings {results}"

    assert results["AllSystemAdminSeeAllSetsCreatedBySysAdmin"] is True, f"Policy key AllSystemAdminSeeAllSetsCreatedBySysAdmin should be False {results}"

    admin2_session, api_user = cds_session
    admin1_session = core_session

    set_name1 = f"test_visibility_{guid()}"
    set_name2 = f"test_visibility_{guid()}"

    success, set_id1 = SetsManager.create_manual_collection(admin1_session, set_name1, 'DataVault', object_ids=None)
    assert success is True, f'Failed to create manual set {set_id1}'
    set_cleaner.append(set_id1)

    success, set_id2 = SetsManager.create_manual_collection(admin2_session, set_name2, 'DataVault', object_ids=None)
    assert success is True, f'Failed to create manual set {set_id2}'
    set_cleaner.append(set_id2)

    assert SetsManager.get_collection_id(admin1_session, set_name1, "DataVault", reduce_sys_admin=True) is not None, "Admin 1 should be able to see own set"
    assert SetsManager.get_collection_id(admin2_session, set_name2, "DataVault", reduce_sys_admin=True) is not None, "Admin 2 should be able to see own set"
    assert SetsManager.get_collection_id(admin2_session, set_name1, "DataVault", reduce_sys_admin=True) is not None, "Admin 2 should be able to see Admin 1 set WHEN AllSystemAdminSeeAllSetsCreatedBySysAdmin is set to True"
    assert SetsManager.get_collection_id(admin1_session, set_name2, "DataVault", reduce_sys_admin=True) is not None, "Admin 1 should be able to see Admin 2 set WHEN AllSystemAdminSeeAllSetsCreatedBySysAdmin is set to True"

    assert SetsManager.get_collection_id(admin2_session, set_name1, "DataVault", reduce_sys_admin=False) is not None, "Admin 2 should be able to see Admin 1 set when reduce_sys_admin is False"
    assert SetsManager.get_collection_id(admin1_session, set_name2, "DataVault", reduce_sys_admin=False) is not None, "Admin 1 should be able to see Admin 2 set when reduce_sys_admin is False"


@pytest.mark.parametrize('user_rights', ['System Administrator'], indirect=True)
def test_option_all_system_admins_option_false(core_session, cds_session, set_cleaner, _modifying_setting_mutex):

    update_result, update_success = ServerManager.update_server_security_settings(core_session, all_system_admin_see_all_sets_created_by_sys_admin=False)
    assert update_success, f"Failed to update security Settings {update_result}"

    results, success = ServerManager.get_server_settings(core_session, key='policy')
    assert success, f"Failed to retrieve policy settings {results}"

    assert results["AllSystemAdminSeeAllSetsCreatedBySysAdmin"] is False, f"Policy key AllSystemAdminSeeAllSetsCreatedBySysAdmin should be False {results}"

    admin2_session, api_user = cds_session
    admin1_session = core_session

    set_name1 = f"test_visibility_{guid()}"
    set_name2 = f"test_visibility_{guid()}"

    success, set_id1 = SetsManager.create_manual_collection(admin1_session, set_name1, 'DataVault', object_ids=None)
    assert success is True, f'Failed to create manual set {set_id1}'
    set_cleaner.append(set_id1)

    success, set_id2 = SetsManager.create_manual_collection(admin2_session, set_name2, 'DataVault', object_ids=None)
    assert success is True, f'Failed to create manual set {set_id2}'
    set_cleaner.append(set_id2)

    assert SetsManager.get_collection_id(admin1_session, set_name1, "DataVault", reduce_sys_admin=True) is not None, "Admin 1 should be able to see own set"
    assert SetsManager.get_collection_id(admin2_session, set_name2, "DataVault", reduce_sys_admin=True) is not None, "Admin 2 should be able to see own set"
    assert SetsManager.get_collection_id(admin2_session, set_name1, "DataVault", reduce_sys_admin=True) is None, "Admin 2 should NOT be able to see Admin 1 set"
    assert SetsManager.get_collection_id(admin1_session, set_name2, "DataVault", reduce_sys_admin=True) is None, "Admin 1 should NOT be able to see Admin 2 set"

    assert SetsManager.get_collection_id(admin2_session, set_name1, "DataVault", reduce_sys_admin=False) is not None, "Admin 2 should be able to see Admin 1 set when reduce_sys_admin is False"
    assert SetsManager.get_collection_id(admin1_session, set_name2, "DataVault", reduce_sys_admin=False) is not None, "Admin 1 should be able to see Admin 2 set when reduce_sys_admin is False"


@pytest.mark.parametrize('global_option', [True, False])
@pytest.mark.parametrize('user_rights', ['Privileged Access Service Administrator'], indirect=True)
def test_option_all_system_admins_option_has_no_effect_on_non_admins(core_session, cds_session, set_cleaner, global_option, _modifying_setting_mutex):

    update_result, update_success = ServerManager.update_server_security_settings(core_session, all_system_admin_see_all_sets_created_by_sys_admin=global_option)
    assert update_success, f"Failed to update security Settings {update_result}"

    results, success = ServerManager.get_server_settings(core_session, key='policy')
    assert success, f"Failed to retrieve policy settings {results}"

    assert results["AllSystemAdminSeeAllSetsCreatedBySysAdmin"] is global_option, f"Policy key AllSystemAdminSeeAllSetsCreatedBySysAdmin should be {global_option} {results}"

    non_admin_session, api_user = cds_session
    admin1_session = core_session

    set_name1 = f"test_visibility_{guid()}"
    set_name2 = f"test_visibility_{guid()}"

    success, set_id1 = SetsManager.create_manual_collection(admin1_session, set_name1, 'DataVault', object_ids=None)
    assert success is True, f'Failed to create manual set {set_id1}'
    set_cleaner.append(set_id1)

    success, set_id2 = SetsManager.create_manual_collection(non_admin_session, set_name2, 'DataVault', object_ids=None)
    assert success is True, f'Failed to create manual set {set_id2}'
    set_cleaner.append(set_id2)

    assert SetsManager.get_collection_id(admin1_session, set_name1, "DataVault", reduce_sys_admin=True) is not None, "Admin 1 should be able to see own set"
    assert SetsManager.get_collection_id(non_admin_session, set_name2, "DataVault", reduce_sys_admin=True) is not None, "Non admin should be able to see own set"
    assert SetsManager.get_collection_id(non_admin_session, set_name1, "DataVault", reduce_sys_admin=True) is None, "Non admin should NOT be able to see Admin 1 set"
    assert SetsManager.get_collection_id(admin1_session, set_name2, "DataVault", reduce_sys_admin=True) is None, "Admin 1 should NOT be able to see non admin set"

    assert SetsManager.get_collection_id(non_admin_session, set_name1, "DataVault", reduce_sys_admin=False) is None, "Non admin should not be able to see Admin 1 set when reduce_sys_admin is False (because lacking permission)"
    assert SetsManager.get_collection_id(admin1_session, set_name2, "DataVault", reduce_sys_admin=False) is not None, "Admin 1 should be able to see Admin 2 set when reduce_sys_admin is False"
