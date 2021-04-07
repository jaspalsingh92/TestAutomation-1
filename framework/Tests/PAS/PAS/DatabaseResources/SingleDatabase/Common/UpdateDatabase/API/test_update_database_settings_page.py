import pytest
import logging
from Shared.API.redrock import RedrockController
from Utils.guid import guid
from Shared.API.infrastructure import ResourceManager

logger = logging.getLogger("test")


@pytest.mark.pasapi
@pytest.mark.pas
@pytest.mark.bhavna
def test_update_database_settings_page(core_session, database_config,
                                       cleanup_resources):
    """
    TC: C281881 Update Database Settings page
    :param core_session: Authenticated Centrify session
    :param database_config:fixture to create database with accounts
    :param cleanup_resources:cleans up resources
    """
    # Creating a database
    database_list = cleanup_resources[2]
    db_data = database_config['sql_db_config']
    db_name = f"{db_data['db_name']}{guid()}"
    db_description = "Test Description"
    default_checkout_time = 15
    db_result, db_success = ResourceManager.add_database(core_session, name=db_name, port=None,
                                                         fqdn=db_data['hostname'],
                                                         databaseclass=db_data['databaseclass'],
                                                         description=db_description,
                                                         instancename=db_data['instancename'],
                                                         servicename=db_data['servicename'])

    assert db_success, f'Failed to create database without defined port:API response result:{db_result}'
    logger.info(f'Successfully created database without defined port :{db_result}')
    database_list.append(db_result)

    # Updating the database setting
    update_db_res, update_db_success = ResourceManager.update_database(core_session, db_result,
                                                                       db_name,
                                                                       db_data['hostname'], db_data['port'],
                                                                       db_description,
                                                                       db_data['instancename'],
                                                                       DefaultCheckoutTime=default_checkout_time,
                                                                       allowmultiplecheckouts=True)
    assert update_db_success, f"Fail to update database: API response result:{update_db_res}"
    logger.info(f"Successfully updated database with port:{update_db_res}")

    # Query for database description
    query_description = f"SELECT VaultDatabase.Description FROM VaultDatabase where VaultDatabase.Name='{db_name}'"

    description_check = RedrockController.get_result_rows(RedrockController.redrock_query(core_session,
                                                                                          query_description))
    assert description_check[0]['Description'] == db_description, "Password history table did not update"
    logger.info('Password history table API response')

    # Query for database default checkout time
    query_default_checkout_time = f"SELECT VaultDatabase.DefaultCheckoutTime FROM VaultDatabase where " \
                                  f"VaultDatabase.Name='{db_name}' "
    checkout_value_check = RedrockController.get_result_rows(RedrockController.
                                                             redrock_query(core_session,
                                                                           query_default_checkout_time))
    assert checkout_value_check[0]['DefaultCheckoutTime'] == default_checkout_time, "Password history table did not " \
                                                                                    "update "
    logger.info('Password history table API response')

    # Query for allow multiple checkouts
    query_allow_multiple_checkouts = f"SELECT VaultDatabase.AllowMultipleCheckouts FROM VaultDatabase where " \
                                     f"VaultDatabase.Name='{db_name}' "
    allow_multiple_checkouts_value_check = RedrockController.get_result_rows(
        RedrockController.redrock_query(core_session,
                                        query_allow_multiple_checkouts))
    assert allow_multiple_checkouts_value_check[0]['AllowMultipleCheckouts'] is True, "Allow multiple " \
                                                                                      "checkouts value is False"
    logger.info('Allow multiple checkouts value is True')
