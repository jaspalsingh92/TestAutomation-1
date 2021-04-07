import pytest
import logging
from Shared.API.infrastructure import ResourceManager
from Shared.API.redrock import RedrockController
from Shared.UI.Centrify.SubSelectors.grids import GridRowByGuid, GridRowCheckbox
from Utils.config_loader import Configs

logger = logging.getLogger("test")


@pytest.mark.api_ui
@pytest.mark.pas
@pytest.mark.pasapi
@pytest.mark.bhavna
def test_connector_setting(core_session, pas_windows_setup, users_and_roles, core_pas_admin_ui):
    """
    TC:C2170 Check connectors setting.
    :param core_session: Returns a API session.
    :param pas_windows_setup: Returns a fixture.
    :param users_and_roles: Gets user and role on demand.
    :param core_pas_admin_ui: Returns browser session.
    """

    # Creating a system and account.
    system_id, account_id, sys_info, connector_id, user_password = pas_windows_setup()

    # Cloud user session with "Privileged Access Service Administrator".
    cloud_user_session = users_and_roles.get_session_for_user('Privileged Access Service Administrator')
    user_name = cloud_user_session.auth_details['User']
    user_id = cloud_user_session.auth_details['UserId']

    # Assigning "Edit" permission for system to limited user.
    assign_system_perm_res, assign_system_perm_success = ResourceManager.assign_system_permissions(core_session,
                                                                                                   "Edit",
                                                                                                   user_name,
                                                                                                   user_id,
                                                                                                   'User',
                                                                                                   system_id)

    assert assign_system_perm_success, f"Failed to assign 'Edit' permissions to user for the system: API Response " \
                                       f"result: {assign_system_perm_res}. "
    logger.info(f"Successfully assign 'Edit' permissions to user for the system: {assign_system_perm_res}.")

    # Getting the connectors Details.
    connector_details = Configs.get_environment_node('connector_data', 'automation_main')
    connector_name = connector_details['connector']
    list_connectors_id = []
    connectors_details = RedrockController.get_all_proxy(cloud_user_session)
    for connector_detail in connectors_details:
        if connector_detail['Name'] == connector_name:
            list_connectors_id.append(connector_detail['ID'])

    # Choosing the connector for the system.
    update_system_result, update_system_success = ResourceManager.update_system(cloud_user_session,
                                                                                system_id=system_id,
                                                                                name=sys_info[0],
                                                                                fqdn=sys_info[1],
                                                                                computerclass=sys_info[2],
                                                                                proxycollectionlist=connector_id,
                                                                                chooseConnector="on",
                                                                                filterConnectorCombo="all",
                                                                                )
    assert update_system_success, f'Failed to save the connector for the system:' \
                                  f'API response result:{update_system_result}. '
    logger.info(f'Successfully save the connector {update_system_result} for the system.')

    # UI Launch
    ui = core_pas_admin_ui
    ui.navigate('Resources', 'Systems')
    ui.search(sys_info[0])
    ui.click_row(GridRowByGuid(system_id))
    ui.tab('Connectors', check_rendered_tab=False)
    assert ui.check_exists(GridRowCheckbox(connector_name, checked=True)), 'Expect the find connector checked but ' \
                                                                           'failed to find it. '
    logger.info(f'Successfully found the correct connector setting:{connector_name}.')
