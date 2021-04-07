import os
import subprocess
from enum import Enum
from time import sleep
from appium import webdriver
from appium.webdriver import WebElement
from appium.webdriver.webdriver import WebDriver
from selenium.common.exceptions import *
from selenium.webdriver import ActionChains
from Fixtures.CSS.misc import *
from Shared.css_utils import *

logger = logging.getLogger('test')


###### Test helper functions ######

def rdp_session(user_name, password, public_ip):
    logger.info("Launch RDP session for user %s" % user_name)

    cmdline = 'cmdkey /generic:"%s" /user:"%s" /pass:"%s"' % \
              (public_ip, user_name, password)
    # os.system(cmdline)

    os.system(cmdline + ' & start mstsc /f /v:%s' % public_ip)
    logger.info("Launch RDP session done")


def rdp_kill_all():
    """Kill all RDP sessions"""
    logger.info("Kill all RDP sessions")
    os.system("taskkill /FI \"IMAGENAME eq mstsc.exe\" /F")


def get_session_id(winrm, user_name):
    logger.info("Get RDP session id for user %s" % user_name)

    retry = 20
    session_id = 0
    while (session_id == 0 and retry > 0):
        try:
            retry -= 1
            sleep(5)
            rc, result, error = \
                winrm.send_command("powershell.exe -Command Get-SessionId -UserName '%s'" % user_name)
            if rc == 0:
                session_id = int(result.strip())
            else:
                raise Exception(error)
        except Exception as e:
            logger.debug(e)

    logger.info("RDP session id: %d" % session_id)
    return session_id


def logoff_session(winrm, session_id):
    logger.info("Logoff session id %d", session_id)

    winrm.send_command("powershell.exe -Command Logoff-Session -SessionId %d" % session_id)
    logger.info("Logoff session done")


class FindElementBy(Enum):
    """
    Enum to be used in try_find_element
    """
    CLASS = 1
    NAME = 2
    AUTOMATION_ID = 3


def try_find_element(web_driver: WebDriver, by: FindElementBy, unique_val, retry_count, ignore_if_not_found=False) \
        -> WebElement:
    """
    attempts to find element within defined retry count.
    raises NoSuchElementException if ignore_if_not_found=false
    """
    element = None
    retried = 0
    while True:
        try:
            if by == FindElementBy.CLASS:
                element = web_driver.find_element_by_class_name(unique_val)
            elif by == FindElementBy.NAME:
                element = web_driver.find_element_by_name(unique_val)
            elif by == FindElementBy.AUTOMATION_ID:
                element = web_driver.find_element_by_accessibility_id(unique_val)
        except NoSuchElementException:
            retried = retried + 1
            if retried > retry_count:
                if ignore_if_not_found:
                    return None
                raise NoSuchElementException
            else:
                sleep(1)
                continue
        except StaleElementReferenceException:
            if ignore_if_not_found:
                return
            raise StaleElementReferenceException
        break
    retried = 0
    while not element.is_enabled() and retried < retry_count:
        retried = retried + 1
    return element


def ok_centrify_license_dlg(dsk_session):
    """
    hit ok button of license issue alert box, if it appears in 5 seconds else process will continue
    """
    cntry_dlg = try_find_element(dsk_session, FindElementBy.CLASS, "#32770", 5, True)
    if cntry_dlg is not None:
        ok_button = try_find_element(cntry_dlg, FindElementBy.NAME, "Ok", 1, True)
        if ok_button is not None:
            click_hold(dsk_session, ok_button)
        else:
            okay_button = try_find_element(cntry_dlg, FindElementBy.NAME, "OK", 1, True)
            if okay_button is not None:
                click_hold(dsk_session, okay_button)
            else:
                yes_button = try_find_element(cntry_dlg, FindElementBy.NAME, "Yes", 1, True)
                if yes_button is not None:
                    click_hold(dsk_session, yes_button)
                else:
                    raise Exception("Ok or Yes button not found in Dialog Box.")


def get_da_installation_node(dsk_session: WebDriver, installation_name=""):
    """
    get main root node of DA installation
    """
    cntry_main_screen = try_find_element(dsk_session, FindElementBy.CLASS, "MMCMainFrame", 30, True)

    if cntry_main_screen is not None:
        # get main tree root node of the TreeView in left panel
        cntry_tree_root = cntry_main_screen.find_element_by_class_name("SysTreeView32").\
            find_element_by_name("Centrify Audit Manager")

        # all child nodes of root
        cntry_install = cntry_tree_root.find_elements_by_xpath(".//*")
        # it returns root node as well, remove that
        cntry_install.remove(cntry_tree_root)
        # DA installation node must be left only, at 0 index.
        if installation_name == "":
            return cntry_install[0]
        else:
            for node in cntry_install:
                if node.text.lower().find(installation_name.lower()) == 0:
                    return node

        raise None
    else:
        return None


def get_da_analyser_node(dsk_session: WebDriver, node_name):
    """
        get main nodes of DA analyzer
    """
    window = try_find_element(dsk_session, FindElementBy.CLASS, "MMCMainFrame", 60)

    # get main tree root node of the TreeView in left panel
    tree_root = window \
        .find_element_by_class_name("SysTreeView32") \
        .find_element_by_name(
        "Centrify Audit Analyzer - DA Instance Name[WIN-U9UUVP9HOKG.Dev.MyDomain\ABCSQLEXPRESS - DA_Management_DB]")

    if node_name is None:
        return tree_root
    else:
        return try_find_element(tree_root, FindElementBy.NAME, node_name, 15)


def click_context_menu(dsk_session: WebDriver, element: WebElement, menu_name):
    """
    does context menu click (Right Click) on supplied element and performs click on supplied menu item
    """
    context = None
    while context is None:  # retry until context menu opens
        # open context menu
        actions = ActionChains(dsk_session)
        actions.move_to_element(element)
        actions.click(element)
        actions.context_click(element).perform()
        context = dsk_session.find_element_by_name("Context")
    # click context menu
    menu = context.find_element_by_name(menu_name)
    actions = ActionChains(dsk_session)
    actions.move_to_element(menu)
    actions.click(menu).perform()


def double_click(dsk_session: WebDriver, element: WebElement):
    """
    does double click on supplied element
    """
    actions = ActionChains(dsk_session)
    actions.move_to_element(element)
    actions.double_click(element).perform()


def click_hold(desktop_session: WebDriver, element: WebElement):
    """
    click with click, hold and release method. Added to fix intermittent issue of button click on AWS machine.
    """
    actions = ActionChains(desktop_session)
    actions.move_to_element(element)
    actions.click_and_hold(element).perform()
    actions.release(element).perform()


def start_audit_manager(path) -> WebDriver:
    """
    Starts Audit Manager using mmc.exe and input path
    """
    # close existing instance(s) if exists
    import os
    os.system("taskkill /FI \"IMAGENAME eq mmc.exe\" /F")
    # run new instance
    exp_cap = {"app": "mmc.exe",
               "deviceName": "WindowsPC",
               "appArguments": "\"" + path + "\""
               }
    exp_session = webdriver.Remote(
        command_executor='http://127.0.0.1:4723',
        desired_capabilities=exp_cap)
    return exp_session


def launch_application(path) -> WebDriver:
    """
    open any application by just providing the start up path
    """
    try:
        exp_cap = {
            "appId": "mmc",
            "deviceName": "WindowsPC",
            "app": path}
        exp_session = webdriver.Remote(
            command_executor='http://127.0.0.1:4723',
            desired_capabilities=exp_cap)
        return exp_session
    except Exception as ex:
        logger.info(f':Error in launching app  ERROR: {ex}')


def get_desktop():
    # Create session to control the entire desktop
    capabilities = {"app": "Root", "deviceName": "WindowsPC"}
    desktop = webdriver.Remote(
        command_executor='http://127.0.0.1:4723',
        desired_capabilities=capabilities)
    return desktop


def start_collector_configure() -> WebDriver:
    """
    Open collector folder in Explorer. The default collector installation path.
    Starts collector configure using context menu Open
    """
    exp_cap = {
        "app": r"C:\Program Files\Centrify\Audit\Collector\collector.configure.exe",
        "deviceName": "WindowsPC"
    }
    exp_session = webdriver.Remote(
        command_executor='http://127.0.0.1:4723',
        desired_capabilities=exp_cap)
    return exp_session


def show_desktop(dsk_session: WebDriver):
    """
    Minimize all windows before opening window you need to work on.
    use to overcome command not working issue due to working window being overlapped by other unwanted window
    """
    dsk_session.find_element_by_class_name("TrayShowDesktopButtonWClass").click()


def set_sql_login_account(window, desktop_session, sql_login_account=""):
    if sql_login_account == "":
        click_hold(desktop_session,
                   try_find_element(window, FindElementBy.AUTOMATION_ID, "m_defaultAccountOption", 60))
    else:
        click_hold(desktop_session,
                   try_find_element(window, FindElementBy.AUTOMATION_ID, "m_customAccountOption", 60))
        click_hold(desktop_session, try_find_element(window, FindElementBy.AUTOMATION_ID, "m_username", 60))
        uname_combo = try_find_element(desktop_session, FindElementBy.CLASS, "ComboLBox", 60)
        combo_items = uname_combo.find_elements_by_xpath(".//*")
        found = False
        for item in combo_items:
            if item.tag_name == 'ControlType.ListItem' and \
                    item.text.lower() == sql_login_account.lower():
                found = True
                click_hold(desktop_session, item)
        if not found:
            raise Exception("SQL Login Account '" + sql_login_account + "' not found")


def get_remote_session_id(username, public_ip):
    cmd = f'qwinsta /server:{public_ip} {username}'
    try:

        session = subprocess.Popen(cmd,
                                   stdout=subprocess.PIPE,
                                   universal_newlines=True,
                                   stderr=subprocess.STDOUT
                                   )
        result, error = session.communicate(timeout=5)
        rc = session.returncode
        if rc == 0:
            str_list = result.splitlines()
            shift = False
            for line in str_list:
                li = line.split(' ')
                if li[0] == '':
                    shift = True
                li = list(filter(None, li))
                if 'ID' in li:
                    ind = li.index('ID')
                    continue
                if shift:
                    ind = ind - 1
                return li[ind]  # returns the first session of that user
            return ''
        else:
            raise Exception("Failed to get session id")

    except Exception as ex:
        session.kill()
        logger.info(f':Error in getting session id  ERROR: {ex}')
        return '1'


def start_app_remotely(username, password, public_ip, application_path):
    session_id = get_remote_session_id(username, public_ip)
    cmd = ['PsExec.exe', '\\\\' + public_ip, '-u',
           username, '-p',
           password, '-i', session_id, application_path]
    logger.info(cmd)
    try:

        session = subprocess.Popen(cmd, shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   stdin=subprocess.PIPE)
        session.wait(10)
        result, error = session.communicate()
        rc = session.returncode
        if rc != 0:
            raise Exception("Failed to start app %s. Error: %s" % (os.path.basename(application_path), error))

    except subprocess.TimeoutExpired as ex:
        session.kill()
        kill_session(session.pid)
    except Exception as ex:
        session.kill()
        logger.info(
            f':Error in starting app remotely {os.path.basename(application_path)} Session: {session_id} ERROR: {ex}')


def kill_session(proc_pid):
    p = subprocess.Popen("TASKKILL /F /PID {pid} /T".format(pid=proc_pid))
    res, err = p.communicate(timeout=5)


def clear_txtbox(txtbox: WebElement):
    txtbox.click()
    txtbox.clear()
    return txtbox


def open_tree_node(dsk_session: WebDriver, node: WebElement):
    # ExpandCollapse.ExpandCollapseState    Expanded    Collapsed
    double_click(dsk_session, node)
    state = node.get_attribute("ExpandCollapse.ExpandCollapseState")
    # logger.info(node.text + " : " + state)
    while state != "Expanded":  # Collapsed
        double_click(dsk_session, node)
        state = node.get_attribute("ExpandCollapse.ExpandCollapseState")
        logger.info(node.text + " : " + state)
    # logger.info(node.text + " found, returning.")


def hit_key(element: WebElement, key, number_of_times):
    for i in range(number_of_times):
        element.send_keys(key)