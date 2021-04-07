import pytest
#  Tests the computer and account management REST APIs in ServerManageController
import logging
import json
from Utils.guid import guid
from Shared.API.secret import update_secret, create_text_secret, request_secret_upload_url, upload_secret_file_in_chunks,get_secret_contents

logger = logging.getLogger("test")

pytestmark = [pytest.mark.daily, pytest.mark.smoke, pytest.mark.cps, pytest.mark.secrets]

"""
Tests:
    1. test_request_secret_upload
    2. test_request_secret_upload_invalid_filesize
    3. test_invalid_secret_upload
    4. test_block_uploads
    5. test_double_blocklist_invalid
    6. test_add_too_large_secret
    7. test_update_secret

    Testrail Link:
    https://testrail.centrify.com/index.php?/suites/view/5&group_by=cases:section_id&group_order=asc&group_id=4271
"""


@pytest.mark.api
@pytest.mark.pas
def test_request_secret_upload(core_session):
    """Tests Uploading secret into chunks
        Steps:
            1. Request the Upload
                -Verify Success
            2. Upload the file in chunks
                -Verify Success
    """
    logger.info("Running Test for Uploading Secrets File (Expected == Success")
    request_result, request_success = request_secret_upload_url(core_session, "test_secrets_small.txt", 56)
    assert request_result, "Request Secret Upload Url Failed"
    upload_result, upload_success = upload_secret_file_in_chunks(core_session, request_result['FilePath'], "abcde")
    upload_result_final, upload_success_final = upload_secret_file_in_chunks(core_session, request_result['FilePath'], "", True)
    assert upload_success, f"Unable to upload secret file in chucks to filepath {request_result['FilePath']}"
    assert upload_success_final, f"Unable to upload Final secret file in chucks to filepath {request_result['FilePath']}"


@pytest.mark.pas
def test_request_secret_upload_invalid_filesize(core_session):
    """Tests Uploading secret with invalid parameters
        Steps:
            1. Request the Upload with a str (junk) filesize
                -Verify Failure
            2. Request the Upload with a zero filesize
                -Verify Failure
            3. Request the Upload with a filesize too large over 5MB
                -Verify Failure
    """

    request_result_junk, request_success_junk = request_secret_upload_url(core_session, "test_secrets_small.txt", "junk_file_size")
    assert not request_success_junk, f"Was somehow able to upload a file with a bogus filesize, response {json.dumps(request_result_junk)}"

    request_result_empty , request_success_empty = request_secret_upload_url(core_session, "test_secrets_small.txt", 0) #Can't Be Empty
    assert not request_success_empty, f"Was somehow able to upload a file with a 0 filesize, response {json.dumps(request_success_empty)}"


    request_result_too_large, request_success_too_large = request_secret_upload_url(core_session, "test_secrets_small.txt", 50000001) #Too Big 5MB
    assert not request_success_too_large, f"Was somehow able to upload a file with a Massive (>5MB) filesize, response {json.dumps(request_success_too_large)}"


@pytest.mark.pas
def test_invalid_secret_upload(core_session):
    """Testing invalid filepath to upload
            Steps:
            1. Request the Upload with a filesize too large over 5MB
                -Verify Failure
    """

    upload_result, upload_success = upload_secret_file_in_chunks(core_session, "invalid_filepath", "abcde")
    assert not upload_success, f"Was somehow able to upload file with an invalid file_path, response {json.dumps(upload_result)}"


@pytest.mark.pas
def test_block_uploads(core_session):
    """Testing Uploading the secrets into different blocks
            Steps:
            1. Request the Upload
                -Verify Success
            2. Upload the file in many different small chunks
                -Verify Success
    """
    logger.info("Running Test for Uploading Secrets File (Expected == Success")
    request_result, request_success = request_secret_upload_url(core_session, "test_secrets_small.txt", 20)
    assert request_result, "Request Secret Upload Url Failed"
    upload_result, upload_success = upload_secret_file_in_chunks(core_session, request_result['FilePath'], "abcde")
    upload_result_block1, upload_success_block1 = upload_secret_file_in_chunks(core_session, request_result['FilePath'] + '&comp=block', "a")
    upload_result_block2, upload_success_block2 = upload_secret_file_in_chunks(core_session, request_result['FilePath'] + '&comp=block', "b")
    upload_result_final, upload_success_final= upload_secret_file_in_chunks(core_session, request_result['FilePath'], "", True)
    assert upload_success, f"Unable to upload secret file in chucks to filepath {request_result['FilePath']}"
    assert upload_result_block1, f"Unable to upload block 1 to secret file in chucks to filepath {request_result['FilePath']}"
    assert upload_result_block2, f"Unable to upload block 1 secret file in chucks to filepath {request_result['FilePath']}"
    assert upload_success_final, f"Unable to upload final block secret file in chucks to filepath {request_result['FilePath']}"


@pytest.mark.pas
def test_double_blocklist_invalid(core_session):
    """Test makes sure when we call query to say end of upload we mean it and it cannot upload anymore
      Steps:
        1. Request the Upload
            -Verify Success
        2. Upload the file in many different small chunks
            -Verify Success
        2. Try to Upload again with nothgin
            -Verify Success
    """
    logger.info("Running Test for Uploading Secrets File (Expected == Success")
    request_result, request_success = request_secret_upload_url(core_session, "test_secrets_small.txt", 56)
    assert request_result, "Request Secret Upload Url Failed"
    upload_result_final, upload_success_final = upload_secret_file_in_chunks(core_session, request_result['FilePath'], "", True)
    assert upload_success_final, f"Unable to upload block 1 to secret file in chucks to filepath {request_result['FilePath']}"
    upload_result_invalid, upload_success_invalid = upload_secret_file_in_chunks(core_session, request_result['FilePath'], "", True)
    assert not upload_success_invalid, f"Was able to upload nothign to file as final block, shoud fail!"


@pytest.mark.pas
def test_add_too_large_secret(core_session):
    """Testing to make sure some invalid secrets can not be addded
        1. Test Secret Cannot be too large over Over 3MB
            -Verify Failure
    """
    str_too_long = ' '
    for i in range(0,24024):
        str_too_long += 'AAAAAAAAAA'
    add_sec_success, add_sec_parms, add_sec_result = create_text_secret(core_session, 'sname' + guid(), str_too_long)
    assert not add_sec_success, "Was able to create a secret that was far to large (>5MB)"


@pytest.mark.pas
def test_update_secret(core_session, text_secret):
    """Test updating A secret
        Steps:
            Pre: Get a secret
            1. Update the secret with new information
                -Verify Success
            2. Get the secret information
                -Verify Success
    """
    new_name = "test_update_new_name" + guid()
    update_res = update_secret(core_session, text_secret['ID'], new_name,
                                                                 "new_description: TheFountainOfYouthIsJustGreenTea")

    assert update_res['success'], f"Failed to update secret with ID {text_secret['ID']}"

    get_result, get_success, when, text = get_secret_contents(core_session, update_res['Result']['ID'])
    assert get_success, f"Failed to get the secret Contents for {text_secret['ID']}"
    assert get_result['Description'] ==  "new_description: TheFountainOfYouthIsJustGreenTea", f"Description for secret did not match it was new_description: TheFountainOfYouthIsJustGreenTea but instead came back as {get_result['Description']}"
    assert get_result['SecretName'] ==  new_name, f"Name for secret did not match, it was{new_name} but instead came back as {get_result['SecretName']}"
    assert get_result['Type'] ==  "Text", "Secret Type for that ID was File Instead of Text"