import logging
import pytest

logger = logging.getLogger("test")


@pytest.mark.pas
@pytest.mark.api
@pytest.mark.bhavna
def test_imp_add_duplicate_sys(core_session, get_csv_data, import_pow_data):
    """
        This module import duplicate system  through powershell api call to portal
        TC-ID: C284213: Added duplicates system/domains/database/account

        1. Read the excel and import the system in portal
        2. Retrieve the system activity
        3. Import the same system configuration again and capture the error
    """

    get_csv_data(sheetname='DuplicateSys')
    import_pow_data(core_session)
    logger.info(f"Accepted Result: failed to imported duplicate system")
