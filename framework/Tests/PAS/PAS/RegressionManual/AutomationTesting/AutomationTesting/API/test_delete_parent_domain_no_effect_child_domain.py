import pytest
import logging
from Utils.guid import guid
from Shared.API.infrastructure import ResourceManager

logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_delete_parent_domain_no_effect_child_domain(core_session, domain_setup):
    """
      TC:C2216 Delete parent domain no effect child domain.
      :param core_session: Returns API session.
      :param domain_setup: fixture for creating domain.

    """
    # Creating a parent domain.
    parent_domain_id, domain_info = domain_setup

    # Create a child domain.
    child_domain_name = f"{'R1F1C1'}{guid()}"
    new_child_domain_id, add_child_domain_success = ResourceManager.add_child_domain(core_session, child_domain_name,
                                                                                     description='test_child_domain',
                                                                                     parent_id=parent_domain_id)
    assert add_child_domain_success, f'Failed to create child domain:API response result:{new_child_domain_id}'
    logger.info(f"Successfully created child domain:{new_child_domain_id}")

    # Trying to delete parent domain without deleting a child,expecting a failure.
    failed_del_domain_result, failed_del_domain_success = ResourceManager.del_domain(core_session,
                                                                                     parent_domain_id)

    assert failed_del_domain_success is False, f'Could able to delete parent domain:API response ' \
                                               f'result: {failed_del_domain_result} '
    logger.info(f"Could not able to delete parent domain without deleting a child:{failed_del_domain_result}")

    # Trying to delete child domain expecting child domain deleted successfully.
    child_del_domain_result, child_del_domain_success = ResourceManager.del_domain(core_session,
                                                                                   new_child_domain_id)

    assert child_del_domain_success, f'Fail to delete child  domain:API response ' \
                                     f'result: {child_del_domain_result} '
    logger.info(f"Successfully deleted child  domain: {child_del_domain_result}")


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_check_button_status_after_canceling_account_deleted(core_session, add_single_system, pas_config,
                                                             users_and_roles):
    """
    TC:C2217 Check button status after canceling account deleted with user who just has Delete permission.
    :param core_session: Returns a API session.
    :param add_single_system: Returns a fixture.
    :param users_and_roles: Fixture to manage roles and user.
    :param pas_config: Read yaml data.

    """
    # Creating a system.
    created_system_id, system_details = add_single_system

    # Creating a account.
    payload_data = pas_config['Windows_infrastructure_data']
    account_id, account_success = ResourceManager.add_account(core_session, payload_data['account_name'],
                                                              payload_data['password'],
                                                              created_system_id,
                                                              payload_data['account_type'])
    assert account_success, f'Failed to create account: API response result:{account_id}'
    logger.info(f'Successfully created account:{account_id}')

    # Cloud user session with "Privileged Access Service Power User".
    cloud_user_session = users_and_roles.get_session_for_user('Privileged Access Service Power User')
    user_name = cloud_user_session.auth_details['User']
    user_id = cloud_user_session.auth_details['UserId']

    # Assigning account "Delete" permission.
    assign_account_result, assign_account_success = ResourceManager.assign_account_permissions(core_session,
                                                                                               "Delete",
                                                                                               user_name,
                                                                                               user_id,
                                                                                               'User')
    assert assign_account_success, f"Failed to assign account permissions: API response result: {assign_account_result}"
    logger.info(f'Successfully assigned "Delete" permission to user:{assign_account_result}.')

    # Deleting a account by cloud user.
    del_account_result, del_account_success = ResourceManager.del_account(cloud_user_session, account_id)
    assert del_account_success, f"Could not delete account:API response result:{del_account_result}"
    logger.info(f"Successfully deleted account: {del_account_result}")
