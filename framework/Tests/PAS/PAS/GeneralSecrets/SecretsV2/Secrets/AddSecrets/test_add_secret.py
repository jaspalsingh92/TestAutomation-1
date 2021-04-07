import pytest
from Utils.guid import guid
from Shared.UI.Centrify.selectors import GridCell
from Shared.API.secret import find_secret_by_name


@pytest.mark.ui
@pytest.mark.pas
@pytest.mark.daily
@pytest.mark.smoke
@pytest.mark.ui
@pytest.mark.secrets
def test_create_text_secret_works(core_ui, core_session, secret_cleaner):
    ui = core_ui

    secret_name = guid() + ' ui secret'
    secret_description = secret_name + ' Description'
    secret_contents = guid() + ' secret contents'

    ui.navigate('Resources', 'Secrets')
    ui.launch_add('Add Secret')

    ui.input('SecretName', secret_name)
    ui.input('Description', secret_description)

    ui.save_warning()
    ui.select_option('Type', 'Text')

    ui.launch_modal('Enter Text')
    ui.input('SecretText', secret_contents)
    ui.close_modal('OK')

    ui.save()

    secret = find_secret_by_name(core_session, secret_name)
    secret_id = secret['ID']
    secret_cleaner.append(secret_id)

    ui.search(secret_name)
    ui.expect(GridCell(secret_name), 'Could not find secret after creating it')
