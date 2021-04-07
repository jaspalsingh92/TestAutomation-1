import pytest
import logging
from Shared.API.infrastructure import ResourceManager
from Shared.API.core import CoreManager
from Shared.API.users import UserManager
from Shared.UI.Centrify.SubSelectors.grids import GridCell

logger = logging.getLogger("test")


@pytest.mark.api_ui
@pytest.mark.pas
@pytest.mark.pasapi_ui
@pytest.mark.bhavna
@pytest.mark.skip("domain_setups is missing from framework")
def test_check_ui_domain_page(core_session, domain_setups, core_admin_ui):
    """
    Shown the bubble info completely on main Domains page
    :return:
    """
    name, domain_name, password, user_name, administrative_account_name, child_domain = domain_setups
    ui = core_admin_ui

    # Set Administrative account
    directory_services = CoreManager.get_directory_services(core_session)
    logger.info(f" Successfully get all the Domain Directory Services. {directory_services}")
    for directory_service in directory_services.json()['Result']['Results']:  # Get the Active Domain Directory Service
        if directory_service['Row']['Name'] == name:
            directory_service = directory_service['Row']['directoryServiceUuid']
            break

    # Get the child domain details of a Particular Active Directory
    active_directory_service_child_domain, add_success = UserManager.directory_query_user(core_session, "Administ", [directory_service])
    admin_account = active_directory_service_child_domain['SystemName']
    result, add_admin_account_success, message = ResourceManager.set_administrative_account(core_session,
                                                                                            child_domain,
                                                                                            password=password,
                                                                                            user=admin_account,
                                                                                            directoryservices=directory_service)
    assert add_admin_account_success, f'Failed to set administrative account of Active Directory {message}'
    logger.info(f"Administrative account for Active Directory set successfully in the Domain{result}.")

    ui.navigate('Resources', 'Domains')
    ui.search(child_domain)
    actual_administrative_account_bubble = ui.expect(GridCell(user_name, data_content=True), "Domain bubble name").mouse_hover()
    logger.info(f'Shows the bubble info of administrative account {actual_administrative_account_bubble}')
    expected_administrative_account_bubble = administrative_account_name
    actual_administrative_account_bubble = ui.expect(GridCell(user_name, True), "Domain bubble name").get_attribute("data-content")
    assert expected_administrative_account_bubble == actual_administrative_account_bubble, f"Domain name bubble not appeared "
    logger.info(f'successsfully shown the bubble info completely on main Domains page {actual_administrative_account_bubble}')
