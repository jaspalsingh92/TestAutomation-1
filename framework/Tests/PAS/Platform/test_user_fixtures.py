import logging
import pytest
import time

from Shared.API.users import UserManager

logger = logging.getLogger("test")

pytestmark = [pytest.mark.daily, pytest.mark.platform, pytest.mark.ui, pytest.mark.user_fixtures]


def check_rights(session, ui_user, api_user, expected_rights):
    assert ui_user == api_user, f'UI and API fixtures should return the same user'
    response = UserManager.get_user_role_rights(session, api_user.get_id())
    if expected_rights[0] is not None:
        assert response['Result']['Count'] == 2, f'User should be in everybody role, and a role with admin rights'
    else:
        assert response['Result']['Count'] == 1, f'User should be in everybody role only'

    rights_role_found = False
    everbody_found = False
    for result in response['Result']['Results']:
        row = result['Row']
        if len(row['AdministrativeRights']) > 0:
            rights_found = list(map(lambda right: right['Description'], row['AdministrativeRights']))
            rights_found.sort()
            expected_rights.sort()
            assert rights_found == expected_rights, f'Role with administrative rights does not have expected rights {expected_rights}, instead has {rights_found}'
            rights_role_found = True
        elif row['Name'] == 'Everybody':
            everbody_found = True
        else:
            assert False, f'Unexpected role found {row}'

    if expected_rights[0] is not None:
        assert rights_role_found is True, f'Role containing expected rights found'

    assert everbody_found is True, f'Everybody role not found'


@pytest.mark.api_ui
@pytest.mark.pas
@pytest.mark.cds_user
@pytest.mark.parametrize('user_rights', ['Privileged Access Service Administrator'], indirect=True)
def test_cds_single_right(cds_ui, cds_session):
    ui, ui_user = cds_ui
    session, api_user = cds_session

    check_rights(session, ui_user, api_user, ['Privileged Access Service Administrator'])
    ui.navigate('Resources', 'Systems')


@pytest.mark.api_ui
@pytest.mark.pas
@pytest.mark.cds_user
@pytest.mark.parametrize('user_rights', ['System Administrator'], indirect=True)
def test_cds_system_administrator(cds_ui, cds_session):
    ui, ui_user = cds_ui
    session, api_user = cds_session

    check_rights(session, ui_user, api_user, ['All Rights'])
    ui.navigate('Access', 'Users')


@pytest.mark.api_ui
@pytest.mark.pas
@pytest.mark.cds_user
@pytest.mark.parametrize('user_rights', [None], indirect=True)
def test_cds_no_rights(cds_ui, cds_session):
    ui, ui_user = cds_ui
    session, api_user = cds_session

    check_rights(session, ui_user, api_user, [None])
    ui.navigate(('Workspace', 'My Favorites'))


@pytest.mark.api_ui
@pytest.mark.pas_failed
@pytest.mark.cds_user
@pytest.mark.parametrize('user_rights', [['Role Management', 'Report Management']], indirect=True)
def test_cds_multi_rights(cds_ui, cds_session):
    ui, ui_user = cds_ui
    session, api_user = cds_session

    check_rights(session, ui_user, api_user, ['Role Management', 'Report Management'])
    ui.navigate('Access', 'Roles')
    ui.navigate('Reports')


@pytest.mark.ui
@pytest.mark.pas_broken
@pytest.mark.ad_user
@pytest.mark.parametrize('user_rights', ['Privileged Access Service Administrator'], indirect=True)
def test_ad_single_right(ad_ui, ad_session):
    ui, ui_user = ad_ui
    session, api_user = ad_session

    check_rights(session, ui_user, api_user, ['Privileged Access Service Administrator'])
    ui.navigate('Resources', 'Systems')


@pytest.mark.ui
@pytest.mark.pas_broken
@pytest.mark.ad_user
@pytest.mark.parametrize('user_rights', ['System Administrator'], indirect=True)
def test_ad_system_administrator(ad_ui, ad_session):
    ui, ui_user = ad_ui
    session, api_user = ad_session

    check_rights(session, ui_user, api_user, ['All Rights'])
    ui.navigate('Access', 'Users')


@pytest.mark.ui
@pytest.mark.pas_broken
@pytest.mark.ad_user
@pytest.mark.parametrize('user_rights', [None], indirect=True)
def test_ad_no_rights(ad_ui, ad_session):
    ui, ui_user = ad_ui
    session, api_user = ad_session

    check_rights(session, ui_user, api_user, [None])
    ui.navigate(('Workspace', 'My Favorites'))


@pytest.mark.ui
@pytest.mark.pas_broken
@pytest.mark.ad_user
@pytest.mark.parametrize('user_rights', [['Role Management', 'Report Management']], indirect=True)
def test_ad_multi_rights(ad_ui, ad_session):
    ui, ui_user = ad_ui
    session, api_user = ad_session

    check_rights(session, ui_user, api_user, ['Role Management', 'Report Management'])
    ui.navigate('Access', 'Roles')
    ui.navigate('Reports')


@pytest.mark.ui
@pytest.mark.pas
@pytest.mark.browser_override
@pytest.mark.pas_skip(reason="IE isn't downloading json properly and is breaking CI, see https://jira.centrify.com/browse/CC-74877")
@pytest.mark.parametrize('browser_override', ['ie'], indirect=True)
def test_browser_override_works(cds_ui):
    ui, ui_user = cds_ui
    ui.navigate('Resources', 'Systems')