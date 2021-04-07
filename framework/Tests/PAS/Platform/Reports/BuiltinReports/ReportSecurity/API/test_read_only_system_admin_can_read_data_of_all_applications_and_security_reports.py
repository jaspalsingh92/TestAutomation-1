import pytest
import logging
from _datetime import datetime
from Shared.API.reports import ReportsManager

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas_failed
@pytest.mark.bhavna
def test_read_only_system_admin_can_read_data_of_all_applications_and_security_reports(core_session, get_environment,
                                                                                       users_and_roles):
    """
    TC: C6320 - Read only system admin can read data of all Applications and Security reports

    :param core_session: Authenticated Centrify session.
    :param users_and_roles: Allows users, roles and session creation on PAS.
    """
    # Creating session for "Read Only System Administration" user.
    user_session = users_and_roles.get_session_for_user("Read Only System Administration")
    date_param = datetime.now()
    # Get created role Id and role name.
    role = users_and_roles.get_role('Read Only System Administration')

    Engines = get_environment
    if Engines == "AWS - PLV8":
        application_report_path = ReportsManager.get_folder_path("Applications")
        security_report_path = ReportsManager.get_folder_path("Security")
    else:
        application_report_path = '/lib/reports/applications'
        security_report_path = "/lib/reports/security"

    # Fetching Directory contents of "Applications" reports.
    application_reports_contents = ReportsManager.get_directory_contents(user_session, application_report_path)
    for app_reports in application_reports_contents['Result']:
        report_result, report_success = ReportsManager.get_report_info(user_session, app_reports['Path'])
        if report_success is False:
            report_result, report_success = ReportsManager.get_reports_info_with_js(core_session, app_reports['Path'],
                                                                                    role['ID'], role['Name'],
                                                                                    start_date=date_param)
            assert report_success, f"Unable to read report: {app_reports['Name']}, API response result: {report_result}"
            logger.info(f"Read Only System Administrator was successfully able to read report '{app_reports['Name']}' "
                        f"from '{application_report_path}'")
        else:
            logger.info(f"Read Only System Administrator was successfully able to read report '{app_reports['Name']}' "
                        f"from '{application_report_path}'")

    # Fetching Directory contents of "Security" reports.
    security_reports_contents = ReportsManager.get_directory_contents(user_session, security_report_path)
    for security_reports in security_reports_contents['Result']:
        report_result, report_success = ReportsManager.get_report_info(user_session, security_reports['Path'])
        if report_success is False:
            report_result, report_success = ReportsManager.get_reports_info_with_js(core_session,
                                                                                    security_reports['Path'],
                                                                                    role['ID'], role['Name'],
                                                                                    start_date=date_param)
            assert report_success, f"Unable to read report: {security_reports['Name']}, API response result:" \
                                   f" {report_result}"
            logger.info(f"Read Only System Administrator was successfully able to read report "
                        f"'{security_reports['Name']}' from '{security_report_path}'")
        else:
            logger.info(f"Read Only System Administrator was successfully able to read report "
                        f"'{security_reports['Name']}' from '{security_report_path}'")
