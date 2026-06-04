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
def test_scenario_create_informatieobjecttype(page: Page, runner: GherkinRunner):
    _ = runner

    _.given.user_exists()
    _.given.api_config_exists()
    _.given.ztc_service_exists()

    catalogus = _.given.catalogus_exists()

    # Login
    _.when.user_opens_application(page)
    _.when.user_logs_in(page)

    # Open create view
    _.when.user_selects_catalogus(page, catalogus)
    _.when.user_navigates_to_informatieobjecttype_list_page(page, catalogus)
    _.when.user_clicks_on_link(page, "Nieuw informatieobjecttype")

    # Create informatieobjecttype
    _.when.user_clicks_on_checkbox(page, "Basis")
    _.when.user_clicks_on_button(page, "Gebruik dit sjabloon")
    _.when.user_fills_form_field(page, "Omschrijving", "Voorbeeld informatieobjecttype")
    page.screenshot(
        path="../docs/manual/_assets/test_scenario_create_informatieobjecttype.png"
    )

    _.when.user_clicks_on_button(page, "Informatieobjecttype aanmaken")
    _.then.page_should_contain_text(page, "Voorbeeld informatieobjecttype")
