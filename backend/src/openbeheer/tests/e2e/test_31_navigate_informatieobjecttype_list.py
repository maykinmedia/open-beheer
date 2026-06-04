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
def test_scenario_navigate_informatieobjecttype_list(page: Page, runner: GherkinRunner):
    _ = runner

    _.given.api_config_exists()
    _.given.ztc_service_exists()

    _.given.user_exists()
    catalogus = _.given.catalogus_exists()

    _.when.user_logs_in(page)
    _.when.user_selects_catalogus(page, catalogus)
    _.when.user_clicks_on_button(page, "Informatieobjecttypen")
    page.screenshot(
        path="../docs/manual/_assets/test_navigate_informatieobjecttype_list.png"
    )

    _.then.page_should_contain_text(page, "Omschrijving")
    _.then.page_should_contain_text(page, "Vertrouwelijkheidaanduiding")
    _.then.page_should_contain_text(page, "Actief")
    _.then.page_should_contain_text(page, "Einde Geldigheid")
    _.then.page_should_contain_text(page, "Concept")
