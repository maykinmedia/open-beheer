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
def test_scenario_edit_zaaktype(page: Page, runner: GherkinRunner):
    _ = runner

    _.given.user_exists()
    _.given.api_config_exists()
    _.given.ztc_service_exists()

    catalogus = _.given.catalogus_exists()
    zaaktype = _.given.zaaktype_exists(catalogus)

    # Navigate to zaaktype
    _.when.user_logs_in(page)
    _.when.user_selects_catalogus(page, catalogus)
    _.when.user_navigates_to_zaaktype_detail_page(page, zaaktype)

    # Select tab
    _.when.user_selects_tab(page, "Overzicht")

    # Start editing
    _.when.user_clicks_on_button(page, "Bewerken")
    _.then.page_should_contain_text(page, "Opslaan")

    _.when.user_fills_form_field(
        page, "Doel", "Verduidelijken van de werking van het systeem"
    )
    _.when.user_fills_form_field(page, "Selectielijst", "2020 - 1 - ")

    page.screenshot(path="../docs/manual/_assets/test_scenario_edit_zaaktype.png")
    _.when.user_clicks_on_button(page, "Opslaan")
    _.then.page_should_contain_text(page, "Bewerken")
    _.then.page_should_contain_text(
        page, "Verduidelijken van de werking van het systeem"
    )
