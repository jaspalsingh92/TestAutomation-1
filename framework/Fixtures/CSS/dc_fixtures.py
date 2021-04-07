# dc_fixtures.py
#
# Provide DC related fixtures per package or per test.
#

import pytest
import os
import logging
import re

from Shared.css_constants import *
from Shared.dc_functions import *
from Shared.dc_states import *

logger = logging.getLogger('framework')
testees_repo = "testees"
remote_testees_dir = "/wesoft/release"
bundle_suffix = ".tgz"


###### DC fixtures ######

@pytest.fixture(scope='session')
def dc_bundle(css_test_release, css_test_ptag):
    os, ver, arch = css_test_ptag
    bundle = {}
    bundle['repo'] = testees_repo
    bundle['dir'] = remote_testees_dir
    if css_test_release in ["2020.1", "2020", "19.9", "19.6", "18.11"]:
        bundle_prefix = "centrify-infrastructure-services-"
    else:
        bundle_prefix = "centrify-server-suite-"
    bundle['bundle'] = f"{bundle_prefix}{css_test_release}-{os}{ver}-{arch}{bundle_suffix}"
    if os == "coreos":
        bundle['usr_dir'] = "/opt/centrify"  # INSTALL_USR_DIR
        bundle['dc_dir'] = "/opt/centrify"  # INSTALL_CDC_DIR
        bundle['data_dir'] = "/opt/centrify"  # INSTALL_DATA_DIR
        #
        bundle['usr_bin_dir'] = f"{bundle['usr_dir']}/bin"
        bundle['usr_sbin_dir'] = f"{bundle['usr_dir']}/sbin"
        bundle['dc_bin_dir'] = f"{bundle['dc_dir']}/bin"
        bundle['dc_sbin_dir'] = f"{bundle['dc_dir']}/sbin"
        bundle['dc_libexec_dir'] = f"{bundle['dc_dir']}/libexec"
    else:
        bundle['usr_dir'] = "/usr"  # INSTALL_USR_DIR
        bundle['dc_dir'] = "/usr/share/centrifydc"  # INSTALL_CDC_DIR
        bundle['data_dir'] = "/usr/share/"  # INSTALL_DATA_DIR
        #
        bundle['usr_bin_dir'] = f"{bundle['usr_dir']}/bin"
        bundle['usr_sbin_dir'] = f"{bundle['usr_dir']}/sbin"
        bundle['dc_bin_dir'] = f"{bundle['dc_dir']}/bin"
        bundle['dc_sbin_dir'] = f"{bundle['dc_dir']}/sbin"
        bundle['dc_libexec_dir'] = f"{bundle['dc_dir']}/libexec"
    yield bundle


@pytest.fixture
def dc_version(dc_extracted, css_login_as_root):
    """
    Get the DC release version
    """
    rc, result, error = \
        css_login_as_root.send_command(f"cd {dc_extracted['dir']} && ls adcheck-*")
    if rc != 0:
        raise Exception("Failed to find adcheck command in extracted directory")
    result = css_login_as_root.cleanup(result)
    adcheck = result.strip()
    rc, result, error = \
        css_login_as_root.send_command(f"cd {dc_extracted['dir']} && ./{adcheck} --version")
    if rc != 0:
        raise Exception(f"Failed to run './{adcheck} --version'")
    content = ''.join(css_login_as_root.to_list(result))
    logger.debug(content)
    x = re.search(r"\b(\d\.\d.\d-\d\d\d)\b", content)
    if rc != 0:
        raise Exception(f"Failed to get the dc version from the output of 'adcheck --version'")
    version = x.group(1)
    yield version


@pytest.fixture(scope='session')
def dns_configured(css_test_env, css_login_as_root):
    """
    Ensure the DNS is configured.
    """
    logger.debug(f"Updating /etc/resolv.conf with AD DNS IP {css_test_env['dns_ip']}")
    css_login_as_root.send_command(f"echo nameserver {css_test_env['dns_ip']} > /etc/resolv.conf")
    yield


@pytest.fixture
def backup_centrifydc_conf(dc_installed, css_login_as_root):
    """
    Backup the /etc/centrifydc/centrifydc.conf configuration file, the file
    will be restored automatically when the test is done.
    """
    logger.debug(f"Backup {CENTRIFYDC_CONF}")
    backup = CENTRIFYDC_CONF + ".pytest"
    rc, result, error = css_login_as_root.send_command(f"cp -pf {CENTRIFYDC_CONF} {backup}")
    if rc != 0:
        raise Exception(f"Backup via ssh returned error code {rc}. Error message: {error}")
    yield backup
    # Restore
    logger.debug(f"Restore {CENTRIFYDC_CONF}")
    css_login_as_root.send_command(f"mv -f {backup} {CENTRIFYDC_CONF}")


@pytest.fixture
def dc_refreshed(dc_joined, css_login_as_root, backup_centrifydc_conf,
                 centrifydc, adflush):
    """
    Make sure the cache is cleared and adclient pick up the latest (original)
    configurations.
    """
    css_login_as_root.send_command(f"{adflush} -f -y")
    css_login_as_root.send_command(f"{centrifydc} restart")
    yield dc_joined


###### DC required state fixtures ######

@pytest.fixture
def dc_uploaded(css_test_machine, dc_bundle, css_login_as_root):
    """
    Upload DC bundle and provide the upload info.
    """
    auto_upload_dc(css_test_machine, dc_bundle, css_login_as_root)
    yield dc_bundle


@pytest.fixture
def dc_extracted(dc_uploaded, css_login_as_root):
    """
    Upload and extract DC bundle and provide the upload info.
    """
    auto_extract_dc(dc_uploaded, css_login_as_root)
    yield dc_uploaded


@pytest.fixture
def install_mode():
    # Default mode
    default = "licensed"
    yield default


@pytest.fixture
def install_packages():
    # Default packages
    default = ['CentrifyDC']
    yield default


@pytest.fixture
def dc_installed(install_mode, install_packages, dc_extracted, css_test_env,
                 css_test_machine, css_login_as_root):
    """
    Provide the test machine with DirectControl installed.
    """
    auto_install_dc(install_mode, install_packages, css_test_env, dc_extracted, css_login_as_root)
    yield css_test_machine


@pytest.fixture
def dc_join_command():
    raise Exception("The dc_join_command fixture must be provided by test case")


@pytest.fixture
def dc_join_func(dns_configured, dc_bundle, css_login_as_root):
    """
    Provide the default join function to run dc_join_command as root
    """
    def join(command):
        rc = 0
        result = None
        error = None
        if not is_joined(dc_bundle, css_login_as_root):
            logger.debug(f"Running '{command}' to join domain via ssh")
            rc, result, error = css_login_as_root.send_command(command)
        return rc, result, error
    yield join


@pytest.fixture
def dc_joined(dc_join_command, dc_join_func, dc_installed, css_test_env,
              css_test_machine, dc_bundle, css_login_as_root):
    """
    Provide the test machine that has joined domain and the join information.
    """
    auto_join_domain(dc_join_command, dc_join_func, css_test_env, dc_bundle,
                     css_login_as_root)
    dict = css_test_env.copy()
    dict.update(dc_installed)
    yield dict


###### DC exact state fixtures ######

@pytest.fixture
def dc_is_uploaded(install_mode, install_packages, dc_join_command, dc_join_func,
                   css_test_env, css_test_machine, dc_bundle, css_login_as_root):
    """
    Go to the exact state that DC is just uploaded.
    """
    go_dc_state(DC_STATES['uploaded'], install_mode, install_packages,
                dc_join_command, dc_join_func, css_test_env, css_test_machine,
                dc_bundle, css_login_as_root)
    yield dc_bundle


@pytest.fixture
def dc_is_extracted(install_mode, install_packages, dc_join_command, dc_join_func,
                    css_test_env, css_test_machine, dc_bundle, css_login_as_root):
    """
    Go to the exact state that DC is just extracted.
    """
    go_dc_state(DC_STATES['extracted'], install_mode, install_packages,
                dc_join_command, dc_join_func, css_test_env, css_test_machine,
                dc_bundle, css_login_as_root)
    yield dc_bundle


@pytest.fixture
def dc_is_installed(install_mode, install_packages, dc_join_command, dc_join_func,
                    css_test_env, css_test_machine, dc_bundle, css_login_as_root):
    """
    Go to the exact state that DC is just installed.
    """
    go_dc_state(DC_STATES['installed'], install_mode, install_packages,
                dc_join_command, dc_join_func, css_test_env, css_test_machine,
                dc_bundle, css_login_as_root)
    yield css_test_machine


@pytest.fixture
def dc_is_joined(install_mode, install_packages, dc_join_command, dc_join_func,
                 css_test_env, css_test_machine, dc_bundle, css_login_as_root):
    """
    Go to the exact state that DC is just joined.
    """
    go_dc_state(DC_STATES['joined'], install_mode, install_packages,
                dc_join_command, dc_join_func, css_test_env, css_test_machine,
                dc_bundle, css_login_as_root)
    dict = css_test_env.copy()
    dict.update(css_test_machine)
    yield dict


@pytest.fixture
def dc_is_leaved(install_mode, install_packages, dc_join_command, dc_join_func,
                 css_test_env, css_test_machine, dc_bundle, css_login_as_root):
    """
    Go to the exact state that DC is just leaved.
    """
    go_dc_state(DC_STATES['leaved'], install_mode, install_packages,
                dc_join_command, dc_join_func, css_test_env, css_test_machine,
                dc_bundle, css_login_as_root)
    yield css_test_env


@pytest.fixture
def dc_is_uninstalled(install_mode, install_packages, dc_join_command, dc_join_func,
                      css_test_env, css_test_machine, dc_bundle, css_login_as_root):
    """
    Go to the exact state that DC is just uninstalled.
    """
    go_dc_state(DC_STATES['uninstalled'], install_mode, install_packages,
                dc_join_command, dc_join_func, css_test_env, css_test_machine,
                dc_bundle, css_login_as_root)
    yield dc_bundle


@pytest.fixture
def dc_is_removed(install_mode, install_packages, dc_join_command, dc_join_func,
                  css_test_env, css_test_machine, dc_bundle, css_login_as_root):
    """
    Go to the exact state that DC is just removed.
    """
    go_dc_state(DC_STATES['removed'], install_mode, install_packages,
                dc_join_command, dc_join_func, css_test_env, css_test_machine,
                dc_bundle, css_login_as_root)
    yield dc_bundle


@pytest.fixture
def home_path(css_test_ptag):
    """
    Provide the home directory as per the os
    """
    home_path_d = {
        'sol': '/export/home/',
    }
    os, ver, arch = css_test_ptag
    yield home_path_d.get(os, '/home/')


@pytest.fixture
def default_shell(css_test_ptag):
    """
    Provide the default shell as per the os
    """
    default_shell_os = {
        'sol': '/bin/sh',
    }
    os, ver, arch = css_test_ptag
    yield default_shell_os.get(os, '/bin/bash')


@pytest.fixture(scope='session')
def syslog_path(css_test_ptag):
    """
    Provide the syslog path as per the os
    """
    syslog_path_d = {
        'hp': '/var/adm/syslog/',
    }
    os, ver, arch = css_test_ptag
    yield syslog_path_d.get(os, '/var/log/')
