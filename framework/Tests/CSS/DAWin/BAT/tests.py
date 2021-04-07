###### Case# C1238801 ######
# Create DA installation
# TBD - Link to testrail URL

from Shared.CSS import css_win_constants
from .dawin_da_agent_test import test_da_agent_master, tear_down_agent
from Utils.config_loader import Configs
from .common import *
from Shared.CSS.css_win_utils import *

SETTINGS = Configs.get_test_node("da_installation", "settings")
tear_down = SETTINGS["tear_down"]
VRY_SMALL_RETRY = SETTINGS['vry_small_retry']
SMALL_RETRY = SETTINGS['small_retry']
MED_RETRY = SETTINGS['med_retry']
BIG_RETRY = SETTINGS['big_retry']


@pytest.mark.dawin_bat
# def test_master(log_test_name, dawin_testagent_installed, dawin_joined, css_testee_login_as_domain_admin,
#                 css_testee_machine, dawin_test_client_installed, css_client_login, css_client_test_machine):
def test_master(dawin_joined, css_testee_login_as_domain_admin, dawin_test_client_installed, css_client_login,
                css_client_test_machine):
    logger.info("Case# C1238801: \"Create DA installation\"")
    username = r"%s\%s" % (dawin_joined['domain_name'].split('.')[0], "administrator")
    try:
        logger.info("Start the test on test machine...")

        # clean slate
        rdp_kill_all()

        remote_framework_path = css_win_constants.remote_framework_path
        start_slave_cmd = f"cd {remote_framework_path} & " \
                          f"python -m pytest Tests\\CSS\\DAWin\\BAT\\tests.py::test_start_slave_steps"
        logger.info("Running: " + start_slave_cmd)
        rdp_session(username, dawin_joined['admin_password'], dawin_joined['public_ip'])
        # run win app driver
        # start_app_remotely(username,
        #                    dawin_joined['admin_password'],
        #                    dawin_joined['public_ip'],
        #                    css_win_constants.remote_winappdriver_startup_path)

        error_list = []

        rc, result, error = css_testee_login_as_domain_admin.send_command(start_slave_cmd)

        logger.debug("rc %s, result %s, error %s", str(rc), str(result), str(error))

        rdp_kill_all()

        if rc == 0:
            rc, result, error = test_da_agent_master(dawin_test_client_installed, css_client_login,
                                                     css_client_test_machine)
            rdp_kill_all()
            if rc == 0:
                logger.info('video capture test case start')
                start_slave_cmd = f"cd {remote_framework_path} & " \
                                  "python -m pytest " \
                                  "Tests\\CSS\\DAWin\\BAT\\tests.py::test_centrify_da_auditor"
                rdp_session(username, dawin_joined['admin_password'], dawin_joined['public_ip'])
                rc, result, error = css_testee_login_as_domain_admin.send_command(start_slave_cmd)
                if rc != 0:
                    error_list.append([rc, result, error])
            else:
                error_list.append([rc, result, error])
        else:
            logger.info("Last Test Failed: " + str(error))
            error_list.append([rc, result, error])

        if tear_down:
            rc, result, error = tear_down_agent(dawin_test_client_installed, css_client_login, css_client_test_machine)
            if rc != 0:
                error_list.append([rc, result, error])
            # un-configure Audit Store & DA installation
            start_slave_cmd = f"cd {remote_framework_path} & " \
                              "python -m pytest " \
                              "Tests\\CSS\\DAWin\\BAT\\tests.py::test_teardown_unconfigure"

            # if rc != 0:  # open RDP for teardown un-configure if it is not opened till now due to last step failure
            rdp_session(username, dawin_joined['admin_password'], dawin_joined['public_ip'])
            rc, result, error = css_testee_login_as_domain_admin.send_command(start_slave_cmd)
            if rc != 0:
                error_list.append([rc, result, error])

        log_assert(len(error_list) == 0, "Test Failed")

    finally:
        rdp_kill_all()
        for data in error_list:
            logger.info("Error: rc=%s  result=%  error=%s", str(data[0]), str(data[1]), str(data[2]))
        logger.info("test_master() finish")


###### Slave Test Cases ######


def test_start_slave_steps():
    # Create session to control the entire desktop
    dskCap = {"app": "Root", "deviceName": "WindowsPC"}
    dskSession = webdriver.Remote(
        command_executor='http://127.0.0.1:4723',
        desired_capabilities=dskCap)

    logger.info("Run step 1 on test machine")
    test_centrify_da_console_install(dskSession)

    # not being run to simplify as Jacky's comment
    # logger.info("Run step 2 on test machine")
    # test_centrify_da_console_version(dskSession)

    logger.info("Run step 3 on test machine")
    test_configure_audit_store(dskSession)

    logger.info("Run step 4 'Configure Controller' on test machine")
    show_desktop(dskSession)
    test_configure_collector(dskSession)

    logger.info("Run step 5 Configure audit manager on test machine")
    test_centrify_audit_manager(dskSession)

    logger.info("Exiting")
    dskSession.quit()


def test_centrify_da_auditor():
    launch_application(css_win_constants.da_auditor_startup_path)
    desktop = get_desktop()
    ok_centrify_license_dlg(desktop)
    window = try_find_element(desktop, FindElementBy.CLASS, "MMCMainFrame", MED_RETRY)

    toolbar = try_find_element(window,
                               FindElementBy.CLASS,
                               'ToolbarWindow32', SMALL_RETRY)
    while True:
        one_level_up = try_find_element(toolbar, FindElementBy.NAME, "Up One Level", VRY_SMALL_RETRY, True)
        if one_level_up is not None:
            click_hold(desktop, one_level_up)
        break

    # get main tree root node of the TreeView in left panel
    list_view = window \
        .find_element_by_class_name("SysListView32")

    audit_session = try_find_element(desktop, FindElementBy.NAME, 'Audit Sessions', SMALL_RETRY)

    double_click(desktop, audit_session)

    # subtree element
    subtree_element = try_find_element(desktop, FindElementBy.NAME, 'Today', SMALL_RETRY)

    double_click(desktop, subtree_element)

    # filter condition for demo only
    filter = try_find_element(desktop, FindElementBy.NAME, 'Completed', SMALL_RETRY, True)
    if filter is None:
        filter = try_find_element(desktop, FindElementBy.NAME, 'In Progress', SMALL_RETRY)

    right_button = list_view.find_element_by_name('Column right')

    while not filter.is_displayed():
        double_click(desktop, right_button)

    double_click(desktop, filter)

    # daplayer
    video_player_window = try_find_element(desktop, FindElementBy.NAME,
                                           "Centrify DirectAudit Session Player", SMALL_RETRY)
    click_hold(desktop,
               try_find_element(video_player_window, FindElementBy.AUTOMATION_ID, "MaximizeButton", SMALL_RETRY))

    click_hold(desktop, try_find_element(video_player_window, FindElementBy.AUTOMATION_ID, "CloseButton", SMALL_RETRY))
    click_hold(desktop, try_find_element(window, FindElementBy.NAME, "Close", SMALL_RETRY))

    log_assert(video_player_window is not None, "test_centrify_da_auditor FAILED")


def test_centrify_audit_manager(desktop):
    da_instance_name = SETTINGS['da_instance_name']

    audit_manager_session = launch_application(css_win_constants.audit_manager_startup_path)
    # configure

    main_window = try_find_element(desktop, FindElementBy.CLASS, 'WindowsForms10.Window.8.app.0.34f5582_r6_ad1',
                                   SMALL_RETRY)

    click_hold(desktop, try_find_element(main_window, FindElementBy.AUTOMATION_ID, 'm_configureButton', SMALL_RETRY))

    window = try_find_element(desktop, FindElementBy.CLASS, 'WindowsForms10.Window.8.app.0.34f5582_r6_ad1', SMALL_RETRY)

    da_list = try_find_element(window, FindElementBy.AUTOMATION_ID, 'm_installList', SMALL_RETRY)

    # select DA installation window
    da_instance = try_find_element(da_list, FindElementBy.NAME, da_instance_name, SMALL_RETRY)
    timer = 0
    while not da_instance.is_enabled() and timer < 100:
        timer = timer + 1

    click_hold(desktop, da_instance)

    next_button = try_find_element(window, FindElementBy.AUTOMATION_ID, 'm_nextButton', VRY_SMALL_RETRY)
    timer = 0
    while not next_button.is_enabled() and timer < 100:
        timer = timer + 1

    click_hold(desktop, next_button)
    # select windows authentication mode
    click_hold(desktop, try_find_element(window, FindElementBy.AUTOMATION_ID, 'm_windowsOption', SMALL_RETRY))

    click_hold(desktop, try_find_element(window, FindElementBy.AUTOMATION_ID, 'm_nextButton', VRY_SMALL_RETRY))

    # review and confirm options
    click_hold(desktop, try_find_element(window, FindElementBy.AUTOMATION_ID, 'm_nextButton', SMALL_RETRY))

    # finish
    click_hold(desktop, try_find_element(window, FindElementBy.NAME, 'Finish', MED_RETRY))

    # restart the service
    click_hold(desktop, try_find_element(main_window, FindElementBy.AUTOMATION_ID, 'm_restartButton', SMALL_RETRY))

    audit_manager_session.quit()


def test_centrify_da_console_install(desktop):
    da_console_config = SETTINGS['audit_console']
    sql_instance_name = SETTINGS['sql_instance_name']
    sql_machine_name = SETTINGS['sql_machine_name']
    new_management_db_name = SETTINGS['new_management_db_name']
    da_instance_name = SETTINGS['da_instance_name']
    licence_key = SETTINGS['licence_key']
    disable_video_capturing = da_console_config['disable_video_capturing']
    review_own_session = da_console_config['review_own_session']
    delete_own_session = da_console_config['delete_own_session']
    disable_audit_store_install_now = da_console_config['disable_audit_store_install_now']

    launch_application(css_win_constants.da_administrator_startup_path)

    ok_centrify_license_dlg(desktop)
    window = try_find_element(desktop, FindElementBy.CLASS, 'WindowsForms10.Window.8.app.0.141b42a_r41_ad1',
                              MED_RETRY, True)
    da_installed = False
    if window is not None:
        # if multiple da installations are present
        installed_da_popup = try_find_element(window, FindElementBy.AUTOMATION_ID, 'm_forest', VRY_SMALL_RETRY, True)
        if installed_da_popup is not None:
            cancel = try_find_element(window, FindElementBy.AUTOMATION_ID, 'm_cancelButton', VRY_SMALL_RETRY)
            click_hold(desktop, cancel)
            da_installed = True

    # new_install = try_find_element(window, FindElementBy.NAME, 'New Installation Wizard', SMALL_RETRY, True)

    if window is None or da_installed:
        da_node = get_da_installation_node(desktop)
        click_hold(desktop, da_node)
        click_context_menu(desktop, da_node, "New Installation...")

    if window is None:
        window = try_find_element(desktop, FindElementBy.CLASS, 'WindowsForms10.Window.8.app.0.141b42a_r41_ad1',
                                  SMALL_RETRY, True)

    try_find_element(window, FindElementBy.AUTOMATION_ID, 'm_name', SMALL_RETRY).send_keys(da_instance_name)
    click_hold(desktop, try_find_element(window, FindElementBy.AUTOMATION_ID, 'm_nextButton', SMALL_RETRY))
    click_hold(desktop, try_find_element(window, FindElementBy.AUTOMATION_ID, 'm_createOption', SMALL_RETRY))

    sql_to_connect = sql_machine_name + '\\' + sql_instance_name
    sql_to_connect = sql_to_connect.strip("\\")

    try_find_element(window, FindElementBy.AUTOMATION_ID, '1001', SMALL_RETRY).send_keys(sql_to_connect)

    try_find_element(window, FindElementBy.AUTOMATION_ID, 'm_database', SMALL_RETRY).send_keys(new_management_db_name)
    click_hold(desktop, try_find_element(window, FindElementBy.AUTOMATION_ID, 'm_nextButton', SMALL_RETRY))

    ## Page 3
    set_sql_login_account(window, desktop, SETTINGS["sql_login_account"])
    click_hold(desktop, try_find_element(window, FindElementBy.AUTOMATION_ID, 'm_nextButton', SMALL_RETRY))

    ## For AdminPopUp
    popup_handle = try_find_element(desktop, FindElementBy.NAME, 'OK', VRY_SMALL_RETRY, True)

    if popup_handle is not None:
        click_hold(desktop, popup_handle)

    key_page = try_find_element(window, FindElementBy.AUTOMATION_ID, 'm_key', VRY_SMALL_RETRY, True)
    while key_page is None:
        click_hold(desktop, try_find_element(window, FindElementBy.AUTOMATION_ID, 'm_nextButton', SMALL_RETRY))
        key_page = try_find_element(window, FindElementBy.AUTOMATION_ID, 'm_key', VRY_SMALL_RETRY, True)

    key_page.send_keys(licence_key)

    ## Product key Page
    # try_find_element(window, FindElementBy.AUTOMATION_ID, 'm_key', SMALL_RETRY).send_keys(licence_key)
    click_hold(desktop, try_find_element(window, FindElementBy.AUTOMATION_ID, 'm_addButton', SMALL_RETRY))
    click_hold(desktop, try_find_element(window, FindElementBy.AUTOMATION_ID, 'm_nextButton', SMALL_RETRY))

    ## location page
    click_hold(desktop, try_find_element(window, FindElementBy.AUTOMATION_ID, 'm_nextButton', SMALL_RETRY))

    ## permissions
    if disable_video_capturing:
        click_hold(desktop,
                   try_find_element(window, FindElementBy.AUTOMATION_ID, 'EnableVideoAuditCheckBox', SMALL_RETRY))
    if review_own_session:
        click_hold(desktop,
                   try_find_element(window, FindElementBy.AUTOMATION_ID, 'DisableSelfReviewCheckBox', SMALL_RETRY))
    if delete_own_session:
        click_hold(desktop,
                   try_find_element(window, FindElementBy.AUTOMATION_ID, 'DisableSelfDeleteCheckBox', SMALL_RETRY))

    click_hold(desktop, try_find_element(window, FindElementBy.AUTOMATION_ID, 'm_nextButton', SMALL_RETRY))

    ## review
    click_hold(desktop, try_find_element(window, FindElementBy.AUTOMATION_ID, 'm_nextButton', SMALL_RETRY))

    ## finish
    if disable_audit_store_install_now:
        click_hold(desktop, try_find_element(desktop, FindElementBy.AUTOMATION_ID, 'm_option', BIG_RETRY))

    click_hold(desktop, try_find_element(desktop, FindElementBy.AUTOMATION_ID, 'm_nextButton', BIG_RETRY))


def test_centrify_da_console_version(desktop):
    window = try_find_element(desktop, FindElementBy.CLASS, 'MMCMainFrame', SMALL_RETRY)
    pop_up = try_find_element(window, FindElementBy.NAME, 'OK', VRY_SMALL_RETRY, True)
    if pop_up is not None:
        click_hold(desktop, pop_up)

    help_elements = window.find_elements_by_name('Help')

    for element in help_elements:
        if element.get_attribute('LocalizedControlType') == 'menu item':
            click_hold(desktop, element)
            element.send_keys(Keys.ARROW_DOWN)
            element.send_keys(Keys.ARROW_DOWN)
            element.send_keys('b')

    complete_text = str(try_find_element(window, FindElementBy.AUTOMATION_ID, '4160', SMALL_RETRY).text)
    click_hold(desktop, window.find_element_by_accessibility_id('1'))
    index = complete_text.index('Version')
    version = complete_text[index:]

    assert (SETTINGS['version'] == version), 'version mismatch it should be:' + SETTINGS['version']


def test_configure_audit_store(desktop):
    """
    Configures audit store in a pre-configured Direct Audit installation.
    Expects Audit Manager window to be open
    """
    ok_centrify_license_dlg(desktop)

    audit_store_setting = SETTINGS["audit_store"]
    da_instance_name = SETTINGS['da_instance_name']
    cntry_install = get_da_installation_node(desktop, da_instance_name)

    # double click to open tree-node
    double_click(desktop, cntry_install)
    ok_centrify_license_dlg(desktop)
    open_tree_node(desktop, cntry_install)

    # region go to Audit Stores tree-node and context-click Add Audit Store...
    cntry_audit_stores = cntry_install.find_element_by_name("Audit Stores")
    double_click(desktop, cntry_audit_stores)
    click_context_menu(desktop, cntry_audit_stores, "Add Audit Store...")
    # endregion

    # region Add Audit Store Wizard
    audit_store_wizard = try_find_element(desktop, FindElementBy.NAME, "Add Audit Store Wizard", MED_RETRY)
    if audit_store_setting["store_display_name"] == "":
        raise Exception("store_display_name cannot be blank")
    clear_txtbox(try_find_element(audit_store_wizard, FindElementBy.NAME, "Display name:", MED_RETRY)) \
        .send_keys(audit_store_setting["store_display_name"])

    while try_find_element(audit_store_wizard, FindElementBy.AUTOMATION_ID, "m_winAndUnixRadioBtn",
                           VRY_SMALL_RETRY, ignore_if_not_found=True) is None:
        click_hold(desktop, try_find_element(audit_store_wizard, FindElementBy.NAME, "Next >", MED_RETRY))

    while try_find_element(audit_store_wizard, FindElementBy.NAME, "Add Site",
                           VRY_SMALL_RETRY, ignore_if_not_found=True) is None:  # retry until next screen found
        affinity = audit_store_setting["affinity"].lower()
        if affinity == "windows and unix":
            click_hold(desktop,
                       try_find_element(audit_store_wizard, FindElementBy.AUTOMATION_ID, "m_winAndUnixRadioBtn",
                                       MED_RETRY))
        elif affinity == "windows":
            click_hold(desktop,
                       try_find_element(audit_store_wizard, FindElementBy.AUTOMATION_ID, "m_winRadioBtn", MED_RETRY))
        elif affinity == "unix":
            click_hold(desktop,
                       try_find_element(audit_store_wizard, FindElementBy.AUTOMATION_ID, "m_unixRadioBtn", MED_RETRY))
        click_hold(desktop, try_find_element(audit_store_wizard, FindElementBy.NAME, "Next >", MED_RETRY))

    # select AD-site
    add_site = try_find_element(audit_store_wizard, FindElementBy.NAME, "Add Site", MED_RETRY)
    while try_find_element(audit_store_wizard, FindElementBy.NAME, "Select Active Directory Sites",
                           VRY_SMALL_RETRY, ignore_if_not_found=True) is None:
        click_hold(desktop, add_site)  # retry click until next screen loaded

    ad_sites = try_find_element(audit_store_wizard, FindElementBy.NAME, "Select Active Directory Sites", MED_RETRY)
    click_hold(desktop, try_find_element(ad_sites, FindElementBy.NAME, "Select a site from current forest", MED_RETRY))
    sites_list = try_find_element(ad_sites, FindElementBy.AUTOMATION_ID, "m_siteList", MED_RETRY)
    click_hold(desktop, sites_list)  # focus it

    # retry AD site selecting until it's OK button is enabled
    while not try_find_element(ad_sites, FindElementBy.NAME, "OK", MED_RETRY).is_enabled():
        if audit_store_setting["ad_site"] == "":
            click_hold(desktop, try_find_element(sites_list, FindElementBy.AUTOMATION_ID, "ListViewItem-0", MED_RETRY))
        else:
            # all child in list
            found = False
            ad_sites_items = sites_list.find_elements_by_xpath(".//*")
            for item in ad_sites_items:
                if item.tag_name == 'ControlType.ListItem' and \
                        item.text.lower() == audit_store_setting["ad_site"].lower():
                    found = True
                    click_hold(desktop, item)
            if not found:
                raise Exception("AD Site '" + audit_store_setting["ad_site"] + "' not found")

    while not try_find_element(audit_store_wizard, FindElementBy.NAME, "Next >", MED_RETRY).is_enabled():
        click_hold(desktop,
                   try_find_element(ad_sites, FindElementBy.NAME, "OK", MED_RETRY))  # retry clicks until next enables

    click_hold(desktop, try_find_element(audit_store_wizard, FindElementBy.NAME, "Next >", MED_RETRY))
    while try_find_element(audit_store_wizard, FindElementBy.NAME, "Finish",
                           VRY_SMALL_RETRY, ignore_if_not_found=True) is None:  # retry clicks until Finish found
        click_hold(desktop, try_find_element(audit_store_wizard, FindElementBy.NAME, "Next >", MED_RETRY))
    click_hold(desktop, try_find_element(audit_store_wizard, FindElementBy.NAME, "Finish", MED_RETRY))

    # endregion

    # region Add Audit Store Database Wizard
    audit_store_db_wizard = try_find_element(desktop, FindElementBy.NAME, "Add Audit Store Database Wizard",
                                             MED_RETRY)
    clear_txtbox(try_find_element(audit_store_db_wizard, FindElementBy.NAME, "Display name:", MED_RETRY)) \
        .send_keys(audit_store_setting["db_display_name"])
    click_hold(desktop, try_find_element(audit_store_db_wizard, FindElementBy.NAME, "Next >", MED_RETRY))

    sql_to_connect = SETTINGS["sql_machine_name"] + "\\" + SETTINGS["sql_instance_name"]
    sql_to_connect = sql_to_connect.strip("\\")
    clear_txtbox(try_find_element(audit_store_db_wizard, FindElementBy.CLASS, "Edit", MED_RETRY)) \
        .send_keys(sql_to_connect)
    click_hold(desktop, try_find_element(audit_store_db_wizard, FindElementBy.NAME, "Next >", MED_RETRY))

    clear_txtbox(try_find_element(audit_store_db_wizard, FindElementBy.NAME, "Database name:", MED_RETRY)) \
        .send_keys(audit_store_setting["db_name"])
    active_chk = try_find_element(audit_store_db_wizard, FindElementBy.NAME, "Set as active database", MED_RETRY)

    if audit_store_setting["db_set_active"]:
        if not active_chk.is_selected():
            click_hold(desktop, active_chk)
    else:
        if active_chk.is_selected():
            click_hold(desktop, active_chk)
    click_hold(desktop, try_find_element(audit_store_db_wizard, FindElementBy.NAME, "Next >", VRY_SMALL_RETRY))

    set_sql_login_account(audit_store_db_wizard, desktop, SETTINGS["sql_login_account"])

    click_hold(desktop, try_find_element(audit_store_db_wizard, FindElementBy.NAME, "Next >", VRY_SMALL_RETRY))
    click_hold(desktop, try_find_element(audit_store_db_wizard, FindElementBy.NAME, "Next >", VRY_SMALL_RETRY))
    click_hold(desktop, try_find_element(audit_store_db_wizard, FindElementBy.NAME, "Finish", MED_RETRY))

    # endregion

    # region open tree-node, check Audit Store

    # refresh and open Audit Stores tree-node
    click_context_menu(desktop, cntry_audit_stores, "Refresh")
    open_tree_node(desktop, cntry_audit_stores)
    # open Audit Store tree-node
    cntry_audit_store = cntry_audit_stores.find_element_by_name(audit_store_setting["store_display_name"])
    open_tree_node(desktop, cntry_audit_store)
    # open Databases tree-node
    databases = cntry_audit_store.find_element_by_name("Databases")
    double_click(desktop, databases)

    # endregion

    log_assert(databases is not None, "test_config_audit_store PASSED")
    cntry_main_screen = try_find_element(desktop, FindElementBy.CLASS, "MMCMainFrame", SMALL_RETRY)
    click_hold(desktop, try_find_element(cntry_main_screen, FindElementBy.NAME, "Close", MED_RETRY))
    logger.info('application closed')


def test_configure_collector(desktop):
    """
    Configures controller in a pre-configured Direct Audit installation.
    """
    collector_setting = SETTINGS["collector"]
    collector_session = start_collector_configure()

    collector_win = try_find_element(desktop, FindElementBy.AUTOMATION_ID, "CollectorControlPanel", MED_RETRY)
    click_hold(desktop, try_find_element(collector_win, FindElementBy.AUTOMATION_ID, "m_configureButton", MED_RETRY))
    config_win = try_find_element(desktop, FindElementBy.NAME,
                                  "Centrify DirectAudit Collector Configuration Wizard", MED_RETRY)
    install_list = try_find_element(config_win, FindElementBy.AUTOMATION_ID, "m_installList", MED_RETRY)

    # all child in list
    found = False
    while not found:
        da_instances = install_list.find_elements_by_xpath(".//*")
        for item in da_instances:
            logger.info("item.tag_name: " + item.tag_name)
            logger.info("item.text.lower(): " + item.text.lower())
            if item.tag_name == 'ControlType.ListItem' and \
                    item.text.lower() == SETTINGS["da_instance_name"].lower():
                found = True
                click_hold(desktop, item)

    if not found:
        raise Exception("DA instance '" + SETTINGS["da_instance_name"] + "' not found. ")
    click_hold(desktop, try_find_element(config_win, FindElementBy.AUTOMATION_ID, "m_nextButton", MED_RETRY))

    clear_txtbox(try_find_element(config_win, FindElementBy.AUTOMATION_ID, "m_port", MED_RETRY)). \
        send_keys(collector_setting["listening_port"])

    while try_find_element(config_win, FindElementBy.AUTOMATION_ID, "m_windowsOption",
                           VRY_SMALL_RETRY, ignore_if_not_found=True) is None:
        click_hold(desktop, try_find_element(config_win, FindElementBy.AUTOMATION_ID, "m_nextButton", MED_RETRY))

    click_hold(desktop, try_find_element(config_win, FindElementBy.AUTOMATION_ID, "m_windowsOption", MED_RETRY))
    click_hold(desktop, try_find_element(config_win, FindElementBy.AUTOMATION_ID, "m_nextButton", MED_RETRY))

    clear_txtbox(try_find_element(config_win, FindElementBy.AUTOMATION_ID, "m_maxPoolSize", MED_RETRY)). \
        send_keys(collector_setting["max_pool_size"])
    click_hold(desktop, try_find_element(config_win, FindElementBy.AUTOMATION_ID, "m_nextButton", MED_RETRY))

    click_hold(desktop, try_find_element(config_win, FindElementBy.AUTOMATION_ID, "m_nextButton", MED_RETRY))

    click_hold(desktop, try_find_element(config_win, FindElementBy.NAME, "Finish", MED_RETRY))

    click_hold(desktop, try_find_element(collector_win, FindElementBy.AUTOMATION_ID, "m_restartButton", MED_RETRY))

    current_status = try_find_element(collector_win, FindElementBy.AUTOMATION_ID, "m_currentStatus", MED_RETRY)

    # wait for restart to complete
    sleep(2)

    log_assert(current_status.text.lower() == "started", "Collector not started")

    collector_session.quit()


def test_teardown_unconfigure():
    dskCap = {"app": "Root", "deviceName": "WindowsPC"}
    desktop = webdriver.Remote(
        command_executor='http://127.0.0.1:4723',
        desired_capabilities=dskCap)

    logger.info("Start tear-down")

    da_instance_name = SETTINGS['da_instance_name']
    audit_store_setting = SETTINGS["audit_store"]
    audit_manager = start_audit_manager(css_win_constants.da_administrator_startup_path)

    cntry_install = get_da_installation_node(desktop, da_instance_name)

    if cntry_install is not None:
        # double click to open tree-node
        # double_click(desktop, cntry_install)
        cntry_install.click()
        ok_centrify_license_dlg(desktop)
        open_tree_node(desktop, cntry_install)

        # region go to Audit Stores tree-node
        cntry_audit_stores = cntry_install.find_element_by_name("Audit Stores")
        open_tree_node(desktop, cntry_audit_stores)
        # endregion

        # region open tree-node, check Audit Store

        # refresh Audit Stores tree-node
        click_context_menu(desktop, cntry_audit_stores, "Refresh")
        open_tree_node(desktop, cntry_audit_stores)

        # open Audit Store tree-node
        cntry_audit_store = try_find_element(cntry_audit_stores, FindElementBy.NAME,
                                             audit_store_setting["store_display_name"], 3, True)
        if cntry_audit_store is not None:
            # raise Exception("Specified Audit Store " + audit_store_setting["store_display_name"] + " not found.")
            open_tree_node(desktop, cntry_audit_store)

            # select Databases tree-node
            databases = cntry_audit_store.find_element_by_name("Databases")
            double_click(desktop, databases)

            click_hold(desktop, cntry_audit_store)
            click_context_menu(desktop, cntry_audit_store, "Remove...")
            remove_dlg = try_find_element(desktop, FindElementBy.AUTOMATION_ID, "RemoveAuditStoreDialog", MED_RETRY)
            click_hold(desktop, try_find_element(remove_dlg, FindElementBy.AUTOMATION_ID, "m_delete", SMALL_RETRY))
            click_hold(desktop, try_find_element(remove_dlg, FindElementBy.AUTOMATION_ID, "m_okButton", SMALL_RETRY))

        cntry_confirm_dlg = try_find_element(desktop, FindElementBy.CLASS, "#32770", VRY_SMALL_RETRY, True)
        if cntry_confirm_dlg is not None:
            click_hold(desktop, try_find_element(remove_dlg, FindElementBy.NAME, "Yes", SMALL_RETRY))

        click_context_menu(desktop, cntry_install, "Remove")
        remove_dlg = try_find_element(desktop, FindElementBy.AUTOMATION_ID, "RemoveInstallationDialog", SMALL_RETRY)
        click_hold(desktop, try_find_element(remove_dlg, FindElementBy.AUTOMATION_ID, "m_deleteButton", SMALL_RETRY))

        # endregion
    else:
        pass  # no installation to un-configure

    audit_manager.quit()
