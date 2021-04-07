import os
import subprocess
import sys
from time import sleep
from multiprocessing import Pool
from Utils.windows_gui import WinGui
from Utils.application import App
from Utils.config_loader import Configs
from Utils.win_rdp import rdp_session_from_file, create_rdp_file
from Utils.winrm import WinRM
import logging


logger = logging.getLogger(__name__)
script_dir = os.path.join(os.path.dirname(__file__), 'scripts')
ahk_dir = script_dir + "\\AutoHotKey\\"
ps_dir = script_dir + "\\Powershell\\"
rdp_dir = 'CIS\\SUVP\\rdp_files\\'


def static_agent_install(config):
    ps = ['powershell.exe']
    ps_options = ['-NoProfile']
    ps_commands = ['-username', config['username'], '-password', config['password'], '-ip', config['hostname']]
    agent_dir = ps_dir + 'agent_install.ps1'
    command = []
    command.extend(ps)
    command.extend(ps_options)
    command.append(agent_dir)
    command.extend(ps_commands)
    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        proc.wait(timeout=90)
    except TimeoutError:
        proc.kill()


def parallel_agent_install():
    list_of_dicts = Configs.get_yaml_node('suvp_test_hosts', 'tested_hosts')
    p = Pool(len(list_of_dicts))
    p.map(static_agent_install, list_of_dicts)
    p.join()
    p.close()


def test_install_kb(host_to_test, kb_info, suvp_utilities):
    s = suvp_utilities(host_to_test)
    if host_to_test.windows_version == kb_info.win_version:
        s.install_kb(kb_info.kb_version, kb_info.kb_number)
    else:
        logging.info(f'KB is not for this version of windows {kb_info}')
    # This sleep is to allow the machine to complete installation before any further test steps
    sleep(90)


def kb_install(kb_config, host_config):

    """
    This is to install all the KB patches on the machines necessary.
    :param kb_config: Top line config tuple covering the KBs to be installed
                        kb_config = Configs().get_yaml_node_as_tple('suvp_kb_info', 'kb_info')
    :param host_config:
    :return:
    """

    pass


def change_local_zone(zone_name):
    subprocess.Popen('dzjoin /z ' + zone_name + '')


def remotely_change_zone(host_config, zone_name):
    winrm = WinRM(host_config)
    winrm.send_command('echo ' + host_config.password + ' >> temp_file.txt')
    winrm.send_command('dzjoin /z ' + zone_name + ' /u ' + host_config.username + ' /f /r no < temp_file.txt')
    winrm.send_command('del temp_file.txt')
    winrm.reboot()


class SuvpTestUtilities:

    def __init__(self, config=None):
        self.agent_gui = Configs().get_yaml_node_as_tuple('windows_agent', 'windows_agent_config')
        self.test_config = Configs().get_yaml_node_as_tuple('suvp_test_config', 'config')
        self.powershell_config = Configs().get_yaml_node_as_tuple('powershell', 'powershell')
        self.powershell_app = App(self.powershell_config)
        self.agent_app = App(self.agent_gui)
        self.desktop = WinGui()
        self.rdp_app = None
        if config:
            self.hostname = config.hostname
            self.username = config.username
            self.password = config.password
            self.admin = config.admin
            self.clwmfa = config.clwmfa
            self.endpoints = config.endpoints
            self.rwpmfa = config.rwpmfa
            self.rwpnomfa = config.rwpnomfa
            self.sdwmfa = config.sdwmfa
            self.rdp_window = config.rdp_window
            self.win_version = config.windows_version
            self.defaultwintrayx = config.defaultwintrayx
            self.defaultwintrayy = config.defaultwintrayy
            self.defaultdztrayx = config.defaultdztrayx
            self.defaultdztrayy = config.defaultdztrayy
            self.newdeskdztrayy = config.newdeskdztrayy
            self.newdeskdztrayx = config.newdeskdztrayx
            self.enrolldevicex = config.enrolldevicex
            self.enrolldevicey = config.enrolldevicey
            self.startmenux = config.startmenux
            self.startmenuy = config.startmenuy
            self.powershellx = config.powershellx
            self.servicemenux = config.servicemenux
            self.servicemenuy = config.servicemenuy
            self.altdefaultwintrayx = config.altdefaultwintrayx
            self.altdefaultwintrayy = config.altdefaultwintrayy
            self.winrm = WinRM(config)
        else:
            self.hostname = None
            self.username = None
            self.password = None
            self.admin = None
            self.clwmfa = None
            self.endpoints = None
            self.rwpmfa = None
            self.rwpnomfa = None
            self.sdwmfa = None
            self.rdp_window = None
            self.win_version = None
            self.defaultwintrayx = None
            self.defaultwintrayy = None
            self.defaultdztrayx = None
            self.defaultdztrayy = None
            self.newdeskdztrayx = None
            self.newdeskdztrayy = None
            self.startmenux = None
            self.startmenuy = None
            self.powershellx = None
            self.servicemenux = None
            self.servicemenuy = None
            self.altdefaultwintrayx = None
            self.altdefaultwintrayy = None

    def rdp_session(self, username):
        clean_hostname = self.hostname.replace('.', '')
        clean_username = username.replace('\\', '')
        filename = clean_hostname + clean_username + '.rdp'
        rdp_file = create_rdp_file(self.hostname, username, rdp_dir, filename)
        self.rdp_app = rdp_session_from_file(rdp_file)
        self.rdp_app.run()

    def kill_rdp(self):
        self.rdp_app.kill()

    def install_common_components(self):
        self.winrm.send_command(r'msiexec /i "C:\Users\administrator\downloads\Centrify Common Component64.msi" /qn')

    def uninstall_common_components(self):
        self.winrm.send_command(r'msiexec /x "C:\Users\administrator\downloads\Centrify Common Component64.msi" /quiet')

    def install_agent(self):
        self.install_common_components()
        self.winrm.send_command(r'msiexec /i "C:\Users\administrator\downloads\Centrify Agent for Windows64.msi" /qn')
        self.winrm.send_command(r'reg add HKLM\Software\Centrify\DirevtAuthorize\Agent /v CertPinningTestMode /t REG_DWORD /d 1')

    def uninstall_agent(self):
        self.uninstall_common_components()
        self.winrm.send_command(r'msiexec /x "C:\Users\administrator\downloads\Centrify Agent for Windows64.msi" /quiet')
        self.winrm.send_command(r'msiexec /x "C:\Users\administrator\downloads\Centrify Common Component64.msi" /quiet')

    def check_agent(self):
        self.winrm.send_command(r'if exist C:\Program Files\Centrify\Centrify Agent for Windows\ echo true')
        return self.winrm.expect('true', self.winrm.last_std_out)

    def enable_cis(self):
        logging.info('enabling centrify identity service')
        self.agent_app.run()
        sleep(2)
        self.desktop.click(self.agent_gui.addservice, 30)
        self.desktop.select_list_item(self.agent_gui.winagentserviceconfigviewmodelidentityserviceoptionlistitem)
        self.desktop.click(self.agent_gui.okbutton)
        sleep(2)
        self.desktop.send_keys_to_window('{TAB}', self.agent_gui)
        sleep(1)
        self.desktop.send_keys_to_window('{DOWN}', self.agent_gui)
        sleep(1)
        self.desktop.click(self.agent_gui.nextbutton)
        self.desktop.click(self.agent_gui.nextbutton)
        sleep(5)
        self.desktop.click(self.agent_gui.closebutton)
        sleep(10)
        logging.info('enabling centrify identity service finished')

    def enable_pes(self):
        logging.info('enabling centrify privilege elevation service')
        self.agent_app.run()
        sleep(5)
        self.desktop.click(self.agent_gui.addservice, 30)
        sleep(5)
        self.desktop.select_list_item(self.agent_gui.centrifywinagentserviceconfigviewmodelzoneserviceoption)
        self.desktop.click(self.agent_gui.okbutton)
        self.desktop.click(self.agent_gui.nextbutton)
        sleep(15)
        self.desktop.click(self.agent_gui.yesbutton)
        logging.info('enabling centrify privilege elevation service finished')

    def change_zone(self, zone_name):
        self.winrm.send_command('del temp_file.txt')
        self.winrm.send_command('echo ' + self.password + ' >> temp_file.txt')
        self.winrm.send_command('dzjoin /z ' + zone_name + ' /u ' + self.username + ' /f /r no < temp_file.txt')
        self.winrm.reboot()

    def powershell_remote(self):
        un_fail = self.test_config.ps_remote_un_fail
        un_success = self.test_config.ps_remote_un_success
        password = self.test_config.ps_remote_password
        print('flow control print statement')
        sleep(5)
        self.powershell_app.run()
        sleep(5)
        self.desktop.send_keys_blind(
            'Enter-PSSession{SPACE}-ComputerName{SPACE}%s{SPACE}-Credential{SPACE}%s{ENTER}' % (self.hostname, un_fail))
        sleep(2)
        self.desktop.send_keys_blind('%s{ENTER}' % password)
        # TODO check if we can get 'access is denied'
        sleep(10)
        self.desktop.send_keys_blind(
            'Enter-PSSession{SPACE}-ComputerName{SPACE}%s{SPACE}-Credential{SPACE}%s{ENTER}' % (self.hostname, un_success))
        sleep(2)
        self.desktop.send_keys_blind('%s{ENTER}' % password)
        # TODO check if we can get success info
        sleep(10)
        self.desktop.send_keys_blind('exit{ENTER}')
        sleep(5)
        self.powershell_app.kill()

    def rwp_nomfa(self):
        self.rdp_session(self.rwpnomfa)
        sleep(5)
        self.desktop.set_text('["Windows Security"]["Edit"]', 'P@ssw0rd')
        self.desktop.send_keys_blind('{ENTER}')
        sleep(30)
        self.desktop.click_coord('left', self.startmenux, self.startmenuy)
        sleep(2)
        if "test-2k12r2" in self.hostname:
            self.desktop.send_keys_to_window('p', self.rdp_window)
            sleep(2)
            self.desktop.send_keys_to_window('{VK_DELETE}', self.rdp_window)
            sleep(2)
        self.desktop.send_keys_to_window('powershell.exe{ENTER}', self.rdp_window)
        sleep(5)
        self.desktop.send_keys_to_window('Runasrole{SPACE}/role:role2_runpriv_eventvwr/03_core{SPACE}eventvwr.msc{ENTER}',
                                         self.rdp_window)
        sleep(20)
        self.desktop.send_keys_to_window('{DOWN 2}', self.rdp_window)
        sleep(1)
        self.desktop.send_keys_to_window('{RIGHT}', self.rdp_window)
        sleep(1)
        self.desktop.send_keys_to_window('{DOWN}{ENTER}', self.rdp_window)
        sleep(10)
        self.desktop.send_keys_to_window('%{F4}', self.rdp_window)
        sleep(2)
        self.desktop.send_keys_to_window('logoff{ENTER}', self.rdp_window)
        sleep(5)

    def leave_zone(self):
        self.winrm.send_command('del temp_file.txt')
        self.winrm.send_command('echo ' + self.password + ' >> temp_file.txt')
        self.winrm.send_command('dzleave /u ' + self.username + ' /f /r no < temp_file.txt')
        #self.winrm.reboot()  # No need, already reboots
        # ps_variables = ['-username', r'a1f1r1c1\Administrator', '-password', 'P@ssw0rd', '-ip', computer_name]
        # lz_dir = ps_dir + 'leave_zone.ps1'
        # run_powershell_script_file(lz_dir, ps_variables)

    def run_ps_config(self):
        #TODO remove this because we don't use it anymore until we go to on-the-fly VMs
        ps_config_dir = ps_dir + 'configure_ps.ps1 -username %s -password %s -ip %s' % (self.username, self.password, self.hostname)
        session = subprocess.Popen([r'powershell.exe', ps_config_dir], stdout=subprocess.PIPE)
        session.wait()
        print(session.stdout.read())

    def create_desktop(self):
        self.rdp_session(self.rwpmfa)
        self.desktop.set_text('["Windows Security"]["Edit"]', 'P@ssw0rd')
        self.desktop.send_keys_blind('{ENTER}')
        sleep(30)
        if "test-2k8r2" in self.hostname:
            self.desktop.click_coord('left', self.altdefaultwintrayx, self.defaultwintrayy)
            sleep(5)
            self.desktop.click_coord('right', self.altdefaultwintrayx, self.defaultdztrayy)
        elif "test-2k12r2" in self.hostname:
            self.desktop.click_coord('left', self.altdefaultwintrayx, self.defaultwintrayy)
            sleep(5)
            self.desktop.click_coord('right', self.altdefaultwintrayx, self.altdefaultwintrayy)
        else:
            self.desktop.click_coord('left', self.defaultwintrayx, self.defaultwintrayy)
            sleep(5)
            self.desktop.doubleclick_coord('left', self.defaultwintrayx, self.defaultwintrayy)
            sleep(5)
            self.desktop.click_coord('right', self.defaultdztrayx, self.newdeskdztrayy)
        sleep(5)
        self.desktop.send_keys_to_window('n', self.rdp_window)
        sleep(2)
        self.desktop.send_keys_to_window('{ENTER}', self.rdp_window)
        sleep(20)
        self.desktop.click_coord('left', self.startmenux, self.startmenuy)
        sleep(2)
        if "test-w10-" or "test-2k12r2" in self.hostname:
            self.desktop.send_keys_to_window('{TAB}', self.rdp_window)
            sleep(2)
        self.desktop.send_keys_to_window('services.msc{ENTER}', self.rdp_window)
        sleep(5)
        self.desktop.send_keys_to_window('{TAB}', self.rdp_window)
        sleep(2)
        self.desktop.send_keys_to_window('Centrify{SPACE}Logger', self.rdp_window)
        sleep(2)
        self.desktop.send_keys_to_window('+{VK_F10}e', self.rdp_window)
        sleep(5)
        self.desktop.send_keys_to_window('+{TAB}+{TAB}', self.rdp_window)
        sleep(2)
        self.desktop.send_keys_to_window('%ac', self.rdp_window)
        sleep(2)
        self.desktop.send_keys_to_window('a1css-w2k12r2.a1f1r1c1.a1f1r1.test{ENTER}', self.rdp_window)
        sleep(10)
        self.desktop.send_keys_to_window('{TAB}', self.rdp_window)
        sleep(2)
        self.desktop.send_keys_to_window('Centrify{SPACE}Logger', self.rdp_window)
        sleep(2)
        self.desktop.send_keys_to_window('+{VK_F10}', self.rdp_window)
        sleep(1)
        self.desktop.send_keys_to_window('e', self.rdp_window)
        sleep(5)
        self.desktop.send_keys_to_window('+{TAB}+{TAB}', self.rdp_window)
        sleep(2)
        self.desktop.send_keys_to_window('%ac', self.rdp_window)
        sleep(2)
        self.desktop.send_keys_to_window('%l{ENTER}', self.rdp_window)
        sleep(15)
        if "test-2k8r2" in self.hostname:
            self.desktop.click_coord('left', self.altdefaultwintrayx, self.defaultwintrayy)
            sleep(5)
            self.desktop.click_coord('right', self.defaultwintrayx, self.defaultdztrayy)
        elif "test-2k12r2" in self.hostname:
            self.desktop.click_coord('left', self.altdefaultwintrayx, self.defaultwintrayy)
            sleep(5)
            self.desktop.click_coord('right', self.defaultwintrayx, self.altdefaultwintrayy)
        else:
            self.desktop.click_coord('left', self.defaultwintrayx, self.defaultwintrayy)
            sleep(5)
            self.desktop.click_coord('right', self.defaultdztrayx, self.newdeskdztrayy)
        sleep(2)
        self.desktop.send_keys_to_window('c', self.rdp_window)
        sleep(2)
        self.desktop.send_keys_to_window('{ENTER}', self.rdp_window)
        sleep(2)
        self.desktop.click_coord('left', self.startmenux, self.startmenuy)
        sleep(2)
        if "test-2k12r2" in self.hostname:
            self.desktop.send_keys_to_window('p', self.rdp_window)
            sleep(2)
            self.desktop.send_keys_to_window('{VK_DELETE}', self.rdp_window)
            sleep(2)
        self.desktop.send_keys_to_window("powershell.exe", self.rdp_window)
        sleep(2)
        self.desktop.send_keys_to_window("{ENTER}", self.rdp_window)
        sleep(5)
        self.desktop.send_keys_to_window("logoff{ENTER}", self.rdp_window)
        sleep(5)
        #TODO Figure out how to verify this test succeeded

    def console_login_mfa(self):
        self.rdp_session(self.clwmfa)
        self.desktop.set_text('["Windows Security"]["Edit"]', 'P@ssw0rd')
        self.desktop.send_keys_blind('{ENTER}')
        sleep(15)
        if "test-2k8r2" in self.hostname:
            self.desktop.send_keys_to_window("{TAB}", self.rdp_window)
            sleep(1)
        self.desktop.send_keys_to_window("Centr1fy{ENTER}", self.rdp_window)
        sleep(10)
        self.kill_rdp()

    def pass_reset_mfa(self):
        self.rdp_session(self.endpoints)  # must be endpoints because the same user does pass reset and endpoints
        self.desktop.set_text('["Windows Security"]["Edit"]', 'P@ssw0rd')
        self.desktop.send_keys_blind('{ENTER}')
        sleep(10)
        if "test-2k8r2" in self.hostname:
            self.desktop.send_keys_to_window("{TAB}", self.rdp_window)
            sleep(1)
        self.desktop.send_keys_to_window("Centr1fy{ENTER}", self.rdp_window)
        sleep(10)
        self.desktop.click_coord('left', self.startmenux, self.startmenuy)
        sleep(2)
        if "test-2k12r2" in self.hostname:
            self.desktop.send_keys_to_window('p', self.rdp_window)
            sleep(2)
            self.desktop.send_keys_to_window('{VK_DELETE}', self.rdp_window)
            sleep(2)
        self.desktop.send_keys_to_window("powershell.exe", self.rdp_window)
        sleep(2)
        self.desktop.send_keys_to_window("{ENTER}", self.rdp_window)
        sleep(5)
        self.desktop.send_keys_to_window("rundll32.exe{SPACE}user32.dll,{SPACE}LockWorkStation{ENTER}", self.rdp_window)
        sleep(10)
        self.desktop.send_keys_to_window("{TAB}{TAB}{ENTER}", self.rdp_window)
        sleep(2)
        self.desktop.send_keys_to_window("{ENTER}", self.rdp_window)
        sleep(5)
        if "test-2k8r2" in self.hostname:
            self.desktop.send_keys_to_window("{TAB}", self.rdp_window)
            sleep(1)
        self.desktop.send_keys_to_window("Centr1fy{ENTER}", self.rdp_window)
        sleep(2)
        self.desktop.send_keys_to_window("P@ssw0rd{TAB}P@ssw0rd{ENTER}", self.rdp_window)
        sleep(5)
        self.desktop.send_keys_to_window("{ENTER}", self.rdp_window)
        sleep(10)
        if "test-2k8r2" in self.hostname:
            self.desktop.send_keys_to_window("{ENTER}", self.rdp_window)
            sleep(2)
        self.desktop.send_keys_to_window("P@ssw0rd{ENTER}", self.rdp_window)
        sleep(5)
        if "test-2k8r2" in self.hostname:
            self.desktop.send_keys_to_window("{TAB}", self.rdp_window)
            sleep(1)
        self.desktop.send_keys_to_window("Centr1fy{ENTER}", self.rdp_window)
        sleep(10)
        self.desktop.click_coord('left', self.startmenux, self.startmenuy)
        sleep(2)
        self.desktop.send_keys_to_window("powershell.exe", self.rdp_window)
        sleep(2)
        self.desktop.send_keys_to_window("{ENTER}", self.rdp_window)
        sleep(5)
        self.desktop.send_keys_to_window("logoff{ENTER}", self.rdp_window)

    def run_with_priv_mfa(self):
        self.desktop.send_keys_blind('{VK_LWIN}')
        sleep(2)
        self.desktop.send_keys_blind("C:\\Windows\\System32\\{ENTER}")
        sleep(2)
        self.desktop.send_keys_blind('services{DOWN}+{F10}g')
        sleep(5)
        self.desktop.send_keys_blind('{DOWN}{ENTER}')
        sleep(10)
        self.desktop.send_keys_blind('P@ssw0rd{ENTER}')
        sleep(5)
        self.desktop.send_keys_blind('Centr1fy{ENTER}')
        sleep(10)
        self.desktop.send_keys_blind('{TAB}')
        sleep(2)
        self.desktop.send_keys_blind('Centrify{SPACE}Logger')
        sleep(2)
        self.desktop.send_keys_blind('+{VK_F10}e')
        sleep(5)
        self.desktop.send_keys_blind('+{TAB}+{TAB}')
        sleep(2)
        self.desktop.send_keys_blind('%ac')
        sleep(2)
        self.desktop.send_keys_blind('a1css-w2k12r2.a1f1r1c1.a1f1r1.test{ENTER}')
        sleep(10)
        self.desktop.send_keys_blind('{TAB}')
        sleep(2)
        self.desktop.send_keys_blind('Centrify{SPACE}Logger')
        sleep(2)
        self.desktop.send_keys_blind('+{VK_F10}')
        sleep(1)
        self.desktop.send_keys_blind('e')
        sleep(5)
        self.desktop.send_keys_blind('+{TAB}+{TAB}')
        sleep(2)
        self.desktop.send_keys_blind('%ac')
        sleep(2)
        self.desktop.send_keys_blind('%l{ENTER}')
        sleep(5)
        self.desktop.send_keys_blind('%{F4}')
        sleep(5)
        self.desktop.send_keys_blind('%{F4}')

    def run_with_priv_mfa_admin(self):
        sleep(3)
        # TODO find services window that is open to continue test (maybe we don't need this function and can put this in the original funtion?)
        self.desktop.send_keys_blind('{TAB}print{VK_MENU}ae')
        sleep(10)
        self.desktop.send_keys_blind('+{TAB}+{TAB}')
        sleep(2)
        self.desktop.send_keys_blind('{VK_MENU}ac')
        sleep(2)
        self.desktop.send_keys_blind('a1css-w2k12r2.a1f1r1c1.a1f1r1.test{ENTER}')
        sleep(10)
        self.desktop.send_keys_blind('{TAB}')
        sleep(2)
        self.desktop.send_keys_blind('{c 3}')
        sleep(2)
        self.desktop.send_keys_blind('+(VK_F10}')
        sleep(1)
        self.desktop.send_keys_blind('e')
        sleep(5)
        self.desktop.send_keys_blind('+{TAB 2}')
        sleep(2)
        self.desktop.send_keys_blind('+{VK_F10}')
        sleep(2)
        self.desktop.send_keys_blind('c')
        sleep(2)
        self.desktop.send_keys_blind('%l{ENTER}')
        sleep(5)
        self.desktop.send_keys_blind('%{F4}')

    def switch_desktop_grace(self):
        self.rdp_session(self.sdwmfa)
        sleep(5)
        self.desktop.set_text('["Windows Security"]["Edit"]', 'P@ssw0rd')
        self.desktop.send_keys_blind('{ENTER}')
        sleep(45)
        if "test-2k8r2" or "test-2k12r2" in self.hostname:
            self.desktop.click_coord('right', self.altdefaultwintrayx, self.defaultwintrayy)
        else:
            self.desktop.click_coord('right', self.defaultwintrayx, self.defaultwintrayy)
        sleep(5)
        self.desktop.send_keys_to_window('n', self.rdp_window)
        sleep(2)
        self.desktop.send_keys_to_window('{ENTER}', self.rdp_window)
        sleep(15)
        self.desktop.send_keys_to_window('Centr1fy{ENTER}', self.rdp_window)
        sleep(10)
        if "test-2k8r2" in self.hostname:
            self.desktop.click_coord('right', self.altdefaultwintrayx, self.defaultwintrayy)
        else:
            self.desktop.click_coord('right', self.defaultwintrayx, self.defaultwintrayy)
        sleep(5)
        self.desktop.send_keys_to_window('d', self.rdp_window)
        sleep(5)
        if "test-2k8r2" or "test-2k12r2" in self.hostname:
            self.desktop.click_coord('right', self.altdefaultwintrayx, self.defaultwintrayy)
        else:
            self.desktop.click_coord('right', self.defaultwintrayx, self.defaultwintrayy)
        sleep(5)
        self.desktop.send_keys_to_window('r', self.rdp_window)
        sleep(5)
        if "test-2k8r2" in self.hostname:
            self.desktop.click_coord('right', self.altdefaultwintrayx, self.defaultwintrayy)
        else:
            self.desktop.click_coord('right', self.defaultwintrayx, self.defaultwintrayy)
        sleep(5)
        self.desktop.send_keys_to_window('c', self.rdp_window)
        sleep(2)
        self.desktop.send_keys_to_window('{ENTER}', self.rdp_window)
        sleep(5)
        self.desktop.click_coord('left', self.startmenux, self.startmenuy)
        sleep(2)
        if "test-2k12r2" in self.hostname:
            self.desktop.send_keys_to_window('p', self.rdp_window)
            sleep(2)
            self.desktop.send_keys_to_window('{VK_DELETE}', self.rdp_window)
            sleep(2)
        self.desktop.send_keys_to_window("powershell.exe", self.rdp_window)
        sleep(2)
        self.desktop.send_keys_to_window("{ENTER}", self.rdp_window)
        sleep(5)
        self.desktop.send_keys_to_window("logoff{ENTER}", self.rdp_window)

    def endpoint_enroll(self):
        self.rdp_session(self.endpoints)
        self.desktop.set_text('["Windows Security"]["Edit"]', 'P@ssw0rd')
        self.desktop.send_keys_blind('{ENTER}')
        sleep(45)
        self.desktop.click_coord('left', self.defaultdztrayx, self.defaultwintrayy)
        sleep(5)
        self.desktop.doubleclick_coord('left', self.defaultdztrayx, self.defaultwintrayy)
        sleep(5)
        self.desktop.click_coord('right', self.defaultdztrayx, self.newdeskdztrayy)
        sleep(5)
        self.desktop.send_keys_to_window('d', self.rdp_window)
        sleep(2)
        self.desktop.send_keys_to_window('{ENTER}', self.rdp_window)
        sleep(10)
        self.desktop.send_keys_to_window('{ENTER}', self.rdp_window)
        sleep(15)
        self.desktop.click_coord('left', self.startmenux, self.startmenuy)
        sleep(2)
        self.desktop.send_keys_to_window("powershell.exe", self.rdp_window)
        sleep(2)
        self.desktop.send_keys_to_window("{ENTER}", self.rdp_window)
        sleep(5)
        self.desktop.send_keys_to_window("logoff{ENTER}", self.rdp_window)

    def endpoint_unenroll(self):
        self.rdp_session(self.endpoints)
        self.desktop.set_text('["Windows Security"]["Edit"]', 'P@ssw0rd')
        self.desktop.send_keys_blind('{ENTER}')
        sleep(45)
        self.desktop.click_coord('left', self.defaultdztrayx, self.defaultwintrayy)
        sleep(5)
        self.desktop.doubleclick_coord('left', self.defaultdztrayx, self.defaultwintrayy)
        sleep(5)
        self.desktop.click_coord('right', self.defaultdztrayx, self.newdeskdztrayy)
        sleep(5)
        self.desktop.send_keys_to_window('d', self.rdp_window)
        sleep(2)
        self.desktop.send_keys_to_window('{ENTER}', self.rdp_window)
        sleep(10)
        self.desktop.send_keys_to_window('{ENTER}', self.rdp_window)
        sleep(15)
        self.desktop.click_coord('left', self.startmenux, self.startmenuy)
        sleep(2)
        self.desktop.send_keys_to_window("powershell.exe", self.rdp_window)
        sleep(2)
        self.desktop.send_keys_to_window("{ENTER}", self.rdp_window)
        sleep(5)
        self.desktop.send_keys_to_window("logoff{ENTER}", self.rdp_window)

    def install_kb(self, kbVersion, kbName):
        #TODO check if this waits for cab to finish installing
        msu_path = "C:\\" + self.win_version + "-KB" + kbName +"-x64-V" + kbVersion + ".msu"
        cab_path = "C:\\" + self.win_version + "-KB" + kbName +"-x64.cab"
        self.winrm.send_command(f'expand -f:* {msu_path} C:\\')
        # wait for cab file to be expanded
        sleep(10)
        self.winrm.send_command(f'dism /online /add-package /PackagePath:{cab_path} /quiet')
        # ps_commands = ['-username', self.username, '-password', self.password, '-ip', self.hostname, '-kbName', kbName, '-kbVersion',
        #                kbVersion, '-windowsVersion', self.win_version]
        # ikb_dir = ps_dir + "kb_install.ps1"
        # print(ikb_dir)
        # print(ps_commands)
        # run_powershell_script_file(ikb_dir, ps_commands)

    def change_css_zone(self, computer_name, zone_name):
        ccz_dir = ahk_dir + "Change CSS Zone.ahk"
        logging.info(f'Calling AHK file {ccz_dir}')
        ccz_result = subprocess.call([r'C:\Program Files\AutoHotkey\AutoHotKey.exe', ccz_dir, computer_name, zone_name])

    def run_remote_function(self, func_name, username, wait_time=30):
        self.rdp_session(username)
        self.desktop.set_text('["Windows Security"]["Edit"]', 'P@ssw0rd')
        self.desktop.send_keys_blind('{ENTER}')
        sleep(20)
        if "test-2k8r2" in self.hostname:
            self.desktop.click_coord('right', self.powershellx, self.startmenuy)
            sleep(2)
            self.desktop.send_keys_to_window('r{ENTER}', self.rdp_window)
            sleep(5)
        else:
            self.desktop.click_coord('left', self.startmenux, self.startmenuy)
            sleep(5)
            if "test-2k12r2" in self.hostname:
                self.desktop.send_keys_to_window('p', self.rdp_window)
                sleep(2)
                self.desktop.send_keys_to_window('{VK_DELETE}', self.rdp_window)
                sleep(2)
            self.desktop.send_keys_to_window('powershell.exe', self.rdp_window)
            sleep(5)
            self.desktop.send_keys_blind('+{F10}')
            sleep(3)
        if "test-w10-" in self.hostname:
            self.desktop.send_keys_blind('{DOWN}')
            self.desktop.send_keys_blind('{ENTER}')
            sleep(5)
            self.desktop.click_coord('left', self.powershellx, self.newdeskdztrayy)
        else:
            self.desktop.send_keys_blind('{UP 2}')
            self.desktop.send_keys_blind('{ENTER}')
        sleep(5)
        self.desktop.send_keys_blind('cd{SPACE}c:\\SUVP_Venv\\TestAutomation{ENTER}')
        sleep(2)
        self.desktop.send_keys_blind(r'python{SPACE}-m{SPACE}CIS.SUVP.suvp_utilities{SPACE}"%s"' % func_name)
        sleep(2)
        self.desktop.send_keys_blind('{ENTER}')
        sleep(wait_time)
        if "enable_cis" in func_name and "test-2k8r2" in self.hostname:
            self.desktop.click_coord('left', self.powershellx, self.startmenuy)
            sleep(5)
            self.desktop.send_keys_blind("logoff{ENTER}")
            sleep(5)
        else:
            self.desktop.send_keys_blind("logoff{ENTER}")
            sleep(5)

    def run_remote_function_MFA(self, func_name, wait_time=30):
        self.rdp_session(self.clwmfa)
        self.desktop.set_text('["Windows Security"]["Edit"]', 'P@ssw0rd')
        self.desktop.send_keys_blind('{ENTER}')
        sleep(15)
        if "test-2k8r2" in self.hostname:
            self.desktop.send_keys_to_window("{TAB}", self.rdp_window)
            sleep(1)
        self.desktop.send_keys_to_window("Centr1fy{ENTER}", self.rdp_window)
        sleep(20)
        self.desktop.click_coord('left', self.startmenux, self.startmenuy)
        sleep(2)
        if "test-2k8r2" in self.hostname:
            self.desktop.send_keys_blind("services.msc")
            sleep(2)
            self.desktop.click_coord('right', self.servicemenux, self.servicemenuy)
        elif "test-2k12r2" in self.hostname:
            self.desktop.send_keys_to_window('p', self.rdp_window)
            sleep(2)
            self.desktop.send_keys_to_window('{VK_DELETE}{VK_DELETE}', self.rdp_window)
            sleep(2)
            self.desktop.send_keys_blind("services.msc")
            sleep(2)
            self.desktop.send_keys_blind('+{F10}')
            sleep(2)
            self.desktop.send_keys_blind('{UP}{ENTER}')
            sleep(2)
            self.desktop.send_keys_blind('+{F10}')
        else:
            self.desktop.send_keys_blind("services.msc+{F10}")
            sleep(2)
            self.desktop.send_keys_blind('{DOWN 2}{ENTER}')
            sleep(5)
            self.desktop.send_keys_blind('s+{F10}')
        sleep(2)
        self.desktop.send_keys_blind('g')
        sleep(5)
        self.desktop.send_keys_blind('{DOWN}{ENTER}')
        sleep(10)
        self.desktop.send_keys_blind('P@ssw0rd{ENTER}')
        sleep(5)
        self.desktop.send_keys_blind('Centr1fy{ENTER}')
        sleep(10)
        self.desktop.send_keys_blind('{TAB}')
        sleep(2)
        self.desktop.send_keys_blind('Centrify{SPACE}Logger')
        sleep(2)
        self.desktop.send_keys_blind('+{VK_F10}e')
        sleep(5)
        self.desktop.send_keys_blind('+{TAB}+{TAB}')
        sleep(2)
        self.desktop.send_keys_blind('%ac')
        sleep(2)
        self.desktop.send_keys_blind('a1css-w2k12r2.a1f1r1c1.a1f1r1.test')
        sleep(2)
        self.desktop.send_keys_blind('{ENTER}')
        sleep(10)
        self.desktop.send_keys_blind('{TAB}')
        sleep(2)
        self.desktop.send_keys_blind('Centrify{SPACE}Logger')
        sleep(2)
        self.desktop.send_keys_blind('+{VK_F10}')
        sleep(1)
        self.desktop.send_keys_blind('e')
        sleep(5)
        self.desktop.send_keys_blind('+{TAB}+{TAB}')
        sleep(2)
        self.desktop.send_keys_blind('%ac')
        sleep(2)
        self.desktop.send_keys_blind('%l{ENTER}')
        sleep(5)
        self.desktop.send_keys_blind('%{F4}')
        sleep(5)
        self.desktop.send_keys_blind('%{F4}')
        sleep(5)
        self.kill_rdp()

if __name__ == '__main__':
    test_runner = SuvpTestUtilities()
    if sys.argv[1] == 'enable_pes':
        test_runner.enable_pes()
    if sys.argv[1] == 'enable_cis':
        test_runner.enable_cis()
    if sys.argv[1] == 'run_with_priv_mfa':
        test_runner.run_with_priv_mfa()
    if sys.argv[1] == 'admin_rwp_mfa':
        test_runner.run_with_priv_mfa_admin()
    if sys.argv[1] == 'agent_install':
        parallel_agent_install()
