import pytest
import logging
from Shared.API.infrastructure import ResourceManager
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_invalid_missing_arguments_are_handled_when_sending_rest_calls_to_cps(core_session, database_config,
                                                                              cleanup_resources):
    """
    Test case: C1149
    :param core_session: Centrify Authenticated session
    :param cleanup_resources: Cleanup fixture.
    """
    db_data = database_config
    oracle_db = f"{db_data['oracle_db_config']['db_name']}{guid()}"
    sql_db = f"{db_data['sql_db_config']['db_name']}{guid()}"
    sapase_db = f"{db_data['sap_ase_db_config']['db_name']}{guid()}"
    database_list = cleanup_resources[2]

    # Oracle db REST call test
    # adding oracle without service name.
    failed_oracle_result, status = ResourceManager.add_database(core_session, name=oracle_db,
                                                                port=db_data['oracle_db_config']['port'],
                                                                fqdn=db_data['oracle_db_config']['hostname'],
                                                                databaseclass=db_data['oracle_db_config']
                                                                ['databaseclass'],
                                                                servicename=None)
    assert status is False, f'Database added successfully without service name which should not be the ' \
                            f'case with result {failed_oracle_result} '
    logger.info(f'database not added successfully from api with status code {status} and error '
                '"Invalid argument. Service name is required for Oracle Database" which is expected"')

    # adding oracle db with instance and service name
    oracle_result, status = ResourceManager.add_database(core_session, name=oracle_db,
                                                         port=db_data['oracle_db_config']['port'],
                                                         fqdn=db_data['oracle_db_config']['hostname'],
                                                         description=db_data['oracle_db_config']['description'],
                                                         databaseclass=db_data['oracle_db_config']['databaseclass'],
                                                         instancename=db_data['oracle_db_config']['instancename'],
                                                         servicename=db_data['oracle_db_config']['servicename'])
    assert status, f'Database failed to add with result {oracle_result}'
    database_list.append(oracle_result)
    logger.info('database added successfully with instance name filtered out silently by cloud backend')

    # Sql db REST call test
    sql_result, status = ResourceManager.add_database(core_session, name=sql_db, port=db_data['sql_db_config']['port'],
                                                      fqdn=db_data['sql_db_config']['hostname'],
                                                      description=db_data['sql_db_config']['description'],
                                                      databaseclass=db_data['sql_db_config']['databaseclass'],
                                                      instancename=db_data['sql_db_config']['instancename'],
                                                      servicename=db_data['sql_db_config']['servicename'])
    assert status, f'Database failed to add with result {sql_result}'
    database_list.append(sql_result)
    logger.info(f'database added successfully with service name filtered out silently by cloud backend')

    # SAP ASE db REST call test
    sap_result, status = ResourceManager.add_database(core_session, name=sapase_db,
                                                      port=db_data['sap_ase_db_config']['port'],
                                                      fqdn=db_data['sap_ase_db_config']['hostname'],
                                                      description=db_data['sap_ase_db_config']['description'],
                                                      databaseclass=db_data['sap_ase_db_config']['databaseclass'],
                                                      instancename=db_data['sap_ase_db_config']['instancename'],
                                                      servicename=db_data['sap_ase_db_config']['servicename'])
    assert status, f'Database failed to add with result {sap_result}'
    database_list.append(sap_result)
    logger.info('SAP ASE database added successfully with service name filtered out silently by cloud backend')

    # update Oracle database description.
    result, status = ResourceManager.update_database(core_session, db_id=oracle_result, name=oracle_db,
                                                     fqdn=db_data['oracle_db_config']['hostname'],
                                                     port=db_data['oracle_db_config']['port'],
                                                     description='test_oracle database configuration',
                                                     instance=db_data['oracle_db_config']['instancename'],
                                                     db_class=db_data['oracle_db_config']['databaseclass'],
                                                     service_name=db_data['oracle_db_config']['servicename'])
    assert status, 'failed to update oracle database description as expected.'
    logger.info(f'Oracle db updated successfully {oracle_db}.')

    # Update SAP ASE database description
    result, status = ResourceManager.update_database(core_session, db_id=sap_result, name=sapase_db,
                                                     fqdn=db_data['sap_ase_db_config']['hostname'],
                                                     port=db_data['sap_ase_db_config']['port'],
                                                     description='test_SAP ASE database configuration',
                                                     instance=db_data['sap_ase_db_config']['instancename'],
                                                     db_class=db_data['sap_ase_db_config']['databaseclass'],
                                                     service_name=db_data['sap_ase_db_config']['servicename'])
    assert status, 'failed to update sap ase database description as expected.'
    logger.info(f'SAP ASE db updated successfully {sapase_db}.')

    # Update SQL database description
    result, status = ResourceManager.update_database(core_session, db_id=sql_result, name=sql_result,
                                                     fqdn=db_data['sql_db_config']['hostname'],
                                                     port=db_data['sap_ase_db_config']['port'],
                                                     description='test description for sql database',
                                                     instance=db_data['sql_db_config']['instancename'])
    assert status, f'failed to update sql database {sql_db} description.'
    logger.info(f'sql db updated successfully {sql_db}.')
