import pytest
from playwright.sync_api import Page

from openbeheer.utils.gherkin_e2e import GherkinRunner


@pytest.mark.e2e
def test_not_logged_in(page: Page, runner: GherkinRunner):
    runner.when.user_open_application(page)

    runner.then.path_should_be(page, "/login?next=/")
    runner.then.page_should_contain_text(page, "Gebruikersnaam")
    runner.then.page_should_contain_text(page, "Wachtwoord")
