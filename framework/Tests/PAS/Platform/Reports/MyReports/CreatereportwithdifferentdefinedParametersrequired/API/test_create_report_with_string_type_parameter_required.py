import pytest
from PopulateSplitTenant.Platform.Utils.populate_util\
    import pop_prefix_base, Configs
from Shared.API.redrock import RedrockController
from Shared.API.users import UserManager
from Shared.reports import Reports
from Utils.guid import guid
import logging

logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.bhavna
@pytest.mark.pas
@pytest.mark.pasapi
def test_string_type_parameter(core_session, created_suffix,
                               suffix_cleaner, cleanup_accounts, cleanup_reports):
    """
    TCID: C6340 Create report with String type parameter required
    :param created_suffix: centrify Authentication Session
    :param core_session: Fixture to add the suffix
    :param suffix_cleaner: Fixture to delete the created suffix
    :param cleanup_accounts: Fixture to delete the created user
    :param cleanup_reports: Fixture to delete the created report
    """
    user_list = cleanup_accounts[2]
    user_create_data = Configs.get_test_node('platform_report_data', 'automation_main')
    prefix = user_create_data['prefix']
    user_alias = core_session.auth_details['User'].split('@')[1]

    user_name_1 = prefix + guid() + "@" + user_alias
    user_props = {
        "Mail": user_create_data['user_email'],
        "Password": user_create_data['password'],
        "PasswordNeverExpire": True,
        "Username": user_name_1,
        "Name": user_name_1
    }
    success, result_user_1 = UserManager.create_user_with_args(core_session,
                                                               user_props)
    assert success, f'Failed to create an user:{result_user_1}'
    logger.info(f'Successfully created an user:{result_user_1}')

    suffix_alias = created_suffix
    user_name_2 = prefix + guid() + "@" + suffix_alias['alias']
    user_props = {
        "Mail": user_create_data['user_email'],
        "Password": user_create_data['password'],
        "PasswordNeverExpire": True,
        "Username": user_name_2,
        "Name": user_name_2
    }
    success, result_user_2 = UserManager.create_user_with_args(core_session,
                                                               user_props)
    assert success, f'Failed to create an user:{result_user_2}'
    logger.info(f'Successfully created an user:{result_user_2}')

    reports = Reports(core_session, pop_prefix_base)
    report = reports.create_report(
        {"Name": "report_A",
         "Query": "select Username, "
                  "lastlogin from user where Username like @userNM",
         "Parameters": [
             {"Type": "string", "Name": "userNM",
              "Label": "Input searched username"}
         ]
         })
    assert report, f'Failed to create the report:{report}'
    logger.info(f'Successfully Created report: {report}')

    # All users whose username starts with prefix
    sript_1 = f"select Username, lastlogin from user where Username like '{prefix}%'"
    result_prefix = RedrockController.redrock_query(core_session, sript_1)
    username_with_prefix = []
    for username in result_prefix:
        username_with_prefix.append(username['Row']['Username'])
    for i in username_with_prefix:
        assert i.startswith(prefix), f'The report result user list are not starting with {prefix}'
    logger.info(f'The report result list all users whose Username starts with: {username_with_prefix}')

    # All users whose username ends with suffix
    sript_2 = f"select Username, lastlogin from user where Username like '%{suffix_alias['alias']}'"
    result_suffix = RedrockController.redrock_query(core_session, sript_2)
    username_with_suffix = []
    for username_suffix in result_suffix:
        username_with_suffix.append(username_suffix['Row']['Username'])
    for i in username_with_suffix:
        assert i.endswith(suffix_alias['alias']), f'The report result user list are not ending with:{suffix_alias["alias"]}'
    logger.info(f'The report result list all users whose Username ends with: {username_with_prefix}')

    # Delete created report, user and suffix
    found_report = reports.get_report_by_name(core_session,
                                              report['Name'] + ".report")
    cleanup_reports.append(found_report['Path'])
    user_list.append(result_user_2)
    user_list.append(result_user_1)
    suffix_cleaner.append(suffix_alias['alias'])
