import logging
import pytest

from Shared.API.cloud_provider import CloudProviderManager
from Shared.API.infrastructure import ResourceManager
from Shared.API.ssh import add_ssh_key
from Utils.guid import guid

logger = logging.getLogger("test")

pytestmark = [pytest.mark.api, pytest.mark.cloudprovider, pytest.mark.aws]


def _expected_regions():
    return ['ec2.eu-north-1.amazonaws.com:eu-north-1', 'ec2.ap-south-1.amazonaws.com:ap-south-1',
            'ec2.eu-west-3.amazonaws.com:eu-west-3', 'ec2.eu-west-2.amazonaws.com:eu-west-2',
            'ec2.eu-west-1.amazonaws.com:eu-west-1', 'ec2.ap-northeast-2.amazonaws.com:ap-northeast-2',
            'ec2.ap-northeast-1.amazonaws.com:ap-northeast-1', 'ec2.sa-east-1.amazonaws.com:sa-east-1',
            'ec2.ca-central-1.amazonaws.com:ca-central-1', 'ec2.ap-southeast-1.amazonaws.com:ap-southeast-1',
            'ec2.ap-southeast-2.amazonaws.com:ap-southeast-2', 'ec2.eu-central-1.amazonaws.com:eu-central-1',
            'ec2.us-east-1.amazonaws.com:us-east-1', 'ec2.us-east-2.amazonaws.com:us-east-2',
            'ec2.us-west-1.amazonaws.com:us-west-1', 'ec2.us-west-2.amazonaws.com:us-west-2']


def test_get_aws_security_groups(core_session, cloud_provider_ec2_account_config, live_aws_cloud_provider_and_accounts):
    cloud_provider_ids, iam_account_ids, access_key_ids, root_account_id, cloud_provider_name = live_aws_cloud_provider_and_accounts
    result, success = CloudProviderManager.get_aws_security_groups(core_session, cloud_provider_ids[0], iam_account_ids[0], 'us-west-1')
    assert success, f"Failed to get aws security groups {result}"
    assert len(result) >= 1, f"No results from aws security groups {result}"
    assert result[0]['OwnerId'] == str(cloud_provider_ec2_account_config['id'])


def test_get_aws_regions_rr(core_session, live_aws_cloud_provider_and_accounts):
    cloud_provider_ids, iam_account_ids, access_key_ids, root_account_id, cloud_provider_name = live_aws_cloud_provider_and_accounts
    result, success = CloudProviderManager.get_aws_regions(core_session, cloud_provider_ids[0], iam_account_ids[0], rr_format=True)
    assert success, f"Failed to get AWS Regions {result}"
    extract = [f"{x['Row']['Endpoint']}:{x['Row']['RegionName']}" for x in result['Results']]

    # Do not fail simply because AWS added new regions

    for region in _expected_regions():
        assert region in extract, f"Missing expected region {region} from {result}"


def test_get_aws_regions_not_rr(core_session, live_aws_cloud_provider_and_accounts):
    cloud_provider_ids, iam_account_ids, access_key_ids, root_account_id, cloud_provider_name = live_aws_cloud_provider_and_accounts
    result, success = CloudProviderManager.get_aws_regions(core_session, cloud_provider_ids[0], iam_account_ids[0], rr_format=False)
    assert success, f"Failed to get AWS Regions {result}"
    extract = [f"{x['Endpoint']}:{x['RegionName']}" for x in result]

    # Do not fail simply because AWS added new regions

    for region in _expected_regions():
        assert region in extract, f"Missing expected region {region} from {result}"


def test_get_aws_availability_zones(core_session, live_aws_cloud_provider_and_accounts):
    """
    Fetch availability zones for a single region
    """
    cloud_provider_ids, iam_account_ids, access_key_ids, root_account_id, cloud_provider_name = live_aws_cloud_provider_and_accounts
    result, success = CloudProviderManager.get_aws_availability_zones(core_session, cloud_provider_ids[0], iam_account_ids[0], 'us-west-1', rr_format=False)
    assert success, f"Failed to get AWS Availability Zones {result}"

    # Just make sure it is formatted as we expect

    assert False not in ['ZoneName' in x for x in result], f"Invalid results for availability zones {result}"


def test_aws_vpcs(core_session, live_aws_cloud_provider_and_accounts):
    cloud_provider_ids, iam_account_ids, access_key_ids, root_account_id, cloud_provider_name = live_aws_cloud_provider_and_accounts
    result, success = CloudProviderManager.get_aws_vpcs(core_session, cloud_provider_ids[0], iam_account_ids[0], 'us-west-1')
    assert success, f"Failed to grab vpcs {result}"

    assert len(result) > 0 and 'VpcId' in result[0], f"Missing data in aws_vpcs {result}"

def test_get_keypairs(core_session, live_aws_cloud_provider_and_accounts, cloud_provider_ec2_account_config):
    cloud_provider_ids, iam_account_ids, access_key_ids, root_account_id, cloud_provider_name = live_aws_cloud_provider_and_accounts

    result, success = CloudProviderManager.get_aws_key_pairs(core_session, cloud_provider_ids[0], iam_account_ids[0],
                                                             cloud_provider_ec2_account_config['Region'],
                                                             rr_format=False)
    assert success, f"Failed to grab keypairs {result}"

    assert cloud_provider_ec2_account_config['KeyPairFingerprint'] in f"{result}", "Did not return expected key fingerprint {result}"
    assert cloud_provider_ec2_account_config['KeyPairID'] in f"{result}", f"Did not return expected key Key Pair ID {result}"


def test_subnet_appears(core_session, live_aws_cloud_provider_and_accounts, cloud_provider_ec2_account_config):
    cloud_provider_ids, iam_account_ids, access_key_ids, root_account_id, cloud_provider_name = live_aws_cloud_provider_and_accounts

    result, success = CloudProviderManager.get_aws_subnets(core_session, cloud_provider_ids[0], iam_account_ids[0],
                                                           cloud_provider_ec2_account_config['Region'],
                                                           cloud_provider_ec2_account_config['VpcId'])

    assert cloud_provider_ec2_account_config['SubnetArn'] in f"{result}", "Did not return expected SubnetArn {result}"


def test_can_view_ssh_key_usage(core_session, cleanup_ssh, gen_a_ssh_key_function):
    ssh_key = gen_a_ssh_key_function
    ssh_list = cleanup_ssh

    ssh_name = f"SSH{guid()}"
    add_result, add_success = add_ssh_key(core_session, private_key=ssh_key['PrivateKey'], name=ssh_name)
    assert add_success, f"Fail, as SSH was not added to tenant. API request result: {add_result}."



    ssh_list.append(add_result)

def test_terminate_ec2_instance_fails_when_no_instance_exists(core_session, cloud_provider_ec2_account_config, live_aws_cloud_provider_and_accounts):
    cloud_provider_ids, iam_account_ids, access_key_ids, root_account_id, cloud_provider_name = live_aws_cloud_provider_and_accounts

    fake_instance_name = f"ApiDeployedConnector{guid()}"

    result, success = CloudProviderManager.terminate_ec2_instance(core_session,
                                                                  cloud_provider_id=cloud_provider_ids[0],
                                                                  iam_account_id=iam_account_ids[0],
                                                                  region=cloud_provider_ec2_account_config['Region'],
                                                                  instance_name=fake_instance_name)

    assert not success, f"Expected failure deleting non existing ec2 instance {result}"


def test_deploy_aws_connector_and_terminate(core_session, cloud_provider_ec2_account_config, live_aws_cloud_provider_and_accounts):
    cloud_provider_ids, iam_account_ids, access_key_ids, root_account_id, cloud_provider_name = live_aws_cloud_provider_and_accounts

    instance_name = f"ApiDeployedConnector{guid()}"

    result, success = CloudProviderManager\
        .deploy_aws_connector(core_session,
                              cloud_provider_id=cloud_provider_ids[0],
                              iam_account_id=iam_account_ids[0],
                              region=cloud_provider_ec2_account_config['Region'],
                              ami_id=None,
                              vpc_id=cloud_provider_ec2_account_config['VpcId'],
                              subnet_id=cloud_provider_ec2_account_config['SubnetId'],
                              security_group_id=None,
                              key_pair_name=cloud_provider_ec2_account_config['KeyPairName'],
                              instance_profile_arn=cloud_provider_ec2_account_config['InstanceProfileArn'],
                              instance_name=instance_name,
                              public_ip=False)

    assert success, f"Failed to deploy connector {result}"

    try:
        result, success = CloudProviderManager.get_aws_connectors_in_region(core_session,
                                                                            cloud_provider_id=cloud_provider_ids[0],
                                                                            iam_account_id=iam_account_ids[0],
                                                                            regions=[cloud_provider_ec2_account_config['Region']]
                                                                            )

        assert success, f"Failed to execute get_aws_connectors_in_region {result}"
        assert [{'Region': cloud_provider_ec2_account_config['Region'],
                 'VpcName': None,
                 'VpcId': cloud_provider_ec2_account_config['VpcId']}] == result, f"Unexpected return data for get_aws_connectors_in_region {result}"



    finally:
        result, success = CloudProviderManager.terminate_ec2_instance(core_session,
                                                                      cloud_provider_id=cloud_provider_ids[0],
                                                                      iam_account_id=iam_account_ids[0],
                                                                      region=cloud_provider_ec2_account_config['Region'],
                                                                      instance_name=instance_name)

        assert success, f"Failed to terminate ec2 instance {result}"


def test_verify_aws_assume_role_configuration_fail(core_session, cloud_provider_ec2_account_config, live_aws_cloud_provider_and_accounts, core_blessed_session):

    cloud_provider_ids, iam_account_ids, access_key_ids, root_account_id, cloud_provider_name = live_aws_cloud_provider_and_accounts

    result, success = CloudProviderManager.get_ec2_iam_roles(core_session, cloud_provider_ids[0], iam_account_ids[0])
    assert success and result is not None and len(result) > 0, f"Failed to execute get_ec2_iam_roles and retrieve roles {result}"


    result, success, message = CloudProviderManager.verify_aws_assume_role_configuration(session=core_session,
                                                                                         aws_account_id=cloud_provider_ec2_account_config['id'],
                                                                                         external_id=cloud_provider_ec2_account_config['ExternalId'],
                                                                                         role_arn=cloud_provider_ec2_account_config['RoleArn'])

    assert (not success) and 'is not authorized to perform: sts:AssumeRole' in message,\
                         f"Failure in executing verify_aws_assume_role_configuration {result} {message}"


def test_verify_aws_sqs_queue_configuration_fail(core_session, cloud_provider_ec2_account_config, live_aws_cloud_provider_and_accounts):
    cloud_provider_ids, iam_account_ids, access_key_ids, root_account_id, cloud_provider_name = live_aws_cloud_provider_and_accounts
    result, success, message = CloudProviderManager.verify_aws_sqs_queue_configuration(core_session,
                                                                                       cloud_provider_ids[0],
                                                                                       iam_account_ids[0],
                                                                                       "https://sqs.us-east-2.amazonaws.com/215634055688/termination_queue",  # this is not valid for this cloud provider
                                                                                       cloud_provider_ec2_account_config['Region'])

    assert (not success) and 'Access to the resource https://sqs.us-east-2.amazonaws.com/215634055688/termination_queue is denied.' in message, f"Did not received expected failure in verify aws SQS queue configuration {result} {message}"

def test_verify_aws_sqs_queue_configuration_pass(core_session, cloud_provider_ec2_account_config, live_aws_cloud_provider_and_accounts):
    cloud_provider_ids, iam_account_ids, access_key_ids, root_account_id, cloud_provider_name = live_aws_cloud_provider_and_accounts
    result, success, message = CloudProviderManager.verify_aws_sqs_queue_configuration(core_session,
                                                                                       cloud_provider_ids[0],
                                                                                       iam_account_ids[0],
                                                                                       cloud_provider_ec2_account_config['SqsQueue'],
                                                                                       cloud_provider_ec2_account_config['Region'])

    assert success, f"Failure in verify aws SQS queue configuration {result} {message}"


@pytest.mark.smoke
def test_verify_no_unexpected_nulls_from_aws_cloudproviders_accounts(core_session, fake_cloud_provider, fake_cloud_provider_iam_account, fake_cloud_provider_root_account):

    name, desc, cloud_provider_id, cloud_account_id, test_did_cleaning = fake_cloud_provider
    iam_account_id, iam_username = fake_cloud_provider_iam_account
    root_account_id, root_username, root_password, root_cloud_provider_id, test_did_cleaning = fake_cloud_provider_root_account

    for acc_id, acc_username in [(iam_account_id, iam_username), (root_account_id, root_username)]:
        result, success = ResourceManager.get_account_information(core_session, acc_id)
        msg = f"Incorrect or incomplete information returned from get_account_information {result}"
        assert success and 'VaultAccount' in result, msg
        assert result['VaultAccount'] is not None and 'Row' in result['VaultAccount'], msg
        assert result['VaultAccount']['Row']['User'] == acc_username, msg
        assert 'RelatedResource' in result and result['RelatedResource'] is not None, msg
        assert 'Rsop' in result and 'EnableUnmanagedPasswordRotationReminder' in result['Rsop'], msg
        assert 'Workflow' in result and 'WorkflowApprover' in result['Workflow'], msg
        assert 'Row' in result['RelatedResource'], msg
        assert 'ID' in result['RelatedResource']['Row'], msg
        assert result['RelatedResource']['Row']['ID'] == cloud_provider_id, msg
