# ad_fixtures.py
#
# Provide AD objects per package.
#

import pytest
import logging


logger = logging.getLogger('framework')


###### AD fixtures ######

@pytest.fixture(scope='package')
def ou_created(css_test_env, css_login_as_admin):
    """
    Generate the OU name from user ID in the test env, then create and
    return the OU
    """
    ou_name = f"ou_{css_test_env['user_id']}"
    ou_dn = f"ou={ou_name},{css_test_env['domain_dn']}"
    # Check if the OU already exists
    rc, result, error = \
        css_login_as_admin.send_command("powershell.exe -command Get-ADOrganizationalUnit -Identity '%s'" % ou_dn)
    if rc != 0:
        rc, result, error = \
          css_login_as_admin.send_command("powershell.exe -command New-ADOrganizationalUnit -Name '%s'" % ou_name)
        if rc != 0:
            raise Exception("Creating OU %s via winrm returned error code %s. "
                            "Error message from winrm: %s" % (ou_name, rc, error))
    yield ou_dn


@pytest.fixture(scope='package')
def gpo_created(css_test_env, css_login_as_admin):
    """
    Generate the GPO name from user ID in the test env, then create and
    return the GPO
    """
    gpo_name = f"gpo_{css_test_env['user_id']}"
    # Check if the GPO already exists, if exits, remove it first
    rc, result, error = \
        css_login_as_admin.send_command("powershell.exe -command Get-GPO -Name '%s'" % gpo_name)
    if rc == 0:
        css_login_as_admin.send_command("powershell.exe -command Remove-GPO -Name '%s'" % gpo_name)
    # Creating the GPO
    rc, result, error = \
        css_login_as_admin.send_command("powershell.exe -command New-GPO -Name '%s'" % gpo_name)
    if rc != 0:
        raise Exception("Creating GPO %s via winrm returned error code %s. "
                        "Error message from winrm: %s" % (gpo_name, rc, error))
    yield gpo_name
    # Remove GPO?

    
@pytest.fixture(scope='package')
def gpo_linked(css_login_as_admin, ou_created, gpo_created):
    """
    Provide the GPO that linked to the joined OU
    """
    ou_dn = ou_created 
    gpo_name = gpo_created 
    # Linking GPO to OU
    rc, result, error = \
        css_login_as_admin.send_command("powershell.exe -command New-GPLink -Name '%s' -Target '%s'" %
                                        (gpo_name, ou_dn))
    if rc != 0:
        raise Exception("Linking GPO %s to OU %s via winrm returned error code %s. "
                        "Error message from winrm: %s" % (gpo_name, ou_dn, rc, error))
    dict = {}
    dict['ou_dn'] = ou_dn
    dict['gpo_name'] = gpo_name
    yield dict
    # Unlink GPO?

