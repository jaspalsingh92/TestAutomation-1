import pytest
from PopulateSplitTenant.Platform.Utils.populate_util import pop_prefix_base
from Shared.API.redrock import RedrockController
from Shared.API.users import UserManager
from Shared.reports import Reports
from Utils.guid import guid
from Utils.config_loader import Configs
import logging

logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.bhavna
@pytest.mark.pas
@pytest.mark.pasapi
def test_user_type_parameter(core_session, cleanup_accounts, cleanup_reports):
    """
    TCID: C6341 Create report with User type parameter required
    :param core_session: Centrify Authentication session
    """
    user_list = cleanup_accounts[2]
    session_user = core_session.__dict__
    display_name_1 = session_user['auth_details']['DisplayName']
    user_create_data = Configs.get_test_node('platform_report_data', 'automation_main')
    prefix = user_create_data['prefix']
    user_alias = core_session.auth_details['User'].split('@')[1]

    user_name_2 = prefix + guid() + "@" + user_alias
    user_props = {
        "Mail": user_create_data['user_email'],
        "Password": user_create_data['password'],
        "PasswordNeverExpire": True,
        "DisplayName": user_create_data['display_name'],
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
         "Query": "select Username, LastLogin from user where DisplayName= @userNM",
         "Parameters": [
             {"Type": "User", "Name": "userNM", "Label": "Input searched username", "ObjectProperty": "DisplayName"}
         ]
         })
    assert report, f'Failed to create the report:{report}'
    logger.info(f'Successfully Created report: {report}')

    # Actual result for all user list with display name same as session user display name.
    # and this details will compare all the user from reports page
    actual_script_1 = f'Select Username, LastLogin from user where DisplayName = "{display_name_1}"'
    actual_user_list_1 = []
    actual_result_1 = RedrockController.redrock_query(core_session, actual_script_1)
    for user in actual_result_1:
        actual_user_list_1.append(user['Row'])

    # Expected result for all users which user name same as session user display name and will assert the list
    # of users of actual session user display name list
    expected_result_1 = RedrockController.get_report_result_list_of_user(core_session,
                                                                         "userNM", display_name_1, "Input searched username")
    expected_user_list_1 = []
    for expected_result in expected_result_1:
        expected_user_list_1.append(expected_result['Row'])
    assert expected_user_list_1 == actual_user_list_1, f'The report result list all users whose DisplayName is not ' \
                                                       f'same with selected users DisplayName:{actual_user_list_1}'
    logger.info(f'The report result list all users whose DisplayName is '
                f'same with selected users displayname:{expected_user_list_1}')

    # Actual result for all user list with display name same as another user display name.
    # and this details will compare all the user from reports page
    actual_script_2 = f'Select Username, LastLogin from user where DisplayName = "{user_create_data["display_name"]}"'
    actual_user_list_2 = []
    actual_result_2 = RedrockController.redrock_query(core_session, actual_script_2)
    for user in actual_result_2:
        actual_user_list_2.append(user['Row'])

    # Expected result for all users which user name same as another user display name and will assert the list
    # of users of actual another user display name list
    expected_result_2 = RedrockController.get_report_result_list_of_user(core_session,
                                                                         "userNM", user_create_data['display_name'],
                                                                         "Input searched username")
    expected_user_list_2 = []
    for user in expected_result_2:
        expected_user_list_2.append(user['Row'])
    assert expected_user_list_2 == actual_user_list_2, f'The report result list all users whose DisplayName is not ' \
                                                       f'same with selected users DisplayName:{actual_user_list_2}'
    logger.info(f'The report result list all users whose DisplayName is '
                f'same with selected users displayname:{expected_user_list_2}')

    # Delete the created user
    user_list.append(result_user_2)
    found_report = reports.get_report_by_name(core_session,
                                              report['Name'] + ".report")
    cleanup_reports.append(found_report['Path'])
