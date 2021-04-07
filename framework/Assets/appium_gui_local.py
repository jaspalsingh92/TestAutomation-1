import logging
import time
import unittest
import os
from appium import webdriver

logger = logging.getLogger(__name__)


class AppiumGuiPOC(unittest.TestCase):
    def currentScreenSession(self):
        # set up appium
        desired_caps = {}
        desired_caps["app"] = "Root"
        self.DesktopSession = webdriver.Remote(
            command_executor='http://127.0.0.1:4723',
            desired_capabilities=desired_caps)
        CortanaWindow = self.DesktopSession.find_element_by_class_name("MsiDialogCloseClass")
        CortanaTopLevelWindowHandle = CortanaWindow.get_attribute("NativeWindowHandle")
        CortanaTopLevelWindowHandle1 = hex(int(CortanaTopLevelWindowHandle))
        desired_caps1 = {}
        desired_caps1["appTopLevelWindow"] = CortanaTopLevelWindowHandle1
        self.driver = webdriver.Remote(
            command_executor='http://127.0.0.1:4723',
            desired_capabilities=desired_caps1)
        return self.driver

    def tearDown(self):
        self.driver.quit()

    def test_centrify_windows_agent_install(self):
        # os.startfile(
        #     r"C:\Users\Administrator\Desktop\Centrify-Infrastructure-Services-19.9-mgmt-win64\Agent\Centrify Agent for Windows64.exe")
        os.startfile(
            r"C:\Users\jaspalsingh\Desktop\Centrify-Infrastructure-Services-19.9-mgmt-win64\Agent\Centrify Agent for Windows64.exe")
        time.sleep(10)
        screen = self.currentScreenSession()
        screen.find_element_by_name("Next").click()
        screen = self.currentScreenSession()
        screen.find_element_by_class_name("Button").click()
        screen.find_element_by_name("Next").click()
        screen = self.currentScreenSession()
        screen.find_element_by_name("Next").click()
        screen = self.currentScreenSession()
        screen.find_element_by_name("Install").click()
        screen = self.currentScreenSession()
        screen.find_element_by_name("Cancel").click()
        screen = self.currentScreenSession()
        screen.find_element_by_name("Yes").click()
        screen = self.currentScreenSession()
        screen.find_element_by_name("Finish").click()
        self.tearDown()

    def centrify_directaudit_powershellmodule(self):
        os.startfile(
            r"C:\Users\Administrator\Desktop\PowerShell\Centrify DirectAudit PowerShell64.exe")
        time.sleep(10)
        screen = self.currentScreenSession()
        screen.find_element_by_name("Next").click()
        screen = self.currentScreenSession()
        screen.find_element_by_class_name("Button").click()
        screen.find_element_by_name("Next").click()
        screen = self.currentScreenSession()
        screen.find_element_by_name("Next").click()
        screen = self.currentScreenSession()
        screen.find_element_by_name("Install").click()
        screen = self.currentScreenSession()
        screen.find_element_by_name("Cancel").click()
        screen = self.currentScreenSession()
        screen.find_element_by_name("Yes").click()
        screen = self.currentScreenSession()
        screen.find_element_by_name("Finish").click()
        self.tearDown()
