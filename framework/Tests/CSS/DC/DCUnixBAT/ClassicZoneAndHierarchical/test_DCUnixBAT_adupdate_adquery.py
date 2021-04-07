"""This module is intended to automate the test cases depending on adupdate & adquery functionality"""

import pytest
import hashlib
import time

from .common import *


###### Test constants ######

CONTAINER = "Users"
WAIT_AFTER_ADUPDATE = 5


###### Test helper functions ######

def get_adquery_attributes(content):
    logger.debug("Parsing adquery output to get the attributes")
    dict = {}
    for line in content.splitlines():
        x = re.search(r"^\s*(\w+)\s*:\s*(.*)$", line)
        if x:
            tuple = x.group(1, 2)
            logger.debug("Read %s = %s" % (tuple[0], tuple[1]))
            dict[tuple[0]] = tuple[1]
    return dict


def remove_ad_group(ssh, adupdate, group, env):
    cmd = f"{adupdate} delete group {group['samAccountName']} -p {env['admin_password']} -r"
    rc, result, error = ssh.send_command(cmd)
    content = ssh.to_string(result)
    logger.debug(content)


def remove_ad_user(ssh, adupdate, user, env):
    cmd = f"{adupdate} delete user {user['samAccountName']} -p {env['admin_password']} -r"
    rc, result, error = ssh.send_command(cmd)
    content = ssh.to_string(result)
    logger.debug(content)


###### Test cases ######

@pytest.fixture(scope='module', autouse=True)
def module_cleanup(login_as_root, adupdate, ad_group, ad_user, css_test_env):
    yield
    remove_ad_user(login_as_root, adupdate, ad_user, css_test_env)
    remove_ad_group(login_as_root, adupdate, ad_group, css_test_env)


@pytest.fixture(scope='module')
def user_unix_id(css_test_env):
    """
    Provide 7-digit unique ID (a hash) base on user_id
    """
    b = bytearray()
    b.extend(map(ord, css_test_env['user_id']))
    id = int(hashlib.sha1(b).hexdigest(), 16) % (10 ** 7)
    yield id


@pytest.fixture(scope='module')
def ad_group(user_unix_id):
    dict = {}
    dict['gid'] = str(user_unix_id)
    dict['unixname'] = f"lg{user_unix_id}"
    dict['samAccountName'] = f"lg{user_unix_id}"
    yield dict


@pytest.fixture(scope='module')
def ad_user(user_unix_id):
    dict = {}
    dict['uid'] = str(user_unix_id)
    dict['unixname'] = f"lu{user_unix_id}"
    dict['samAccountName'] = f"lu{user_unix_id}"
    yield dict


@pytest.fixture
def adupdate_add_ad_group(adupdate, ad_group, css_test_env):
    # Example:
    #   /usr/bin/adupdate add group --group/-G lg1103221 --create/-C
    #     --container/-c 5f1r1c1.a5f1r1.test/Users --gid/-g 1103221
    #     --password/-p Lastd\!y8 lg1103221
    cmd = f"{adupdate} add group -G {ad_group['samAccountName']} -C "\
      f"-c {css_test_env['domain_name']}/{CONTAINER} "\
      f"-g {ad_group['gid']} "\
      f"-p {css_test_env['admin_password']} "\
      f"{ad_group['unixname']}"
    yield cmd


@pytest.fixture
def ad_group_removed(ad_user_removed, login_as_root, adupdate, adquery, ad_group, css_test_env):
    remove_ad_group(login_as_root, adupdate, ad_group, css_test_env)
    cmd = f"{adquery} group {ad_group['samAccountName']}"
    rc, result, error = login_as_root.send_command(cmd)
    content = login_as_root.to_string(result)
    logger.debug(content)
    if rc != 53: # ERR_NOT_FOUND_ZONE_GROUP
        raise Exception("Cannot remove AD group {ad_group['samAccountName']}")
    yield


@pytest.fixture
def ad_group_added_as_ad_user(ad_group_removed, login_as_ad_user, adupdate_add_ad_group, ad_group):
    cmd = adupdate_add_ad_group
    rc, result, error = login_as_ad_user.send_command(cmd)
    content = login_as_ad_user.to_string(result)
    logger.debug(content)
    if rc != 0:
        raise Exception(f"Cannot add AD group {ad_group['samAccountName']}")
    yield


@pytest.fixture
def adupdate_add_ad_user(adupdate, ad_group, ad_user, css_test_env):
    # Example:
    #   /usr/bin/adupdate add user --user/-U lu1103221 --create/-C
    #     --container/-c 5f1r1c1.a5f1r1.test/Users --uid/-u 1103221
    #     --new-password/-w password --group/-g lg1103221
    #     --password/-p Lastd\!y8 lu1103221
    cmd = f"{adupdate} add user -U {ad_user['samAccountName']} -C "\
      f"-c {css_test_env['domain_name']}/{CONTAINER} "\
      f"-u {ad_user['uid']} "\
      f"-w password -g {ad_group['unixname']} "\
      f"-p {css_test_env['admin_password']} "\
      f"{ad_user['unixname']}"
    yield cmd


@pytest.fixture
def ad_user_removed(login_as_root, adupdate, adquery, ad_user, css_test_env):
    remove_ad_user(login_as_root, adupdate, ad_user, css_test_env)
    cmd = f"{adquery} user {ad_user['samAccountName']}"
    rc, result, error = login_as_root.send_command(cmd)
    content = login_as_root.to_string(result)
    logger.debug(content)
    if rc != 52: # ERR_NOT_FOUND_ZONE_USER
        raise Exception("Cannot remove AD user {ad_user['samAccountName']}")
    yield


@pytest.fixture
def ad_user_added_as_ad_user(ad_group_added_as_ad_user, login_as_ad_user, adupdate_add_ad_user, ad_user):
    cmd = adupdate_add_ad_user
    rc, result, error = login_as_ad_user.send_command(cmd)
    content = login_as_ad_user.to_string(result)
    logger.debug(content)
    if rc != 0:
        raise Exception(f"Cannot add AD user {ad_user['samAccountName']}")
    yield


###### Test cases ######

### 1. Install CDC

@pytest.mark.bhavna
@pytest.mark.css_underconstruction
@pytest.mark.dc_unix_bat
def test_1_install_cdc_check_adupdate_adquery_via_root\
  (dc_is_installed, login_as_root, adquery, adupdate, dc_version):
    """
    Check adupdate and adquery version via root
    """
    logger.info("--- Case C1267494")
    logger.info("--- Step 1")
    cmd = adquery
    for option in ["--version", "-v"]:
        check_version_or_assert(cmd, option, dc_version, login_as_root)
    logger.info("--- Step 1")
    cmd = adupdate
    for option in ["--version", "-v"]:
        check_version_or_assert(cmd, option, dc_version, login_as_root)


### 2. Join to domain

@pytest.mark.bhavna
@pytest.mark.css_underconstruction
@pytest.mark.dc_unix_bat
@pytest.mark.skip_zone_type("hierarchical")
def test_2_1_as_ad_user_apncu4_login_add_ad_group_both_on_aduc_and_mmc_then_query\
  (dc_is_joined, ad_group_removed, login_as_ad_user, adupdate_add_ad_group, adquery, ad_group, css_test_env):
    """
    Add ad group both on aduc and mmc then query
    """
    logger.info("--- Case C1267495")
    logger.info("--- Step 1")
    cmd = adupdate_add_ad_group
    rc, result, error = login_as_ad_user.send_command(cmd)
    content = login_as_ad_user.to_string(result)
    logger.debug(content)
    log_ok_or_assert(rc == 0,
                     f"'{cmd}' runs successfully",
                     f"'{cmd}' returns error code {rc}, message: {error}")
    time.sleep(WAIT_AFTER_ADUPDATE)
    logger.info("--- Step 2")
    cmd = f"{adquery} group -g -M {ad_group['samAccountName']}"
    rc, result, error = login_as_ad_user.send_command(cmd)
    content = login_as_ad_user.to_string(result)
    logger.debug(content)
    attributes = get_adquery_attributes(content)
    log_ok_or_assert(attributes['gid'] == ad_group['gid'] and
                     attributes['samAccountName'] == ad_group['samAccountName'],
                     f"'{cmd}' returns expected gid {attributes['gid']} and "
                     f"samAccountName {attributes['samAccountName']}",
                     f"'{cmd}' returns unexpected gid {attributes['gid']} and "
                     f"samAccountName {attributes['samAccountName']}")


@pytest.mark.bhavna
@pytest.mark.css_underconstruction
@pytest.mark.dc_unix_bat
@pytest.mark.skip_zone_type("hierarchical")
def test_2_1_as_ad_user_apncu4_login_add_ad_user_both_on_aduc_and_mmc_then_query\
  (dc_is_joined, ad_group_added_as_ad_user, login_as_ad_user,
   adupdate_add_ad_user, adquery, ad_group, ad_user, css_test_env):
    """
    Add ad user both on aduc and mmc (member of above group) then query
    """
    logger.info("--- Case C1267497")
    logger.info("--- Step 1")
    cmd = adupdate_add_ad_user
    rc, result, error = login_as_ad_user.send_command(cmd)
    content = login_as_ad_user.to_string(result)
    logger.debug(content)
    log_ok_or_assert(rc == 0,
                     f"'{cmd}' runs successfully",
                     f"'{cmd}' returns error code {rc}, message: {error}")
    time.sleep(WAIT_AFTER_ADUPDATE)
    logger.info("--- Step 2")
    cmd = f"{adquery} user -u -g -B {ad_user['samAccountName']}"
    rc, result, error = login_as_ad_user.send_command(cmd)
    content = login_as_ad_user.to_string(result)
    logger.debug(content)
    attributes = get_adquery_attributes(content)
    log_ok_or_assert(attributes['uid'] == ad_user['uid'] and
                     attributes['gid'] == ad_group['gid'] and
                     attributes['guid'],
                     f"'{cmd}' returns expected uid {attributes['uid']}, "
                     f"gid {attributes['gid']} and guid {attributes['guid']}",
                     f"'{cmd}' returns unexpected uid {attributes['uid']}, "
                     f"gid {attributes['gid']} or guid {attributes['guid']}")
    logger.info("--- Step 3")
    cmd = f"{adquery} user -A {ad_user['samAccountName']}"
    rc, result, error = login_as_ad_user.send_command(cmd)
    content = login_as_ad_user.to_string(result)
    logger.debug(content)
    attributes = get_adquery_attributes(content)
    user_attr_names = ['unixname', 'uid', 'gid', 'gecos', 'home', 'shell',
                       'auditLevel', 'isAlwaysPermitLogin', 'dn',
                       'samAccountName', 'displayName', 'sid',
                       'userPrincipalName', 'canonicalName', 'passwordHash',
                       'guid', 'requireMfa', 'zoneEnabled', 'unixGroups',
                       'memberOf']
    found_all = True
    for attr in user_attr_names:
        if attr not in attributes:
            found_all = False
    log_ok_or_assert(found_all,
                     f"'{cmd}' returns all expected attributes",
                     f"'{cmd}' cannot return all expected attributes: {attributes}")


@pytest.mark.bhavna
@pytest.mark.css_underconstruction
@pytest.mark.dc_unix_bat
@pytest.mark.skip_zone_type("hierarchical")
def test_2_1_as_ad_user_apncu4_login_modify_ad_group_then_query\
  (dc_is_joined, ad_user_added_as_ad_user, login_as_ad_user,
   adupdate, adquery, ad_group, css_test_env):
    """
    Modify ad group then query
    """
    logger.info("--- Case C1267500")
    logger.info("--- Step 1")
    # Use the last 6-digit as the new gid
    new_gid = ad_group['gid'][-6:]
    # Example:
    #   /usr/bin/adupdate modify group --gid/-g 110356 lg1103221
    #     --password/-p Lastd\!y8
    cmd = f"{adupdate} modify group -g {new_gid} "\
      f"{ad_group['samAccountName']} -p {css_test_env['admin_password']}"
    rc, result, error = login_as_ad_user.send_command(cmd)
    content = login_as_ad_user.to_string(result)
    logger.debug(content)
    time.sleep(WAIT_AFTER_ADUPDATE)
    logger.info("--- Step 2")
    cmd = f"{adquery} group -g {ad_group['samAccountName']}"
    rc, result, error = login_as_ad_user.send_command(cmd)
    content = login_as_ad_user.get_first_line(result)
    logger.debug(content)
    log_ok_or_assert(content == new_gid,
                     f"'{cmd}' returns expected gid {content}",
                     f"'{cmd}' returns unexpected gid {content}")


@pytest.mark.bhavna
@pytest.mark.css_underconstruction
@pytest.mark.dc_unix_bat
@pytest.mark.skip_zone_type("hierarchical")
def test_2_1_as_ad_user_apncu4_login_modify_ad_user_then_query\
  (dc_is_joined, ad_user_added_as_ad_user, login_as_ad_user,
   adupdate, adquery, ad_group, ad_user, css_test_env):
    """
    Modify ad user then query
    """
    logger.info("--- Case C1267502")
    logger.info("--- Step 1")
    # Use the last 6-digit as the new gid
    new_uid = ad_user['uid'][-6:]
    # Example:
    #   /usr/bin/adupdate modify user --uid/-u 110356 lu1103221
    #     --password/-p Lastd\!y8
    cmd = f"{adupdate} modify user -u {new_uid} "\
      f"{ad_user['samAccountName']} -p {css_test_env['admin_password']}"
    rc, result, error = login_as_ad_user.send_command(cmd)
    content = login_as_ad_user.to_string(result)
    logger.debug(content)
    time.sleep(WAIT_AFTER_ADUPDATE)
    logger.info("--- Step 2")
    cmd = f"{adquery} user -u -g -B {ad_user['samAccountName']}"
    rc, result, error = login_as_ad_user.send_command(cmd)
    content = login_as_ad_user.to_string(result)
    logger.debug(content)
    attributes = get_adquery_attributes(content)
    log_ok_or_assert(attributes['uid'] == new_uid and
                     attributes['gid'] == ad_group['gid'] and
                     attributes['guid'],
                     f"'{cmd}' returns expected uid {attributes['uid']}, "
                     f"gid {attributes['gid']} and guid {attributes['guid']}",
                     f"'{cmd}' returns unexpected uid {attributes['uid']}, "
                     f"gid {attributes['gid']} or guid {attributes['guid']}")


@pytest.mark.bhavna
@pytest.mark.css_underconstruction
@pytest.mark.dc_unix_bat
@pytest.mark.skip_zone_type("hierarchical")
def test_2_1_as_ad_user_apncu4_login_delete_ad_group_but_also_exist_on_aduc_then_query\
  (dc_is_joined, ad_user_added_as_ad_user, login_as_ad_user,
   adupdate, adquery, ad_group, css_test_env):
    """
    Delete ad group but also exist on aduc then query
    """
    logger.info("--- Case C1267504")
    logger.info("--- Step 1")
    cmd = f"{adupdate} delete group {ad_group['samAccountName']} "\
      f"-p {css_test_env['admin_password']}"
    rc, result, error = login_as_ad_user.send_command(cmd)
    content = login_as_ad_user.to_string(result)
    logger.debug(content)
    log_ok_or_assert(rc == 0,
                     f"'{cmd}' deletes AD group '{ad_group['samAccountName']}' successfully",
                     f"'{cmd}' returns error code {rc}, message: {error}")
    time.sleep(WAIT_AFTER_ADUPDATE)
    logger.info("--- Step 2")
    cmd = f"{adquery} group {ad_group['samAccountName']}"
    rc, result, error = login_as_ad_user.send_command(cmd)
    content = login_as_ad_user.get_first_line(str(error))
    logger.debug(content)
    log_ok_or_assert(content == f"{ad_group['samAccountName']} is not a zone group",
                     f"'{cmd}' shows error '{content}' as expected",
                     f"'{cmd}' shows error '{content}' and this is unexpected")


@pytest.mark.bhavna
@pytest.mark.css_underconstruction
@pytest.mark.dc_unix_bat
@pytest.mark.skip_zone_type("hierarchical")
def test_2_1_as_ad_user_apncu4_login_delete_ad_user_but_also_exist_on_aduc_then_query\
  (dc_is_joined, ad_user_added_as_ad_user, login_as_ad_user,
   adupdate, adquery, ad_user, css_test_env):
    """
    Modify ad user then query
    """
    logger.info("--- Case C1267506")
    logger.info("--- Step 1")
    cmd = f"{adupdate} delete user -R {ad_user['samAccountName']} "\
          f"--password {css_test_env['admin_password']}"
    rc, result, error = login_as_ad_user.send_command(cmd)
    content = login_as_ad_user.to_string(result)
    logger.debug(content)
    log_ok_or_assert(rc == 0,
                     f"'{cmd}' deletes AD user '{ad_user['samAccountName']}' successfully",
                     f"'{cmd}' returns error code {rc}, message: {error}")
    time.sleep(WAIT_AFTER_ADUPDATE)
    logger.info("--- Step 2")
    cmd = f"{adquery} user {ad_user['samAccountName']}"
    rc, result, error = login_as_ad_user.send_command(cmd)
    content = login_as_ad_user.get_first_line(str(error))
    logger.debug(content)
    log_ok_or_assert(content == f"{ad_user['samAccountName']} is not a zone user",
                     f"'{cmd}' shows error '{content}' as expected",
                     f"'{cmd}' shows error '{content}' and this is unexpected")

