import pytest
from furl import furl
from playwright.sync_api import Page
from zgw_consumers.constants import APITypes
from zgw_consumers.test.factories import ServiceFactory

from openbeheer.accounts.tests.factories import UserFactory
from openbeheer.utils.gherkin_e2e import GherkinRunner
from openbeheer.utils.open_zaak_helper.data_creation import OpenZaakDataCreationHelper


@pytest.mark.e2e
def test_view_informatieobjecttype(page: Page, runner: GherkinRunner):
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
    assert iot.url

    UserFactory.create(username="johndoe", password="secret")

    runner.when.go_to_root_page(page)
    runner.when.user_logs_in(page, username="johndoe", password="secret")

    runner.then.path_should_be(page, "/OZ/")

    runner.when.select_catalogus(page, catalogus)
    runner.when.go_to_informatieobjecttype_list_page(page, catalogus)

    runner.then.page_should_contain_text(page, text=iot.omschrijving)

    runner.when.click_on_link(page, name=iot.omschrijving)

    runner.then.path_should_be(
        page,
        f"/OZ/{furl(catalogus.url).path.segments[-1]}/informatieobjecttypen/{iot.uuid}",
    )

    runner.then.page_should_contain_text(page, iot.omschrijving)
    runner.then.page_should_contain_text(page, "Overview")
    runner.then.page_should_contain_text(page, "Omschrijving")
    runner.then.page_should_contain_text(page, "Vertrouwelijkheidaanduiding")
    runner.then.page_should_contain_text(page, "Begin Geldigheid")
    runner.then.page_should_contain_text(page, "Concept")


@pytest.mark.e2e
def test_edit_and_save_informatieobjecttype(page: Page, runner: GherkinRunner):
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
    assert iot.url

    UserFactory.create(username="johndoe", password="secret")

    runner.when.go_to_root_page(page)
    runner.when.user_logs_in(page, username="johndoe", password="secret")

    runner.then.path_should_be(page, "/OZ/")

    runner.when.select_catalogus(page, catalogus)
    runner.when.go_to_informatieobjecttype_list_page(page, catalogus)

    runner.then.page_should_contain_text(page, text=iot.omschrijving)

    runner.when.click_on_link(page, name=iot.omschrijving)

    runner.then.path_should_be(
        page,
        f"/OZ/{furl(catalogus.url).path.segments[-1]}/informatieobjecttypen/{iot.uuid}",
    )

    runner.when.click_on_button(page, name="Bewerken")

    runner.then.path_should_be(
        page,
        f"/OZ/{furl(catalogus.url).path.segments[-1]}/informatieobjecttypen/{iot.uuid}?editing=true",
    )
    page.get_by_label("Omschrijving").fill("Updated Omschrijving")

    runner.when.click_on_button(page, name="Opslaan")
    runner.then.path_should_be(
        page,
        f"/OZ/{furl(catalogus.url).path.segments[-1]}/informatieobjecttypen/{iot.uuid}",
    )

    runner.then.page_should_contain_text(page, "Updated Omschrijving")


@pytest.mark.e2e
def test_edit_and_cancel_informatieobjecttype(page: Page, runner: GherkinRunner):
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
    assert iot.url

    UserFactory.create(username="johndoe", password="secret")

    runner.when.go_to_root_page(page)
    runner.when.user_logs_in(page, username="johndoe", password="secret")

    runner.then.path_should_be(page, "/OZ/")

    runner.when.select_catalogus(page, catalogus)
    runner.when.go_to_informatieobjecttype_list_page(page, catalogus)

    runner.then.page_should_contain_text(page, text=iot.omschrijving)

    runner.when.click_on_link(page, name=iot.omschrijving)

    runner.then.path_should_be(
        page,
        f"/OZ/{furl(catalogus.url).path.segments[-1]}/informatieobjecttypen/{iot.uuid}",
    )

    runner.when.click_on_button(page, name="Bewerken")

    runner.then.path_should_be(
        page,
        f"/OZ/{furl(catalogus.url).path.segments[-1]}/informatieobjecttypen/{iot.uuid}?editing=true",
    )
    page.get_by_label("Omschrijving").fill("TRALALA!")

    runner.when.click_on_button(page, name="Annuleren")
    runner.then.path_should_be(
        page,
        f"/OZ/{furl(catalogus.url).path.segments[-1]}/informatieobjecttypen/{iot.uuid}",
    )

    runner.then.page_should_not_contain_text(page, "TRALALA!")
    runner.then.page_should_contain_text(page, iot.omschrijving)
