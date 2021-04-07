import pytest
import logging
from Shared.API.sets import SetsManager
from Utils.guid import guid
from Shared.API.infrastructure import ResourceManager

logger = logging.getLogger("test")


@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi
def test_select_more_than_one_domain(core_session, domain_setup, cleanup_resources, clean_up_collections):
    """
      TC:C2215 Select more than one domains.
      :param core_session: Returns API session.
      :param domain_setup: Fixture for domain creation.
      :param cleanup_resources: cleaner for domain.
    """
    # Creating a parent domain.
    parent_domain_id, domain_info = domain_setup

    set_list = clean_up_collections
    # Create a child domain.
    child_domain_name = f"{'child'}{guid()}"
    domain_cleanup_list = cleanup_resources[1]
    new_child_domain_id, add_child_domain_success = ResourceManager.add_child_domain(core_session, child_domain_name,
                                                                                     description='test_child_domain',
                                                                                     parent_id=parent_domain_id)
    assert add_child_domain_success, f'Failed to create child domain:API response result:{new_child_domain_id}'
    logger.info(f"Successfully created child domain:API response result: {new_child_domain_id}")
    domain_cleanup_list.append(new_child_domain_id)

    Result, success = ResourceManager.get_administrative_account(core_session, "administrator")
    logger.info(f" Successfully get Domain for adding Administrative account.")
    assert success, f'Failed to get Domain account {Result}'

    # set name created with guid and add it in the domain set
    set_name = f'set_name{guid()}'
    add_success, add_result = SetsManager.create_manual_collection(core_session, set_name, "VaultDomain",
                                                                   object_ids=[parent_domain_id])
    assert add_success, f'Failed to create set and addition of member to set as: {add_result}'
    logger.info(f'Successfully created set with member:{add_result}')

    # cleanup the set and account
    set_list.append(add_result)
