import pytest
from playwright.sync_api import Page

from openbeheer.utils.gherkin_e2e import GherkinRunner


@pytest.mark.e2e
def test_list_zaaktypen(page: Page, runner: GherkinRunner):
    _ = runner

    _.given.user_exists()
    _.given.api_config_exists()
    _.given.ztc_service_exists()

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
    _.when.user_clicks_on_button(page, "volgende")
    _.when.user_clicks_on_link(page, "ZAAKTYPE-2025-0000000001")

    # Navigate to detail view
    _.then.page_should_contain_text(page, "Overzicht")
    _.then.page_should_contain_text(page, zaaktypen[0].omschrijving)
