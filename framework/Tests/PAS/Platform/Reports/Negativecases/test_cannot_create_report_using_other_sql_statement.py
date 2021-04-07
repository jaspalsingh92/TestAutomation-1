import pytest
from Shared.UI.Centrify.SubSelectors.modals import Modal, ErrorModal
from Shared.UI.Centrify.selectors import Anchor, Div
import logging

logger = logging.getLogger("test")

lock_tenant = True


@pytest.mark.ui
@pytest.mark.bhavna
@pytest.mark.pas_failed
def test_only_support_select_statement_when_create_report_using_sql_script(core_session, create_report, core_admin_ui):
    """
    TCID: C6368 Cannot create report using other sql statement (delete/update/create...) except "select"
    :param core_session: Centrify Session
    :param create_report: To Create the report
    :param core_admin_ui: To open the browser
    """
    my_report = create_report(core_session, "Select * From Role")

    core_admin_ui.navigate("Reports")
    core_admin_ui.check_row(my_report['Name'])
    core_admin_ui.action("Modify")
    core_admin_ui.clear_codemirror()
    core_admin_ui.write_to_codemirror("Delete role")

    core_admin_ui.expect(Anchor(button_text="Save"), f'Failed to get the save button').try_click()
    core_admin_ui._waitUntilSettled()
    core_admin_ui.expect(ErrorModal(), f'Failed to get the error modal')
    core_admin_ui.switch_context(Modal())
    core_admin_ui.expect(Div("Query has failed:"), f'Failed to get expected error "Query has failed:xxx"')
    logger.info(f'It supports ONLY the "SELECT" SQL statement, and complies to the syntax that SQLite supports.'
                f' Please refer to http://www.sqlite.org/lang_select.html for the details.')
