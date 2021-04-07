from itertools import chain
from Utils.guid import guid

import pytest
import logging
from Shared.API.infrastructure import ResourceManager
from Shared.API.sets import SetsManager

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi
def test_check_ui_after_changing_setting(core_session, pas_setup, clean_up_collections):
    """
    Test case: C2206  Check permission for set
    :param core_session: Authenticated centrify session
    :param pas_setup: Creating a new system with accounts

    """
    # Adding Systems for test execution
    created_system_id, created_account_id, system_details = pas_setup
    user_details = core_session.__dict__
    collection_name = "testManualCollection" + guid()

    # Get list of permission
    get_sys_result, get_sys_success = ResourceManager.get_system_permissions(core_session, created_system_id)
    assert get_sys_success, f"Failed to get system permissions for resource, API result:{get_sys_result}"
    permission = get_sys_result[0]['Rights']
    permission_list = list(chain(*zip(permission.split())))[:-1]
    permission_index_value = [list((i, permission_list[i])) for i in range(len(permission_list))]
    assert (permission_index_value[3][0] < permission_index_value[4][0]), f"Failed to get permission 'Grant' is in front of 'View'"
    logger.info(f'Grant is successfully shows in front of View. as Grant index is {permission_index_value[3][0]} and View index is {permission_index_value[4][0]}')

    # Create set
    add_set_success, new_set_id = SetsManager.create_manual_collection(core_session, collection_name, "Server")
    assert add_set_success, "Collection " + new_set_id + " Failed to Create"

    # Set cleanup list
    clean_up_collections.append(new_set_id)

    # Assign permission to the set
    set_permissions_result = SetsManager.set_collection_permissions(core_session, "Grant,View,Edit,Delete", user_details["auth_details"]["User"],
                                                                    user_details['auth_details']['UserId'],
                                                                    new_set_id)
    logger.info(f'Successfully set collection Permissions for the set page :{set_permissions_result}')

    # Get collection permission rights
    get_permissions_result = SetsManager.get_collection_rights(core_session, new_set_id)
    set_permission = get_permissions_result['Result']

    # Actual set permission rights list
    actual_set_permission_list = 'View, Edit, Delete, Grant'
    assert set_permission == actual_set_permission_list, f'Failed to verify permissions:{actual_set_permission_list}'
    logger.info(f'Successfully verify Permissions for the set page created:{actual_set_permission_list}')
