import pytest


@pytest.mark.pas
@pytest.mark.daily
@pytest.mark.smoke
@pytest.mark.ui
@pytest.mark.ui_navigation
def test_basic_navigation(core_ui):
    """
    C1352247: Main navigation selection should update when using browser back button
    :param core_ui: Authenticates UI session
    :return:
    """
    ui = core_ui
    ui.navigate(('Downloads', 'Centrify Downloads'))
    ui.navigate('Access', 'Users')
    ui.navigate('Settings', 'Authentication', ('Authentication Profiles', 'Authentication Profiles'))
    ui.navigate('Settings', 'Resources', 'Security', 'Security Settings')


@pytest.mark.pas
@pytest.mark.daily
@pytest.mark.ui
@pytest.mark.ui_navigation
def test_invalid_encoded_layout_in_hash(core_ui, core_tenant):
    """
    C1352246: Main navigation selection should be set on initial page load
    Ensures that if the user has an invalid url bookmarked or accidentally typed/etc the UI will still load.
    Catches errors in UI boot logic around determining what layout to load.
    """
    ui = core_ui
    fqdn = core_tenant['fqdn']
    ui.browser.navigate(f'https://{fqdn}/My#TXIBcHBz')
    ui.wait_for_portal_to_be_ready()
    ui.navigate('Access', 'Users')
