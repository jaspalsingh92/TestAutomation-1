import logging

import pytest

from Shared.API.cloud_provider import CloudProviderType

logger = logging.getLogger("test")


pytestmark = [pytest.mark.api, pytest.mark.cloudprovider, pytest.mark.azure]

@pytest.mark.skip("Azure not implemented")
@pytest.mark.parametrize('cloud_provider_type', [CloudProviderType.AZURE], indirect=True)
def test_create_azure_cloud_provider_no_cleanup(fake_cloud_provider):
    name, desc, cloud_provider_id, cloud_account_id, _test_deleted = fake_cloud_provider
    _test_deleted()