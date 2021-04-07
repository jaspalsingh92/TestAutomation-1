import pytest
import logging
from Shared.API.infrastructure import ResourceManager
from Utils.config_loader import Configs

logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_check_text_in_about_page(core_session):
    """
    TC:C2045 Check text in About page.
    :param:core_session:Returns a API session.
    """
    # Getting the data from about "About" in dashboard and validating the text.
    get_about_dashboard_detail, get_about_dashboard_success = ResourceManager.get_about_menu_details(core_session)
    assert get_about_dashboard_success, f'Fail to get the details of about menu: ' \
                                        f'API response result:{get_about_dashboard_detail}'
    logger.info(f"Successfully get the details of about menu{get_about_dashboard_detail}")
    if "Version" in get_about_dashboard_detail:
        logger.info('The text is aligned and shown correctly.')
    else:
        raise Exception('The text is not aligned and shown correctly.')
