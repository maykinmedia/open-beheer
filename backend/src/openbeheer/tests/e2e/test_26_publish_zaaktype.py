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
def test_scenario_publish_informatieobjecttype(page: Page, runner: GherkinRunner):
    _ = runner

    _.given.user_exists()
    _.given.api_config_exists()
    _.given.ztc_service_exists()

    catalogus = _.given.catalogus_exists()
    zaaktype = _.given.zaaktype_exists(catalogus)

    # At least two statustypen should be added to a zaaktype to allow publishing
    _.given.statustype_exists(zaaktype, "In behandeling", 1)
    _.given.statustype_exists(zaaktype, "Afgehandeld", 2)

    # At least one roltype should be added to a zaaktype to allow publishing
    _.given.roltype_exists(zaaktype)

    # At least one resultaattype should be added to a zaaktype to allow publishing
    _.given.resultaattype_exists(zaaktype)

    # Navigate to zaaktype
    _.when.user_logs_in(page)
    _.when.user_selects_catalogus(page, catalogus)
    _.when.user_navigates_to_zaaktype_detail_page(page, zaaktype)
    _.then.page_should_contain_text(page, "Concept")

    # Publish zaaktype
    _.when.user_clicks_on_button(page, "Bewerken")
    _.then.page_should_contain_text(page, "Opslaan")
    page.screenshot(
        path="../docs/manual/_assets/test_scenario_publish_informatieobjecttype.png"
    )

    _.when.user_clicks_on_button(page, "Publiceren")
    _.then.page_should_contain_text(page, "Actueel")
