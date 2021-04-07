import pytest
import logging
from Shared.UI.Centrify.SubSelectors.navigation import RenderedTab
from Utils.guid import guid
from Shared.API.infrastructure import ResourceManager

logger = logging.getLogger("test")


@pytest.mark.api_ui
@pytest.mark.pas
@pytest.mark.pasapi_ui
@pytest.mark.bhavna
def test_domain_action_try_to_delete_parent_domain(core_session, domain_setup, cleanup_resources, core_admin_ui):
    """
      TC:C2112 Check domain's "Actions" when try to delete the parent domain"".
      :param core_session: Returns API session.
      :param domain_setup: Fixture for domain creation.
      :param cleanup_resources: cleaner for domain.
      :param core_admin_ui: Return browser session.

    """

    # Creating a parent domain.
    parent_domain_id, domain_info = domain_setup
    parent_domain_name = domain_info[0]

    # Create a child domain.
    child_domain_name = f"{'child'}{guid()}"
    domain_cleanup_list = cleanup_resources[1]
    new_child_domain_id, add_child_domain_success = ResourceManager.add_child_domain(core_session, child_domain_name,
                                                                                     description='test_child_domain',
                                                                                     parent_id=parent_domain_id)
    assert add_child_domain_success, f'Failed to create child domain:API response result:{new_child_domain_id}'
    logger.info(f"Successfully created child domain:API response result: {new_child_domain_id}")
    domain_cleanup_list.append(new_child_domain_id)

    # Trying to delete parent domain without deleting a child,expecting a failure.
    failed_del_domain_result, failed_del_domain_success = ResourceManager.del_domain(core_session,
                                                                                     parent_domain_id)

    assert failed_del_domain_success is False, f'Could able to delete domain:API response ' \
                                               f'result: {failed_del_domain_result} '
    logger.info(
        f"Successfully found error message Unable to delete the domain."
        f"Domain has child domains {failed_del_domain_result}")

    # UI Launch
    ui = core_admin_ui
    ui.navigate('Resources', 'Domains')
    ui.switch_context(RenderedTab('Domains'))
    ui.check_span(parent_domain_name)
    ui.check_span(child_domain_name)
    ui.check_actions(["Set Administrative Account", "Add To Set"])
    logger.info('Successfully find "Set Administrative Account" & "Add To Set" in Actions Menu.')
