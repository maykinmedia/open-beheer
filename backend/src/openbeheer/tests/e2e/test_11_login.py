import pytest
from playwright.sync_api import Page

from openbeheer.conftest import vcr_overrides
from openbeheer.utils.gherkin_e2e import GherkinRunner
from openbeheer.utils.tests import matcher_query_without_datum_geldigheid


@pytest.mark.e2e
@vcr_overrides(
    custom_matchers=[
        ("query_without_datum_geldigheid", matcher_query_without_datum_geldigheid)
    ],
    custom_match_on=[
        "method",
        "scheme",
        "host",
        "port",
        "path",
        "query_without_datum_geldigheid",
    ],
)
def test_scenario_log_in(page: Page, runner: GherkinRunner):
    _ = runner

    _.given.api_config_exists()
    _.given.ztc_service_exists()

    user = _.given.user_exists()

    # Login
    _.when.user_opens_application(page)
    _.when.user_fills_form_field(page, "Gebruikersnaam", user.username)
    _.when.user_fills_form_field(page, "Wachtwoord", "secret")
    page.screenshot(path="../docs/manual/_assets/test_scenario_log_in.png")

    _.when.user_clicks_on_button(page, "Inloggen")
    _.then.page_should_contain_text(page, "Open Beheer")


@pytest.mark.e2e
@vcr_overrides(
    custom_matchers=[
        ("query_without_datum_geldigheid", matcher_query_without_datum_geldigheid)
    ],
    custom_match_on=[
        "method",
        "scheme",
        "host",
        "port",
        "path",
        "query_without_datum_geldigheid",
    ],
)
def test_scenario_log_out(page: Page, runner: GherkinRunner):
    _ = runner

    _.given.api_config_exists()
    _.given.ztc_service_exists()

    user = _.given.user_exists()
    _.given.user_is_logged_in(page, user)

    # when user opens application
    _.then.page_should_contain_text(page, "Open Beheer")

    _.when.user_clicks_on_button(page, "Profiel")  # Shown as initials
    _.then.page_should_contain_text(page, "Account")
    page.screenshot(path="../docs/manual/_assets/test_scenario_log_out.png")

    _.when.user_clicks_on_button(page, "Uitloggen")
    _.then.page_should_contain_text(page, "Inloggen")
