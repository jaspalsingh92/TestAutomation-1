import pytest
from Shared.API.infrastructure import ResourceManager
from Utils.guid import guid
import logging

logger = logging.getLogger("test")


@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_Change_Account_managed(core_session, pas_config, remote_users_qty1, detect_proxy):
    """
    :param core_session:  Authenticated Centrify Session.
    :param pas_config: fixture reading data from resources_data.yaml file.
    TC: C2544 - Change Account to be a managed account and verify password changed in 5 minutes
    trying to validate the added manage Account password Activity log's
            Steps:
                1. Try to add a system along with an manage account
                    -Assert Failure
                2. Try to check in the account password is rotated
                    -Assert Failure
                3. Try to validate account activity log's
    """
    user = core_session.get_user()
    user_name = user.get_login_name()

    sys_name = f"Automatedsystem{guid()}"
    res_data = pas_config
    user = remote_users_qty1
    sys_result, status = ResourceManager.add_system(core_session, sys_name,
                                                    res_data['Windows_infrastructure_data']['FQDN'], 'Windows', "Rdp")
    assert status, f"failed to add system"

    success, response = ResourceManager.update_system(core_session, sys_result, sys_name,
                                                      res_data['Windows_infrastructure_data']['FQDN'], 'Windows',
                                                      managementmode='RpcOverTcp')
    assert success, f"failed to change the management mode:API response result:{response}"
    logger.info(f"Successfully updated the system:{response}")

    account_id, status = ResourceManager.add_account(core_session, user[0], 'Hello123', sys_result)
    assert status, f'failed to add account'

    success, response = ResourceManager.update_account(core_session, account_id, user[0],
                                                       host=sys_result, ismanaged=True)
    assert success, f'Updating account failed. API response: {response}'

    server_id = ResourceManager.wait_for_server_to_exist_return_id(core_session, sys_name)
    acc_id = ResourceManager.wait_for_account_to_exist_return_id(core_session, user[0])
    assert server_id == sys_result, "Server was not created"
    assert acc_id == account_id, "Account was not created"

    res, success = ResourceManager.rotate_password(core_session, account_id)
    assert success, f"Failed to add account in the portal: {res}"

    checkout_password, response = ResourceManager.check_out_password(core_session, 1,
                                                                     accountid=account_id)

    assert checkout_password['Password'] != 'Hello123', f'Checkout Password Failed. API response: {response}'
    row = ResourceManager.get_system_activity(core_session, sys_result)
    checkout_activity = row[0]['Detail']
    created_date_json = str(row[0]['When'])
    ResourceManager.get_date(created_date_json)
    assert f'{user_name} checked out local account "{user[0]}" password for system "{sys_name}"' \
           f'({res_data["Windows_infrastructure_data"]["FQDN"]})' == checkout_activity, "No system activity data "
    logger.info(f"account activity list:{row}")
