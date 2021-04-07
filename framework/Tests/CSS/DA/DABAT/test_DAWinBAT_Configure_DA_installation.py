"""This module is intended to Automate the DA installation and configuration"""

import pytest

from Shared.CSS import css_win_constants
from Shared.CSS.css_win_utils import *
from Utils.config_loader import Configs
from .common import login_and_execute_cmds

logger = logging.getLogger('test')


class TestConfigureDAInstallation:
    """
    Install and configure the DA installation
    """
    settings = Configs.get_test_node("da_installation", "settings")
    vry_small_retry = settings['vry_small_retry']
    small_retry = settings['small_retry']
    med_retry = settings['med_retry']
    big_retry = settings['big_retry']
    filename = "test_DAWinBAT_Configure_DA_installation.py"
    class_name = "TestConfigureDAInstallation"

    @pytest.mark.bhavna
    @pytest.mark.css
    @pytest.mark.da_win_bat
    def test_master_create_da_installation(self, dawin_testagent_uploaded, dawin_installed, \
                                           css_testee_login_as_domain_admin):
        username = r"%s\%s" % (dawin_installed['domain_name'].split('.')[0], "administrator")
        login_and_execute_cmds(username, dawin_installed['admin_password'], dawin_installed['public_ip'],
                               css_testee_login_as_domain_admin, self.filename, self.class_name,
                               'test_create_da_installation')

    @pytest.mark.bhavna
    @pytest.mark.css
    @pytest.mark.da_win_bat
    def test_master_configure_connector_and_verify_version(self, dawin_installed, css_testee_login_as_domain_admin):
        username = r"%s\%s" % (dawin_installed['domain_name'].split('.')[0], "administrator")
        login_and_execute_cmds(username, dawin_installed['admin_password'], dawin_installed['public_ip'],
                               css_testee_login_as_domain_admin, self.filename, self.class_name,
                               'test_configure_collector_and_verify_version')

    @pytest.mark.bhavna
    @pytest.mark.css
    @pytest.mark.da_win_bat
    def test_master_centrify_da_agent_configure(self, css_client_login, css_client_test_machine):
        username = r"%s\%s" % (css_client_test_machine['domain_name'].split('.')[0], "administrator")
        login_and_execute_cmds(username, css_client_test_machine['admin_password'],
                               css_client_test_machine['public_ip'],
                               css_client_login, self.filename, self.class_name,
                               'test_centrify_da_agent_configure')
        
    # 1.Configure DA installation

    def test_create_da_installation(self):
        logger.info("--- Case C1238801")

        dsksession = get_desktop()
        logger.info("Creating the DA installation")
        self.test_centrify_da_console_install(dsksession)

        logger.info("Checking the DA package version")
        self.test_centrify_da_console_version(dsksession)

        logger.info("Adding the audit store")
        self.test_configure_audit_store(dsksession)

        logger.info("Exiting")
        dsksession.quit()

    def test_centrify_da_console_install(self, desktop):
        da_console_config = self.settings['audit_console']
        sql_instance_name = self.settings['sql_instance_name']
        sql_machine_name = self.settings['sql_machine_name']
        new_management_db_name = self.settings['new_management_db_name']
        da_instance_name = self.settings['da_instance_name']
        licence_key = self.settings['licence_key']
        disable_video_capturing = da_console_config['disable_video_capturing']
        review_own_session = da_console_config['review_own_session']
        delete_own_session = da_console_config['delete_own_session']
        disable_audit_store_install_now = da_console_config['disable_audit_store_install_now']

        launch_application(css_win_constants.da_administrator_startup_path)

        ok_centrify_license_dlg(desktop)
        window = try_find_element(desktop, FindElementBy.CLASS, 'WindowsForms10.Window.8.app.0.141b42a_r41_ad1',
                                  self.med_retry, True)
        da_installed = False
        if window is not None:
            # if multiple da installations are present
            installed_da_popup = try_find_element(window, FindElementBy.AUTOMATION_ID, 'm_forest', self.vry_small_retry,
                                                  True)
            if installed_da_popup is not None:
                cancel = try_find_element(window, FindElementBy.AUTOMATION_ID, 'm_cancelButton', self.vry_small_retry)
                click_hold(desktop, cancel)
                da_installed = True

        if window is None or da_installed:
            da_node = get_da_installation_node(desktop)
            click_hold(desktop, da_node)
            click_context_menu(desktop, da_node, "New Installation...")

        new_install = try_find_element(desktop, FindElementBy.NAME, 'New Installation Wizard', self.small_retry, True)
        try_find_element(new_install, FindElementBy.AUTOMATION_ID, 'm_name', self.small_retry).send_keys(
            da_instance_name)
        click_hold(desktop,
                   try_find_element(new_install, FindElementBy.AUTOMATION_ID, 'm_nextButton', self.small_retry))
        click_hold(desktop,
                   try_find_element(new_install, FindElementBy.AUTOMATION_ID, 'm_createOption', self.small_retry))

        sql_to_connect = sql_machine_name + '\\' + sql_instance_name
        sql_to_connect = sql_to_connect.strip("\\")

        try_find_element(new_install, FindElementBy.AUTOMATION_ID, '1001', self.small_retry).send_keys(sql_to_connect)

        try_find_element(new_install, FindElementBy.AUTOMATION_ID, 'm_database', self.small_retry).send_keys(
            new_management_db_name)
        click_hold(desktop,
                   try_find_element(new_install, FindElementBy.AUTOMATION_ID, 'm_nextButton', self.small_retry))

        ## Page 3
        set_sql_login_account(new_install, desktop, self.settings["sql_login_account"])
        click_hold(desktop,
                   try_find_element(new_install, FindElementBy.AUTOMATION_ID, 'm_nextButton', self.small_retry))

        ## For AdminPopUp
        popup_handle = try_find_element(desktop, FindElementBy.NAME, 'OK', self.vry_small_retry, True)

        if popup_handle is not None:
            click_hold(desktop, popup_handle)

        key_page = try_find_element(new_install, FindElementBy.AUTOMATION_ID, 'm_key', self.vry_small_retry, True)
        while key_page is None:
            click_hold(desktop,
                       try_find_element(new_install, FindElementBy.AUTOMATION_ID, 'm_nextButton', self.small_retry))
            key_page = try_find_element(new_install, FindElementBy.AUTOMATION_ID, 'm_key', self.vry_small_retry, True)

        key_page.send_keys(licence_key)

        ## Product key Page
        # try_find_element(window, FindElementBy.AUTOMATION_ID, 'm_key', SMALL_RETRY).send_keys(licence_key)
        click_hold(desktop, try_find_element(new_install, FindElementBy.AUTOMATION_ID, 'm_addButton', self.small_retry))
        click_hold(desktop,
                   try_find_element(new_install, FindElementBy.AUTOMATION_ID, 'm_nextButton', self.small_retry))

        ## location page
        click_hold(desktop,
                   try_find_element(new_install, FindElementBy.AUTOMATION_ID, 'm_nextButton', self.small_retry))

        ## permissions
        if disable_video_capturing:
            click_hold(desktop,
                       try_find_element(new_install, FindElementBy.AUTOMATION_ID, 'EnableVideoAuditCheckBox',
                                        self.small_retry))
        if review_own_session:
            click_hold(desktop,
                       try_find_element(new_install, FindElementBy.AUTOMATION_ID, 'DisableSelfReviewCheckBox',
                                        self.small_retry))
        if delete_own_session:
            click_hold(desktop,
                       try_find_element(new_install, FindElementBy.AUTOMATION_ID, 'DisableSelfDeleteCheckBox',
                                        self.small_retry))

        click_hold(desktop,
                   try_find_element(new_install, FindElementBy.AUTOMATION_ID, 'm_nextButton', self.small_retry))

        ## review
        click_hold(desktop,
                   try_find_element(new_install, FindElementBy.AUTOMATION_ID, 'm_nextButton', self.small_retry))

        ## finish
        if disable_audit_store_install_now:
            click_hold(desktop, try_find_element(desktop, FindElementBy.AUTOMATION_ID, 'm_option', self.big_retry))

        click_hold(desktop, try_find_element(desktop, FindElementBy.AUTOMATION_ID, 'm_nextButton', self.big_retry))

    def test_centrify_da_console_version(self, desktop):
        window = try_find_element(desktop, FindElementBy.CLASS, 'MMCMainFrame', self.small_retry)
        pop_up = try_find_element(window, FindElementBy.NAME, 'OK', self.vry_small_retry, True)
        if pop_up is not None:
            click_hold(desktop, pop_up)

        help_elements = window.find_elements_by_name('Help')

        for element in help_elements:
            if element.get_attribute('LocalizedControlType') == 'menu item':
                click_hold(desktop, element)
                element.send_keys(Keys.ARROW_DOWN)
                element.send_keys(Keys.ARROW_DOWN)
                element.send_keys('b')

        complete_text = str(try_find_element(window, FindElementBy.AUTOMATION_ID, '4160', self.small_retry).text)
        click_hold(desktop, window.find_element_by_accessibility_id('1'))
        index = complete_text.index('Version')
        version = complete_text[index:]

        assert (self.settings['version'] == version), 'version mismatch it should be:' + self.settings['version']

    def test_configure_audit_store(self, desktop):
        """
        Configures audit store in a pre-configured Direct Audit installation.
        Expects Audit Manager window to be open
        """
        ok_centrify_license_dlg(desktop)
        da_node = get_da_installation_node(desktop)
        double_click(desktop, da_node)
        ok_centrify_license_dlg(desktop)

        audit_store_setting = self.settings["audit_store"]
        da_instance_name = self.settings['da_instance_name']
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
        audit_store_wizard = try_find_element(desktop, FindElementBy.NAME, "Add Audit Store Wizard", self.med_retry)
        if audit_store_setting["store_display_name"] == "":
            raise Exception("store_display_name cannot be blank")
        clear_txtbox(try_find_element(audit_store_wizard, FindElementBy.NAME, "Display name:", self.med_retry)) \
            .send_keys(audit_store_setting["store_display_name"])

        while try_find_element(audit_store_wizard, FindElementBy.AUTOMATION_ID, "m_winAndUnixRadioBtn",
                               self.vry_small_retry, ignore_if_not_found=True) is None:
            click_hold(desktop, try_find_element(audit_store_wizard, FindElementBy.NAME, "Next >", self.med_retry))

        while try_find_element(audit_store_wizard, FindElementBy.NAME, "Add Site",
                               self.vry_small_retry, ignore_if_not_found=True) is None:  # retry until next screen found
            affinity = audit_store_setting["affinity"].lower()
            if affinity == "windows and unix":
                click_hold(desktop,
                           try_find_element(audit_store_wizard, FindElementBy.AUTOMATION_ID, "m_winAndUnixRadioBtn",
                                            self.med_retry))
            elif affinity == "windows":
                click_hold(desktop,
                           try_find_element(audit_store_wizard, FindElementBy.AUTOMATION_ID, "m_winRadioBtn",
                                            self.med_retry))
            elif affinity == "unix":
                click_hold(desktop,
                           try_find_element(audit_store_wizard, FindElementBy.AUTOMATION_ID, "m_unixRadioBtn",
                                            self.med_retry))
            click_hold(desktop, try_find_element(audit_store_wizard, FindElementBy.NAME, "Next >", self.med_retry))

        # select AD-site
        add_site = try_find_element(audit_store_wizard, FindElementBy.NAME, "Add Site", self.med_retry)
        while try_find_element(audit_store_wizard, FindElementBy.NAME, "Select Active Directory Sites",
                               self.vry_small_retry, ignore_if_not_found=True) is None:
            click_hold(desktop, add_site)  # retry click until next screen loaded

        ad_sites = try_find_element(audit_store_wizard, FindElementBy.NAME, "Select Active Directory Sites",
                                    self.med_retry)
        click_hold(desktop,
                   try_find_element(ad_sites, FindElementBy.NAME, "Select a site from current forest", self.med_retry))
        sites_list = try_find_element(ad_sites, FindElementBy.AUTOMATION_ID, "m_siteList", self.med_retry)

        if audit_store_setting["ad_site"] == "":
            click_hold(desktop,
                       try_find_element(sites_list, FindElementBy.AUTOMATION_ID, "ListViewItem-0", self.med_retry))
        else:
            # all child in list

            found = listbox_select_item(desktop, sites_list, audit_store_setting["ad_site"])

            if not found:
                raise Exception("AD Site '" + audit_store_setting["ad_site"] + "' not found")

        while not try_find_element(audit_store_wizard, FindElementBy.NAME, "Next >", self.med_retry).is_enabled():
            click_hold(desktop,
                       try_find_element(ad_sites, FindElementBy.NAME, "OK",
                                        self.med_retry))  # retry clicks until next enables

        click_hold(desktop, try_find_element(audit_store_wizard, FindElementBy.NAME, "Next >", self.med_retry))
        while try_find_element(audit_store_wizard, FindElementBy.NAME, "Finish",
                               self.vry_small_retry,
                               ignore_if_not_found=True) is None:  # retry clicks until Finish found
            click_hold(desktop, try_find_element(audit_store_wizard, FindElementBy.NAME, "Next >", self.med_retry))
        click_hold(desktop, try_find_element(audit_store_wizard, FindElementBy.NAME, "Finish", self.med_retry))

        # endregion

        # region Add Audit Store Database Wizard
        audit_store_db_wizard = try_find_element(desktop, FindElementBy.NAME, "Add Audit Store Database Wizard",
                                                 self.med_retry)
        clear_txtbox(try_find_element(audit_store_db_wizard, FindElementBy.NAME, "Display name:", self.med_retry)) \
            .send_keys(audit_store_setting["db_display_name"])
        click_hold(desktop, try_find_element(audit_store_db_wizard, FindElementBy.NAME, "Next >", self.med_retry))

        sql_to_connect = self.settings["sql_machine_name"] + "\\" + self.settings["sql_instance_name"]
        sql_to_connect = sql_to_connect.strip("\\")
        clear_txtbox(try_find_element(audit_store_db_wizard, FindElementBy.CLASS, "Edit", self.med_retry)) \
            .send_keys(sql_to_connect)
        click_hold(desktop, try_find_element(audit_store_db_wizard, FindElementBy.NAME, "Next >", self.med_retry))

        clear_txtbox(try_find_element(audit_store_db_wizard, FindElementBy.NAME, "Database name:", self.med_retry)) \
            .send_keys(audit_store_setting["db_name"])
        active_chk = try_find_element(audit_store_db_wizard, FindElementBy.NAME, "Set as active database",
                                      self.med_retry)

        if audit_store_setting["db_set_active"]:
            if not active_chk.is_selected():
                click_hold(desktop, active_chk)
        else:
            if active_chk.is_selected():
                click_hold(desktop, active_chk)
        click_hold(desktop, try_find_element(audit_store_db_wizard, FindElementBy.NAME, "Next >", self.vry_small_retry))

        set_sql_login_account(audit_store_db_wizard, desktop, self.settings["sql_login_account"])

        click_hold(desktop, try_find_element(audit_store_db_wizard, FindElementBy.NAME, "Next >", self.vry_small_retry))
        click_hold(desktop, try_find_element(audit_store_db_wizard, FindElementBy.NAME, "Next >", self.vry_small_retry))
        click_hold(desktop, try_find_element(audit_store_db_wizard, FindElementBy.NAME, "Finish", self.med_retry))

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
        assert databases is not None, "test_config_audit_store PASSED"
        cntry_main_screen = try_find_element(desktop, FindElementBy.CLASS, "MMCMainFrame", self.small_retry)
        click_hold(desktop, try_find_element(cntry_main_screen, FindElementBy.NAME, "Close", self.med_retry))
        logger.info('application closed')

    def test_configure_collector_and_verify_version(self):
        """
        Configures controller in a pre-configured Direct Audit installation and verify the version.
        """
        logger.info("--- Case C1238802")
        logger.info("------Step 1")

        logger.info("Configuring the collector")
        desktop = get_desktop()
        collector_setting = settings["collector"]
        collector_session = start_collector_configure()

        collector_win = try_find_element(desktop, FindElementBy.AUTOMATION_ID, "CollectorControlPanel", self.med_retry)
        click_hold(desktop,
                   try_find_element(collector_win, FindElementBy.AUTOMATION_ID, "m_configureButton", self.med_retry))
        config_win = try_find_element(desktop, FindElementBy.NAME,
                                      "Centrify DirectAudit Collector Configuration Wizard", self.med_retry)
        install_list = try_find_element(config_win, FindElementBy.AUTOMATION_ID, "m_installList", self.med_retry)

        found_instance_name = listbox_select_item(desktop, install_list, settings["da_instance_name"])

        if not found_instance_name:
            raise Exception("DA instance '" + settings["da_instance_name"] + "' not found. ")
        click_hold(desktop, try_find_element(config_win, FindElementBy.AUTOMATION_ID, "m_nextButton", self.med_retry))

        clear_txtbox(try_find_element(config_win, FindElementBy.AUTOMATION_ID, "m_port", self.med_retry)). \
            send_keys(collector_setting["listening_port"])

        while try_find_element(config_win, FindElementBy.AUTOMATION_ID, "m_windowsOption",
                               self.vry_small_retry, ignore_if_not_found=True) is None:
            click_hold(desktop,
                       try_find_element(config_win, FindElementBy.AUTOMATION_ID, "m_nextButton", self.med_retry))

        click_hold(desktop,
                   try_find_element(config_win, FindElementBy.AUTOMATION_ID, "m_windowsOption", self.med_retry))
        click_hold(desktop, try_find_element(config_win, FindElementBy.AUTOMATION_ID, "m_nextButton", self.med_retry))

        clear_txtbox(try_find_element(config_win, FindElementBy.AUTOMATION_ID, "m_maxPoolSize", self.med_retry)). \
            send_keys(collector_setting["max_pool_size"])
        click_hold(desktop, try_find_element(config_win, FindElementBy.AUTOMATION_ID, "m_nextButton", self.med_retry))

        click_hold(desktop, try_find_element(config_win, FindElementBy.AUTOMATION_ID, "m_nextButton", self.med_retry))

        click_hold(desktop, try_find_element(config_win, FindElementBy.NAME, "Finish", self.med_retry))

        click_hold(desktop,
                   try_find_element(collector_win, FindElementBy.AUTOMATION_ID, "m_restartButton", self.med_retry))
        status_txt = try_find_element(collector_win, FindElementBy.AUTOMATION_ID, "m_status", self.med_retry).text.lower()
        timer = 0
        while status_txt != "running" and timer < self.big_retry:
            timer = timer + 1
            status_txt = try_find_element(collector_win, FindElementBy.AUTOMATION_ID, "m_status",
                                          self.med_retry).text.lower()
        assert status_txt == "running", "Collector not started " + status_txt

        logger.info("Verifying the Collector version")
        logger.info("------Step 2")

        version_lbl = try_find_element(collector_win, FindElementBy.AUTOMATION_ID, "m_verLabel", self.med_retry)
        actual_version = ''.join(re.compile(r'([0-9]+)+').findall(
            re.search(r"\(.*?\)", version_lbl.text).group().split(": ")[1].rstrip(r'\)')))
        expected_version = ''.join(re.compile(r'([0-9]+)+').findall(settings['version']))

        # Close the Collector application
        collector_session.quit()
        assert (expected_version == actual_version), 'Collector version mismatch it should be:' + self.settings['version']

    def test_centrify_da_agent_configure(self, css_client_test_machine):
        logger.info("--- Case C1238803")
        logger.info("------Step 1")
        desktop = get_desktop()
        da_agent = settings['agent']
        ad_admin = r"%s\%s" % (css_client_test_machine['domain_name'].split('.')[0], 'administrator')
        ad_admin_password = css_client_test_machine['ad_admin_password']
        enable_session_capture = da_agent['enable_session_capture']
        da_instance_name = settings['da_instance_name']

        launch_application(css_win_constants.remote_da_agent_start_path)

        window = try_find_element(desktop,
                                  FindElementBy.NAME,
                                  'Centrify Agent Configuration', self.small_retry)
        # add_services
        try_find_element(window, FindElementBy.NAME, 'Add service', self.small_retry).click()

        # select the services
        if enable_session_capture:
            click_hold(desktop,
                       try_find_element(window, FindElementBy.NAME, 'Enable session capture and replay',
                                        self.small_retry))

        try_find_element(window, FindElementBy.NAME, 'OK', self.small_retry).click()

        # select da instance name
        popup_win = try_find_element(desktop, FindElementBy.NAME, 'Centrify Auditing and Monitoring Service',
                                     self.small_retry)
        found_instance_name = try_find_element(desktop, FindElementBy.NAME, da_instance_name, self.vry_small_retry,
                                               True)
        try_find_element(desktop, FindElementBy.CLASS, 'ListView', self.small_retry).click()

        retry = 0
        while not found_instance_name or not found_instance_name.is_selected() and retry < self.med_retry:
            ActionChains(desktop).key_down(Keys.ARROW_DOWN).perform()
            found_instance_name = try_find_element(desktop, FindElementBy.NAME, da_instance_name, self.vry_small_retry,
                                                   True)
        else:
            found_instance_name.click()
        if found_instance_name is None:
            raise Exception("DA instance '" + settings["da_instance_name"] + "' not found. ")

        try_find_element(popup_win, FindElementBy.NAME, '_Next', self.vry_small_retry).click()

        popup_win = try_find_element(desktop, FindElementBy.NAME, 'Centrify Auditing and Monitoring Service',
                                     self.vry_small_retry, True)
        if popup_win is None:
            actions = ActionChains(desktop)
            actions.send_keys(ad_admin)
            actions.send_keys(Keys.TAB)
            actions.send_keys(ad_admin_password)
            actions.send_keys(Keys.ENTER)
            actions.perform()
        else:
            popup_win = try_find_element(desktop, FindElementBy.NAME, 'Centrify Auditing and Monitoring Service',
                                     self.vry_small_retry, True)
        retry = 0
        while try_find_element(popup_win, FindElementBy.NAME, 'Progress', self.vry_small_retry,
                               True) is None and retry < 10:
            retry = retry + 1

        list_item = try_find_element(window,
                                     FindElementBy.NAME,
                                     'Centrify.WinAgent.ServiceConfig.ViewModel.AuditService',
                                     self.small_retry, True)

        if list_item is not None:
            service_installed = try_find_element(list_item,
                                                 FindElementBy.NAME,
                                                 'Centrify Auditing and Monitoring Service',
                                                 self.small_retry, True)

        assert list_item is not None and service_installed is not None, "Agent service configuration failed"

        logger.info("Verifying the Agent version")
        logger.info("------Step 2")

        try_find_element(window, FindElementBy.CLASS, 'ListBoxItem', small_retry).click()
        try_find_element(window, FindElementBy.NAME, 'Settings', small_retry).click()
        agent_panel_win = try_find_element(desktop, FindElementBy.AUTOMATION_ID, 'AgentControlPanel', small_retry)

        version_lbl = try_find_element(agent_panel_win, FindElementBy.AUTOMATION_ID, "m_verLabel",
                                       self.med_retry)
        actual_version = ''.join(re.compile(r'([0-9]+)+').findall(
            re.search(r"\(.*?\)", version_lbl.text).group().split(": ")[1].rstrip(r'\)')))
        expected_version = ''.join(re.compile(r'([0-9]+)+').findall(settings['version']))

        # Close the Agent app
        try_find_element(agent_panel_win, FindElementBy.NAME, 'Close', self.small_retry).click()
        try_find_element(window, FindElementBy.NAME, 'Close', self.small_retry).click()
        assert (expected_version == actual_version), 'Collector version mismatch it should be:' + \
                                                     self.settings['version']