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
def test_add_resultaattypen(page: Page, runner: GherkinRunner):
    _ = runner

    _.given.user_exists()
    _.given.api_config_exists()
    _.given.ztc_service_exists()

    catalogus = _.given.catalogus_exists()
    zaaktypen = _.given.zaaktypen_exist(catalogus, 1)

    # Login
    _.when.user_open_application(page)
    _.when.user_logs_in(page)

    # Navigate to detail view
    _.when.user_selects_catalogus(page, catalogus)
    _.when.user_navigates_to_zaaktype_list_page(page)
    _.when.user_clicks_on_link(page, zaaktypen[0].identificatie or "")

    # Navigate to resultaattypen tab
    _.when.user_selects_tab(page, "Resultaattypen")
    _.when.user_clicks_on_button(page, name="Bewerken")

    # Zero state
    _.then.page_should_not_contain_text(
        page, "1.1.2 - Ingericht - blijvend_bewaren - Gemeentewapen"
    )
    _.then.page_should_not_contain_text(
        page,
        "1.1.3 - Ingericht - vernietigen - P10Y - Wijziging inrichting BRP systeem",
    )

    # Add resultaattype
    _.when.user_clicks_on_button(page, name="Voeg toe")
    _.when.user_fills_form_field(
        page,
        "Selectielijstklasse",
        "1.1.2 - Ingericht - blijvend_bewaren - Gemeentewapen",
    )
    _.when.user_clicks_on_button(page, name="Doorgaan")

    # Add another
    _.when.user_clicks_on_button(page, name="Voeg toe")
    _.when.user_fills_form_field(
        page,
        "Selectielijstklasse",
        "1.1.3 - Ingericht - vernietigen - P10Y - Wijziging inrichting BRP systeem",
    )
    _.when.user_clicks_on_button(page, name="Doorgaan")

    # Save
    _.when.user_clicks_on_button(page, name="Opslaan")

    _.then.page_should_not_contain_text(page, "Voeg toe")
    _.then.page_should_contain_text(
        page, "1.1.2 - Ingericht - blijvend_bewaren - Gemeentewapen", timeout=3000
    )
    _.then.page_should_contain_text(
        page,
        "1.1.3 - Ingericht - vernietigen - P10Y - Wijziging inrichting BRP systeem",
    )

    # Check "Overzicht" tab
    _.when.user_selects_tab(page, "Overzicht")
