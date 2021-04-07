import logging
import pytest
from Shared.API.infrastructure import ResourceManager
from Shared.UI.Centrify.SubSelectors.grids import GridRowByGuid
from Shared.UI.Centrify.SubSelectors.modals import WarningModal
from Shared.UI.Centrify.SubSelectors.navigation import ActiveMainContentArea
from Utils.guid import guid
from Shared.UI.Centrify.selectors import TextArea, Modal, ConfirmModal, Div, LoadingMask

logger = logging.getLogger("test")

lock_tenant = True

pytestmark = [pytest.mark.ui, pytest.mark.pas, pytest.mark.bhavna]


def test_system_settings_Policy_page(add_single_system, core_admin_ui):
    """C2540 Settings on Policy page
       trying to get rdp through system account with in 15 minute
            Steps:
                Pre: Create system
                1. Try to update description for system
                    -Assert Failure
        """

    ui = core_admin_ui
    added_system_id, sys_info = add_single_system
    logger.info(
        f"System {sys_info[0]}, with fqdn {sys_info[1]} created successfully with Uuid {added_system_id}")
    description = f'{sys_info[0]}{guid()}'
    ui.navigate('Resources', 'Systems')
    ui.search(sys_info[0])
    ui.click_row(sys_info[0])
    ui.tab('Settings')

    # Step1: Update the description and compare the description
    ui.input('Description', description)
    ui.save()
    ui.expect(TextArea('Description', description), description, time_to_wait=15)
    logger.info(f"Update description for this System : {sys_info[0]}")

    ui.switch_context(ActiveMainContentArea())
    ui.input('Description', guid())
    ui.action('Select/Request Account')
    ui.switch_context(Modal(f'{sys_info[0]} Login'))
    ui.close_modal('Cancel')

    # Step2: Update the description and check weather Unsaved Changes pop is occurred without save
    ui.switch_context(ActiveMainContentArea())
    ui.input('Description', guid())
    ui.action('Add To Set')
    ui.switch_context(ConfirmModal())
    ui.button("No")
    ui.switch_context(Modal('Add To Set'))
    ui.button('Cancel')

    # Step3: Update the description and check weather Unsaved Changes pop is occurred without save and \
    # Add to set pop will occurred
    ui.switch_context(ActiveMainContentArea())
    ui.input('Description', guid())
    ui.action('Add To Set')
    ui.switch_context(ConfirmModal())
    ui.button('Yes')

    # Step4: Add to set name in windows system set
    ui.switch_context(Modal('Add To Set'))
    member_set_name = f'test_set_{guid()}'
    ui.tag_input('tagComboInput', member_set_name)
    ui.remove_context()
    ui.close_modal('Save')

    # Step3: Update the description and check weather Unsaved Changes pop is occurred without save and \
    # Add to set pop will occurred and then cancel
    ui.switch_context(ActiveMainContentArea())
    ui.input('Description', guid())
    ui.action('Add To Set')
    ui.switch_context(ConfirmModal())
    ui.button('Cancel')


@pytest.mark.rdp
def test_settings_Policy_page(core_session, pas_config, remote_users_qty1, cleanup_resources, cleanup_accounts,
                              core_admin_ui):
    """C2541 Settings on Policy page
       trying to get rdp through system account with in 15 minute
            Steps:
                Pre: Create system with 1 account hand
                1. Try to take rdp for system
                    -Assert Failure
                2. Try to checkout password for account
                    -Assert Failure
        """
    core_ui = core_admin_ui
    user_name = core_ui.get_user().get_login_name()
    system_list = cleanup_resources[0]
    accounts_list = cleanup_accounts[0]
    # Getting system details.
    sys_name = f'{"Win-2012"}{guid()}'
    user_password = 'Hello123'
    sys_details = pas_config
    add_user_in_target_system = remote_users_qty1
    fdqn = sys_details['Windows_infrastructure_data']['FQDN']
    # Adding system.
    add_sys_result, add_sys_success = ResourceManager.add_system(core_session, sys_name,
                                                                 fdqn,
                                                                 'Windows',
                                                                 "Rdp")
    assert add_sys_success, f"failed to add system:API response result:{add_sys_result}"
    logger.info(f"Successfully added system:{add_sys_result}")
    system_list.append(add_sys_result)

    success, response = ResourceManager.update_system(core_session, add_sys_result, sys_name,
                                                      fdqn, 'Windows',
                                                      allowremote=True, defaultcheckouttime=15)
    assert success, f"failed to change the management mode:API response result:{response}"
    logger.info(f"Successfully updated the system:{add_sys_result}")

    # Adding account in portal.
    acc_result, acc_success = ResourceManager.add_account(core_session, add_user_in_target_system[0],
                                                          password=user_password, host=add_sys_result,
                                                          ismanaged=True)
    assert acc_success, f"Failed to add account in the portal: {acc_result}"
    logger.info(f"Successfully added account {add_user_in_target_system[0]} in the portal")
    accounts_list.append(acc_result)
    core_ui.navigate('Resources', 'Accounts')
    core_ui.search(add_user_in_target_system[0])
    core_ui.right_click_action(GridRowByGuid(acc_result), 'Login')
    core_ui.switch_to_pop_up_window()
    core_ui.expect_disappear(LoadingMask(), f'RDP session never exited loading state for system {sys_name}',
                             time_to_wait=50)
    core_ui.switch_to_main_window()
    row = ResourceManager.get_system_activity(core_session, add_sys_result)
    assert f'{user_name} logged into system "{sys_name}"({fdqn}) from "web" using local account ' \
           f'"{add_user_in_target_system[0]}"' in row[0]['Detail'], "user not able to take rdp"
    password_checkout_result, password_checkout_success = \
        ResourceManager.check_out_password(core_session, 1, accountid=acc_result)
    new_cid = password_checkout_result['COID']
    assert password_checkout_result['Password'] is not user_password, \
        f"expected password equal to actual password: {password_checkout_result}"
    logger.info(f"password successfully checkout Account password: {new_cid}")


@pytest.mark.pas_failed
def test_account_settings_Policy_page(core_session, pas_setup, core_admin_ui, update_tenant_remote):
    """C2543 Update Account Settings page
            Steps:
                Pre: Create system with 1 account hand
                1. Try to update description for account
                    -Assert Failure
        """
    ui = core_admin_ui
    # Disable 'Allow access from a public network' policy on Global Security Setting page
    result, success = update_tenant_remote(core_session, False)
    assert success, f"Not able to disable 'Allow access from a public network' policy on Global Security Setting " \
                    f"page. API response result: {result}. "
    logger.info(f"'Allow access from a public network' policy disabled on Global Security Setting page")
    system_id, account_id, sys_info = pas_setup
    description = f'{sys_info[0]}{guid()}'
    logger.info(f"System: {sys_info[0]} successfully added with UUID: {system_id} and account: {sys_info[4]} "
                f"with UUID: {account_id} associated with it.")
    ui.navigate('Resources', 'Accounts')
    ui.search(sys_info[0])
    ui.click_row(sys_info[0])
    ui.tab('Settings')

    # Step1: Update the description and compare the description.
    ui.input('Description', description)
    ui.save()
    ui.expect(TextArea('Description', description), description, time_to_wait=15)
    logger.info(f"Update description for this account : {sys_info[4]}")

    # Step2: Update the description and check weather Unsaved Changes pop is occurred without save.
    ui.switch_context(ActiveMainContentArea())
    ui.input('Description', guid())
    ui.action('Update Password')
    ui.switch_context(ConfirmModal())
    ui.button('No')
    ui.switch_context(Modal('Update Unmanaged Password'))
    ui.button('Cancel')

    # Step3: Update the description and check weather Unsaved Changes pop is occurred without save.
    ui.switch_context(ActiveMainContentArea())
    ui.input('Description', guid())
    ui.action('Update Password')
    ui.switch_context(ConfirmModal())
    ui.button('Cancel')

    # Step3: Update the description and check weather Unsaved Changes pop is occurred without save and \
    # update unmanaged password pop will occurred.
    ui.switch_context(ActiveMainContentArea())
    ui.input('Description', guid())
    ui.action('Update Password')
    ui.switch_context(ConfirmModal())
    ui.button('Yes')
    ui.switch_context(Modal('Update Unmanaged Password'))
    ui.button('Cancel')

    # Step3: Update the description and check weather take rdp tab giving error.
    ui.switch_context(ActiveMainContentArea())
    ui.input('Description', guid())
    ui.action('Login')
    ui.wait_for_tab_with_name(f"Login session {sys_info[0]}")
    expected_alert_message = "Remote access not allowed. Please enable the 'Allow access from a public network' " \
                             "policy if web login from a public network is required."
    ui.switch_to_pop_up_window()
    ui.switch_context(WarningModal())
    assert ui.check_exists((Div(expected_alert_message))), \
        f"pop up warning message for Remote access is not same as : {expected_alert_message}"
    logger.info(f"Correct pop up warning message displayed for Remote access.")


def test_update_system_description(pas_setup, core_ui):
    """C2542 Save changes for two pages
       validate the updated system"""
    core_ui = core_ui
    system_description = guid()
    added_system_id, account_id, sys_info = pas_setup
    core_ui.navigate('Resources', 'Systems')
    core_ui.search(sys_info[0])
    core_ui.click_row(sys_info[0])
    core_ui.tab('Settings')
    core_ui.input('Description', system_description)
    core_ui.tab('Policy')
    core_ui.select_option("AllowRemote", "Yes")
    core_ui.save()
    core_ui.tab('Settings')
    core_ui.inner_text_of_element(TextArea('Description'), f'{system_description}',
                                  f'{sys_info[0]} failed to update description')
