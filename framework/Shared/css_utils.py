# css_utils.py

import re
import logging

from Utils.ssh_util import SshUtil


logger = logging.getLogger('framework')
test_logger = logging.getLogger('test')


###### CSS Utilities ######

def log_assert(test, error):
    """
    If test is false, write error message to log and assert.

    :param test: Some sort of test
    :param error: Error message to show if test is false
    """
    if not test:
        logger.info("ASSERT %s" % error)
        test_logger.info("ASSERT %s" % error)
        assert test, error


def log_ok_or_assert(test, ok, error):
    """
    If test is true, write OK message to log. Otherwise, write error
    message to log and assert.

    :param test: Some sort of test
    :param ok: OK message to show if test is true
    :param error: Error message to show if test is false
    """
    if test:
        logger.info(ok)
        test_logger.info(ok)
    else:
        logger.info("ASSERT %s" % error)
        test_logger.info("ASSERT %s" % error)
        assert test, error


def get_version(content):
    """
    Get the version number from the content.

    :param content: Content
    :return: Version string if found, None otherwise.
    """
    x = re.search(r"\b(\d\.\d.\d-\d\d\d)\b", content)
    if x:
        version = x.group(1)
        logger.debug("version = %s" % version)
        return version
    else:
        return None


def get_basename(cmd):
    """
    Get the basename of a command.

    :param content: Content
    :return: The basename of the command
    """
    basename = cmd.rsplit(" ", 1)[-1]
    basename = basename.rsplit("/", 1)[-1]
    return basename


def check_substring(content, substring, ignorecase=False):
    """
    Check if the substring exist in the content.

    :param content: The content to be checked
    :param substring: Substring 
    :param ignorecase: Specify whether the checking should ignore case
    :return: True if all substrings are in the content
    """
    flags = re.MULTILINE
    if ignorecase:
        flags |= re.IGNORECASE
    x = re.search(re.escape(substring), content, flags)
    return x


def check_keyword(content, keyword, ignorecase=False):
    """
    Check if the keyword exist in the content.

    :param content: The content to be checked
    :param keyword: Keyword
    :param ignorecase: Specify whether the checking should ignore case
    :return: True if line is found
    """
    flags = re.MULTILINE
    if ignorecase:
        flags |= re.IGNORECASE
    x = re.search(r"\b" + re.escape(keyword) + r"\b", content, flags)
    return x


def check_line(content, line, ignorecase=False):
    """
    Check if all substrings exist in the content.

    :param content: The content to be checked
    :param line: Line
    :param ignorecase: Specify whether the checking should ignore case
    :return: True if line is found
    """
    flags = re.MULTILINE
    if ignorecase:
        flags |= re.IGNORECASE
    x = re.search(r"^" + re.escape(line) + r"$", content, flags)
    return x


def check_substrings(content, substrings, ignorecase=False):
    """
    Check if all substrings exist in the content.

    :param content: The content to be checked
    :param substrings: Substrings
    :param ignorecase: Specify whether the checking should ignore case
    :return: True if all substrings are in the content
    """
    found_all = True
    flags = re.MULTILINE
    if ignorecase:
        flags |= re.IGNORECASE
    for substring in substrings:
        x = re.search(re.escape(substring), content, flags)
        if not x:
            found_all = False
            break
    return found_all


def check_no_substrings(content, keywords, ignorecase=False):
    """
    Check if all substrings do not exist in the content.

    :param content: The content to be checked
    :param keywords: Keywords
    :param ignorecase: Specify whether the checking should ignore case
    :return: True if all keywords are in the content
    """
    found_any = False
    flags = re.MULTILINE
    if ignorecase:
        flags |= re.IGNORECASE
    for keyword in keywords:
        x = re.search(re.escape(keyword), content, flags)
        if x:
            found_any = True
            break
    return not found_any


def check_keywords(content, keywords, ignorecase=False):
    """
    Check if all keywords exist in the content.

    :param content: The content to be checked
    :param keywords: Keywords
    :param ignorecase: Specify whether the checking should ignore case
    :return: True if all keywords are in the content
    """
    found_all = True
    flags = re.MULTILINE
    if ignorecase:
        flags |= re.IGNORECASE
    for keyword in keywords:
        logger.debug(f"checking {keyword}")
        x = re.search(r"\b" + re.escape(keyword) + r"\b", content, flags)
        if not x:
            found_all = False
            break
    return found_all


def check_no_keywords(content, keywords, ignorecase=False):
    """
    Check if all keywords do not exist in the content.

    :param content: The content to be checked
    :param keywords: Keywords
    :param ignorecase: Specify whether the checking should ignore case
    :return: True if all keywords are in the content
    """
    found_any = False
    flags = re.MULTILINE
    if ignorecase:
        flags |= re.IGNORECASE
    for keyword in keywords:
        x = re.search(r"\b" + re.escape(keyword) + r"\b", content, flags)
        if x:
            found_any = True
            break
    return not found_any


def check_man_page_or_assert(cmd, ssh):
    basename = get_basename(cmd)
    rc, result, error = ssh.send_command(f"man {cmd}")
    # If no man page, we will get "No manual" error.
    # In short, we should not get any error at all.
    #In Solaris system in error some output is comming
    #Need to verify using rc == 0 ,as rc is not equal to 0 then "No manual" page in error
    assert rc == 0 ,f"No man page for '{cmd}': {result}"


def check_help_page_or_assert(cmd, helpopt, ssh):
    basename = get_basename(cmd)
    keywords = ["usage", basename]
    logger.debug(basename)
    rc, result, error = ssh.send_command(f"{cmd} {helpopt}")
    content = ssh.to_string(result)
    logger.debug(content)
    log_ok_or_assert(check_keywords(content, keywords, True),
                     f"'{cmd} {helpopt}' shows help page",
                     f"'{cmd} {helpopt}' does not show help page")


def check_version_or_assert(cmd, veropt, dcver, ssh):
    basename = get_basename(cmd)
    rc, result, error = ssh.send_command(f"{cmd} {veropt}")
    content = ssh.to_string(result)
    logger.debug(content)
    version = get_version(content)
    log_ok_or_assert(version == dcver,
                     f"'{cmd} {veropt}' shows correct version {version}",
                     f"'{cmd} {veropt}' shows incorrect version {version}, "
                     f"the expected version is '{dcver}'")


class UserUnixProfile():
    def __init__(self):
        self.username = ''
        self.password = ''
        self.uid = ''
        self.gid = ''
        self.gecos = ''
        self.home_dir = ''
        self.shell = ''

    def load_str(self, s):
        try:
            self.username, self.password, self.uid, self.gid, self.gecos, self.home_dir, self.shell = s.split(':')
        except Exception:
            raise ValueError(f'Failed to split and load passwd string: "{s}"')

    def __repr__(self):
        return ':'.join([
            self.username,
            self.password,
            self.uid,
            self.gid,
            self.gecos,
            self.home_dir,
            self.shell,
            ])

