# css_options.py

import pytest
import os

import Utils.settings


@pytest.fixture(scope='session')
def css_test_release(pytestconfig):
    """
    Provide the selected CSS package release.
    """
    release = pytestconfig.getoption("--css_release")
    if release not in [
        "18.11",
        "19.6",
        "19.9",
        "2020",
        "2020.1",
        "2021"
    ]:
        raise ValueError("Unknown release: " + release)
    return release


@pytest.fixture(scope='session')
def css_test_ptag(pytestconfig):
    """
    Provide the selected CSS package tag.

    The term "package tag" is one of the elements in the package file name.
    It provides the information about what platform, version and architecture
    the package is for. For example, this package (bundle) file:
       centrify-infrastructure-services-2020-rhel5-x86_64.tgz
   
    The package tag is "rhel5-x86_64", which means the package is for:
       "rhel"   : Red Hat Enterprise Linux
       "5"      : version 5 or above
       "x86_64" : x86_64 architecture

    This fixture reads the ptag option from command line and provides the
    breakdown of the package tag: os, version and architecture.

    """
    ptag = pytestconfig.getoption("--css_ptag")
    os = ver = arch = None
    os_ver = ptag
    if "-" in ptag:
        os_ver, arch = ptag.split("-",  1)
    oses = [
        "aix",
        "coreos",
        "deb",
        "hp",
        "rhel",
        "sol",
        "suse",
        # TBD: Testing Windows package is another story
        "win",
    ]
    for i in oses:
        if os_ver.startswith(i):
            os = i
            ver = os_ver[len(i):]
            break
    if not os:
        raise ValueError("Unknown ptag: " + ptag)        
    if not arch:
        if os in ["rhel", "suse", "deb", "coreos"]:
            arch = "x86_64"
        elif os == "sol":
            arch = "x86"
        elif os == "hp":
            arch = "ia64"
    return os, ver, arch


@pytest.fixture(scope='session')
def css_test_env_info(pytestconfig, request):
    """
    Provide the test env file info.

    The env file is Config\environment\CSS\<site_name>\<env_name>.yaml

    If using "terraform", the env is a directory Fixtures\CSS\terraform\<env_name>
    """
    #
    # Note that this fixture requires the environment name to work,
    # and this is passed as a param that provided by the test.
    # For example, the test (or tests in the same module or package)
    # requires the environment named env_SCA2, we can have this codelet
    # in the test source file to provide the environment name:
    #
    # def pytest_generate_tests(metafunc):
    #     if "css_test_env_info" in metafunc.fixturenames:
    #         metafunc.parametrize("css_test_env_info", ["env_SCA2"],
    #                              indirect=True)
    #
    env = {}
    name = pytestconfig.getoption("--css_site")
    dir = os.path.join("Config", "environment", "CSS", name)
    tdir = os.path.join("Fixtures", "CSS", "terraform")
    file = f"{request.param}.yaml"
    env['site'] = name
    env['name'] = request.param
    env['dir'] = dir
    env['tdir'] = tdir
    env['file'] = file
    if name != "terraform":
        if not os.path.exists(os.path.join(dir, file)):
            raise Exception(f"Cannot find env file {file} in {dir}")
    else:
        if not os.path.isdir(os.path.join(tdir, request.param)):
            raise Exception(f"Cannot find env terraform dir {request.param} in {tdir}")
    return env


def get_os_ver_from_os_tag(os_tag):
    """
    Get the OS, version and architecture from the OS tag.

    The OS tag is from the command line option and it is used to select the
    machine. Currently, those options will be used to test Windows package
    only and therefore only Windows is recognized.

    """
    os = ver = arch = None
    os_ver = os_tag
    if "-" in os_tag:
        os_ver, arch = os_tag.split("-", 1)
    oses = [
        "win"
    ]
    for i in oses:
        if os_ver.startswith(i):
            os = i
            ver = os_ver[len(i):]
            break
    if not os:
        raise ValueError("Unknown OS tag: " + ptag)
    if not arch:
        if os in ["win"]:
            arch = "x86_64"
    return os, ver, arch


@pytest.fixture(scope='session')
def css_testee_os_tag(pytestconfig):
    """
    Provide the selected CSS package platform tag.
    """
    ptag = pytestconfig.getoption("--css_testee_os_tag")
    return get_os_ver_from_os_tag(ptag)


@pytest.fixture(scope='session')
def css_client_os_tag(pytestconfig):
    """
       Provide the selected os tag for client machine.
       """
    os_tag = pytestconfig.getoption("--css_client_os_tag")
    return get_os_ver_from_os_tag(os_tag)


@pytest.fixture(scope='session')
def css_repo_os_tag(pytestconfig):
    """
       Provide the selected CSS package platform tag.
       """
    os_tag = pytestconfig.getoption("--css_repo_os_tag")
    return get_os_ver_from_os_tag(os_tag)


def get_mapped_os(os, ver, arch):
    key = f"{os}-{arch}-{ver}"

    # currently only windows machine os have been added, more machines will be added
    machines = {
        'win-x86_64-2012r2': "win2012r2",
        'win-x86_64-2016': "win2016",
        'win-x86_64-10': "win10"
    }
    if not key in machines.keys():
        return None
    return machines[key]


@pytest.fixture(scope='session')
def css_mapped_machine(css_test_ptag):
    """
    Provide the test machine name by mapping the ptag.
    """
    os, ver, arch = css_test_ptag
    key = f"{os}-{arch}"
    machines = {
        'rhel-x86_64':  "rhel8",
        'suse-x86_64':  "sles15",
        'deb-x86_64':   "deb10",
        'sol-x86':      "sol11",
        "hp-ia64":      "hp",
        'win-':         "win2012r2",
    }
    if not key in machines.keys():
        return None
    return machines[key]


@pytest.fixture(scope='session')
def css_testee_mapped_os_machine(css_testee_os_tag):
    """
    Provide the test machine name by mapping the ptag.
    """
    os, ver, arch = css_testee_os_tag
    return get_mapped_os(os, ver, arch)


@pytest.fixture(scope='session')
def css_repo_mapped_os_machine(css_repo_os_tag):
    """
       Provide the test machine name by mapping the repo ptag.
       """
    os, ver, arch = css_repo_os_tag
    return get_mapped_os(os, ver, arch)


@pytest.fixture(scope='session')
def css_client_mapped_os_machine(css_client_os_tag):
    """
       Provide the test machine name by mapping the client ptag.
       """
    os, ver, arch = css_client_os_tag
    return get_mapped_os(os, ver, arch)


def get_machine_info(machine_file, env_info, mapped_machine, file_type):
    machine = {'site': ""}

    if machine_file:
        dir = os.path.dirname(machine_file)
        if not dir:
            dir = "."
        file = os.path.basename(machine_file)
        name = os.path.splitext(file)
        if os.path.exists(machine_file):
            machine['name'] = name
            machine['dir'] = dir
            machine['file'] = file
        else:
            raise Exception(f"Cannot find machine file {file} in {dir}")
    else:
        # Auto select in the site of the test environment
        if not mapped_machine:
            raise Exception("No mapped machine for the specified repo ptag")
        name = mapped_machine
        dir = os.path.join(env_info['dir'], file_type)
        file = f"{mapped_machine}.yaml"
        tdir = os.path.join(env_info['tdir'], file_type)
        machine['name'] = name
        machine['dir'] = dir
        machine['file'] = file

    if env_info['site'] != "terraform":
        if not os.path.exists(os.path.join(dir, file)):
            raise Exception(f"Cannot find machine info file {file} in {dir}")
    else:
        if not os.path.isdir(os.path.join(tdir, name)):
            raise Exception(f"Cannot find machine terraform dir {name} in {tdir}")

    machine['site'] = env_info['site']
    machine['tdir'] = tdir

    return machine


@pytest.fixture(scope='session')
def css_repo_test_machine_info(pytestconfig, css_test_env_info, css_repo_mapped_os_machine):
    """
    gets the repository test machine details
    """
    repo_machine_file = pytestconfig.getoption("--css_repo_machine_file")
    return get_machine_info(repo_machine_file, css_test_env_info, css_repo_mapped_os_machine, "repo_machines")


@pytest.fixture(scope='session')
def css_client_test_machine_info(pytestconfig, css_test_env_info, css_client_mapped_os_machine):
    """
        gets the client test machine details
    """
    client_machine_file = pytestconfig.getoption("--css_client_machine_file")
    return get_machine_info(client_machine_file, css_test_env_info, css_client_mapped_os_machine, "client_machines")


@pytest.fixture(scope='session')
def css_testee_machine_info(pytestconfig, css_test_env_info, css_testee_mapped_os_machine):
    """
    Provide the testee machine file info.

    The machine file is Config\environment\CSS\bhavna\testvm\machines\<machine_name>.yaml

    If not specified, auto select in test site with ptag mapping, that is
    the <site_name>\machines\<mapped_machine>.yaml
    """
    machine_file = pytestconfig.getoption("--css_machine_file")
    return get_machine_info(machine_file, css_test_env_info, css_testee_mapped_os_machine, "machines")


@pytest.fixture(scope='session')
def css_test_machine_info(pytestconfig, css_test_env_info, css_mapped_machine):
    """
    Provide the test machine file info.

    The machine file is Config\fixures\CSS\machines\<machine_name>.yaml

    If not specified, auto select in test site with ptag mapping, that is
    the <site_name>\machines\<mapped_machine>.yaml
    """
    machine = {}
    machine['site'] = ""
    machine_file = pytestconfig.getoption("--css_machine_file")
    if machine_file:
        dir = os.path.dirname(machine_file)
        if not dir:
            dir = "."
        file = os.path.basename(machine_file)
        name = os.path.splitext(file)
        if os.path.exists(machine_file):
            machine['name'] = name
            machine['dir'] = dir
            machine['file'] = file
        else:
            raise Exception(f"Cannot find machine file {file} in {dir}")
    else:
        name = pytestconfig.getoption("--css_machine")
        if name:
            dir = os.path.join("Config", "fixtures", "CSS", "machines")
            file = f"{name}.yaml"
            if os.path.exists(os.path.join(dir, file)):
                machine['name'] = name
                machine['dir'] = dir
                machine['file'] = file
            else:
                raise Exception(f"Cannot find machine file {file} in {dir}")
        else:
            # Auto select in the site of the test environment
            if not css_mapped_machine:
                raise Exception("No mapped machine for the specified ptag")
            name = css_mapped_machine
            env = css_test_env_info['name']
            dir = os.path.join(css_test_env_info['dir'], "machines")
            tdir = os.path.join(css_test_env_info['tdir'], "machines")
            file = f"{css_mapped_machine}.yaml"
            machine['site'] = css_test_env_info['site']
            machine['name'] = name
            machine['dir'] = dir
            machine['tdir'] = tdir
            machine['file'] = file
            if css_test_env_info['site'] != "terraform":
                if not os.path.exists(os.path.join(dir, file)):
                    raise Exception(f"Cannot find machine info file {file} in {dir}")
            else:
                if not os.path.isdir(os.path.join(tdir, name)):
                    raise Exception(f"Cannot find machine terraform dir {name} in {tdir}")
    return machine
