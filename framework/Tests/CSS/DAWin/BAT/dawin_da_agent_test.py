from selenium.webdriver.common.keys import Keys
from Shared.CSS.css_win_utils import *
from Shared.CSS import css_win_constants
from Utils.config_loader import Configs, logger
from .common import *

SETTINGS = Configs.get_test_node("da_installation", "settings")
tear_down = SETTINGS["tear_down"]
VRY_SMALL_RETRY = SETTINGS['vry_small_retry']
SMALL_RETRY = SETTINGS['small_retry']
MED_RETRY = SETTINGS['med_retry']


@pytest.mark.dawin_da_agent
def test_da_agent_master(dawin_test_client_installed, css_client_login, css_client_test_machine):
    logger.info("\"Create DA agent installation\"")
    framework_dir = dawin_test_client_installed['frameworkdir']
    user = css_client_test_machine['user_name']
    username = r"%s\%s" % (css_client_test_machine['domain_name'].split('.')[0], user)
    password = css_client_test_machine['password']
    public_ip = css_client_test_machine['public_ip']
    rc = 0
    result = ""
    error = ""
    try:
        logger.info("Start the test on test machine...")
        rdp_session(user, password, public_ip)
        start_app_remotely(user, password,
                           public_ip,
                           css_win_constants.remote_winappdriver_startup_path)

        start_slave_cmd = f"cd {framework_dir} & " \
                          "python -m pytest --css_site bhavna "\
                          "Tests\\CSS\\DAWin\\BAT\\dawin_da_agent_test.py::test_da_agent_slave_steps"
        logger.info("Running: " + start_slave_cmd)

        rc, result, error = css_client_login.send_command(start_slave_cmd)

        log_assert(rc == 0, "Test is failed")
        logger.info("Test is done.")
    except Exception as ex:
        logger.info(f'error in test_da_agent_master Exception: {ex}')
    finally:
        logger.info("test_da_agent_master() finish")
        return rc, result, error


def tear_down_agent(dawin_test_client_installed, css_client_login, css_client_test_machine):
    framework_dir = dawin_test_client_installed['frameworkdir']
    user = css_client_test_machine['user_name']
    password = css_client_test_machine['password']
    public_ip = css_client_test_machine['public_ip']

    # tear-down starts, un-configure Agent configurations
    start_slave_cmd = f"cd {framework_dir} & " \
                      "python -m pytest Tests\\CSS\\DAWin\\BAT\\dawin_da_agent_test.py::test_da_agent_unconfigure"

    rdp_session(user, password, public_ip)
    rc, result, error = css_client_login.send_command(start_slave_cmd)
    logger.debug("tear down agent: rc %s, result %s, error %s", rc, result, error)
    rdp_kill_all()
    return rc, result, error


def test_centrify_da_agent_configure(desktop, css_client_test_machine):
    da_agent = SETTINGS['agent']
    ad_admin = r"%s\%s" % (css_client_test_machine['domain_name'].split('.')[0], 'administrator')
    ad_admin_password = css_client_test_machine['ad_admin_password']
    enable_session_capture = da_agent['enable_session_capture']
    da_instance_name = SETTINGS['da_instance_name']

    launch_application(css_win_constants.remote_da_agent_start_path)

    window = try_find_element(desktop,
                              FindElementBy.NAME,
                              'Centrify Agent Configuration', SMALL_RETRY)
    # add_services
    click_hold(desktop, try_find_element(window, FindElementBy.NAME, 'Add service', SMALL_RETRY))

    # select the services
    if enable_session_capture:
        click_hold(desktop,
                   try_find_element(window, FindElementBy.NAME, 'Enable session capture and replay', SMALL_RETRY))

    ok_button = try_find_element(window, FindElementBy.NAME, 'OK', SMALL_RETRY)

    while not ok_button.is_enabled():
        pass
    click_hold(desktop, ok_button)
    # select da instance name
    popup_window = try_find_element(desktop,
                                    FindElementBy.NAME,
                                    'Centrify Auditing and Monitoring Service',
                                    SMALL_RETRY)
    click_hold(desktop, try_find_element(popup_window, FindElementBy.NAME, da_instance_name, VRY_SMALL_RETRY))
    click_hold(desktop, try_find_element(popup_window, FindElementBy.NAME, '_Next', VRY_SMALL_RETRY))

    popup_window = try_find_element(desktop,
                                    FindElementBy.NAME,
                                    'Centrify Auditing and Monitoring Service',
                                    VRY_SMALL_RETRY, True)

    if popup_window is None:
        actions = ActionChains(desktop)
        actions.send_keys(ad_admin)
        actions.send_keys(Keys.TAB)
        actions.send_keys(ad_admin_password)
        actions.send_keys(Keys.ENTER)
        actions.perform()

    popup_window = try_find_element(desktop,
                                    FindElementBy.NAME,
                                    'Centrify Auditing and Monitoring Service',
                                    VRY_SMALL_RETRY, True)
    retry = 0
    while try_find_element(popup_window, FindElementBy.NAME, 'Progress', VRY_SMALL_RETRY, True) is None and retry < 10:
        retry = retry + 1

    list_item = try_find_element(window,
                                 FindElementBy.NAME,
                                 'Centrify.WinAgent.ServiceConfig.ViewModel.AuditService',
                                 SMALL_RETRY, True)

    if list_item is not None:
        service_installed = try_find_element(list_item,
                                             FindElementBy.NAME,
                                             'Centrify Auditing and Monitoring Service',
                                             SMALL_RETRY, True)

        if service_installed is not None:
            while try_find_element(desktop,
                                   FindElementBy.NAME,
                                   'Centrify Agent Configuration',
                                   VRY_SMALL_RETRY,
                                   True) is not None:
                click_hold(desktop, try_find_element(window, FindElementBy.NAME, 'Close', SMALL_RETRY))

    log_assert(list_item is not None and service_installed is not None, "Agent service configuration failed")


def test_da_agent_unconfigure():
    desktop = get_desktop()

    agent_window_session = launch_application(css_win_constants.remote_da_agent_start_path)

    agent_window = try_find_element(desktop, FindElementBy.NAME, 'Centrify Agent Configuration', SMALL_RETRY)
    service_list = try_find_element(agent_window, FindElementBy.NAME,
                                    "Centrify.WinAgent.ServiceConfig.ViewModel.AuditService",
                                    SMALL_RETRY, ignore_if_not_found=True)
    if service_list is not None:
        click_hold(desktop, service_list)
        click_hold(desktop, try_find_element(service_list, FindElementBy.NAME, "Remove", SMALL_RETRY))
        ok_centrify_license_dlg(desktop)

        is_removed = try_find_element(agent_window, FindElementBy.NAME, "No services are currently enabled.", MED_RETRY)
        log_assert(is_removed is not None, "Agent service un-configuration failed")
    else:
        pass    # no installation to un-configure
    agent_window_session.quit()
    desktop.quit()


def test_da_agent_slave_steps(css_client_test_machine):
    desktop = get_desktop()
    logger.info("configure da agent on test machine")
    test_centrify_da_agent_configure(desktop, css_client_test_machine)


def remoteDesktopConnection(class_name, local_server):
    desired_caps = {}
    desired_caps["app"] = "Root"
    DesktopSession = webdriver.Remote(
        command_executor=local_server,
        desired_capabilities=desired_caps)
    CortanaWindow = DesktopSession.find_element_by_class_name(class_name)
    CortanaTopLevelWindowHandle = CortanaWindow.get_attribute("NativeWindowHandle")
    CortanaTopLevelWindowHandle1 = hex(int(CortanaTopLevelWindowHandle))
    desired_caps1 = {}
    desired_caps1["appTopLevelWindow"] = CortanaTopLevelWindowHandle1
    driver = webdriver.Remote(
        command_executor=local_server,
        desired_capabilities=desired_caps1)

    return driver
