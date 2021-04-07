import random
import string
import pytest
import logging
import json
import time

from Shared.API.cloud_provider import CloudProviderManager
from Shared.API.infrastructure import ResourceManager
from Shared.API.policy import PolicyManager
from Shared.API.users import UserManager
from Shared.UI.Centrify.SubSelectors.forms import GridField, DisabledCombobox, DisabledTextBox
from Shared.UI.Centrify.SubSelectors.modals import Modal
from Shared.UI.Centrify.SubSelectors.navigation import ActiveMainContentArea
from Shared.UI.Centrify.SubSelectors.grids import GridRow
from Utils.guid import guid

logger = logging.getLogger("test")

pytestmark = [pytest.mark.ui, pytest.mark.cloudprovider, pytest.mark.aws]


class AwsCloudProviderTester:

    session = None
    cleaner = None
    ui = None
    policies = None
    policies_map = {}

    def __init__(self, core_session, fake_cloud_provider_cleaner, core_ui, generate_description=False, clean_up_policy=None):

        assert core_session is not None, "Must have valid session"
        assert fake_cloud_provider_cleaner is not None, "Must have valid cleaner"
        assert core_ui is not None, "Must have valid ui"

        self.ui = core_ui
        self.session = core_session
        self.cleaner = fake_cloud_provider_cleaner

        self.account_id = guid()[0:12]
        self.name = f"AutomatedWizardTest{guid()}"
        if generate_description:
            self.generate_random_description()
        if clean_up_policy is not None:
            self.policies = self.create_policies(4, clean_up_policy)

    already_cleaned = False

    def delete_cloud_provider_return_secret(self, secret_cleaner):
        cloud_id = CloudProviderManager.get_cloud_provider_id_by_cloud_account_id(self.session, self.account_id, retries=1)
        secret_name = f"apisecret{guid()}"
        result, success = CloudProviderManager.delete_cloud_providers(self.session, [cloud_id], run_sync=True,
                                                                      save_passwords=True, secret_name=secret_name)
        assert success, f"Failed to delete cloud providers {cloud_id}"

        secret_file_contents = ResourceManager.fetch_and_delete_secret(self.session, secret_name, secret_cleaner)

        if cloud_id in self.cleaner:
            self.cleaner.remove(cloud_id)
        self.already_cleaned = True

        return secret_file_contents

    def generate_random_description(self):
        self.description = f"Automated Wizard Test description {guid()} with !! spaces"

    def launch_wizard(self):
        """
        Provider details
        """

        self.ui.navigate('Resources', ('Cloud Providers', 'Cloud Providers'))
        self.ui.launch_add('Add Cloud Provider', 'Add AWS Cloud Provider')

    def done(self):
        self.ui.step("Done")
        self.ui.switch_context(ActiveMainContentArea())
        self.ui.expect(GridRow(self.name), f'Could not find grid row for cloud provider {self.name} after wizard completed')
        # Make sure we always keep track of the cloud provider id we created for later cleanup
        self._cloud_provider_db_row()

    # Step 1 -- Cloud Provider
    account_id = None
    name = None
    description = None

    def step_1(self):
        """
        Provider details. Must have called launch_wizard first
        """

        self.ui.input("CloudAccountId", self.account_id)
        self.ui.input("Name", self.name)
        self.ui.input("Description", self.description)

    def verify_step_1(self):
        my_row = self._cloud_provider_db_row()
        assert my_row['CloudAccountId'] == self.account_id, f"Invalid AWS Cloud Provider ID in table {my_row}"
        assert my_row['Name'] == self.name, f"Invalid name in table {my_row}"
        assert my_row['Description'] == self.description, f"Invalid description in table {my_row}"

    # Step 2 -- Cloud Provider Permissions

    # todo, return here

    def step_2(self):
        """
        Cloud Provider Permissions
        """

        self.ui.step("Next")  # go to step 2

    def verify_step_2(self):
        assert False, "NOT IMPLEMENTED"

    # Step 3 -- Root Account Permissions

    root_email = None
    root_password = None

    # policy: only applied if root is created

    enable_rotation = None
    prompt_to_change = None
    enable_reminder = None
    minimum_days = None  # available and required if enable_reminder True
    mfa_code = None

    def step_3(self, populate_user=False, rotation=None, prompt=None, reminder=None, min_days=None, mfa_code=None):
        """
        Root Account and MFA
        """
        self.ui.step("Next")  # go to step 3

        assert prompt is None or rotation, "Cannot set prompt if rotation is not set"
        assert reminder is None or rotation, "Cannot set reminder if rotation is not set"
        assert min_days is None or reminder, "Cannot set min days if reminder is not set"
        assert mfa_code != '', "Use None for no MFA code or _click_mfa_button to click and abort setting MFA"
        assert mfa_code is None or populate_user, "Cannot click MFA without a user"
        assert min_days is None or int(min_days) > 0, "invalid value for min_days"

        if populate_user:
            self.root_email = f'fake_email{guid()}@fun.net'
            self.root_password = f'fake.Pass{guid()}word!'

        self.ui.input('User', self.root_email)
        self.ui.input('Password', self.root_password)

        values = {True: "Yes", False: "No"}

        self.enable_rotation = rotation
        self.prompt_to_change = prompt
        self.enable_reminder = reminder
        self.minimum_days = min_days

        if self.enable_rotation is not None:
            self.ui.select_option('EnableUnmanagedPasswordRotation', values[self.enable_rotation])
        else:
            self.ui.expect(DisabledCombobox('EnableUnmanagedPasswordRotationPrompt'), "Disabled EnableUnmanagedPasswordRotationPrompt not found")
            self.ui.expect(DisabledCombobox('EnableUnmanagedPasswordRotationReminder'), "Disabled EnableUnmanagedPasswordRotationReminder not found")

        if self.prompt_to_change is not None:
            self.ui.select_option('EnableUnmanagedPasswordRotationPrompt', values[self.prompt_to_change])

        if self.enable_reminder is not None:
            self.ui.select_option('EnableUnmanagedPasswordRotationReminder', values[self.enable_reminder])
        else:
            self.ui._waitUntilSettled()
            # check failing but the control isn't visible
            #self.ui.expect(DisabledTextBox('UnmanagedPasswordRotationReminderDuration'), f'UnmanagedPasswordRotationReminderDuration is not disabled.')

        if self.minimum_days is not None:
            self.ui.input('UnmanagedPasswordRotationReminderDuration', self.minimum_days)

        if mfa_code is not None:
            self.ui.card("Root Account Virtual MFA Device", "Add Provider")
            self.ui.switch_context(Modal("Add Provider"))
            if not mfa_code:
                self.mfa_code = False
                self.ui.button("Cancel")
                self.ui.remove_context()
                self.ui.switch_context(ActiveMainContentArea())
            else:
                self.mfa_code = f"OTEQ25NK6S{''.join([random.choice(string.ascii_uppercase) for _ in range(20)])}XLFSQQXQZSBGBNJXITMIXPATP5NKFTC33I"
                self.ui.input('SharedSecret', self.mfa_code)
                self.ui.button("Next")
                self.ui.button("Confirm")
                self.ui.remove_context()
                self.ui.switch_context(ActiveMainContentArea())

    def _verify_root_password_checkout(self, db_row):

        assert db_row['CredentialType'] == 'Password', f"Credential type should be password {db_row}"
        assert db_row['User'] == self.root_email, f"Invalid user name {db_row}"

    def _verify_get_mfa_token(self, account_id, expect_challenge_on_checkout):
        pas_user = self.session.get_user()

        result, success = ResourceManager.assign_account_permissions(self.session,
                                                                     "Owner,View,Manage,Delete,Login,Naked,UpdatePassword,RotatePassword",
                                                                     pas_user.get_login_name(), pas_user.get_id(),
                                                                     pvid=account_id)

        assert success, f"Failed to set account permissions {result}"

        result, success = ResourceManager.check_out_password(self.session, 6, account_id)

        if not expect_challenge_on_checkout:
            assert success and result['Password'] == self.root_password, f"Unexpected value for password {result}"

            new_coid = result['COID']

            result, success = ResourceManager.check_in_password(self.session, coid=new_coid)
            assert success, "Did not check in password"
        else:
            assert 'ChallengeId' in result and len(
                result) == 1, f"Did not receive expected challenge {result} {success}"

        result, success = CloudProviderManager.get_mfa_token(self.session, account_id)
        if self.mfa_code:
            assert success, f"Failed to get_mfa_token {result}"
            assert len(result['code']) == 6, f"Token returned was wrong length {result}"
        else:
            assert not success, f"Should fail with MFA not set {result}"

    def _verify_step_3_policy_settings(self, cp_row):
        result = UserManager.user_policy_pas_summary(self.session, cp_row['ID'], "CloudProviders", None)
        result_data = self.session.get_response_data(result)
        rsop = result_data["rsop"]

        assert rsop['/PAS/ConfigurationSetting/CloudProviders/EnableUnmanagedPasswordRotationPrompt'] == (self.prompt_to_change is True), f"Policy wrong {rsop}"
        assert rsop['/PAS/ConfigurationSetting/CloudProviders/EnableUnmanagedPasswordRotation'] == (self.enable_rotation is True), f"Policy wrong {rsop}"

        min_days_numeric = self.minimum_days
        if min_days_numeric is None:
            min_days_numeric = 0

        assert rsop['/PAS/ConfigurationSetting/CloudProviders/EnableUnmanagedPasswordRotationReminder'] == (self.enable_reminder is True), f"Policy wrong {rsop}"
        assert rsop['/PAS/ConfigurationSetting/CloudProviders/UnmanagedPasswordRotationReminderDuration'] == min_days_numeric, f"Policy wrong {rsop}"

    def verify_step_3(self, expect_challenge_on_checkout=False):

        cp_row = self._cloud_provider_db_row()
        root_account_row = self._cloud_provider_root_account_db_row(cp_row['ID'])

        self._verify_root_password_checkout(root_account_row)
        self._verify_get_mfa_token(root_account_row['ID'], expect_challenge_on_checkout)
        self._verify_step_3_policy_settings(cp_row)


    def step_4(self):
        """
        Root User Account Permissions
        """
        self.ui.step("Next")  # go to step 4

    def verify_step_4(self):
        assert False, "NOT IMPLEMENTED"

    login_default_rules = None
    login_conditional_rules = None
    checkout_default_rules = None
    checkout_conditional_rules = None

    def step_5(self, uncheck_copy=False, root_account_login_default_profile=False, password_checkout_default_profile=False,
               root_account_login_conditional_profile=False, password_checkout_conditional_profile=False):
        """
        Cloud And Root User Policy
        """

        assert self.policies is not None or\
            [root_account_login_default_profile, password_checkout_default_profile,
             root_account_login_conditional_profile, password_checkout_conditional_profile] == \
            [False] * 4, "Policies must be initialized if any options are set to True"

        assert uncheck_copy or not password_checkout_default_profile, "password_checkout_default_profile must be False if uncheck_copy is False"
        assert uncheck_copy or not password_checkout_conditional_profile, "password_checkout_conditional_profile must be False if uncheck_copy is False"

        if root_account_login_default_profile:
            self.login_default_rules = self.policies[0]
        if root_account_login_conditional_profile:
            self.login_conditional_rules = self.policies[1]
        if password_checkout_default_profile:
            self.checkout_default_rules = self.policies[2]
        if password_checkout_conditional_profile:
            self.checkout_conditional_rules = self.policies[3]

        if uncheck_copy is False:
            self.checkout_default_rules = self.login_default_rules
            self.checkout_conditional_rules = self.login_conditional_rules

        self.ui.step("Next")  # go to step 5

        if uncheck_copy:
            self.ui.uncheck("SameAsLoginRules")

        if root_account_login_default_profile:
            self.ui.select_option("LoginDefaultProfile", self.login_default_rules)

        if password_checkout_default_profile:
            self.ui.select_option("RootAccountLoginDefaultProfile", self.checkout_default_rules)

        if root_account_login_conditional_profile:
            self.ui.remove_context()
            self.ui.switch_context(GridField("LoginRules"))
            self.ui.button("Add Rule")
            self.ui.switch_context(Modal("Root Account Login Challenge Rules"))

            self.ui.select_option("ProfileId", self.login_conditional_rules)

            self.ui.button("Add Filter")
            self.ui.select_option("Prop", "IP Address")
            self.ui.select_option("Op", "inside corporate IP range")
            self.ui.button("Add")
            self.ui.button("OK")

            self.ui.remove_context()
            self.ui.switch_context(ActiveMainContentArea())

        if password_checkout_conditional_profile:
            self.ui.remove_context()
            self.ui.switch_context(GridField("RootAccountLoginRules"))

            self.ui.button("Add Rule")

            self.ui.remove_context()
            self.ui.switch_context(Modal("Password Checkout Challenge Rules"))

            self.ui.select_option("ProfileId", self.checkout_conditional_rules)

            self.ui.button("Add Filter")
            self.ui.select_option("Prop", "IP Address")
            self.ui.select_option("Op", "inside corporate IP range")
            self.ui.button("Add")
            self.ui.button("OK")

            self.ui.remove_context()
            self.ui.switch_context(ActiveMainContentArea())

    def verify_step_5(self):
        # todo: Revisit combining all verify steps

        counts_as_none = [None, '', '--', []]

        assert self.root_email is not None, "This should not be called if root account not configured"
        cp_row = self._cloud_provider_db_row()

        results, success = CloudProviderManager.\
            get_account_db_rows_by_cloud_provider_id(self.session, cp_row['ID'], root_accounts=True, retries=10)

        assert success and len(results) == 1, f"Expected exactly one result {results}"

        result = results[0]

        account_id = result['ID']

        result = UserManager.user_policy_pas_summary(self.session, cp_row['ID'], "CloudProviders", None)
        result_data = self.session.get_response_data(result)

        rsop = result_data["rsop"]

        result = UserManager.user_policy_pas_summary(self.session, account_id, "VaultAccount", None)
        result_data = self.session.get_response_data(result)
        rsop2 = result_data["rsop"]

        key = '/PAS/CloudProviders/LoginRules'
        login_rules = None
        if key in rsop:
            login_rules = rsop[key]
            if login_rules in counts_as_none:
                login_rules = None

        if self.login_conditional_rules is not None:
            expected_value = [{'Conditions': [{'Prop': 'IpAddress', 'Op': 'OpInCorpIpRange'}],
                               'ProfileId': self.policies_map[self.login_conditional_rules]}]

            actual_value = json.dumps(login_rules['_Value'], sort_keys=True)
            expected_value = json.dumps(expected_value, sort_keys=True)

            assert actual_value == expected_value, f"Invalid policy for login conditional {actual_value} expected {expected_value}"
        else:
            assert login_rules is None or login_rules['_Value'] in counts_as_none, f"Policy should be none for login conditional {login_rules}"

        key = '/PAS/CloudProviders/LoginDefaultProfile'
        actual_id = None
        if key in rsop:
            actual_id = rsop[key]
            if actual_id in counts_as_none:
                actual_id = None
        expected_id = None
        if self.login_default_rules is not None:
            expected_id = self.policies_map[self.login_default_rules]
            if expected_id in counts_as_none:
                expected_id = None

        assert actual_id == expected_id, f"Invalid default login rules {actual_id} != {expected_id}"

        expected_id = None
        if self.checkout_default_rules is not None:
            expected_id = self.policies_map[self.checkout_default_rules]

        actual_id = None
        key = '/PAS/VaultAccount/PasswordCheckoutDefaultProfile'
        if key in rsop2:
            actual_id = rsop2[key]
            if actual_id in counts_as_none:
                actual_id = None

        assert actual_id == expected_id, f"Invalid default checkout rules {rsop2}"

        key = '/PAS/VaultAccount/PasswordCheckoutRules'
        actual_value = None
        if key in rsop2:
            actual_value = rsop2[key]['_Value']
            if actual_value in counts_as_none:
                actual_value = None

        expected_value = None

        if self.checkout_conditional_rules is not None:
            expected_value = [{'Conditions': [{'Prop': 'IpAddress', 'Op': 'OpInCorpIpRange'}],
                               'ProfileId': self.policies_map[self.checkout_conditional_rules]}]
            if expected_value in counts_as_none:
                expected_value = None
            else:
                actual_value = json.dumps(actual_value, sort_keys=True)
                expected_value = json.dumps(expected_value, sort_keys=True)

        assert actual_value == expected_value, f"Invalid root account conditional policy {actual_value} {expected_value}"

    def create_policies(self, n, clean_up_policy):

        assert 1 <= n <= 4, f"Number of profiles must be between 1 and 4"

        policy_names = []

        count = 0

        while len(policy_names) < n:
            assert count < n, "Loop malfunction"
            count += 1

            # creating new policy
            profile_name = guid()
            policy_result = PolicyManager.create_new_auth_profile(self.session, profile_name, ["EMAIL", None], None, "30")
            assert policy_result is not None, f'Failed to create policy:{policy_result}'
            logger.info(f' Creating new policy:{policy_result}')
            clean_up_policy.append(policy_result)
            policy_names.append(profile_name)
            self.policies_map.update({profile_name: policy_result})

        # order policies were created shouldn't matter, so let's make sure it doesn't
        random.shuffle(policy_names)

        return policy_names

    def _cloud_provider_db_row(self):

        cloud_id = CloudProviderManager.get_cloud_provider_id_by_cloud_account_id(self.session, self.account_id, retries=30)
        assert cloud_id is not None, "Failed to create fake cloud provider using wizard"

        if cloud_id not in self.cleaner:
            self.cleaner.append(cloud_id)

        rows = CloudProviderManager.get_cloud_provider_table_rows(self.session, cloud_id)
        assert len(rows) == 1, f"Should be exactly one result row returned: {rows}"

        return rows[0]

    def _cloud_provider_root_account_db_row(self, account_id):
        results, success = CloudProviderManager. \
            get_account_db_rows_by_cloud_provider_id(self.session, account_id, root_accounts=True, retries=10)

        assert success and len(results) == 1, f"Expected exactly one result {results}"

        return results[0]


def test_cloud_provider_wizard_min_config_creates_valid_cloud_provider(core_session, fake_cloud_provider_cleaner, core_ui):

    helper = AwsCloudProviderTester(core_session, fake_cloud_provider_cleaner, core_ui, generate_description=True)

    helper.launch_wizard()
    helper.step_1()
    helper.step_2()
    helper.step_3()
    helper.done()

    helper.verify_step_1()


def test_cloud_provider_add_user(core_session, fake_cloud_provider_cleaner, core_ui):

    helper = AwsCloudProviderTester(core_session, fake_cloud_provider_cleaner, core_ui)

    helper.launch_wizard()
    helper.step_1()
    helper.step_2()
    helper.step_3(populate_user=True)
    helper.step_4()
    helper.step_5()
    helper.done()

    helper.verify_step_1()
    helper.verify_step_3()


@pytest.mark.smoke
def test_cloud_provider_add_user_with_policy(core_session, fake_cloud_provider_cleaner, core_ui):

    helper = AwsCloudProviderTester(core_session, fake_cloud_provider_cleaner, core_ui)

    helper.launch_wizard()
    helper.step_1()
    helper.step_2()
    helper.step_3(populate_user=True, rotation=True, prompt=True, reminder=True, min_days=11)
    helper.step_4()
    helper.step_5()
    helper.done()

    helper.verify_step_1()
    helper.verify_step_3()


@pytest.mark.parametrize('mfa_state', [True, False, None])
def test_cloud_provider_mfa_choices(core_session, fake_cloud_provider_cleaner, core_ui, mfa_state):

    helper = AwsCloudProviderTester(core_session, fake_cloud_provider_cleaner, core_ui)

    helper.launch_wizard()
    helper.step_1()
    helper.step_2()
    helper.step_3(populate_user=True, mfa_code=mfa_state)
    helper.step_4()
    helper.step_5()
    helper.done()

    helper.verify_step_1()
    helper.verify_step_3()


@pytest.mark.parametrize('default_rules', [False, True])
@pytest.mark.parametrize('conditional_rules', [False, True])
def test_cloud_provider_step_5_copy(core_session, fake_cloud_provider_cleaner, core_ui, clean_up_policy,
                                    default_rules, conditional_rules):

    mfa_state = random.choice([True, False, None])

    helper = AwsCloudProviderTester(core_session, fake_cloud_provider_cleaner, core_ui, clean_up_policy=clean_up_policy)

    helper.launch_wizard()
    helper.step_1()
    helper.step_2()
    helper.step_3(populate_user=True, mfa_code=mfa_state)
    helper.step_4()

    helper.step_5(
        root_account_login_default_profile=default_rules,
        root_account_login_conditional_profile=conditional_rules
    )

    helper.done()

    helper.verify_step_5()


@pytest.mark.parametrize('login_default_rules', [False, True])
@pytest.mark.parametrize('login_conditional_rules', [False, True])
@pytest.mark.parametrize('checkout_default_rules', [False, True])
@pytest.mark.parametrize('checkout_conditional_rules', [False, True])
def test_cloud_provider_step_5_no_copy(core_session, fake_cloud_provider_cleaner, core_ui, clean_up_policy,
                                       secret_cleaner, login_default_rules, login_conditional_rules,
                                       checkout_default_rules, checkout_conditional_rules):
    mfa_state = random.choice([True, False, None])

    helper = AwsCloudProviderTester(core_session, fake_cloud_provider_cleaner, core_ui, clean_up_policy=clean_up_policy)

    helper.launch_wizard()
    helper.step_1()
    helper.step_2()
    helper.step_3(populate_user=True, mfa_code=mfa_state)
    helper.step_4()

    helper.step_5(
        uncheck_copy=True,
        root_account_login_default_profile=login_default_rules,
        root_account_login_conditional_profile=login_conditional_rules,
        password_checkout_default_profile=checkout_default_rules,
        password_checkout_conditional_profile=checkout_conditional_rules
    )

    helper.done()

    helper.verify_step_5()

    secret_contents = helper.delete_cloud_provider_return_secret(secret_cleaner)

    logger.info(f"Retrieved secret {secret_contents}")

    if mfa_state:
        assert helper.mfa_code in secret_contents, f"Failed to retrieve MFA code from secret"
    assert helper.root_password in secret_contents, f"Failed to retrieve password from secret"
