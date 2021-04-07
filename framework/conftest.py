import datetime
import logging
import math
import socket
import os
import glob
import pathlib
import pytest
import subprocess
import uuid
import re
import shutil
import Utils.settings
from collections import namedtuple
from datetime import timezone

from Shared.elasticsearch_data_manager import ElasticsearchRequestData
from Utils.cent_logger import setup_root_logger
from Utils.config_loader import Configs
from Utils.elasticsearch import Elasticsearch


settings = Configs.get_node("framework", "framework")
for i in settings:
    setattr(Utils.settings, i, settings[i])
setattr(Utils.settings, 'options', {})

_session_es_info = {}  # alias for elasticsearch_run_data

# fixtures which use syntax not acceptable as a plugin from a conftest.py file
excluded_fixtures = [
    'application_management_fixtures',
    'cis_fixtures',
    'core_bat_fixtures',
    'credman_fixtures',
    'pdst_fixtures',
    'selenium_webdriver_fixtures',
    'suvp_fixtures',
    'user_login_with_mfa_rts_fixture'
]

pytest_plugins = []
# import all fixtures automatically, except for those being excluded.
glob_pattern = 'Fixtures' + os.sep + '**' + os.sep + '*.py'
for filename in glob.iglob(glob_pattern, recursive=True):

    is_init = re.search('__init__', filename)

    if is_init is None:
        is_excluded = False
        for excluded_fixture in excluded_fixtures:
            if re.search(excluded_fixture, filename):
                is_excluded = True

        if is_excluded is False:
            plugin_notation = re.sub(re.escape(".py"), '', filename)
            plugin_notation = re.sub(re.escape(os.sep), '.', plugin_notation)
            pytest_plugins.append(plugin_notation)


# Load CSS related fixtures only
if pathlib.Path('css_fixtures_only').exists():

    pytest_plugins = []

    skip_set = {
            'Fixtures.CSS.__init__', # This is not a fixture.
            }

    for l in pathlib.Path('./Fixtures/CSS').rglob('*.py'):

        fixture_name = '.'.join(l.parent.parts) + '.' + l.stem
        # Example:
        #     ./Fixtures/CSS/my_fixture.py
        #     -> parent     : "Fixtures/CSS"  + stem: "my_fixture"
        #     -> parts      : [Fixtures, CSS] + stem: "my_fixture"
        #     -> join by '.': "Fixtures.CSS"  + stem: "my_fixture"
        #     -> concat stem: "Fixtures.CSS"  + "." + "my_fixture"
        #     -> result     : "Fixtures.CSS.my_fixture"


        if fixture_name not in skip_set:
            pytest_plugins.append(fixture_name)


def pytest_addoption(parser):
    parser.addoption("--log_level", action="store", default="ERROR", help="Set default logging level")
    parser.addoption("--log_dir", action="store", default=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Logs'), help="Set logging directory")
    parser.addoption("--log_config_file", action="store", default=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Utils', 'cent_logger.json'), help="log configuration file in json format")
    parser.addoption("--core_config_node", action="store", default="automation_main", help="Define the core configuration node to use.  Defaults to the primary automation node. ")
    parser.addoption("--core_config_file", action="store", default="core", help="Define which file to use for core configuration, default to core.yaml")
    parser.addoption("--core_config_strict", action="store_false", default=True, help="disables use of strict mode on get_parametrized_yaml_nodes")
    parser.addoption("--windows_config_file", action="store", default="windows", help="Define which file to use for windows configuration, default to windows.yaml")
    parser.addoption("--windows_config_node", action="store", default="automation_main", help="Define the windows configuration node to use.  Defaults to automation_main. ")
    parser.addoption("--pas_config_node", action="store", default="automation_main", help="Define the PAS configuration node to use.  Defaults to the primary automation node. ")
    parser.addoption("--pas_config_file", action="store", default="pas", help="Define which file to use for PAS tests, default to pas.yaml")
    parser.addoption("--pas_config_strict", action="store_false", default=True, help="disables use of strict mode on get_parametrized_yaml_nodes")
    parser.addoption("--cis_config_node", action="store", default="automation_main", help="Define the CIS configuration node to use.  Defaults to the primary automation node.")
    parser.addoption("--cis_config_file", action="store", default="cis", help="Define which file to use for CIS tests, default to cis.yaml")
    parser.addoption("--cis_config_strict", action="store_false", default=True, help="Disables use of strict mode on get_parametrized_yaml_nodes")
    parser.addoption("--mte_config_node", action="store", default="automation_main", help="Define the MTE configuration node to use.  Defaults to the primary automation node.")
    parser.addoption("--mte_config_file", action="store", default="mte", help="Define which file to use for mte tests, default to mt.yaml")
    parser.addoption("--elasticsearch", action="store_true", default=False, help="Upload test result data to Elasticsearch")
    parser.addoption("--credman_user", action="store", default=None)
    parser.addoption("--credman_pass", action="store", default=None)
    parser.addoption("--credman_url", action="store", default=None)
    parser.addoption("--headless", action="store", type=bool, default=False, help="--headless True to use a headless browser during testing. --headless False otherwise")
    parser.addoption("--credman_tenantid", action="store", default=None)
    parser.addoption("--credman_disable", action="store_true", default=True)
    parser.addoption("--selenium_config_file", action="store", default="selenium", help="Pulls default info from selenium.yaml")
    parser.addoption("--selenium_config_node", action="store", default="chrome_windows_local", help="Get the browser you want from the config file - defaults to Chrome Local")
    parser.addoption("--selenium_config_strict", action="store_false", default=True, help="Disables use strict mode on get_parametrized_yaml_nodes")
    parser.addoption("--pdst_pods_node", action="store", default="prod_pods", help="Define the pdst configuration node to use for pod information. Defaults to Production Pods")
    parser.addoption("--pdst_files_node", action="store", default="prod_files", help="Define the pdst configuration node to use for file information. Defaults to a set of all current Downloads Files")
    parser.addoption("--pdst_config_file", action="store", default="pdst", help="Define which file to use for pdst tests, default to pas.yaml")
    parser.addoption("--pdst_deploy_release", action="store", help="Define which deploy matrix should be downloaded from the release candidate.")
    parser.addoption("--css_site", action='store', default="santaclara", help="Define which MTE site will be used. Default is santaclara.")
    parser.addoption("--css_machine", action='store', default="", help="Define which machine will be used. Default is env (shared machine).")
    parser.addoption("--css_machine_file", action='store', default="", help="Specify the machine yaml file which will override the --css_machine option.")
    parser.addoption("--css_release", action='store', default="19.9", help="Define which CSS release to be tested. Default is 19.9.")
    parser.addoption("--css_ptag", action='store', default="rhel5", help="Define which CSS package to be tested by the package platform tag. Default is rhel5.")
    parser.addoption("--cc_release", action='store', default="station", help="Define which Cloud Client branch to be tested. Defaults to 'station'.")
    parser.addoption("--css_client_machine_file", action='store', default='', help="Specify the client machine yaml file which will be used")
    parser.addoption("--css_repo_machine_file", action='store', default='', help="Specify the repo machine yaml file which will be used")
    parser.addoption("--css_client_os_tag", action='store', default="win2016", help="Define which CSS client user to be tested by the os tag. Default is win2016.")
    parser.addoption("--css_repo_os_tag", action='store', default="win2016", help="Define which CSS repo to be tested by the os tag. Default is win2016.")
    parser.addoption("--css_testee_os_tag", action='store', default="win2012r2",help="Define which CSS testee to be tested by the os tag. Default is win2012r2.")

def pytest_configure(config):
    setup_root_logger(config.getoption('--log_level'), config.getoption('--log_dir'),
                      config.getoption('--log_config_file'))
    custom_marks = {
        "api": "Tests which exercises APIs and not the UI.",
        "bhavana": "Test Marker",
        "bhavna": "Tests written by bhavna",
        "bhavna_ui": "UI tests written by bhavna",
        "bulk_account_delete": "All tests related to deleting multiple accounts in PAS",
        "bulk_manage_accounts": "All tests related to managing multiple accounts in PAS",
        "bulk_rotate_passwords": "All tests related to rotating passwords for multiple accounts in PAS",
        "bulk_system_delete": "All tests related to deleting multiple systems in PAS",
        "bulk_system_delete_apps_and_services": "All tests related to deleting multiple systems in PAS, when those systems may have apps/services related to them",
        "discovery": "All tests related to deleting discovery",
        "pas": "All tests related to the PAS product.",
        "pas_api_ui": "All tests related to the PAS product which use api and ui? This mark should be deleted imo.",
        "pas_ui": "All PAS ui tests? This mark should be deleted imo. Can run marks logically. python -m pytest -m 'pas and ui'",
        "pasapi": "Same comment as above, should be deleted.",
        "pasapi_ui": "Same comment as above, should be deleted.",
        "pasui": "Same comment as above, should be deleted.",
        "pasui_api": "Same comment as above, should be deleted.",
        "roleright": "Tests related to roles and rights in Platform section of PAS",
        "cps": "PAS tests that relate to what used to be called CPS, i.e. - anything not platform.",
        "report": "PAS tests related to reports",
        "plumbing": "PAS tests which exercise the 'plumbing' of our product's implementation. These don't correlate to a particular section of the product.",
        "loginbatapi": "API tests for the login basic acceptance test",
        "corebatapi": "API tests for the core basic acceptance test",
        "applications": "All tests related to applications",
        "platform": "All tests that fall under the 'platform' section of our product: users/roles/applications/ and more...",
        "bhavna_api": "API tests written by bhanvna. Another mark that should be deleted.",
        "bhavnaapi_ui": "API/UI tests written by bhavna. Another mark that should be deleted.",
        "deletesshacc": "Tests related to deleting accounts in PAS which use SSH keys as credentials.",
        "deletessh": "Tests related to deleting SSH keys",
        "ed25519_ssh": "?",
        "ecdsa_ssh": "?",
        "dsa_ssh": "?",
        "rsa_ssh": "?",
        "sshadd": "Tests related to adding ssh keys",
        "sshgenfile": "Tests related to generating an ssh key file",
        "sshgen": "?",
        "bhavna1": "?",
        "sets": "Tests related to sets",
        "cps_api": "Another mark to delete, combination of cps and api",
        "system": "?",
        "ssh": "?",
        "database": "Tests related to databases in PAS",
        "unix_password_reconciliation": "Tests for unix password reconciliation in PAS",
        "unix_lapr": "Tests for unix password reconciliation in PAS",
        "unix_agent": "Tests for agent based account management on unix",
        "windows_agent": "Tests for agent based account management on windows",
        "secrets": "Tests for secrets in PAS",
        "ibe": "Tests for idaptive browser extension. Delete?",
        "pas_api": "Another mark to delete, combination of pas and api",
        "cbe": "Tests related to Centrify browser extension",
        "bat": "Tests that should be included in a basic acceptance test",
        "testfixture": "?",
        "ui_framework": "Tests related to the ui framework instead of a specific section of our product offering",
        "ui_navigation": "Tests related to navigation in the ui",
        "ui": "UI (E2E) tests",
        "smoke": "Tests that should be run pre-commit",
        "daily": "Tests that should be run once a day to ensure stability",
        "example": "Tests included as examples",
        "xss": "Tests focused on verifying xss attacks won't work",
        "csrf": "Tests focused on verifying csrf attacks won't work",
        "security": "Tests focused on known security holes which were fixed",
        "embedded_json": "Tests for json embedded in html documents",
        "browser_override": "Tests to make sure we can test more than just chrome",
        "ad_user": "Tests to make sure we can test AD users",
        "cds_user": "Tests to make sure we can test CDS users",
        "xss_fixtures": "Tests which verify the xss fixtures",
        "user_fixtures": "Tests which verify the user fixtures a lot of other tests depend on",
        "pas1": "?",
        "workflow": "Tests which verify our workflow functionality",
        "windows_lapr": "Tests for windows local password reconciliation in PAS",
        "scen1": "Legacy mark, tests should be depricated",
        "scen2": "Legacy mark, tests should be depricated",
        "redhat": "?",
        "agents": "?",
        "test_dc_state_fixture": "?",
        "test_dc_functions": "?",
        "css": "?",
        "dzwin_bat": "?",
        "pas_scale": "Mark for the pas scale tests",
        "api_ui": "Combo mark that should be deleted",
        "customssh": "Resource profile tests",
        "resourcecounts": "Resource counts dashboard test",
        "cloudprovider": "Cloud Provider Tests",
        "aws": "Used to specify AWS specific cloud provider tests (not included with generic tests)",
        "azure": "Used to specify Azure specific cloud provider tests (not included with generic tests)",
        "managedssh": "ManagedSSH accounts",
        "pas_pdst": "mark for pas pdst automation",
        "favorites": "Tests related to PAS favorite functionality",
        "debugme": "temporary test marker used while debugging",
        "cclient_regression": "all tests for regression of cclient features",
        "cclient_sanity": "sanity tests, selections from cclient.regression",
        "cclient_pdst": "post-deployment tests, selections from cclient.regression",
        "cclient_setup": "download and install of agent",
        "cclient_takedown": "uninstall and removal of agent",
        "cclient_windows": "all windows agent tests",
        "cclient_linux": "all linux agent tests",
        "cclient_privelevation" : "Specific tests relating to the Privilege Elevation Feature",
        "devicestab": "Tests related to Devices tab",
        "sysadminsetoption": "Tests related to admin visibility of sets not owned by them"
    }

    for m in custom_marks:
        config.addinivalue_line("markers", f"{m}: {custom_marks[m]}")

    Utils.settings.options['log_level'] = config.getoption("--log_level")
    Utils.settings.options['log_dir'] = config.getoption("--log_dir")
    Utils.settings.options['log_config_file'] = config.getoption("--log_config_file")
    Utils.settings.options['core_config_node'] = config.getoption("--core_config_node")
    Utils.settings.options['core_config_file'] = config.getoption("--core_config_file")
    Utils.settings.options['css_client_machine_file'] = config.getoption("--css_client_machine_file")
    Utils.settings.options['core_config_strict'] = config.getoption("--core_config_strict")
    Utils.settings.options['pas_config_node'] = config.getoption("--pas_config_node")
    Utils.settings.options['windows_config_file'] = config.getoption("--windows_config_file")
    Utils.settings.options['windows_config_node'] = config.getoption("--windows_config_node")
    Utils.settings.options['pas_config_file'] = config.getoption("--pas_config_file")
    Utils.settings.options['pas_config_strict'] = config.getoption("--pas_config_strict")
    Utils.settings.options['cis_config_node'] = config.getoption("--cis_config_node")
    Utils.settings.options['cis_config_file'] = config.getoption("--cis_config_file")
    Utils.settings.options['cis_config_strict'] = config.getoption("--cis_config_strict")
    Utils.settings.options['elasticsearch'] = config.getoption("--elasticsearch")
    Utils.settings.options['credman_user'] = config.getoption("--credman_user")
    Utils.settings.options['credman_pass'] = config.getoption("--credman_pass")
    Utils.settings.options['credman_url'] = config.getoption("--credman_url")
    Utils.settings.options['creadman_tenantid'] = config.getoption("--credman_tenantid")
    Utils.settings.options['credman_disable'] = config.getoption("--credman_disable")
    Utils.settings.options['selenium_config_node'] = config.getoption("--selenium_config_node")
    Utils.settings.options['selenium_config_file'] = config.getoption("--selenium_config_file")
    Utils.settings.options['selenium_config_strict'] = config.getoption("--selenium_config_strict")
    Utils.settings.options['pdst_pods_node'] = config.getoption("--pdst_pods_node")
    Utils.settings.options['pdst_files_node'] = config.getoption("--pdst_files_node")
    Utils.settings.options['pdst_config_file'] = config.getoption("--pdst_config_file")
    Utils.settings.options['pdst_deploy_release'] = config.getoption("--pdst_deploy_release")
    Utils.settings.options['css_site'] = config.getoption("--css_site")
    Utils.settings.options['css_machine'] = config.getoption("--css_machine")
    Utils.settings.options['css_machine_file'] = config.getoption("--css_machine_file")
    Utils.settings.options['css_release'] = config.getoption("--css_release")
    Utils.settings.options['css_ptag'] = config.getoption("--css_ptag")
    Utils.settings.options['css_client_os_tag'] = config.getoption("--css_client_os_tag")
    Utils.settings.options['css_repo_os_tag'] = config.getoption("--css_repo_os_tag")
    Utils.settings.options['css_testee_os_tag'] = config.getoption("--css_testee_os_tag")
    Utils.settings.options['headless'] = config.getoption("--headless")
    Utils.settings.options['css_client_machine_file'] = config.getoption("--css_client_machine_file")
    Utils.settings.options['css_repo_machine_file'] = config.getoption("--css_repo_machine_file")

@pytest.fixture(scope="session")
def elasticsearch_run_data(request):
    if request.config.option.elasticsearch:
        # Try get P4 user
        p4_user = "unknown"
        try:
            p4_user_process = subprocess.Popen(['p4', 'info', '-s'], stdout=subprocess.PIPE, universal_newlines=True)
            p4_user_output = p4_user_process.stdout.read()
            lines = p4_user_output.split("\n")
            for line in lines:
                if line.find("User name:") != -1:
                    p4_user = line.split(" ")[-1]
                    break
        except Exception as ex:
            logging.getLogger(__name__).debug(f'Exception getting P4 user of type {ex.__class__.__name__}: {ex}.')

        # TODO: If applicable, add CallerURL, Environment, Interval, Team
        es_state = {
            '@timestamp': datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S%z"),
            'Hostname': socket.gethostname(),
            'RunId': str(uuid.uuid4()),
            'P4User': p4_user,
            'NumPassed': 0,
            'NumFailed': 0,
            'NumSkipped': 0,
            'NumXpassed': 0,
            'NumXfailed': 0
        }

        run_start_time = datetime.utcnow()
    else:
        es_state = {}

    yield es_state

    # After all tests
    if request.config.option.elasticsearch:
        run_end_time = datetime.utcnow()
        difference = math.floor((run_end_time - run_start_time).total_seconds())
        es_state['Duration'] = difference
        Elasticsearch.upload_es_data(Elasticsearch.DEVSTATS, Elasticsearch.PYTEST_RUNS, es_state)


@pytest.fixture(scope="session", autouse=True)
def es_data_initializer(elasticsearch_run_data):
    """
    This exists solely to allow indirect usage of the elasticsearch_run_data fixture. It is not possible to use it in
     pytest_runtest_makereport, which requires a fixed function name and signature.
    :param elasticsearch_run_data: fixture with information for the current test run
    :return:
    """
    global _session_es_info
    _session_es_info = elasticsearch_run_data


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    global _session_es_info

    outcome = yield
    if not Utils.settings.options['elasticsearch']:
        return

    rep = outcome.get_result()
    setattr(item, rep.when + '_result', rep)
    if rep.when in ['setup', 'call']:
        setattr(rep, 'time', datetime.now(timezone.utc))
    if rep.when == 'setup' and rep.outcome == 'skipped':
        #  report_to_elasticsearch is not called in this case.
        es_data = ElasticsearchRequestData.get_single_test_data(_session_es_info, str(item.fspath), item)
        Elasticsearch.upload_es_data(Elasticsearch.DEVSTATS, Elasticsearch.PYTEST_RESULTS, es_data)
        _session_es_info['NumSkipped'] += 1


@pytest.fixture(autouse=True)
def report_to_elasticsearch(request, elasticsearch_run_data):
    yield

    if request.config.option.elasticsearch:
        this_test_result = ElasticsearchRequestData.get_single_test_data(elasticsearch_run_data, str(request.fspath), request.node)
        Elasticsearch.upload_es_data(Elasticsearch.DEVSTATS, Elasticsearch.PYTEST_RESULTS, this_test_result)
        elasticsearch_run_data['Num' + this_test_result['Result']] += 1


