import pytest
from Shared.API.infrastructure import ResourceManager
from Utils.guid import guid
from Shared.API.redrock import RedrockController

pytestmark = [pytest.mark.example]


@pytest.mark.api_ui
@pytest.mark.pas
def test_navigation_benchmark_example_with_implicit_start_and_end(core_ui, csv_benchmark):
    """
    This example demonstrates how start and end don't need to be explicitly called, if we are measuring the entire test

    See example output at bottom of this file
    """
    start, end, info = csv_benchmark
    info(filenamesuffix="Single Navigation", column="Servers Tab", row="Test 1")
    ui = core_ui
    ui.navigate('Resources', 'Systems')


@pytest.mark.api_ui
@pytest.mark.pas
@pytest.mark.parametrize('user', ["Privileged Access Service Power User", "System Administrator"])
@pytest.mark.parametrize('tab', ["Systems", "Accounts", "Secrets"])
def test_navigation_benchmark_with_parameter_data(users_and_roles, csv_benchmark, user, tab):
    """
    This example demonstrates using columns for different tests and rows for different users

    See example output at bottom of this file
    """
    start, end, info = csv_benchmark
    info(filenamesuffix="Navigation Times", column=f"{tab} Tab", row=user)
    ui = users_and_roles.get_ui_as_user(user)
    start()  # start timing
    ui.navigate('Resources', tab)
    end()  # stop timing


@pytest.mark.api
@pytest.mark.bhavna
@pytest.mark.pas
def test_add_and_delete_system_with_multiple_benchmarks_per_test(core_session, created_system_id_list, csv_benchmark):
    """
    This test demonstrates measuring multiple things within the same pytest test

    See example output at bottom of this file
    """
    start, end, info = csv_benchmark
    info(filenamesuffix="Bulk System Delete Time Test")
    for i in range(3):
        info(row=f"Test Run {i+1}")
        info(column="Generate Systems")
        start()
        batch = ResourceManager.add_multiple_systems_with_accounts(core_session, 2, 2, created_system_id_list)
        end()
        secret_name = f"secret{guid()}"
        info(column="Delete Job")
        start()
        job_id, result = ResourceManager.del_multiple_systems(core_session, batch.keys(), secretname=secret_name)
        result = ResourceManager.get_job_state(core_session, job_id)
        assert result == "Succeeded", "Job did not execute"
        end()
        info(column="Query Systems and Accounts")
        start()
        remaining_accounts = set(ResourceManager.get_multi_added_account_ids(core_session, created_system_id_list))
        remaining_systems = set(ResourceManager.get_multi_added_system_ids(core_session, created_system_id_list).values())
        assert remaining_accounts == set(), "Remaining accounts did not match expectation"
        assert remaining_systems == set(), "Remaining systems did not match expectation"
        end()
        info(column="Query Secret")
        start()
        secret_id = RedrockController.get_secret_id_by_name(core_session, secret_name)
        assert secret_id is not None, "No secret was created"
        end()

"""
Sample output file Logs\\Csv\\20200113_110658 Bulk System Delete Time Test.csv

Bulk System Delete Time Test,Generate Systems,Delete Job,Query Systems and Accounts,Query Secret
Test Run 1,0.308987 s,2.147153 s,0.034832 s,0.017926 s
Test Run 2,0.190836 s,3.132843 s,0.051775 s,0.009056 s
Test Run 3,0.209406 s,2.134667 s,0.01496 s,0.015964 s


Sample output file Logs\\Csv\\20200113_110658 Navigation Times.csv

Navigation Times,Systems Tab,Accounts Tab,Secrets Tab
Privileged Access Service Power User,1.286537 s,1.235349 s,2.649767 s
System Administrator,0.491022 s,0.509833 s,1.360811 s


Sample output file Logs\\Csv\\20200113_110658 Single Navigation.csv

Single Navigation,Servers Tab
Test 1,0.657878 s
"""
