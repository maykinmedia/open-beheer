import pytest
from playwright.sync_api import Page

from openbeheer.utils.gherkin_e2e import GherkinRunner


@pytest.mark.e2e
def test_log_out(page: Page, runner: GherkinRunner):
    runner.given.ztc_service_exists()
    runner.given.user_exists()

    runner.when.user_logs_in(page)
    runner.then.path_should_be(page, "/OZ/")
    runner.when.user_logs_out(page)

    runner.then.path_should_be(page, "/login")
    runner.then.session_storage_should_be_cleared(page)
