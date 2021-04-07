import pytest
import logging
from Shared.API.infrastructure import ResourceManager
from Shared.API.redrock import RedrockController

logger = logging.getLogger('test')


@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi
def test_check_account_view_permission_under_system_domain_database(core_session, pas_setup,
                                                                    create_databases_with_accounts,
                                                                    create_domains_with_accounts,
                                                                    get_limited_no_view_user_function,
                                                                    users_and_roles):
    """
    Test case: C2127
    :param core_session: Authenticated centrify session
    :param pas_setup: fixture to create system with account
    :param create_databases_with_accounts: fixture to create database with account
    :param create_domains_with_accounts: fixture to create domain with account
    """

    system_id, account_id, sys_info = pas_setup
    database = create_databases_with_accounts(core_session, databasecount=1, accountcount=1)
    domain = create_domains_with_accounts(core_session, domaincount=1, accountcount=1)
    db_name, db_id, db_account, db_account_id = database[0]['Name'], database[0]['ID'], \
                                                database[0]['Accounts'][0]['User'], database[0]['Accounts'][0]['ID']
    domain_name, domain_id, domain_account, domain_account_id = domain[0]['Name'], domain[0]['ID'], \
                                                                domain[0]['Accounts'][0]['User'], \
                                                                domain[0]['Accounts'][0]['ID']

    # Step3 : Get user has "Privilege Service Administrator" right
    cloud_user_session, cloud_user = get_limited_no_view_user_function
    cloud_user, user_id, user_password = \
        cloud_user.get_login_name(), cloud_user.get_id(), cloud_user.get_password()
    user = {"Username": cloud_user, "Password": user_password}

    # Assigning permissions to system excluding "View" Permission
    result, status = ResourceManager.assign_system_permissions(core_session, "Grant", cloud_user, user_id,
                                                               pvid=system_id)
    assert status, f'failed to assign rights of system to user {cloud_user}'
    logger.info(f'successfully assigned rights to user {cloud_user} excluding "View" permission')

    # Assigning permissions to system account including "View" Permission
    result, status = ResourceManager.assign_account_permissions(core_session, "View", cloud_user, user_id,
                                                                pvid=account_id)
    assert status, f'failed to assign rights of accounts to user {cloud_user}'
    logger.info(f'successfully assigned rights to user {cloud_user} excluding "View" permission')

    # Assigning permissions to domain excluding "View" Permission
    result, status = ResourceManager.set_domain_account_permissions(core_session, "Grant", cloud_user, user_id,
                                                                    pvid=domain_id)
    assert status, f'failed to assign rights of domain to user {cloud_user}'
    logger.info(f'successfully assigned rights to user {cloud_user} excluding "View" permission')

    # Assigning permissions to domain account including "View" Permission
    result, status = ResourceManager.assign_account_permissions(core_session, "View", cloud_user, user_id,
                                                                pvid=domain_account_id)
    assert status, f'failed to assign rights of domain account to user {cloud_user}'
    logger.info(f'successfully assigned rights to user {cloud_user} excluding "View" permission')

    # Assigning permissions to database excluding "View" Permission
    result, status = ResourceManager.assign_database_permissions(core_session, "Grant", cloud_user, user_id, pvid=db_id)
    assert status, f'failed to assign rights of database to user {cloud_user}'
    logger.info(f'successfully assigned rights to user {cloud_user} excluding "View" permission')

    # Assigning permissions to database account including "View" Permission
    result, status = ResourceManager.assign_account_permissions(core_session, "View", cloud_user, user_id,
                                                                pvid=db_account_id)
    assert status, f'failed to assign rights of database account to user {cloud_user}'
    logger.info(f'successfully assigned rights to user {cloud_user} excluding "View" permission')

    query = "@/lib/server/get_accounts.js(mode:'AllAccounts', newcode:true, localOnly:true, " \
            "colmemberfilter:'Select ID from VaultAccount WHERE Host IS NOT NULL')"
    result = RedrockController.redrock_query(cloud_user_session, query,
                                             args={"PageNumber": 1, "PageSize": 100, "Limit": 100000, "SortBy": "Name",
                                                   "Ascending": True, "FilterBy": ["Name", "User"],
                                                   "FilterValue": f'{sys_info[0]}',
                                                   "FilterQuery": None, "Caching": 0})
    assert len(result) == 0, f'User able to see the account details under account records user ' \
                             f'have different rights: {get_limited_no_view_user_function}'
    logger.info(f'Local account {sys_info[4]} of system {sys_info[0]} is not visible to user {cloud_user}')

    query = "SELECT * FROM (SELECT VaultAccount.ID, VaultAccount.User, VaultAccount.OwnerName, " \
            "VaultAccount.Description, VaultAccount.LastChange, VaultAccount.Status, " \
            "VaultAccount.DefaultCheckoutTime, VaultAccount.MissingPassword, VaultAccount.ActiveCheckouts, " \
            "VaultAccount.NeedsPasswordReset, VaultAccount.PasswordResetRetryCount, " \
            "VaultAccount.PasswordResetLastError, VaultAccount.IsManaged, VaultAccount.Host, VaultAccount.DomainID, " \
            "VaultAccount.DatabaseID, VaultAccount.IsFavorite, VaultAccount.UseWheel, VaultAccount.CredentialType, " \
            "SshKeys.Name as CredentialName, VaultAccount.WorkflowEnabled, COALESCE(NULLIF(" \
            "VaultAccount.WorkflowApprovers, ''),NULLIF(VaultAccount.WorkflowApprover, '')) as WorkflowApprovers, " \
            "VaultAccount.DiscoveredTime as AccountDiscoveredTime, VaultAccount.Name, VaultAccount.FQDN, " \
            "VaultAccount.SessionType, VaultAccount.ComputerClass, VaultDatabase.DatabaseClass, " \
            "VaultAccount.ProxyUser, VaultAccount.LastHealthCheck FROM VaultAccount LEFT OUTER JOIN VaultDatabase ON " \
            "DatabaseID = VaultDatabase.ID LEFT OUTER JOIN SshKeys ON CredentialId = SshKeys.ID WHERE IFNULL(" \
            "VaultAccount.Name, '') <> '') WHERE DomainID is not null AND IFNULL(Name, \"\") <> \"\" "
    result = RedrockController.redrock_query(cloud_user_session, query,
                                             args={"PageNumber": 1, "PageSize": 100, "Limit": 100000, "SortBy": "Name",
                                                   "Ascending": True, "FilterBy": ["Name", "User"],
                                                   "FilterValue": f"{domain_account}", "FilterQuery": None,
                                                   "Caching": 0})
    assert len(result) == 1, f'User able to see the account details under account records user ' \
                             f'have different rights: {get_limited_no_view_user_function}'
    logger.info(f'user {cloud_user} can see domain account {domain_account}')

    query = "SELECT * FROM (SELECT VaultAccount.ID, VaultAccount.User, VaultAccount.OwnerName, " \
            "VaultAccount.Description, VaultAccount.LastChange, VaultAccount.Status, " \
            "VaultAccount.DefaultCheckoutTime, VaultAccount.MissingPassword, VaultAccount.ActiveCheckouts, " \
            "VaultAccount.NeedsPasswordReset, VaultAccount.PasswordResetRetryCount, " \
            "VaultAccount.PasswordResetLastError, VaultAccount.IsManaged, VaultAccount.Host, VaultAccount.DomainID, " \
            "VaultAccount.DatabaseID, VaultAccount.IsFavorite, VaultAccount.UseWheel, VaultAccount.CredentialType, " \
            "SshKeys.Name as CredentialName, VaultAccount.WorkflowEnabled, COALESCE(NULLIF(" \
            "VaultAccount.WorkflowApprovers, ''),NULLIF(VaultAccount.WorkflowApprover, '')) as WorkflowApprovers, " \
            "VaultAccount.DiscoveredTime as AccountDiscoveredTime, VaultAccount.Name, VaultAccount.FQDN, " \
            "VaultAccount.SessionType, VaultAccount.ComputerClass, VaultDatabase.DatabaseClass, " \
            "VaultAccount.ProxyUser, VaultAccount.LastHealthCheck FROM VaultAccount LEFT OUTER JOIN VaultDatabase ON " \
            "DatabaseID = VaultDatabase.ID LEFT OUTER JOIN SshKeys ON CredentialId = SshKeys.ID WHERE IFNULL(" \
            "VaultAccount.Name, '') <> '') WHERE DatabaseID IS NOT NULL AND IFNULL(Name, \"\") <> \"\" "
    result = RedrockController.redrock_query(cloud_user_session, query,
                                             args={"PageNumber": 1, "PageSize": 100, "Limit": 100000, "SortBy": "Name",
                                                   "Ascending": True, "FilterBy": ["Name", "User"],
                                                   "FilterValue": f"{db_account}", "FilterQuery": None, "Caching": 0})
    assert len(result) == 0, f'User able to see the account details under account records user ' \
                             f'have different rights: {get_limited_no_view_user_function}'
    logger.info(f'database account {db_account} is not visible to user {cloud_user}.')
