import logging
import pytest
from collections import OrderedDict
from Utils.config_loader import Configs


logger = logging.getLogger("test")

val = Configs.get_environment_node('import_export', 'import_data')
ordered = OrderedDict(val)
regular = {**ordered}


@pytest.mark.pas
@pytest.mark.api
@pytest.mark.bhavna
def test_imp_script_with_wrong_cred(core_session, get_csv_data, import_pow_data):
    """
        This module will import account with wrong import credentials and capture a failure report

        TC-ID: C1275051: Run script with wrong credentials
    """
    get_csv_data(sheetname='ParentEntity')
    import_pow_data(core_session, regular['wrong_cloud_username'])
    logger.info(f"Failed to import data because of wrong import credentials.")
