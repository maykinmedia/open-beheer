import pytest
from playwright.sync_api import Page

from openbeheer.utils.gherkin_e2e import GherkinRunner


@pytest.mark.e2e
def test_create_zaaktype(page: Page, runner: GherkinRunner):
    _ = runner

    _.given.user_exists()
    _.given.api_config_exists()
    _.given.ztc_service_exists()

    catalogus = _.given.catalogus_exists()

    # Login
    _.when.user_open_application(page)
    _.when.user_logs_in(page)

    # Open create view
    _.when.user_selects_catalogus(page, catalogus)
    _.when.user_navigates_to_zaaktype_list_page(page)
    _.when.user_clicks_on_link(page, "Nieuw zaaktype")

    # Create zaaktype
    _.when.user_clicks_on_checkbox(page, "Basis")
    _.when.user_clicks_on_button(page, name="Gebruik dit sjabloon")
    _.when.user_fills_form_field(page, "Identificatienummer", "gh-305")
    _.when.user_fills_form_field(page, "Omschrijving", "created zaaktype")
    _.when.user_clicks_on_button(page, name="Zaaktype aanmaken")
    _.then.page_should_contain_text(page, "gh-305", timeout=10000)

    # Navigate to algemeen tab
    _.when.user_selects_tab(page, "Algemeen")
    _.then.page_should_contain_text(page, "created zaaktype")
