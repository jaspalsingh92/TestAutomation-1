# css_win_fixtures.py
#
# Provide DAWin related fixtures per package or per test.
#
import collections
import os
import shutil
import sys
from datetime import datetime
from enum import Enum
from time import sleep

import paramiko
import pytest
from paramiko import SSHClient
from scp import SCPClient
from Shared.CSS import css_win_constants
from Utils.config_loader import Configs
from Utils.putty_util import *
from Utils.winrm import WinRM

logger = logging.getLogger('framework')

tear_down = Configs.get_test_node("da_installation", "settings")["tear_down"]

repo_python_path = css_win_constants.repo_python_path
remote_python_path = css_win_constants.remote_python_path
python_install_path = css_win_constants.python_install_path

repo_da_administrator_console_path = css_win_constants.repo_da_administrator_console_path
remote_da_administrator_console_path = css_win_constants.remote_da_administrator_console_path

repo_da_auditor_path = css_win_constants.repo_da_auditor_path
remote_da_auditor_path = css_win_constants.remote_da_auditor_path

remote_audit_manager_path = css_win_constants.remote_audit_manager_path
repo_audit_manager_path = css_win_constants.repo_audit_manager_path

repo_da_agent_path = css_win_constants.repo_da_agent_path
remote_da_agent_path = css_win_constants.remote_da_agent_path

remote_testframework_dir = css_win_constants.remote_framework_path
remote_da_testscripts_dir = css_win_constants.remote_da_testscripts_dir

repo_winappdriver_path = css_win_constants.repo_winappdriver_path
remote_winappdriver_path = css_win_constants.remote_winappdriver_path

remote_collector_path = css_win_constants.remote_collector_path
repo_collector_path = css_win_constants.repo_collector_path

safe_win_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                     "abcdefghijklmnopqrstuvwxyz"
                     "0123456789"
                     "-+=/:.,_\\$")


class ScpOperations(Enum):
    GET = 1
    PUT = 2


def dawin_upload_files_folders(dest_path, dest_login: WinRM, source_path, source_login: WinRM = None):
    """
        transfer files and folders between servers
        if source login is none that means source is local
    """
    try:
        if not dest_login.check_path(dest_path):
            logger.info(f"Uploading {source_path} to {dest_path}")
            dest_dir = os.path.dirname(dest_path)
            source_config = None
            if source_login is not None:
                source_config = source_login.get_config()
            dest_config = dest_login.get_config()
            # create directory
            cmd = 'mkdir.exe "%s"' % dest_dir
            dest_login.send_command(cmd)

            # upload file
            source_to_dest_upload(dest_config, dest_path, source_path, source_config)
    except Exception as ex:
        raise Exception(f"error in dawin_upload_files_folders: {ex}")


def win_escape(s):
    r"""Given bl"a, returns "bl^"a".
    """
    if isinstance(s, bytes):
        s = s.decode('utf-8')
    if any(c not in safe_win_chars for c in s):
        return '"%s"' % (s.replace('^', '^^')
                         .replace('"', '^"')
                         .replace('%', '^%'))
    else:
        return s


def get_scp_client(ssh_client):
    return SCPClient(ssh_client.get_transport(), progress=progress)


def progress(filename, size, sent):
    """
        Define progress callback that prints the current percentage completed for the file
    """
    sys.stdout.write("%s\'s progress: %.2f%%   \r" % (filename, float(sent) / float(size) * 100))


def get_ssh_session(server, user, password, port=22, key_filename=None, pkey=None):
    logger.info('getting ssh_session')
    ssh = SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_system_host_keys()
    ssh.connect(hostname=server, username=user,
                password=password, port=port,
                key_filename=key_filename, pkey=pkey)
    return ssh


def scp_transfer(from_path, to_path, remote_config, scp_operation):
    """
        transfer files between local and remote servers
        if scp_operation is get then to_path should be local
        if scp_operation is put then from_path should be local
    """

    ssh = None
    scp = None
    try:
        ssh = get_ssh_session(remote_config.hostname,
                              remote_config.username,
                              remote_config.password)
        scp = get_scp_client(ssh)
        scp.sanitize = lambda x: x

        if scp_operation == ScpOperations.GET:
            from_path = win_escape(from_path)
            scp.get(remote_path=from_path, local_path=to_path, recursive=True)
        elif scp_operation == ScpOperations.PUT:
            to_path = win_escape(to_path)
            scp.put(files=from_path, remote_path=to_path, recursive=True)

    finally:
        if ssh is not None:
            ssh.close()
        if scp is not None:
            scp.close()


def source_to_dest_upload(dest_config: WinRM, dest_path, source_path, source_config: WinRM = None):
    """
        transfer files and folders from remote to remote/ local to remote
        keep source config None if source is local
    """
    logger.info('starting remote to remote upload')
    local_path = ''
    try:
        # os.mkdir(local_path)

        if source_config is not None:  # source is remote machine
            local_path = '.\\temp' + str(datetime.now()).replace(':', '_')
            scp_transfer(source_path, local_path, source_config, ScpOperations.GET)
        else:
            local_path = source_path
        # connection with slave server
        scp_transfer(local_path, dest_path, dest_config, ScpOperations.PUT)

    except Exception as ex:
        raise Exception(f"error in remote_to_remote_upload method : {ex}")
    finally:
        if source_config is not None:
            if os.path.exists(local_path):
                if os.path.isfile(local_path):
                    os.remove(local_path)
                if os.path.isdir(local_path):
                    shutil.rmtree(local_path)


def dawin_uploadfile(css_testee_login_as_domain_admin, config, source, dest, dest_dir):
    logger.info("Uploading %s to %s %s using scp" % (source, config.hostname, dest))
    # create directory
    cmd = 'mkdir.exe "%s"' % dest_dir
    css_testee_login_as_domain_admin.send_command(cmd)
    # upload file
    rc, result, error = scp_upload(config.hostname, config.username, config.password, source, dest)
    if rc != 0:
        raise Exception("Failed to upload file %s. Error: %s" % (source, error))


def dawin_uploadfolder(css_testee_login_as_domain_admin, config, source, dest):
    logger.info("Uploading %s to %s %s using scp" % (source, config.hostname, dest))
    # create directory
    cmd = 'mkdir.exe "%s"' % dest
    css_testee_login_as_domain_admin.send_command(cmd)
    # upload folder
    rc, result, error = scp_uploadfolder(config.hostname, config.username, config.password,
                                         source, dest)
    if rc != 0:
        raise Exception("Failed to upload folder %s. Error: %s" % (source, error))


def create_install_commandline(full_path):
    installable_name = os.path.basename(full_path)
    installable_dir = os.path.dirname(full_path)
    cmdline = f'cd "{installable_dir}" & start /wait msiexec.exe /i \"{installable_name}\" /q'
    return cmdline


def create_uninstall_commandline(full_path, wait=True):
    installable_name = os.path.basename(full_path)
    installable_dir = os.path.dirname(full_path)
    cmdline = f'cd "{installable_dir}" & start "{"/wait" if wait else ""}" msiexec.exe /x \"{installable_name}\" /q'
    return cmdline


def dawin_runinstaller(css_testee_login_as_domain_admin, command, package):
    """
    Runs installer package/command to install or un-install package
    """
    action = "un-installing" if command.find("/x") > -1 else "installing"
    logger.info("%s %s via WinRM" % (action, package))
    logger.debug("Running %s" % command)

    rc, result, error = \
        css_testee_login_as_domain_admin.send_command(command)
    if rc != 0:
        raise Exception("Failed to %s %s. Error: %s" % (action, package, error))


def test_client_installed(test_client_uploaded, css_client_login):
    """
            Install client da agent, python and python modules on the client test machine
    """
    logger.info("Install test tools...")
    cmdline = create_install_commandline(test_client_uploaded['winappdriver_fullpath'])
    dawin_runinstaller(css_client_login, cmdline, 'WindowsApplicationDriver.msi')

    cmdline = create_install_commandline(test_client_uploaded['test_da_agent_fullpath'])
    dawin_runinstaller(css_client_login, cmdline, test_client_uploaded['test_da_agent'])

    install = False
    if not css_client_login.check_file("%s\\python.exe" % python_install_path):
        install = True

    if install == True:
        cmdline = "start /wait %s /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1 TargetDir=%s" % (
            test_client_uploaded['pythonfullpath'], python_install_path)
        dawin_runinstaller(css_client_login, cmdline, test_client_uploaded['python'])

        cmdline = "cacls.exe %s /E /G Everyone:F" % python_install_path
        logger.debug(cmdline)
        css_client_login.send_command(cmdline)

    cmdline = "pip install -r %s\\requirements.txt" % test_client_uploaded['frameworkdir']
    dawin_runinstaller(css_client_login, cmdline, "python modules")

    cmdline = "pip install --ignore-installed pywin32"
    dawin_runinstaller(css_client_login, cmdline, "python pywin32")

    logger.info("Install test tools done.")


@pytest.fixture(scope='session')
def dawin_test_client_installed(dawin_test_client_uploaded, css_client_login):
    """
        Install client da agent, python and python modules on the client test machine
    """
    test_client_installed(dawin_test_client_uploaded,css_client_login)
    yield dawin_test_client_uploaded
    if tear_down:
        # cmdline = create_uninstall_commandline(dawin_test_client_uploaded['winappdriver_fullpath'])
        # dawin_runinstaller(css_client_login, cmdline, 'WindowsApplicationDriver.msi')

        cmdline = create_uninstall_commandline(dawin_test_client_uploaded['test_da_agent_fullpath'])
        dawin_runinstaller(css_client_login, cmdline, dawin_test_client_uploaded['test_da_agent'])


@pytest.fixture(scope='session')
def dawin_testagent_installed(dawin_testagent_uploaded, css_testee_machine, css_testee_login_as_domain_admin):
    """
    Install test agent, python and python modules on the test machine
    """
    logger.info("Install test tools...")

    install = False
    if not css_testee_login_as_domain_admin.check_file("%s\\python.exe" % python_install_path):
        install = True

    if install:
        cmdline = "start /wait %s /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1 TargetDir=%s" % (
            dawin_testagent_uploaded['pythonfullpath'], python_install_path)
        dawin_runinstaller(css_testee_login_as_domain_admin, cmdline, dawin_testagent_uploaded['python'])

        cmdline = "cacls.exe %s /E /G Everyone:F" % python_install_path
        logger.debug(cmdline)
        css_testee_login_as_domain_admin.send_command(cmdline)

    cmdline = "pip install -r %s\\requirements.txt" % dawin_testagent_uploaded['frameworkdir']
    dawin_runinstaller(css_testee_login_as_domain_admin, cmdline, "python modules")

    cmdline = "pip install --ignore-installed pywin32"
    dawin_runinstaller(css_testee_login_as_domain_admin, cmdline, "python pywin32")

    logger.info("Install test tools done.")

    yield dawin_testagent_uploaded
    # Teardown to uninstall testagent


def upload_test_framework(css_login, remote_testscripts_dir):
    logger.info("uploading framework files")
    dawin_upload_files_folders(remote_testframework_dir + r"\requirements.txt",
                               css_login, r".\requirements.txt")
    dawin_upload_files_folders(remote_testframework_dir + r"\conftest.py",
                               css_login, r".\conftest.py")
    dawin_upload_files_folders(remote_testframework_dir + r".\Assets",
                               css_login, r".\Assets")
    dawin_upload_files_folders(remote_testframework_dir + r".\Shared",
                               css_login, r".\Shared")
    dawin_upload_files_folders(remote_testframework_dir + r".\Config",
                               css_login, r".\Config")
    dawin_upload_files_folders(remote_testframework_dir + r".\Fixtures",
                               css_login, r".\Fixtures")
    dawin_upload_files_folders(remote_testframework_dir + r".\Utils",
                               css_login, r".\Utils")
    dawin_upload_files_folders(remote_testframework_dir + remote_testscripts_dir,
                               css_login, remote_testscripts_dir)

    logger.info("change framework folder permission to allow test users write logs")
    cmdline = "cacls.exe %s /E /G Everyone:F" % remote_testframework_dir
    logger.debug(cmdline)
    css_login.send_command(cmdline)


def tear_down_client(css_client_login):
    css_client_login.send_command('rmdir "%s" /s /q' % remote_testframework_dir)
    css_client_login.send_command('rmdir "%s" /s /q' % remote_winappdriver_path)
    css_client_login.send_command('rmdir "%s" /s /q' % remote_da_agent_path)


def test_client_uploaded(css_client_login, css_repo_login, test_dir):
    """
            Upload test scripts, test agent package,  python package and provide the upload info.
    """
    logger.info("Upload test tool packages...")
    uploaded = {}
    # upload test scripts

    upload_test_framework(css_client_login, test_dir)

    logger.info("uploading da agent")
    dawin_upload_files_folders(remote_da_agent_path, css_client_login, repo_da_agent_path, css_repo_login)

    logger.info("uploading win app driver")
    dawin_upload_files_folders(remote_winappdriver_path, css_client_login, repo_winappdriver_path, css_repo_login)

    logger.info("uploading python")
    dawin_upload_files_folders(remote_python_path, css_client_login, repo_python_path, css_repo_login)

    uploaded['pythonfullpath'] = remote_python_path
    uploaded['python'] = 'python package'
    uploaded['winappdriver_fullpath'] = remote_winappdriver_path
    uploaded['test_da_agent'] = os.path.basename(remote_da_agent_path)
    uploaded['test_da_agent_fullpath'] = remote_da_agent_path
    uploaded['frameworkdir'] = remote_testframework_dir

    logger.info("Upload test tool packages done.")

    return uploaded


@pytest.fixture(scope='session')
def dawin_test_client_uploaded(css_client_login, css_repo_login):
    """
        Upload test scripts, test agent package,  python package and provide the upload info.
    """
    yield test_client_uploaded(css_client_login, css_repo_login, remote_da_testscripts_dir)

    if tear_down:
        tear_down_client(css_client_login)


@pytest.fixture(scope='session')
def dawin_testagent_uploaded(css_testee_login_as_domain_admin, css_repo_login):
    """
    Upload test scripts, python package and provide the upload info.
    """
    logger.info("Upload test tool packages...")
    uploaded = {}
    # upload test scripts

    upload_test_framework(css_testee_login_as_domain_admin, remote_da_testscripts_dir)

    logger.info("uploading python")
    dawin_upload_files_folders(remote_python_path, css_testee_login_as_domain_admin, repo_python_path, css_repo_login)

    uploaded['python'] = 'python_package'
    uploaded['pythonfullpath'] = remote_python_path
    uploaded['frameworkdir'] = remote_testframework_dir

    logger.info("Upload test tool packages done.")

    yield uploaded

    if tear_down:
        css_testee_login_as_domain_admin.send_command('rmdir "%s" /s /q' % remote_testframework_dir)


@pytest.fixture(scope='session')
def dawin_uploaded(css_testee_login_as_domain_admin, css_repo_login):
    """
    Upload DAWin package and provide the upload info.
    """
    logger.info("Upload dawin packages...")

    uploaded = {}

    logger.info("uploading win app driver")
    dawin_upload_files_folders(remote_winappdriver_path, css_testee_login_as_domain_admin, repo_winappdriver_path,
                               css_repo_login)

    logger.info("uploading Collector")
    dawin_upload_files_folders(remote_collector_path, css_testee_login_as_domain_admin, repo_collector_path,
                               css_repo_login)

    logger.info("uploading Audit manager")
    dawin_upload_files_folders(remote_audit_manager_path, css_testee_login_as_domain_admin, repo_audit_manager_path,
                               css_repo_login)

    logger.info("uploading DA Admin")
    dawin_upload_files_folders(remote_da_administrator_console_path, css_testee_login_as_domain_admin,
                               repo_da_administrator_console_path,
                               css_repo_login)

    logger.info("uploading DA Auditor")
    dawin_upload_files_folders(remote_da_auditor_path, css_testee_login_as_domain_admin,
                               repo_da_auditor_path,
                               css_repo_login)

    uploaded['da_auditor'] = remote_da_auditor_path
    uploaded['da_admin_console'] = remote_da_administrator_console_path
    uploaded['audit_manager'] = remote_audit_manager_path
    uploaded['da_collector'] = remote_collector_path
    uploaded['winAppDrvr'] = remote_winappdriver_path

    logger.info("Upload dawin packages done")

    yield uploaded
    if tear_down:
        css_testee_login_as_domain_admin.send_command('del "%s"' % uploaded['da_auditor'])
        css_testee_login_as_domain_admin.send_command('del "%s"' % uploaded['da_admin_console'])
        css_testee_login_as_domain_admin.send_command('del "%s"' % uploaded['audit_manager'])
        css_testee_login_as_domain_admin.send_command('del "%s"' % uploaded['da_collector'])
        css_testee_login_as_domain_admin.send_command('del "%s"' % uploaded['winAppDrvr'])


@pytest.fixture(scope='session')
def dawin_installed(dawin_uploaded, css_testee_machine, css_testee_login_as_domain_admin):
    """
    Install DAWin package on the test machine
    """
    logger.info("Install dawin packages...")

    # region install da_auditor and audit_manager
    cmdline = create_install_commandline(dawin_uploaded['da_auditor'])
    dawin_runinstaller(css_testee_login_as_domain_admin, cmdline, dawin_uploaded['da_auditor'])
    cmdline = create_install_commandline(dawin_uploaded['audit_manager'])
    dawin_runinstaller(css_testee_login_as_domain_admin, cmdline, dawin_uploaded['audit_manager'])
    # endregion

    # region install da_admin_console
    cmdline = create_install_commandline(dawin_uploaded['da_admin_console'])
    dawin_runinstaller(css_testee_login_as_domain_admin, cmdline, dawin_uploaded['da_admin_console'])
    # endregion

    # region install collector
    cmdline = create_install_commandline(dawin_uploaded['da_collector'])
    dawin_runinstaller(css_testee_login_as_domain_admin, cmdline, dawin_uploaded['da_collector'])
    # endregion

    # region install Windows Application Driver
    cmdline = create_install_commandline(dawin_uploaded['winAppDrvr'])
    dawin_runinstaller(css_testee_login_as_domain_admin, cmdline, dawin_uploaded['winAppDrvr'])
    # endregion

    logger.info("Install dawin packages done")

    yield css_testee_machine
    if tear_down:
        logger.info("Un-Install dawin packages...")

        # region un-install da_auditor and audit_manager
        cmdline = create_uninstall_commandline(dawin_uploaded['da_auditor'])
        dawin_runinstaller(css_testee_login_as_domain_admin, cmdline, dawin_uploaded['da_auditor'])
        cmdline = create_uninstall_commandline(dawin_uploaded['audit_manager'])
        dawin_runinstaller(css_testee_login_as_domain_admin, cmdline, dawin_uploaded['audit_manager'])
        # endregion

        # region un-install da_admin_console
        cmdline = create_uninstall_commandline(dawin_uploaded['da_admin_console'])
        dawin_runinstaller(css_testee_login_as_domain_admin, cmdline, dawin_uploaded['da_admin_console'])
        # endregion

        # region un-install collector
        cmdline = create_uninstall_commandline(dawin_uploaded['da_collector'], False)
        # wait few seconds for blocking process collector.configure.exe to start
        cmdline = cmdline + " & waitfor SomethingThatIsNeverHappening /t 10 2>NUL "
        # kill blocking process to enable un-install
        cmdline = cmdline + " & taskkill /FI \"IMAGENAME eq collector.configure.exe\" /F"
        dawin_runinstaller(css_testee_login_as_domain_admin, cmdline, dawin_uploaded['da_collector'])
        # endregion

        # region install Windows Application Driver
        cmdline = "taskkill /FI \"IMAGENAME eq WinAppDriver.exe\" /F & "
        cmdline = cmdline + create_uninstall_commandline(dawin_uploaded['winAppDrvr'])
        dawin_runinstaller(css_testee_login_as_domain_admin, cmdline, dawin_uploaded['winAppDrvr'])
        # endregion

        logger.info("Un-Install dawin packages done")


def test_machine_connectin(css_testee_machine):
    logger.debug("Start testing machine connection")
    winrm_config = collections.namedtuple('winrm_config', ('hostname username password'))
    config = winrm_config(hostname=css_testee_machine['public_ip'],
                          username="Administrator",
                          password=css_testee_machine['admin_password'])
    winrm = WinRM(config)

    rc, result, error = \
        winrm.send_command("powershell.exe -Command Check-TestAgentConnection")
    logger.debug("rc %s, result %s, error %s" % (rc, result.strip(), error))
    if rc == 0:
        logger.debug("Testing machine connection succeeded")
    else:
        raise Exception("Test machine connection failed. Error: %s" % error)


@pytest.fixture(scope='session')
def dawin_joined(dawin_testagent_installed, dawin_installed, css_testee_login_as_domain_admin, css_testee_machine, css_test_env):
    logger.info("Testing connection to test machine...")
    # wait until restart finish
    retry = 2
    while retry > 0:
        try:
            test_machine_connectin(css_testee_machine)
        except Exception as e:
            retry -= 1
            logger.debug(e)
            sleep(10)
    yield dawin_installed


@pytest.fixture
def get_aduser_from_yaml(css_test_env):
    """
    Get aduser from env config file and return list of aduser
    """
    aduser_dict = {}
    for i, j in css_test_env.items():
        if 'aduser' in i:
            aduser_dict[i] = j
    yield ([value for key, value in aduser_dict.items()])