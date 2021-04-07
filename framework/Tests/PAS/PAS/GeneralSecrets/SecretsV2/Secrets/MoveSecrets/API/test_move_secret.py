import pytest
#  Tests the computer and account management REST APIs in ServerManageController
import logging
import json
import datetime

from Utils.guid import guid
from Shared.API.secret import get_folder, del_folder, move_secret, create_secret_folder, move_folder, \
    give_user_permissions_to_folder

logger = logging.getLogger("test")

pytestmark = [pytest.mark.daily, pytest.mark.smoke, pytest.mark.cps, pytest.mark.secrets]

"""Tests:
    1. test_get_folder
    2. test_heirachy_delete
    3. test_move_secret_basic_id
    4. test_move_secret_basic_name
    5. test_move_folders
    6. test_move_secret_to_invalid_location
    7. test_move_permissions

    Testrail Links:
        https://testrail.centrify.com/index.php?/suites/view/5&group_by=cases:section_id&group_order=asc&group_id=6744
        https://testrail.centrify.com/index.php?/suites/view/5&group_by=cases:section_id&group_order=asc&group_id=816
        https://testrail.centrify.com/index.php?/suites/view/5&group_by=cases:section_id&group_order=asc&group_id=6745
"""


@pytest.mark.api
@pytest.mark.pas
def test_get_folder(core_session, secret_folder):
    """ Testing Adding and deleting Folder
        Steps:
            1. Get the folder information
                -Verify Success and ensure information
    """

    get_folder_result = get_folder(core_session, secret_folder['ID'])
    assert get_folder_result['success'], f"Getting Folder with Folder ID {secret_folder['ID']} failed, response {json.dumps(get_folder_result['response'])}"
    assert get_folder_result['Result']['Results'][0]['Row']['Name'] == secret_folder['Name'],\
        f"Folder name {secret_folder['Name']} did not match {get_folder_result['Result']['Results'][0]['Row']['Name']}"
    assert get_folder_result['Result']['Results'][0]['Row']['Description'] == secret_folder['Description'], \
        f"Folder Description{secret_folder['Description']} did not match {get_folder_result['Result']['Results'][0]['Row']['Description']}"


@pytest.mark.api
@pytest.mark.pas
def test_heirachy_delete(core_session, nested_secret_folder):
    """Ensures that a parent cannot be deleted with a child inside
        Steps:
            Pre:.Get a folder in a folder
            1. Try to delete outer folder
                -Verify Failure
    """
    parent_folder, child_folder = nested_secret_folder
    del_folder_res = del_folder(core_session, parent_folder['ID'])
    assert not del_folder_res['success'], f"Deleted Folder {parent_folder['Name']} with Child inside, should be impossible, " \
        f"response {json.dumps(del_folder_res['response'])}"


@pytest.mark.api
@pytest.mark.pas
def test_move_secret_basic_id(core_session, secret_folder, text_secret):
    """Tests that movign a secret works
        Steps:
            1. Move a secret
                -Verify Success
            2. Get info
                - Verify information is correct
    """

    move_result = move_secret(core_session, text_secret['ID'], secret_folder['ID'])
    assert move_result['success'], f"Was unable to move secret {text_secret['SecretName']} to folder {secret_folder['Name']}"


@pytest.mark.api
@pytest.mark.pas
def test_move_secret_basic_name(core_session, secret_folder, text_secret):
    """Tests that movign a secret works into a deep folder
        Steps:
            1. Move a secret
                -Verify Success
            2. Get info
                - Verify information is correct
    """
    move_result = move_secret(core_session, text_secret['ID'], secret_folder['Name'], True)
    assert move_result['success'], f"Failed to move secret {text_secret['SecretName']} to folder {secret_folder['Name']}"


@pytest.mark.api
@pytest.mark.pas
def test_move_folders(core_session, secret_folder, cleanup_secrets_and_folders):
    """Tests that movign a secret works
        Steps:
            1. Add a folder
                -Verify Success
            2. Move the folder
                -Verify Success
            3. Get info
                - Verify information is correct
    """

    add_folder_success, folder_params, folder_id = create_secret_folder(core_session, "FolderName" + guid() + str(datetime.time()))
    assert add_folder_success, f"User was able to create a folder in a folder they did not create, should have failed, response {json.dumps(folder_params)}"

    cleanup_secrets_and_folders[1].append(folder_id)

    move_result = move_folder(core_session, folder_id, secret_folder['ID'])
    assert move_result['success'], f"Failed to move secret folder {folder_params['Name']} to folder {secret_folder['Name']}, resposne {json.dumps(move_result)}"

    move_result = move_folder(core_session, folder_id, "")
    assert move_result['success'], f"Failed to move secret folder {folder_params['Name']} to folder {secret_folder['Name']}, resposne {json.dumps(move_result)}"


@pytest.mark.api
@pytest.mark.pas
def test_move_secret_to_invalid_location(core_session, text_secret, secret_folder):       # vv Should be name not id vv
    """Tests that movign a secret works
        Steps:
            1. Move Secret with invalid target id
                -Verify Failure
            2. Move folder using the name, but wrong call
                -Verify Failure
            3. Move to with a bogus secret it
                -Verify Failure
    """
    move_result = move_secret(core_session, text_secret['ID'], secret_folder['ID'], True)
    assert not move_result['success'], "Was able to move secret to folder using id in name parameter, should be impossible"

    move_result = move_secret(core_session, text_secret['ID'], secret_folder['Name'])
    assert not move_result['success'], "Was able to move secret to folder using name in id parameter, should be impossible"

    move_result = move_secret(core_session, "BogusSecretId", secret_folder['ID'])
    assert not move_result['success'], f"Was able to move BogusSecretId into folder {secret_folder['ID']}"


@pytest.mark.api
@pytest.mark.pas
def test_move_permissions(core_session, get_admin_user_function, cleanup_secrets_and_folders, secret_folder):
    """Tests moving folders with permissions

        Steps:
            1. Have the admin add a folder
                -Verify Succes
            2.Have core set permissions on seperate folder
                -Verify Success
            3. Try to let admin move an item into that folder
                -Verify Failure (No Edit Permission yet)
            4. Give user Edit Permission
                -Verify Success
            5. Let admin try to move them folders
                -Verify Success

    """
    admin_sesh, admin_user = get_admin_user_function
    fol_name = 'test_folder' + guid()

    add_folder_success, folder_params, folder_id = create_secret_folder(core_session, fol_name)
    assert add_folder_success, f"User was able to create a folder in a folder they did not create, should have failed, response {json.dumps(folder_params)}"

    cleanup_secrets_and_folders[1].append(folder_id)

    give_perm_result = give_user_permissions_to_folder(core_session, admin_user.get_login_name(),
                                                       admin_user.get_id(),
                                                       secret_folder['ID'], "View,Edit,Grant")

    assert give_perm_result['success'], f"Core Session Should have been able to give User Permission to folder {secret_folder['Name']}"

    move_result = move_folder(admin_sesh, secret_folder['ID'], folder_id)
    assert not move_result['success']

    give_perm_result = give_user_permissions_to_folder(core_session, admin_user.get_login_name(),
                                                       admin_user.get_id(), secret_folder['ID'],
                                                       "View,Edit,Grant")

    assert give_perm_result['success'], f"Core Session Should have been able to give User Permission to folder {secret_folder['Name']}"

    give_perm_result = give_user_permissions_to_folder(core_session, admin_user.get_login_name(),
                                                       admin_user.get_id(), folder_id,
                                                       "View,Add")

    assert give_perm_result['success'], f"Core Session Should have been able to give User Permission to folder {secret_folder['Name']}"

    move_result = move_folder(admin_sesh, secret_folder['ID'], folder_id)
    assert move_result['success'], f"User should have been able to move folder {secret_folder['ID']} to {folder_id}, response {json.dumps(move_result)}"
