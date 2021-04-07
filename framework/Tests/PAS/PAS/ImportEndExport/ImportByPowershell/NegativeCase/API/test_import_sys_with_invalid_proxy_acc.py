import logging
import pytest


logger = logging.getLogger("test")


@pytest.mark.pas
@pytest.mark.api
@pytest.mark.bhavna
def test_imp_invalid_proxy_account(core_session, get_csv_data, import_pow_data):
    """
        This module will import systems with invalid proxy account through powershell to portal
        TC-ID : C284214: Imported systems with invalid proxy account
    """

    get_csv_data(sheetname='InvalidProxyAcc')
    import_pow_data(core_session)
    logger.info(f"Failed to import system because of invalid proxy account")
