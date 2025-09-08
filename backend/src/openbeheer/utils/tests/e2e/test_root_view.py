import pytest
from playwright.sync_api import Page

from openbeheer.utils.gherkin_e2e import GherkinRunner


@pytest.mark.e2e
def test_not_logged_in(page: Page, runner: GherkinRunner):
    runner.when.go_to_root_page(page)

    runner.then.path_should_be(page, "/login?next=/")
    runner.then.page_should_contain_text(
        page, "404"
    )  # TODO: Update when frontend is fixed
