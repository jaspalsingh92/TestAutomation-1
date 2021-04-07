import os
import pytest
import logging
import pandas as pd
from Shared.API.infrastructure import ResourceManager
from Shared.API.redrock import RedrockController
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_import_system(core_session, cleanup_accounts, cleanup_resources):
    """
    Test case: C2177 Import system
    :param core_session: Authenticated Centrify Session.
    """

    # dataframe to store systems in csv import template
    # datframe to store systems with unique name in csv import template
    system_list = cleanup_resources[0]
    accounts_list = cleanup_accounts[0]
    dataframe = pd.read_csv('Assets\\serverimport.csv')
    server_list = dataframe['Name']
    for server in server_list:
        dataframe = dataframe.replace(server, f'{server}{guid()}')
    temp_server_csv = f"Assets\\serverimport{guid()}.csv"
    dataframe.to_csv(temp_server_csv, encoding='utf-8', index=False)

    # API call with server import template
    result, success = ResourceManager.bulk_import_system(core_session, temp_server_csv)
    assert success, f"failed to add systems, return result is: {result}"
    logger.info('bulk import successful')

    server = RedrockController.get_accounts(core_session)
    for row in server:
        if row['User'].__contains__("Administrator"):
            accounts_list.append(row["ID"])

    server = RedrockController.get_computers(core_session)
    for row in server:
        if row['Name'].__contains__("host"):
            system_list.append(row["ID"])
    if os.path.exists(temp_server_csv):
        os.remove(temp_server_csv)
    else:
        pass
