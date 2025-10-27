import pytest
from furl import furl
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
def test_subfields_are_present(page: Page, runner: GherkinRunner):
    runner.given.user_exists()
    runner.given.api_config_exists()
    runner.given.ztc_service_exists()

    catalogus = runner.given.catalogus_exists()
    zaaktype = runner.given.zaaktypen_exist(
        catalogus=catalogus,
        amount=1,
        **{
            "referentieproces": {
                "naam": "Referentie Process Bla",
                "link": "https://selectielijst.openzaak.nl/api/v1/procestypen/aa8aa2fd-b9c6-4e34-9a6c-58a677f60ea0",
            },
            "broncatalogus": {
                "url": "http://localhost:8003/catalogi/api/v1/catalogussen7c91d49f-765e-46f2-867a-6fb70460e21c",
                "domein": "CXCWE",
                "rsin": "123456782",
            },
            "bronzaaktype": {
                "url": "http://localhost:8003/catalogi/api/v1/zaaktypen/8e137651-e6a6-4b2a-b70d-818c653ea3ba",
                "identificatie": "ZAAKTYPE-2025-0000000001",
                "omschrijving": "Sign family fact recent condition whom couple.",
            },
        },
    )[0]
    assert catalogus.url and zaaktype.identificatie

    runner.when.user_open_application(page)
    runner.when.user_logs_in(page)
    runner.then.path_should_be(page, "/OZ/")
    runner.when.user_selects_catalogus(page, catalogus)
    runner.then.path_should_be(
        page, f"/OZ/{furl(catalogus.url).path.segments[-1]}/zaaktypen"
    )
    runner.when.user_clicks_on_link(page, zaaktype.identificatie)
    runner.when.user_selects_tab(page, "Algemeen")

    runner.when.user_clicks_on_button(page, name="Behandeling en Proces")
    runner.when.user_clicks_on_button(
        page, name="Behandeling en Proces"
    )  # For some reason you need to click on it twice
    runner.then.table_should_contain(
        page, table_header="Referentieproces.naam", table_value="Referentie Process Bla"
    )
    runner.then.table_should_contain(
        page,
        table_header="Referentieproces.link",
        table_value="https://selectielijst.openzaak.nl/api/v1/procestypen/aa8aa2fd-b9c6-4e34-9a6c-58a677f60ea0",
    )

    runner.when.user_clicks_on_button(page, name="Bronnen en relaties")
    runner.when.user_clicks_on_button(
        page, name="Bronnen en relaties"
    )  # For some reason you need to click on it twice
    runner.then.table_should_contain(
        page,
        table_header="Broncatalogus.url",
        table_value="http://localhost:8003/catalogi/api/v1/catalogussen7c91d49f-765e-46f2-867a-6fb70460e21c",
    )
    runner.then.table_should_contain(
        page, table_header="Broncatalogus.domein", table_value="CXCWE"
    )
    runner.then.table_should_contain(
        page, table_header="Broncatalogus.rsin", table_value="123456782"
    )
    runner.then.table_should_contain(
        page,
        table_header="Bronzaaktype.url",
        table_value="http://localhost:8003/catalogi/api/v1/zaaktypen/8e137651-e6a6-4b2a-b70d-818c653ea3ba",
    )
    runner.then.table_should_contain(
        page,
        table_header="Bronzaaktype.identificatie",
        table_value="ZAAKTYPE-2025-0000000001",
    )
    runner.then.table_should_contain(
        page,
        table_header="Bronzaaktype.omschrijving",
        table_value="Sign family fact recent condition whom couple.",
    )
