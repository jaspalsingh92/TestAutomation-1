import pytest
import logging

from Utils.config_loader import Configs
from Shared.UI.Centrify.SubSelectors.navigation import TopLevelNavigationItem, ExpandedTopLevelNavigationItem, \
                                                       SelectedToplevelNavigationItem, SubNavigationItem, \
                                                       ExpandedSubNavigationItem, NavigationItem, SelectedNavigationItem

pytestmark = [pytest.mark.ui, pytest.mark.navigation]

logger = logging.getLogger('test')

@pytest.fixture(scope="session")
def navigation_visibility(request):
    return Configs.get_environment_node('navigation', 'automation_main')

@pytest.fixture(scope="session")
def all_known_tabs(navigation_visibility):
    """
    Returns an array of tabs, each of which has several properties:
    [{
        "text": <human readable name of the tab>,
        "rights": <array of administrative rights which are allowed to see it,
        "children": <array of child tabs, empty if it has no children.
        "no_children": <boolean value, special property which disambiguates two tabs at the same level, one of which has children and the other does not>
    },...]
    """
    def add_missing_tabs(right, tabs, all_known_tabs):
        """
        Walks the array of tabs, which are the tabs available to the parameterized right,
        and updates our data structure of all known tabs, and what rights can see that tab
        """
        for tab in tabs:
            # a tab which contains sub tabs
            if isinstance(tab, dict):
                found_tab = None
                for known_tab in all_known_tabs:
                    if known_tab['text'] == tab['text'] and known_tab['no_children'] is False:
                        found_tab = known_tab

                # we already know about this tab, but might not know about the children
                if found_tab is not None:
                    found_tab['rights'].append(right)
                    add_missing_tabs(right, tab['children'], found_tab['children'])
                else:
                    # we didn't know about this tab, so make a new entry in all known, and process children
                    new_known_tab = {
                        "text": tab["text"],
                        "rights": [right],
                        "no_children": False,
                        "children": []
                    }
                    all_known_tabs.append(new_known_tab)
                    add_missing_tabs(right, tab['children'], new_known_tab['children'])
            else:
                # a tab which does not contain sub tabs
                found_tab = None
                for known_tab in all_known_tabs:
                    if known_tab['text'] == tab and known_tab['no_children'] is True:
                        found_tab = known_tab

                if found_tab is not None:
                    found_tab['rights'].append(right)
                else:
                    all_known_tabs.append({
                        "text": tab,
                        "rights": [right],
                        "no_children": True,
                        "children": []
                    })

    all_known_tabs = []

    for right in navigation_visibility.keys():
        tabs = navigation_visibility[right]
        add_missing_tabs(right, tabs, all_known_tabs)

    return all_known_tabs


def should_tab_exist(tab, right):
    return right in tab['rights']


def walk_tabs(all_tabs, ui, right, parent_tab_text, parent_tab_selector):
    is_top_level_tab = parent_tab_selector is None
    parent_tab_text = "" if parent_tab_text is None else parent_tab_text

    for tab in all_tabs:
        is_leaf = len(tab['children']) == 0
        should_exist = should_tab_exist(tab, right)

        if is_top_level_tab:
            tab_selector = TopLevelNavigationItem(tab['text']) if parent_tab_selector is None else TopLevelNavigationItem(tab['text']).inside(parent_tab_selector)
        else:
            if is_leaf:
                tab_selector = NavigationItem(tab['text']) if parent_tab_selector is None else NavigationItem(tab['text']).inside(parent_tab_selector)
            else:
                tab_selector = SubNavigationItem(tab['text']) if parent_tab_selector is None else SubNavigationItem(tab['text']).inside(parent_tab_selector)

        exists = ui.check_exists(tab_selector, time_to_wait=0)

        current_tab_text = parent_tab_text + " > " + tab["text"]

        assert exists is should_exist, f'User with only right {right} {"should" if should_exist is True else "should not"} be able to see {current_tab_text}. {tab_selector}'

        if should_exist:
            if is_leaf:
                logger.debug(f'Selecting navigation {current_tab_text}')
                ui.select_navigation(tab['text'], parent_tab_text, parent_tab_selector)
            else:
                logger.debug(f'Expanding navigation {current_tab_text}')
                current_tab_selector = ui.expand_navigation(tab['text'], parent_tab_text, parent_tab_selector)

            if is_leaf is False:
                walk_tabs(tab['children'], ui, right, current_tab_text, current_tab_selector)
                ui.collapse_navigation(tab['text'], parent_tab_text, parent_tab_selector)


@pytest.mark.parametrize('user_rights', [
                                            "Admin Portal Login",
                                            "Application Management",
                                            "Computer Login and Privilege Elevation",
                                            "Customer Management",
                                            "Device Management",
                                            "Federation Management",
                                            "MFA Unlock",
                                            "Privileged Access Service Administrator",
                                            "Privileged Access Service Power User",
                                            "Privileged Access Service User",
                                            "Query as a Different User",
                                            "Radius Management",
                                            "Read Only System Administration",
                                            "Register and Administer Connectors",
                                            "Report Management",
                                            "Role Management",
                                            "System Enrollment",
                                            "User Management"
                                        ], indirect=True)
def test_navigation_tabs_are_correct_for_user_with_single_admin_right(cds_ui, user_rights, all_known_tabs):
    logger.debug(f'All known UI tabs {all_known_tabs}')
    # All admin rights can see workspace, navigate here first to eliminate any timing issues
    # with when tabs that can only be seen by sys admins are added to the nav tree
    ui, user = cds_ui
    ui.navigate('Workspace', check_rendered_tab=False)

    # Now walk all known tabs. At each level we can check for existence if it should be there, and that it doesn't exist
    # if it should not be there.
    walk_tabs(all_known_tabs, ui, user_rights[0], None, None)

