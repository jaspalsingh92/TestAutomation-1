import pytest
import logging
from Utils.guid import guid
from Shared.API.infrastructure import ResourceManager

logger = logging.getLogger("test")


@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_add_delete_database_permission_port_specified(core_session, database_config, users_and_roles,
                                                       cleanup_resources):
    """
    C281976 Add/delete database permissions if database port has been specified.
    :param core_session: Authenticated Centrify session.
    :param database_config:fixture to create database with accounts.
    :param users_and_roles: Fixture to manage roles and user.
    :param cleanup_resources:cleans up resources
    """
    # Creating a database without defined port.
    database_list = cleanup_resources[2]
    db_data = database_config['sql_db_config']
    db_name = f"{db_data['db_name']}{guid()}"
    db_result, db_success = ResourceManager.add_database(core_session, name=db_name, port=None,
                                                         fqdn=db_data['hostname'],
                                                         databaseclass=db_data['databaseclass'],
                                                         description=db_data['description'],
                                                         instancename=db_data['instancename'],
                                                         servicename=db_data['servicename'])

    assert db_success, f'Failed to create database without defined port:API response result:{db_result}'
    logger.info(f'Successfully created database without defined port :{db_result}')
    database_list.append(db_result)

    # Updating the database setting.
    update_db_res, update_db_success = ResourceManager.update_database(core_session, db_result,
                                                                       db_name,
                                                                       db_data['hostname'], db_data['port'],
                                                                       db_data['description'],
                                                                       db_data['instancename'])
    assert update_db_success, f"Fail to update database: API response result:{update_db_res}"
    logger.info(f"Successfully updated database with port:{update_db_res}")

    # Cloud user session with "Privileged Access Service Administrator"rights.
    cloud_user_session = users_and_roles.get_session_for_user('Privileged Access Service Administrator')
    assert cloud_user_session.auth_details, f'Failed to create with PAS administrator:{cloud_user_session}'
    cloud_user = cloud_user_session.auth_details['User']
    cloud_user_id = cloud_user_session.auth_details['UserId']
    logger.info(
        f'User with Privileged Access Service Administrator Rights login successfully: user_Name:{cloud_user}')

    # Assigning "Delete" permission to Cloud user.
    db_perm_result, db_perm_success = ResourceManager.assign_database_permissions(core_session, "Delete",
                                                                                  cloud_user,
                                                                                  cloud_user_id,
                                                                                  pvid=db_result)
    assert db_perm_success, f'Failed to "Delete rights:API response result:{db_perm_result}'
    logger.info(f'successfully assigned "Delete" rights to user: {db_perm_result}')
