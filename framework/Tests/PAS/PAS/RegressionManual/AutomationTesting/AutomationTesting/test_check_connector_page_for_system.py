import pytest
import logging
from Shared.API.infrastructure import ResourceManager
from Shared.API.redrock import RedrockController
from Shared.UI.Centrify.SubSelectors.forms import ReadOnlyTextField
from Shared.UI.Centrify.SubSelectors.grids import GridRowByGuid
from Shared.UI.Centrify.SubSelectors.navigation import ActiveMainContentArea
from Utils.config_loader import Configs

logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi_ui
def test_check_connector_page_for_system(core_session, pas_windows_setup, users_and_roles):
    """
    TC:C2171 Check UI on Connectors page for a system.
    :param:core_session: Returns Authenticated Centrify session.
    :param:users_and_roles:Fixture to manage roles and user.
    :param pas_windows_setup: Return a fixture.
    """

    # Creating a system and account.
    system_id, account_id, sys_info, connector_id, user_password = pas_windows_setup()

    # Cloud user session with "Privileged Access Service Administrator".
    cloud_user_session = users_and_roles.get_session_for_user('Privileged Access Service Administrator')
    user_name = cloud_user_session.auth_details['User']
    user_id = cloud_user_session.auth_details['UserId']

    # UI session with "Privileged Access Service Administrator" rights.
    ui = users_and_roles.get_ui_as_user('Privileged Access Service Administrator')

    # Assigning system "View,Delete" permission
    assign_system_result, assign_system_success = ResourceManager.assign_system_permissions(core_session,
                                                                                            "View,Delete",
                                                                                            user_name,
                                                                                            user_id,
                                                                                            'User',
                                                                                            system_id)
    assert assign_system_success, f"Failed to assign system permissions: API response result: {assign_system_result}"
    logger.info(f'Successfully assigned "View" permission to user:{assign_system_result}.')

    # Getting the connectors Details.
    connector_details = Configs.get_environment_node('connector_data', 'automation_main')
    list_connectors_id = []
    connectors_details = RedrockController.get_all_proxy(core_session)
    for connector_detail in connectors_details:
        if connector_detail['Name'] == connector_details['connector']:
            list_connectors_id.append(connector_detail['ID'])

    # Choosing the connector for the system.
    result, success = ResourceManager.update_system(core_session,
                                                    system_id=system_id,
                                                    name=sys_info[0],
                                                    fqdn=sys_info[1],
                                                    computerclass=sys_info[2],
                                                    proxycollectionlist=connector_id,
                                                    chooseConnector="on",
                                                    filterConnectorCombo="all"
                                                    )
    assert success, f'Failed to save the connector for the system: API response result: {result}.'
    logger.info(f'Successfully save the connector  for the system: API response result: {result}.')

    # UI Launch
    ui.navigate('Resources', 'Systems')
    ui.search(sys_info[0])
    ui.click_row(GridRowByGuid(system_id))
    ui.tab('Connectors', check_rendered_tab=False)
    ui.switch_context(ActiveMainContentArea())
    ui.expect(ReadOnlyTextField('filterConnectorCombo'),
              'Expected the username field to be readonly for this filterConnectorCombo strategy but it is not.')
    logger.info('Successfully found connector settings  grayed and no error icon')
