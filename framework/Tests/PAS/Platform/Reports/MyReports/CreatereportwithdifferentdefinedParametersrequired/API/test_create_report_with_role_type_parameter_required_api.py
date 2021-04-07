import pytest
from PopulateSplitTenant.Platform.Utils.populate_util import pop_prefix_base
from Shared.API.redrock import RedrockController
from Shared.reports import Reports
import logging

logger = logging.getLogger("test")


@pytest.mark.bhavna
@pytest.mark.api
@pytest.mark.pas_broken
def test_role_type_parameter(core_session, created_role, get_environment, cleanup_reports):
    """
    TCID: C6342 Create report with Role type parameter required
    :param core_session: Centrify Authentication Session
    :param created_role: To create the role
    :param core_admin_ui: To open the browser
    :param cleanup_reports: To delete the created report
    """
    role = created_role

    reports = Reports(core_session, pop_prefix_base)
    report = reports.create_report(
        {"Name": "report_A",
         "Query": "select name  from Role where Name= @roleNM",
         "Parameters": [
             {"Type": "Role", "Name": "roleNM",
              "Label": "Input searched role name", "ObjectProperty": "Name"}
         ]
         })
    assert report, f'Failed to create the report:{report}'
    logger.info(f'Successfully Created report: {report}')

    args = {"PageNumber": 1, "PageSize": 100, "Limit": 100000, "SortBy": "", "direction": "False", "Caching": -1,
            "Parameters": [{"Name": "roleNM", "Value": f"{role['Name']}", "Label": "Input searched role name",
                            "Type": "Role", "ColumnType": 12}]}

    # Fetch all role and assign to specific report.
    query = "select name  from Role where Name= @roleNM"
    result = RedrockController.redrock_query(core_session, query, args=args)
    Engines = get_environment
    if Engines == "AWS - PLV8":
        for i in result:
            if i['Row']['Name'] == role['Name']:
                logger.info(f'Successfully added the role under report: {report}')
        else:
            logger.info(f'unable to added the role under report: {report}')
    else:
        for i in result:
            if i['Row']['name'] == role['Name']:
                logger.info(f'Successfully added the role under report: {report}')
        else:
            logger.info(f'unable to added the role under report: {report}')

    # API to find the report and delete it
    found_report = reports.get_report_by_name(core_session, report['Name'] + ".report")
    cleanup_reports.append(found_report['Path'])
