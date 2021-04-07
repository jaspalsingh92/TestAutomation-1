import logging
import pytest


logger = logging.getLogger("test")


@pytest.mark.pas
@pytest.mark.api
@pytest.mark.bhavna
def test_imp_missing_field(core_session, get_csv_data, import_pow_data):
    """
        This module will import missing data through powershell to portal
        TC-ID : C284216: Imported systems with must filled field does not filled
    """

    get_csv_data(sheetname='MissingField')
    import_pow_data(core_session)
    logger.info(f"Successfully imported.")


