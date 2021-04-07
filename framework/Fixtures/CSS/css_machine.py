# css_machine.py
#
# Provide test machine per session.
#

import pytest
import os
import collections
import logging

from Utils.terraform_functions import *
from Utils.ssh_util import SshUtil
from Utils.winrm import WinRM

logger = logging.getLogger('framework')


def get_config_file_details(test_machine_info):
    """
         get the details of the config.
    """
    config_file = os.path.join(test_machine_info['dir'],
                               test_machine_info['file'])
    # If the site is terraform, run terraform to prepare the machine.
    # For other site, read the corresponding yaml file.
    if test_machine_info['site'] == "terraform":
        machine_dir = os.path.join(test_machine_info['tdir'],
                                   test_machine_info['name'])
        dict = terraform_instance(machine_dir, config_file)
    else:
        with open(config_file, 'r') as stream:
            dict = yaml.safe_load(stream)
    return dict


@pytest.fixture(scope='session')
def css_repo_test_machine(css_repo_test_machine_info):
    """
            Provide the repository test machine.
    """
    yield get_config_file_details(css_repo_test_machine_info)


@pytest.fixture(scope='session')
def css_client_test_machine(css_client_test_machine_info):
    """
        Provide the client test machine.
    """
    yield get_config_file_details(css_client_test_machine_info)


@pytest.fixture(scope='session')
def css_testee_machine(css_testee_machine_info):
    """
    Provide the test machine.
    """
    # If the site is terraform, run terraform to prepare the machine.
    # For other site, read the corresponding yaml file.
    yield get_config_file_details(css_testee_machine_info)

    # Do not destroy for now
    # terraform_destroy(machine_dir, config_file)


@pytest.fixture(scope='session')
def css_test_machine(css_test_machine_info):
    """
    Provide the test machine.
    """
    # If the site is terraform, run terraform to prepare the machine.
    # For other site, read the corresponding yaml file.
    config_file = os.path.join(css_test_machine_info['dir'],
                               css_test_machine_info['file'])
    if css_test_machine_info['site'] == "terraform":
        machine_dir = os.path.join(css_test_machine_info['tdir'],
                                   css_test_machine_info['name'])
        dict = terraform_instance(machine_dir, config_file)
    else:
        with open(config_file, 'r') as stream:
            dict = yaml.safe_load(stream)
    yield dict
    # Do not destroy for now
    # terraform_destroy(machine_dir, config_file)


@pytest.fixture(scope='session')
def css_login_as_root(css_test_machine):
    """
    Provide a SSH connection to the machine as root user
    """
    ssh_config = collections.namedtuple('ssh_config',
                                        ('hostname port username '
                                         'rsa_key_file password'))
    config = ssh_config(hostname=css_test_machine['public_ip'],
                        port=22,
                        username="root",
                        rsa_key_file="",  # Use password for now
                        password=css_test_machine['root_password'])
    logger.debug("ssh instantiated")
    yield SshUtil(config)
    # Close connection?


@pytest.fixture(scope='session')
def css_repo_login(css_repo_test_machine):
    """
        Provide a WinRM connection to the Windows test machine
    """
    yield get_local_user_winrm(css_repo_test_machine)


@pytest.fixture(scope='session')
def css_client_login(css_client_test_machine):
    yield get_local_user_winrm(css_client_test_machine)

@pytest.fixture(scope='session')
def css_testee_login_as_domain_admin(css_testee_machine):
    yield get_domain_admin_winrm(css_testee_machine)

@pytest.fixture(scope='session')
def css_login_as_localadmin(css_test_machine):
    """
    Provide a WinRM connection to the Windows test machine as Administrator
    """
    winrm_config = collections.namedtuple('winrm_config', 'hostname username password')
    config = winrm_config(hostname=css_test_machine['public_ip'],
                          username="Administrator",
                          password=css_test_machine['admin_password'])
    logger.debug("winrm instantiated")
    yield WinRM(config)
    # Close connection?


@pytest.fixture(scope='session')
def css_login_as_domainadmin(css_test_machine):
    """
    Provide a WinRM connection to the Windows test machine as Administrator
    """
    winrm_config = collections.namedtuple('winrm_config', 'hostname username password')
    config = winrm_config(hostname=css_test_machine['public_ip'],
                          username=css_test_machine['domain_name'].split('.')[0] + r"\Administrator",
                          password=css_test_machine['admin_password'])
    logger.debug("winrm instantiated")
    yield WinRM(config)
    # Close connection?


def get_domain_admin_winrm(test_machine):
    """
        Provide a WinRM connection to the Windows test machine as Administrator
    """
    winrm_config = collections.namedtuple('winrm_config', 'hostname username password transport')
    config = winrm_config(hostname=test_machine['public_ip'],
                          username=test_machine['domain_name'].split('.')[0] + r"\Administrator",
                          password=test_machine['admin_password'],
                          transport='credssp')
    logger.debug("winrm instantiated")
    return WinRM(config)


def get_local_user_winrm(test_machine):
    """
           Provide a WinRM connection to the Windows test machine as User
       """
    winrm_config = collections.namedtuple('winrm_config', ('hostname username password'
                                                           ))
    config = winrm_config(hostname=test_machine['public_ip'],
                          username=test_machine['user_name'],
                          password=test_machine['password'])
    logger.debug("winrm instantiated")
    return WinRM(config)
