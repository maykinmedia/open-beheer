import pytest
from playwright.sync_api import Page

from openbeheer.conftest import vcr_overrides
from openbeheer.utils.gherkin_e2e import GherkinRunner
from openbeheer.utils.open_zaak_helper.data_creation import OpenZaakDataCreationHelper
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
    informatieobjecttype = _.given.informatieobjecttype_exists(
        catalogus, omschrijving="Informatieobjecttype om te publiceren"
    )

    # Navigate to informatieobjecttype
    _.when.user_logs_in(page)
    _.when.user_selects_catalogus(page, catalogus)
    _.when.user_navigates_to_informatieobjecttype_detail_page(
        page, catalogus, informatieobjecttype
    )
    _.then.page_should_contain_text(page, "ConceptJa")
    page.screenshot(
        path="../docs/manual/_assets/test_scenario_publish_informatieobjecttype.png"
    )

    # Publish informatieobjecttype
    _.when.user_clicks_on_button(page, "Publiceren")
    _.then.page_should_contain_text(page, "ConceptNee")

    # Clean up
    helper = OpenZaakDataCreationHelper(ztc_service_slug="OZ")
    helper.delete_resource(informatieobjecttype)
