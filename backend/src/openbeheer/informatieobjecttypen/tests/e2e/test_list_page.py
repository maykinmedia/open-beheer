import pytest
from playwright.sync_api import Page, expect
from zgw_consumers.constants import APITypes
from zgw_consumers.test.factories import ServiceFactory

from openbeheer.accounts.tests.factories import UserFactory
from openbeheer.utils.gherkin_e2e import GherkinRunner
from openbeheer.utils.open_zaak_helper.data_creation import OpenZaakDataCreationHelper


@pytest.mark.e2e
def test_retrieve_informatieobjecttypen(page: Page, runner: GherkinRunner):
    ServiceFactory.create(
        api_type=APITypes.ztc,
        api_root="http://localhost:8003/catalogi/api/v1",
        client_id="test-vcr",
        secret="test-vcr",
        slug="OZ",
    )
    helper = OpenZaakDataCreationHelper(ztc_service_slug="OZ")
    catalogus = helper.create_catalogus()
    assert catalogus.url
    iot = helper.create_informatieobjecttype(catalogus=catalogus.url)
    UserFactory.create(username="johndoe", password="secret")

    runner.when.go_to_root_page(page)
    runner.when.user_logs_in(page, username="johndoe", password="secret")

    runner.then.path_should_be(page, "/OZ/")

    runner.when.select_catalogus(page, catalogus)
    runner.when.go_to_informatieobjecttype_list_page(page, catalogus)

    expect(page.get_by_text(iot.omschrijving)).to_be_visible()
