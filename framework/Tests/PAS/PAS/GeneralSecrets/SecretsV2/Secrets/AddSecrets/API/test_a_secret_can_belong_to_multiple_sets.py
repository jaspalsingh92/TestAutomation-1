import pytest
import logging
from Shared.API.redrock import RedrockController
from Shared.API.sets import SetsManager
from Utils.guid import guid

logger = logging.getLogger('test')


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.bhavna
@pytest.mark.pasapi
def test_a_secret_can_belong_to_multiple_sets(core_session,
                                              create_set_manual,
                                              added_secrets,
                                              pas_general_secrets,
                                              cleanup_secrets_and_folders, set_cleaner):

    """test method to check that a secret belongs to multiple set"""
    added_secret_id, added_secret_name = added_secrets
    set_params = pas_general_secrets
    prefix = guid()
    set_success, set_id = create_set_manual

    """Api to create another set manually"""
    success, setid = SetsManager.create_manual_collection(core_session, prefix + set_params['set_name'], 'DataVault')
    logger.info(f'creating manual set:{success} with setid as: {setid}')
    assert success is True, f'Failed to create manual set with one initial member {setid}'

    text_secret_id = added_secret_id[0]

    """Api to add set to existing secret"""
    added_to_set_success, added_to_set_result = SetsManager.update_members_collection(core_session,
                                                                                      'add',
                                                                                      [text_secret_id],
                                                                                      "DataVault", set_id)
    assert added_to_set_success, f'Failed to add secret to set{added_to_set_result}'
    logger.info(f'Adding secret to one set: {added_to_set_success}')

    """Api to add another set to same secret"""
    added_to_set_success, added_to_set_result = SetsManager.update_members_collection(core_session, 'add',
                                                                                      [text_secret_id], "DataVault",
                                                                                      setid)
    assert added_to_set_success, f'Failed to add secret to set{added_to_set_result}'
    logger.info(f'Adding secret to another set: {added_to_set_success}')

    """Redrock query to fetch set related details"""
    get_set_1 = RedrockController.verify_set_secret(core_session, set_id, text_secret_id)
    logger.info(f'{get_set_1}')
    logger.info(f'Verifiying secret name {get_set_1[0]["Row"]["SecretName"]} in '
                f'set 1 with ID {get_set_1[0]["Row"]["CollectionID"]} ')

    get_set_2 = RedrockController.verify_set_secret(core_session, setid, text_secret_id)
    logger.info(
        f'Verifiying secret name {get_set_2[0]["Row"]["SecretName"]} in another '
        f'set with ID {get_set_2[0]["Row"]["CollectionID"]}')

    """to verify that same secret is added to multiple sets"""
    text_to_verify = 'secret1'
    assert (text_to_verify in get_set_1[0]["Row"]["SecretName"]) and (
            text_to_verify in get_set_2[0]["Row"]["SecretName"]), f'secret doesnt belong to multiple set'
    set_cleaner.append(setid)
