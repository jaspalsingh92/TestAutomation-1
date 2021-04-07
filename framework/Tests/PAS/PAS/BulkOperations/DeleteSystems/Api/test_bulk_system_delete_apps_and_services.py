import logging
import pytest
from Shared.API.infrastructure import ResourceManager
from Shared.API.jobs import JobManager
from Shared.API.redrock import RedrockController
from Shared.data_manipulation import DataManipulation
from Shared.API.desktopapps import get_desktop_apps
from Utils.guid import guid

logger = logging.getLogger('test')


pytestmark = [pytest.mark.api, pytest.mark.cps, pytest.mark.bulk_system_delete, pytest.mark.bulk_system_delete_apps_and_services]


@pytest.mark.api
@pytest.mark.pas
def test_delete_systems_respects_skip_parameter(core_session, desktop_application_factory, list_of_created_systems, service_factory, core_ui):
    session = core_session
    factory = desktop_application_factory

    batch1 = ResourceManager.add_multiple_systems_with_accounts(session, 3, 4, list_of_created_systems)
    batch2 = ResourceManager.add_multiple_systems_with_accounts(session, 1, 2, list_of_created_systems)
    batch3 = ResourceManager.add_multiple_systems_with_accounts(session, 4, 6, list_of_created_systems)
    batch4 = ResourceManager.add_multiple_systems_with_accounts(session, 1, 8, list_of_created_systems)

    all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values([batch1, batch2, batch3, batch4])

    # these should get deleted
    systems_without_apps_and_services_ids, accounts_without_apps_and_services_ids = DataManipulation.aggregate_lists_in_dict_values([batch1])

    # these should not
    systems_with_apps_and_services_ids, accounts_with_apps_and_services_ids = DataManipulation.aggregate_lists_in_dict_values([batch2, batch3])

    # these should not
    keep_system_ids, keep_account_ids = DataManipulation.aggregate_lists_in_dict_values([batch4])

    delete_system_ids = systems_without_apps_and_services_ids.union(systems_with_apps_and_services_ids)

    system_ids_that_should_stay = keep_system_ids.union(systems_with_apps_and_services_ids)
    account_ids_that_should_stay = keep_account_ids.union(accounts_with_apps_and_services_ids)

    desktop_apps = ['SQL Server Management Studio', 'TOAD for Oracle', 'VMware vSphere Client']
    template_ids = list(map(lambda app_name: factory.get_template_id_from_name(app_name), desktop_apps))

    resource_user = core_session.get_current_session_user_info().json()['Result']
    application_user = factory.session.get_current_session_user_info().json()['Result']

    for system_id in systems_with_apps_and_services_ids:
        # give 3 desktop apps per system
        ResourceManager.assign_system_permissions(core_session, ('View'), application_user['Name'], application_user['Id'], 'User', system_id)
        for template_id in template_ids:
            app_id = factory.add_desktop_app(template_id)
            factory.give_user_permissions(app_id, resource_user['Name'], resource_user['Id'])
            factory.assign_system(app_id, system_id)
            service_name = template_id + '_' + guid()
            service_factory.add_service(system_id, guid(), service_name, f'Service for {template_id} {service_name}')

    created_service_ids = service_factory.get_all_service_ids()
    created_desktop_app_ids = factory.get_all_app_ids()
    assert len(created_service_ids) == len(systems_with_apps_and_services_ids) * len(template_ids), f'Failed to create all services. {created_service_ids}'
    assert len(created_desktop_app_ids) == len(systems_with_apps_and_services_ids) * len(template_ids), f'Failed to create all desktop apps. {created_desktop_app_ids}'

    logger.info(f'Created apps {created_desktop_app_ids}')
    logger.info(f'Created services {created_service_ids}')

    secret_name = "TestSecret-" + str(ResourceManager.time_mark_in_hours()) + "-" + guid()

    # Send the system ids that both have and do not have apps and services so we can test that only the ones w/o apps and services are deleted.
    job_id, success = ResourceManager.del_multiple_systems(core_session, delete_system_ids, True, secret_name, skip_if_has_apps_or_services=True)

    job_report = JobManager.get_job_report(core_session, job_id)

    assert set(ResourceManager.get_multi_added_system_ids(core_session, all_systems).values()) == system_ids_that_should_stay, f"Set of expected remaining systems did not match search. Job results {job_report}"
    assert set(ResourceManager.get_multi_added_account_ids(core_session, all_systems)) == account_ids_that_should_stay, "Set of expected remaining accounts did not match search"

    remaining_apps = get_desktop_apps(core_session, created_desktop_app_ids)

    assert len(remaining_apps) == len(created_desktop_app_ids), f'Some desktop apps were deleted that should not have been.'

    logger.debug(f'Checking on services {created_service_ids}')
    remaining_services = RedrockController.get_rows_matching_ids(core_session, 'Subscriptions', created_service_ids)
    assert len(remaining_services) == len(created_service_ids), f'Some services were deleted that should not have been.'


@pytest.mark.api
@pytest.mark.pas
def test_delete_systems_with_accounts_and_apps(core_session, desktop_application_factory, list_of_created_systems, service_factory, core_ui):
    session = core_session
    factory = desktop_application_factory

    batch1 = ResourceManager.add_multiple_systems_with_accounts(session, 3, 4, list_of_created_systems)
    batch2 = ResourceManager.add_multiple_systems_with_accounts(session, 1, 2, list_of_created_systems)

    batch3 = ResourceManager.add_multiple_systems_with_accounts(session, 4, 6, list_of_created_systems)
    batch4 = ResourceManager.add_multiple_systems_with_accounts(session, 1, 8, list_of_created_systems)

    all_systems, all_accounts = DataManipulation.aggregate_lists_in_dict_values([batch1, batch2, batch3, batch4])

    delete_system_ids, delete_account_ids = DataManipulation.aggregate_lists_in_dict_values([batch1, batch2, batch3])
    keep_system_ids, keep_account_ids = DataManipulation.aggregate_lists_in_dict_values([batch4])

    desktop_apps = ['SQL Server Management Studio', 'TOAD for Oracle', 'VMware vSphere Client']
    template_ids = list(map(lambda app_name: factory.get_template_id_from_name(app_name), desktop_apps))

    resource_user = core_session.get_current_session_user_info().json()['Result']
    application_user = factory.session.get_current_session_user_info().json()['Result']

    for system_id in delete_system_ids:
        # give 3 desktop apps per system
        ResourceManager.assign_system_permissions(core_session, ('View'), application_user['Name'], application_user['Id'], 'User', system_id)
        for template_id in template_ids:
            app_id = factory.add_desktop_app(template_id)
            factory.give_user_permissions(app_id, resource_user['Name'], resource_user['Id'])
            factory.assign_system(app_id, system_id)
            service_name = template_id + '_' + guid()
            service_factory.add_service(system_id, guid(), service_name, f'Service for {template_id} {service_name}')

    created_service_ids = service_factory.get_all_service_ids()
    created_desktop_app_ids = factory.get_all_app_ids()
    assert len(created_service_ids) == len(delete_system_ids) * len(template_ids), f'Failed to create all services. {created_service_ids}'
    assert len(created_desktop_app_ids) == len(delete_system_ids) * len(template_ids), f'Failed to create all desktop apps. {created_desktop_app_ids}'

    logger.info(f'Created apps {created_desktop_app_ids}')
    logger.info(f'Created services {created_service_ids}')

    secret_name = "TestSecret-" + str(ResourceManager.time_mark_in_hours()) + "-" + guid()

    job_id, success = ResourceManager.del_multiple_systems(core_session, delete_system_ids, True, secret_name, skip_if_has_apps_or_services=False)

    job_report = JobManager.get_job_report(core_session, job_id)

    assert set(ResourceManager.get_multi_added_system_ids(core_session, all_systems).values()) == keep_system_ids, f"Set of expected remaining systems did not match search. Job results {job_report}"
    assert set(ResourceManager.get_multi_added_account_ids(core_session, all_systems)) == keep_account_ids, "Set of expected remaining accounts did not match search"

    remaining_apps = get_desktop_apps(core_session, created_desktop_app_ids)

    assert len(remaining_apps) == 0, f'Failed to delete desktop apps even though the bulk system delete succeeded. {remaining_apps} are zombied.'

    logger.debug(f'Checking on services {created_service_ids}')
    remaining_services = RedrockController.get_rows_matching_ids(core_session, 'Subscriptions', created_service_ids)
    assert len(remaining_services) == 0, f'Failed to delete services even though the bulk system delete succeeded. {remaining_services} are zombied.'
