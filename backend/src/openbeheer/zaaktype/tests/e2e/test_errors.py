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
def test_errors(page: Page, runner: GherkinRunner):
    _ = runner

    _.given.user_exists()
    _.given.api_config_exists()
    _.given.ztc_service_exists()
    _.given.catalogus_exists()

    catalogus = _.given.catalogus_exists()
    zaaktypen = _.given.zaaktypen_exist(catalogus)

    # Login
    _.when.user_open_application(page)
    _.when.user_logs_in(page)
    _.then.path_should_be(page, "/OZ/")

    # Open detail view
    _.when.user_selects_catalogus(page, catalogus)
    _.when.user_navigates_to_zaaktype_detail_page(page, zaaktypen[0])
    _.then.page_should_contain_text(page, str(zaaktypen[0].identificatie))

    # Open edit mode.
    _.when.user_clicks_on_button(page, "Bewerken")
    _.then.url_should_match(page, "editing=true")

    # Clear omschrijving
    _.when.user_fills_form_field(page, "Omschrijving", "", 0)

    # Navigate to statustypen tab
    _.when.user_selects_tab(page, "Statustypen")
    _.when.user_clicks_on_button(page, "Voeg toe")
    _.when.user_clicks_on_button(page, "Opslaan")
    _.then.page_should_contain_text(page, "Overzicht (!)")
    _.then.page_should_contain_text(page, "Statustypen (!)")

    # Navigate to overzicht tab to check and fix error message
    _.when.user_selects_tab(page, "Overzicht (!)")
    _.then.page_should_contain_text(page, "Dit veld mag niet leeg zijn.")
    _.when.user_fills_form_field(page, "Omschrijving", "TEST OMSCHRIJVING", 0)

    # Navigate to statustypen tab to check and fix error message
    _.when.user_selects_tab(page, "Statustypen (!)")
    _.then.page_should_contain_text(page, "Dit veld mag niet leeg zijn.", None, 0)
    _.when.user_fills_form_field(
        page, "Omschrijving", "TEST STATUSTYPE OMSCHRIJVING", 2
    )

    # Save changes.
    _.when.user_clicks_on_button(page, "Opslaan")
    _.then.page_should_not_contain_text(page, "Dit veld mag niet leeg zijn.")

    # Check update.
    _.when.user_selects_tab(page, "Overzicht")
    _.then.page_should_contain_text(page, "TEST OMSCHRIJVING")
    _.when.user_selects_tab(page, "Statustypen")
    _.then.page_should_contain_text(page, "TEST STATUSTYPE OMSCHRIJVING", None, 1)
