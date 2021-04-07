import logging
import pytest
from Shared.API.infrastructure import ResourceManager
from Shared.API.redrock import RedrockController
from Utils.guid import guid

logger = logging.getLogger("test")


@pytest.mark.api
@pytest.mark.pas
def test_update_managed_account(pas_setup, core_session, pas_config):
    """
    :param pas_config:
    :param pas_setup:    Fixture for adding a system and an account associated with it.
    :param core_admin_ui: Authenticated Centrify Session.
    :param core_session: Authenticated Centrify Session.
     TC: C2547 - Update managed account
     trying to Update managed account password
            Steps:
                Pre: Create system with 1 manage account hand
                1. Try to update invalid password
                    -Assert Failure
                2. Try to update valid password
                    -Assert Failure
                3. Try to check password history
    """
    user_name = core_session.get_user().get_login_name()
    System_configurations_from_yaml = pas_config
    system_data = System_configurations_from_yaml['Windows_infrastructure_data']
    added_system_id, account_id, sys_info = pas_setup
    Result, success = ResourceManager.update_password(core_session, account_id, guid())
    assert success, "Did not update password"
    Result, success = ResourceManager.update_password(core_session, account_id, system_data['password'])
    assert success, "Did not update password"
    result, success = ResourceManager.check_out_password(core_session, 1, account_id)
    assert success, "Did not retrieve password"
    query = f"select EntityId, State, StateUpdatedBy, StateUpdatedTime from PasswordHistory where EntityId=" \
            f"'{account_id}' and StateUpdatedBy='{user_name}' and State='Retired'"
    password_history = RedrockController.get_result_rows(RedrockController.redrock_query(core_session, query))[0]
    assert len(password_history) > 0, "Password history table did not update"
