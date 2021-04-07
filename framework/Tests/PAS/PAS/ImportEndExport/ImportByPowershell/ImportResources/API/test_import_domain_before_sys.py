import logging
import pytest

logger = logging.getLogger("test")


@pytest.mark.pas
@pytest.mark.api
@pytest.mark.bhavna
def test_imp_dom_before_sys(core_session, get_csv_data, import_pow_data):
    """
        This module import domain before system through powershell api call to portal
        TC-ID: C284209: Import system with setting domain
    """

    get_csv_data(sheetname='DomainBeforeSys')
    import_pow_data(core_session)
    logger.info(f"Successfully imported.")



