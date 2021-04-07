import pytest
import logging
from Shared.API.infrastructure import ResourceManager

logger = logging.getLogger('test')


@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi
def test_not_apply_password_profile_global(core_session, create_basic_pass_profile):
    """
      Test case: C1647
            :param core_session: Returns API session
            :param core_admin_ui: Centrify admin Ui session
            :param create_basic_pass_profile: Created a basic password complexity profile.
            """
    unix_profile_id = None
    profile_result, profile_success = ResourceManager.get_password_prof_for_target_types(core_session, 'Unix')
    assert profile_success, f'failed to get all profile for target unix type.'
    for row in profile_result:
        if row['Name'] == "Unix Profile":
            unix_profile_id = row['_RowKey']

    # Setting password profile mapping to default.
    result, success = ResourceManager.update_global_pass_profile_mapping(core_session, "Unix", unix_profile_id)
    assert success, f"failed to update global password profile mapping {result}"

    # Creating one password complexity profile
    profile = create_basic_pass_profile(core_session, 1)[0]
    cps_prof_id = profile[0]['_RowKey']
    profile_name_cps = profile[0]['Name']
    logger.info(f"Created password complex profile {profile_name_cps} with Id {cps_prof_id}")

    # getting and updating global password profile default value to Unix Profile
    result, success = ResourceManager.get_global_pass_profile_mapping(core_session)
    profile_name = []
    for row in result:
        if row['Name'] == "Unix Profile":
            profile_name.append(row['_RowKey'])
            profile_name.append(row['Name'])

    result, success = ResourceManager.update_global_pass_profile_mapping(core_session, "Unix", profile_name[0])
    assert success, f"failed to update global password profile mapping {result}"
    logger.info(f"Password complexity profile {profile_name_cps} not deleted")

    update_profile = []
    profile_result, profile_success = ResourceManager.get_password_prof_for_target_types(core_session, 'Unix')
    assert profile_success, f'failed to get all profile for target unix type.'
    for row in profile_result:
        if row['Name'] == profile_name_cps:
            update_profile.append(row['_RowKey'])

    # Setting password profile mapping to default.
    result, success = ResourceManager.update_global_pass_profile_mapping(core_session, "Unix", None)
    assert success is False, f"failed to update global password profile mapping {result}"

    # Getting the global password profile mapping profiles
    result, success = ResourceManager.get_global_pass_profile_mapping(core_session)
    profile_names = []
    for row in result:
        if row['Name'] == "Unix Profile":
            profile_names.append(row['_RowKey'])
            profile_names.append(row['TargetType'])

    # Getting the password profile by id
    cps_prof_result, cps_prof_success = ResourceManager.get_password_profile_by_id(core_session, profile_names[0])
    assert cps_prof_result['ProfileType'] == profile_names[1], \
        f"Global Password Profile not saved with Profile {profile_names[0]} with the result {cps_prof_result}"
    logger.info(f"Password profile created successfully with {cps_prof_result}")
