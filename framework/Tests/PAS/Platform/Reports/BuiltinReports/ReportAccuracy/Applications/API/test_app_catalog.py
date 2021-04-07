import pytest
import logging
from Shared.API.redrock import RedrockController

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi
def test_app_catalog(core_session):
    """
    TC: C6329 - App Catalog
        1. Login portal, go to Report - > Builtin Reports -> Application
        2. Click "App Catalog" >> Enter report result page and list all applications supported by Centrify.

    :param core_session: Authenticated Centrify Session.
    """
    application_list = []
    script = "select ID AS _ID, DisplayName, AppTypeDisplayName, Category, Description from SysApps where AppType = " \
             "'Desktop' or CatalogVisibility in ('All', 'Centrify') order by AppTypeDisplayName, Category, DisplayName"
    app_catalog_details = RedrockController.redrock_query(core_session, script)
    for applications in app_catalog_details:
        application_list.append(applications['Row']['DisplayName'])

    assert application_list, "Application list is empty, i.e. failed to retrieve  applications from 'App Catalog.'"
    logger.info(f"Application list retrieved from 'App Catalog' is as follows: {application_list}.")

