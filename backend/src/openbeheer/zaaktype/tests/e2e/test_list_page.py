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
def test_list_zaaktypen(page: Page, runner: GherkinRunner):
    _ = runner

    _.given.user_exists()
    _.given.api_config_exists()
    _.given.ztc_service_exists()
    _.given.catalogus_exists()  # Added so that there are 2 catalogi (so the user has to select the one they want)

    catalogus = _.given.catalogus_exists()
    zaaktypen = _.given.zaaktypen_exist(catalogus, 20)

    # Login
    _.when.user_open_application(page)
    _.when.user_logs_in(page, username="johndoe", password="secret")
    _.then.path_should_be(page, "/OZ/")

    # Open list view
    _.when.user_selects_catalogus(page, catalogus)
    _.when.user_navigates_to_zaaktype_list_page(page)
    _.then.page_should_contain_text(page, "ZAAKTYPE-2025-0000000020")
    _.then.page_should_contain_text(page, "ZAAKTYPE-2025-0000000019")
    _.then.page_should_contain_text(page, "ZAAKTYPE-2025-0000000018")

    # Navigate to next page.
    _.when.user_clicks_on_button(page, name="volgende")
    _.when.user_clicks_on_link(page, "ZAAKTYPE-2025-0000000001")

    # Navigate to detail view
    _.then.page_should_contain_text(page, "Overzicht")
    _.then.page_should_contain_text(page, zaaktypen[0].omschrijving)
