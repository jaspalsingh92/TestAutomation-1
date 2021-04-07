import logging
import time
import unittest
import os
from appium import webdriver
from subprocess import Popen, PIPE
from Utils import powershell
from Utils.assets import get_asset_path
from Utils.config_loader import Configs

logger = logging.getLogger(__name__)


class AppiumGui(unittest.TestCase):
    system_data = Configs.get_environment_node('gui', 'automation_main')
    system_data_values = system_data['Windows_infrastructure_data']
    remote_ip = system_data_values['remote_ip']
    script_file = system_data_values['script_file_name']
    remote_username = system_data_values['remote_username']
    remote_password = system_data_values['remote_password']
    local_server = system_data_values['local_appium_server']
    remote_server = system_data_values['remote_appium_server']
    remote_installation_path = system_data_values['remote_installation_path']
    remote_setup_path = system_data_values['remote_setup_directory']
    remote_headless_script = system_data_values['remote_headless_script']

    def remoteDesktopConnection(self, class_name):
        desired_caps = {}
        desired_caps["app"] = "Root"
        self.DesktopSession = webdriver.Remote(
            command_executor=self.local_server,
            desired_capabilities=desired_caps)
        CortanaWindow = self.DesktopSession.find_element_by_class_name(class_name)
        CortanaTopLevelWindowHandle = CortanaWindow.get_attribute("NativeWindowHandle")
        CortanaTopLevelWindowHandle1 = hex(int(CortanaTopLevelWindowHandle))
        desired_caps1 = {}
        desired_caps1["appTopLevelWindow"] = CortanaTopLevelWindowHandle1
        self.driver = webdriver.Remote(
            command_executor=self.local_server,
            desired_capabilities=desired_caps1)
        return self.driver

    def tearDown(self):
        self.driver.quit()

    def close_rdp_session(self):
        os.system("TASKKILL /F /IM mstsc.exe")

    def open_rdp_session(self):
        os.startfile(
            r"C:\Windows\system32\mstsc.exe")
        time.sleep(5)

    def remove_remote_file(self):
        powershell.remote_execute_using_ip_and_creds(self.remote_ip, self.remote_username, self.remote_password,
                                                     f"Remove-Item {self.remote_installation_path}{self.script_file}")

    def run_remote_headless_installation(self):
        powershell.remote_execute_using_ip_and_creds(self.remote_ip, self.remote_username, self.remote_password,
                                                     f"python {self.remote_headless_script}")

    def get_remote_installation_folder(self, password=remote_password,
                                       ad_user=remote_username,
                                       splitter=";",
                                       script_block1=f"Get-ChildItem {remote_setup_path}",
                                       computer_name=remote_ip):
        remote_command1 = f'$password = ConvertTo-SecureString “{password}” -AsPlainText -Force{splitter} ' \
                          f'$Cred = New-Object System.Management.Automation.PSCredential ("{ad_user}", $password){splitter}' \
                          f'Invoke-Command -ComputerName ' + computer_name + ' -ScriptBlock{' + script_block1 + '} -Credential $Cred;'
        command1 = self.build_powershell_command([remote_command1])
        proc1 = Popen(command1, shell=True, stdout=PIPE, stderr=PIPE)
        _stdout_buff = proc1.communicate()
        return _stdout_buff

    def build_powershell_command(self, variables):
        """
        Takes a list of variables and concatentaes them into a command line for powershell
        :param list variables: ['list', 'of', 'strings']
        :return: Popen list of commands for powershell
        """
        command = []
        command.extend(['powershell.exe'])
        command.extend([''])
        command.extend(variables)
        return command

    def copy_remote_sys_file(self, computer_name=remote_ip,
                             ad_user=remote_username,
                             password=remote_password,
                             splitter=";",
                             cp_file="",
                             d_path=remote_installation_path, ):
        remote_command = f'$password = ConvertTo-SecureString “{password}” -AsPlainText -Force{splitter} ' \
                         f'$Cred = New-Object System.Management.Automation.PSCredential ("{ad_user}", $password){splitter}' \
                         f'$Session = New-PSSession -ComputerName {computer_name} -Credential $Cred{splitter}' \
                         f'Copy-Item "{cp_file}" -Destination "{d_path}" -ToSession $Session{splitter}' \
                         f'Remove-PSSession -Session $Session{splitter}'
        command = self.build_powershell_command([remote_command])
        Popen(command, shell=True, stdout=PIPE, stderr=PIPE)

    def remote_ipconfig(self, file):
        desired_caps1 = {}
        desired_caps1["app"] = f'{self.remote_installation_path}{file}'
        self.driver = webdriver.Remote(
            command_executor=self.remote_server,
            desired_capabilities=desired_caps1)
        return self.driver

    def test_remote_rdp_script(self):
        self.open_rdp_session()
        screen = self.remoteDesktopConnection(class_name="#32770")
        screen.find_element_by_class_name("ComboBox").send_keys(self.remote_ip)
        screen.find_element_by_name("Connect").click()
        time.sleep(3)
        screen = self.remoteDesktopConnection("Credential Dialog Xaml Host")
        time.sleep(1)
        screen.find_element_by_class_name("PasswordBox").send_keys(self.remote_password)
        screen.find_element_by_name("OK").click()
        time.sleep(3)
        screen = self.remoteDesktopConnection("TscShellContainerClass")
        assert screen is not None, "Unable to get the Remote session."
        path = get_asset_path(self.script_file)
        self.copy_remote_sys_file(cp_file=path)
        time.sleep(4)
        screen = self.remote_ipconfig(self.script_file)
        assert screen is not None, "Unable to get the Remote session."
        time.sleep(30)
        self.remove_remote_file()
        installation_folder = self.get_remote_installation_folder()
        if "Centrify.DirectAudit.AuditDatabase" in installation_folder:
            assert True, "The installation is not successful"
        self.close_rdp_session()

    def test_remote_headless_installation(self):
        path = get_asset_path(self.remote_headless_script)
        self.copy_remote_sys_file(cp_file=path)
        time.sleep(4)
        self.run_remote_headless_installation()
        time.sleep(30)
        self.remove_remote_file()
        installation_folder = self.get_remote_installation_folder()
        if "Centrify.DirectAudit.AuditDatabase" in installation_folder:
            assert True, "The installation is not successful"
