import pytest
import json
import logging
from Shared.endpoint_manager import EndPoints
from Shared.API.secret import create_file_type_secret, get_file_secret_contents, \
    find_secret_by_id, give_user_permissions_to_folder, create_secret_folder, get_users_effective_folder_permissions, \
    create_text_secret_within_folder
from Shared.API.sets import SetsManager
from Utils.assets import get_asset_path
from Utils.guid import guid

logger = logging.getLogger('test')

pytestmark = [pytest.mark.cps, pytest.mark.secrets]


@pytest.fixture(scope="function")
def folder_cleaner(core_session):
    folder_ids = []
    yield folder_ids
    for folder_id in folder_ids:
        result = core_session.post(EndPoints.SECRET_FOLDER_DELETE, {'ID': folder_id}).json()
        assert result['success'] is True, f'Failed to cleanup secret folder  {json.dumps(result)}'


@pytest.fixture(scope="function")
def set_cleaner(core_session):
    set_ids = []
    yield set_ids
    for set_id in set_ids:
        success, result = SetsManager.delete_collection(core_session, set_id)
        assert success is True, f'Failed to cleanup manual set. Not the end of the world but sub-optimal. {json.dumps(result)}'


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.daily
@pytest.mark.parametrize("administrative_right", ['Privileged Access Service Power User',
                                                  'Privileged Access Service Administrator',
                                                  'Privileged Access Service User',
                                                  'System Administrator'])
def test_create_text_secret_with_valid_parameters_allowed_admin_rights(users_and_roles, secret_cleaner, administrative_right):
    session = users_and_roles.get_session_for_user(administrative_right)
    secret_prefix = guid()
    secret_parameters = {
        'SecretName': secret_prefix + '_test_text_secret',
        'SecretText': secret_prefix + ' my secret',
        'Type': 'Text',
        'Description': secret_prefix + ' my secret description'
    }

    logger.info(f'Creating secret {secret_parameters["SecretName"]}')

    result = session.post(EndPoints.SECRET_ADD, secret_parameters).json()
    assert result['success'] is True, f'{EndPoints.SECRET_ADD} failed for {secret_parameters["SecretName"]}, response {json.dumps(result)}'
    secret_id = result['Result']
    secret_cleaner.append(secret_id)

    secret_data = find_secret_by_id(session, secret_id)
    assert secret_data is not False, 'Could not find secret in return results from secret get endpoint'
    assert secret_data['SecretName'] == secret_parameters['SecretName'], 'Name stored incorrectly'
    assert 'SecretText' not in secret_data, 'The text secret\'s secret content should not be included when getting a secret folder contents'
    assert secret_data['Description'] == secret_parameters['Description'], 'Secret\'s description stored incorrectly'


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.smoke
@pytest.mark.smokes
@pytest.mark.parametrize("administrative_right", ['Privileged Access Service Power User',
                                                  'Privileged Access Service Administrator',
                                                  'Privileged Access Service User',
                                                  'System Administrator'])
def test_create_file_secret_with_valid_parameters_allowed_admin_rights(users_and_roles, secret_cleaner, administrative_right):
    session = users_and_roles.get_session_for_user(administrative_right)
    secret_prefix = guid()
    secret_parameters = {
        'SecretName': secret_prefix + '_test_file_secret',
        'Description': secret_prefix + ' my secret description'
    }

    logger.info(f'Creating secret {secret_parameters["SecretName"]}')

    local_secret_path = get_asset_path('test_secret_upload.txt')
    result = create_file_type_secret(session, secret_parameters, local_secret_path)
    assert result['success'] is True, f'Failed to create file type secret {secret_parameters["SecretName"]}, response {json.dumps(result)}'
    secret_id = result['Result']
    secret_cleaner.append(secret_id)

    secret_data = find_secret_by_id(session, secret_id)
    assert secret_data is not False, 'Could not find secret in return results from secret get endpoint'

    secret_file_contents = get_file_secret_contents(session, secret_id)
    secret_local_file_contents = open(local_secret_path, 'r').read()
    assert secret_file_contents == secret_local_file_contents, 'The remote secret contents do not match the local secret contents'


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.daily
@pytest.mark.parametrize("administrative_right", ['Admin Portal Login',
                                                  'Application Management',
                                                  'Computer Login and Privilege Elevation',
                                                  'Federation Management',
                                                  'MFA Unlock',
                                                  'Query as a different user',
                                                  'Radius Management',
                                                  'Read Only System Administration',
                                                  'Register and Administer Connectors',
                                                  'Report Management',
                                                  'Role Management',
                                                  'System Enrollment',
                                                  'User Management',
                                                  None])
def test_create_text_secret_with_valid_parameters_disallowed_admin_rights(users_and_roles, secret_cleaner, administrative_right):
    session = users_and_roles.get_session_for_user(administrative_right)
    secret_prefix = guid()
    secret_parameters = {
        'SecretName': secret_prefix + '_test_text_secret',
        'SecretText': secret_prefix + ' my secret',
        'Type': 'Text',
        'Description': secret_prefix + ' my secret description'
    }

    logger.info(f'Creating secret {secret_parameters["SecretName"]}')
    result = session.post(EndPoints.SECRET_ADD, secret_parameters).json()
    assert result['success'] is False, f'A user in a role that should not be able to create a secret was allowed to create the secret {json.dumps(result)}'


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.daily
@pytest.mark.parametrize("administrative_right", ['Admin Portal Login',
                                                  'Application Management',
                                                  'Computer Login and Privilege Elevation',
                                                  'Federation Management',
                                                  'MFA Unlock',
                                                  'Query as a different user',
                                                  'Radius Management',
                                                  'Read Only System Administration',
                                                  'Register and Administer Connectors',
                                                  'Report Management',
                                                  'Role Management',
                                                  'System Enrollment',
                                                  'User Management',
                                                  None])
def test_create_file_secret_with_valid_parameters_disallowed_admin_rights(users_and_roles, secret_cleaner, administrative_right):
    session = users_and_roles.get_session_for_user(administrative_right)
    secret_prefix = guid()
    secret_parameters = {
        'SecretName': secret_prefix + '_test_file_secret',
        'Description': secret_prefix + ' my secret description'
    }

    logger.info(f'Creating secret {secret_parameters["SecretName"]}')
    local_secret_path = get_asset_path('test_secret_upload.txt')
    result = create_file_type_secret(session, secret_parameters, local_secret_path)
    assert result['success'] is False, f'A user in a role that should not be able to create a secret was allowed to create the secret {json.dumps(result)}'


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.smoke
@pytest.mark.parametrize("invalid_case", ['<', '&#', 'blank'])
def test_create_secret_invalid_name(core_session, invalid_case):
    secret_prefix = guid()
    if invalid_case == 'blank':
        secret_parameters = {
            'SecretName': '',
            'Description': 'Secret with invalid character in name',
            'SecretText': secret_prefix + ' my secret',
            'Type': 'Text'
        }
    else:
        secret_parameters = {
            'SecretName': secret_prefix + invalid_case + 'foo',
            'Description': 'Secret with invalid character in name',
            'SecretText': secret_prefix + ' my secret',
            'Type': 'Text'
        }

    logger.info(f'Creating text secret with invalid character in name {secret_parameters["SecretName"]}')
    result = core_session.post(EndPoints.SECRET_ADD, secret_parameters).json()
    assert result['success'] is False, f'Able to create a secret with invalid parameters. {json.dumps(secret_parameters)} {json.dumps(result)}'


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.smoke
def test_create_secret_duplicate_name(core_session, text_secret):
    logger.info(f'Creating text secret with duplicate name {text_secret["SecretName"]}')
    secret_parameters = {
        'SecretName': text_secret['SecretName'],
        'SecretText': text_secret['SecretText'],
        'Type': 'Text'
    }
    result = core_session.post(EndPoints.SECRET_ADD, secret_parameters).json()
    assert result['success'] is False, f'Able to create a secret with duplicate name. {json.dumps(secret_parameters)} {json.dumps(result)}'


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.daily
def test_create_secret_invalid_folder_id(core_session):
    secret_prefix = guid()
    secret_parameters = {
        'SecretName': secret_prefix + 'foo',
        'Description': 'Secret with invalid character in name',
        'SecretText': secret_prefix + ' my secret',
        'Type': 'Text',
        'FolderId': 'bar'
    }

    logger.info(f'Creating text secret with invalid folder id {secret_parameters["SecretName"]}')
    result = core_session.post(EndPoints.SECRET_ADD, secret_parameters).json()
    assert result['success'] is False, f'Able to create a secret with invalid folder id. {json.dumps(secret_parameters)} {json.dumps(result)}'


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.smoke
def test_create_secret_valid_folder_id(core_session, secret_folder, secret_cleaner):
    secret_prefix = guid()
    secret_parameters = {
        'SecretName': secret_prefix + 'foo',
        'Description': 'Secret with invalid character in name',
        'Type': 'Text',
        'SecretText': secret_prefix + ' my secret',
        'FolderId': secret_folder['ID']
    }

    logger.info(f'Creating text secret with valid folder id {secret_parameters["SecretName"]}')
    result = core_session.post(EndPoints.SECRET_ADD, secret_parameters).json()
    assert result['success'] is True, f'Unable to create a secret with invalid folder id. {json.dumps(secret_parameters)} {json.dumps(result)}'
    secret_cleaner.append(result['Result'])


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.smoke
@pytest.mark.parametrize("separator", ['\\', '/'])
def test_create_secret_where_folder_name_in_secret_name(core_session, separator, secret_folder, secret_cleaner):
    secret_prefix = guid()
    secret_parameters = {
        'SecretName': secret_folder['Name'] + separator + secret_prefix + 'foo',
        'Description': 'Secret with invalid character in name',
        'Type': 'Text',
        'SecretText': secret_prefix + ' my secret'
    }

    logger.info(f'Creating text secret with folder name in secret name {secret_parameters["SecretName"]}')
    result = core_session.post(EndPoints.SECRET_ADD, secret_parameters).json()
    assert result['success'] is True, f'Unable to create a secret with valid folder name in secret name. {json.dumps(secret_parameters)} {json.dumps(result)}'
    secret_cleaner.append(result['Result'])


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.smoke
def test_create_secret_where_folder_name_in_secret_name_with_back_and_forward_slash(core_session, nested_secret_folder, secret_cleaner):
    secret_prefix = guid()
    grand_parent_folder, parent_folder = nested_secret_folder
    secret_parameters = {
        'SecretName': grand_parent_folder['Name'] + '/' + parent_folder['Name'] + '\\' + secret_prefix + 'foo',
        'Description': 'Secret with invalid character in name',
        'Type': 'Text',
        'SecretText': secret_prefix + ' my secret'
    }

    logger.info(f'Creating text secret with folder name in secret name {secret_parameters["SecretName"]}')
    result = core_session.post(EndPoints.SECRET_ADD, secret_parameters).json()
    assert result['success'] is True, f'Unable to create a secret with valid folder name in secret name. {json.dumps(secret_parameters)} {json.dumps(result)}'
    secret_id = result['Result']
    secret_cleaner.append(secret_id)

    found_folder = find_secret_by_id(core_session, secret_id, parent_folder['ID'])
    assert found_folder is not None, 'Unable to find newly created folder inside parent folder'


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.smoke
def test_create_folder_valid_parameters(core_session, folder_cleaner):
    secret_prefix = guid()
    secret_folder_parameters = {
        'Name': secret_prefix + ' folder',
        'Description': secret_prefix + ' folder description'
    }

    logger.info('Creating secret folder with valid parameters')
    result = core_session.post(EndPoints.SECRET_FOLDER_CREATE, secret_folder_parameters).json()
    assert result['success'] is True, f'A user in a role that should not be able to create a secret was allowed to create the secret {json.dumps(result)}'
    folder_cleaner.append(result['Result'])


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.smoke
@pytest.mark.parametrize("invalid_case", ['<', '&#', 'blank'])
def test_create_secret_folder_invalid_name(core_session, invalid_case):
    secret_prefix = guid()
    if invalid_case == 'blank':
        secret_folder_parameters = {
            'Name': '',
            'Description': 'Secret with invalid character in name'
        }
    else:
        secret_folder_parameters = {
            'Name': secret_prefix + invalid_case + 'foo',
            'Description': 'Secret with invalid character in name'
        }

    logger.info(f'Creating secret folder with invalid character in name {secret_folder_parameters["Name"]}')
    result = core_session.post(EndPoints.SECRET_FOLDER_CREATE, secret_folder_parameters).json()
    assert result['success'] is False, f'Able to create a secret folder with invalid parameters. {json.dumps(secret_folder_parameters)} {json.dumps(result)}'


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.smoke
def test_create_folder_in_another_folder(core_session, secret_folder, folder_cleaner):
    secret_prefix = guid()
    secret_folder_parameters = {
        'Name': secret_prefix + 'nested_folder',
        'Description': 'Secret with invalid character in name',
        'Parent': secret_folder['ID']
    }

    logger.info(f'Creating secret folder in a parent folder {json.dumps(secret_folder_parameters)}')
    result = core_session.post(EndPoints.SECRET_FOLDER_CREATE, secret_folder_parameters).json()
    assert result['success'] is True, f'Unable to create a secret folder inside another folder. {json.dumps(secret_folder_parameters)} {json.dumps(result)}'

    nested_folder_id = result['Result']
    found_folder = find_secret_by_id(core_session, nested_folder_id, secret_folder['ID'])
    assert found_folder is not None, 'Unable to find newly created folder inside parent folder'

    folder_cleaner.append(nested_folder_id)


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.smoke
def test_create_secret_in_folder_no_permissions(users_and_roles, secret_folder):
    # secret folder was created by administrator account so should not
    # be able to add a secret to it as a different user.
    application_management_session = users_and_roles.get_session_for_user('Privileged Access Service Power User')

    secret_prefix = guid()

    folder_id = secret_folder['ID']

    secret_parameters = {
        'SecretName': secret_prefix + '_test_text_secret',
        'SecretText': secret_prefix + ' my secret',
        'Type': 'Text',
        'Description': secret_prefix + ' my secret description',
        'FolderId': folder_id
    }

    logger.info(f'Creating secret in other user\'s folder with no permissions {secret_parameters["SecretName"]}')
    result = application_management_session.post(EndPoints.SECRET_ADD, secret_parameters).json()
    assert result['success'] is False, f'Able to create a secret in another user\'s folder. {json.dumps(secret_parameters)} {json.dumps(result)}'


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.smoke
def test_create_secret_in_folder_with_permissions(core_session, users_and_roles, secret_folder, secret_cleaner):
    # secret folder was created by administrator account so should not
    # be able to add a secret to it as a different user.
    application_management_user = users_and_roles.get_user('Privileged Access Service Power User')
    application_management_session = users_and_roles.get_session_for_user('Privileged Access Service Power User')

    user_name = application_management_user.get_login_name()
    user_id = application_management_user.get_id()
    folder_id = secret_folder['ID']

    give_user_permissions_to_folder(core_session, user_name, user_id, folder_id, 'View,Add')

    secret_prefix = guid()

    secret_parameters = {
        'SecretName': secret_prefix + '_test_text_secret',
        'SecretText': secret_prefix + ' my secret',
        'Type': 'Text',
        'Description': secret_prefix + ' my secret description',
        'FolderId': folder_id
    }

    logger.info(f'Creating secret in other user\'s folder with no permissions {secret_parameters["SecretName"]}')
    result = application_management_session.post(EndPoints.SECRET_ADD, secret_parameters).json()
    assert result['success'] is True, f'Unable to create a secret in another user\'s folder when given permissions to. {json.dumps(secret_parameters)} {json.dumps(result)}'
    secret_cleaner.append(result['Result'])


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.smoke
def test_system_administrator_permissions_on_other_users_folder(core_session, users_and_roles, folder_cleaner):
    secret_prefix = guid()
    application_management_session = users_and_roles.get_session_for_user('Privileged Access Service Power User')
    success, parameters, folder_id = create_secret_folder(application_management_session, secret_prefix + 'folder')
    assert success is True, 'Failed to create secret folder as PAS Power User'
    folder_cleaner.append(folder_id)

    grants = get_users_effective_folder_permissions(core_session, folder_id)
    expected_grants = ["Grant", "View", "Edit", "Delete"]
    for expected in expected_grants:
        assert expected in grants, f'Expected grant of {expected} not found in list of grants for admin. {json.dumps(grants)}'


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.daily
def test_secret_in_different_folders_with_same_name(core_session, nested_secret_folder, secret_cleaner):
    grand_parent_folder, parent_folder = nested_secret_folder
    secret_name = guid() + ' my secret'
    secret_text = 'my secret'

    success, secret_id = create_text_secret_within_folder(core_session, secret_name, secret_text, 'description', grand_parent_folder['ID'])
    assert success is True, f'Failed to create secret in first folder. {secret_id}'
    secret_cleaner.append(secret_id)

    success, secret_id = create_text_secret_within_folder(core_session, secret_name, secret_text, 'description', parent_folder['ID'])
    assert success is True, f'Failed to create secret in second folder with same name as secret in first folder. {secret_id}'
    secret_cleaner.append(secret_id)


@pytest.mark.api
@pytest.mark.pas
@pytest.mark.smoke
def test_secret_added_to_set(core_session, text_secret, set_cleaner):
    set_1_name = guid() + ' Secret Set'
    set_2_name = guid() + ' Secret Set'

    success, set_1_id = SetsManager.create_manual_collection(core_session, set_1_name,
                                                             'DataVault', object_ids=[text_secret['ID']])
    assert success is True, f'Failed to create manual set with one initial member {set_1_id}'
    set_cleaner.append(set_1_id)
    success, set_2_id = SetsManager.create_manual_collection(core_session, set_2_name,
                                                             'DataVault', object_ids=[text_secret['ID']])
    assert success is True, f'Failed to create manual set with one initial member {set_2_id}'
    set_cleaner.append(set_2_id)

    results = SetsManager.search_object_in_set(core_session, set_1_name, text_secret['SecretName'],
                                               'DataVault', search_columns=['SecretName'])
    assert results[0]['Row']['ID'] == text_secret['ID'], 'Searching for new secret in set 1 and could not find it. {json.dumps(results)}'

    results = SetsManager.search_object_in_set(core_session, set_2_name,
                                               text_secret['SecretName'], 'DataVault', search_columns=['SecretName'])
    assert results[0]['Row']['ID'] == text_secret['ID'], \
        f'Searching for new secret in set 2 and could not find it. {json.dumps(results)}'
