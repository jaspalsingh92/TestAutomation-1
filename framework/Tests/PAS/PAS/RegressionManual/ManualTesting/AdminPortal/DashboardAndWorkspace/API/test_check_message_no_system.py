import pytest
import logging
from Shared.API.infrastructure import ResourceManager
from Shared.API.redrock import RedrockController

logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.bhavna
@pytest.mark.pas_skip("This one is not execute because multi thread not possible and not a valid test script for now.")
def test_check_message_no_system(core_session, users_and_roles):
    """
    TC:C2047 Check message when there are no systems.
    :param:core_session:Returns a API session.
    :param:users_and_roles:Fixture to manage roles and user.
    :param:cleanup_resources: Fixture for cleanup resources.

    """
    # finding all systems for cleanup:
    acc_script = "@/lib/server/get_accounts.js(mode:'AllAccounts', newcode:true, localOnly:true, colmemberfilter:" \
                 "'Select ID from VaultAccount WHERE Host IS NOT NULL')"
    acc = RedrockController.redrock_query(core_session, acc_script)
    for account in acc:
        if account['Row']['FQDN'] == "Check.Point":
            # Removing Admin Account for successful cleanup of system and account
            result, success, message = ResourceManager.set_administrative_account(core_session,
                                                                                  systems=[account['Row']['Host']])
            assert success, f"Failed to update Administrative account for system {account['Row']['Name']}"

            # Removing Admin Account for successful cleanup of system and account
            update_result, update_success = ResourceManager.update_system(core_session,
                                                                          account['Row']['Host'],
                                                                          account['Row']['Name'],
                                                                          account['Row']['FQDN'],
                                                                          'CheckPointGaia',
                                                                          sessiontype=account['Row']['SessionType'])
            assert update_success, f"Unable to remove admin account from this system: {account['Row']['Host']}"
            logger.info(f'System successfully updated with result: {result}')

            # deleting administrative account from this system
            del_result, del_success = ResourceManager.del_account(core_session, account['Row']['ID'])
            assert del_success, "Account could not be deleted"
            logger.info(f'account successfully deleted with result: {del_result}')

            # Removing Admin Account for successful cleanup of system and account
            result, success, message = ResourceManager.set_administrative_account(core_session, systems=[account['Row']['Host']])
            assert success, f"Failed to update Administrative account for system {account['Row']['Name']}"

    accounts = RedrockController.redrock_query(core_session, acc_script)
    for account in accounts:
        ResourceManager.del_account(core_session, account['Row']['ID'])

    # Delete computers from tenant
    system = RedrockController.get_computers(core_session)
    for SYS in system:
        ResourceManager.del_system(core_session, SYS["ID"])

    # Trying to get the data from system_by_type on dashboard and expecting no data or an empty list.
    get_system_type_result = RedrockController.get_system_type_dashboard_pie_chart(core_session)
    assert len(get_system_type_result) == 0, f"Data found in system_by_type in dashboard:" \
                                             f"API response result:{get_system_type_result}"
    logger.info(f"Could not found any data in system_by_type on"
                f" dashboard in without any system in tenant{get_system_type_result}")

    # Trying to get the data form system health on dashboard and expecting no data or an empty list.
    get_system_health_dashboard = RedrockController.get_systems_health_dashboard(core_session)
    assert len(get_system_health_dashboard) == 0, f"Data found in system health in dashboard:" \
                                                  f" API response result:{get_system_health_dashboard}"
    logger.info(f"Could not found any data in system health on  "
                f"dashboard without any system in tenant{get_system_health_dashboard}")
