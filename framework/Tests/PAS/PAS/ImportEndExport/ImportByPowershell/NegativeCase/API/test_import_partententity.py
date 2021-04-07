import logging
import pytest

logger = logging.getLogger("test")


@pytest.mark.pas
@pytest.mark.api
@pytest.mark.bhavna
def test_imp_parententity(core_session, get_csv_data, import_pow_data):
    """
        This module will import account without filling partententity field and capture a failure report

        TC-ID: C284217: Imported account with must partententity does not filled
    """
    get_csv_data(sheetname='ParentEntity')
    import_pow_data(core_session)
    logger.info(f"Successfully imported.")
