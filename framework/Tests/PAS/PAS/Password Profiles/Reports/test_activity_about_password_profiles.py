import pytest
import logging
from Shared.API.infrastructure import ResourceManager
from Shared.API.reports import ReportsManager

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pas_ui
def test_activity_about_password_profiles(core_session, create_basic_pass_profile):
    """
    Test case: C1665
        :param core_session: Centrify session
        :param create_basic_pass_profile: Created a basic password complexity profile.
    """
    # Creating basic password profile.
    profile = create_basic_pass_profile(core_session, 1, 8)[0]
    cps_prof_id = profile[0]['_RowKey']
    profile_name_cps = profile[0]['Name']
    username = core_session.__dict__["auth_details"]["User"]
    cps_prof_result, cps_prof_succcess = ResourceManager.get_password_profile_by_id(core_session, cps_prof_id)

    # Checking the created custom password complexity profile.
    assert cps_prof_succcess, f"Getting Password Profile Failed for Profile {cps_prof_id} for core user"
    logger.info(f"Password profile created successfully with {cps_prof_result}")
    profile_delete = ResourceManager.delete_password_profile(core_session, cps_prof_id)

    # Deleting the custom password complexity profile.
    assert profile_delete, f"Password complexity profile {profile_name_cps} not deleted"
    logger.info(f"Password complexity profile {profile_name_cps} deleted successfully")
    recent_activity = ResourceManager.get_recent_activity(core_session)

    # Get recent activity details and finding the recent delete activity.
    recent_activity_list = []
    for column in range(len(recent_activity)):
        if recent_activity[column]["Row"]["Detail"].__contains__("deleted password profile"):
            recent_activity_list.append(recent_activity[column]["Row"]["Detail"])
    assert f'{username} deleted password profile "{profile_name_cps}"' == recent_activity_list[0], \
        f'Could not find the related activity about password profile deletion {recent_activity}'
    logger.info(f'Could find the related activity about password profile deletion {recent_activity_list}')

    # Getting the recent administration activity details.
    admin_report = ReportsManager.get_administration_activity(core_session, system_name=None)
    recent_admin_activity_list = []
    for column in range(len(admin_report)):
        if admin_report[column]["Detail"].__contains__("deleted password profile"):
            recent_admin_activity_list.append(admin_report[column]["Detail"])
    assert f'{username} deleted password profile "{profile_name_cps}"' == recent_admin_activity_list[0], \
        f'Could not find the related activity about password profile deletion {recent_activity}'
    logger.info(f'Could find the related activity about password profile deletion {admin_report}')
