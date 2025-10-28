from django.core.cache import caches

import pytest
from furl import furl
from playwright.sync_api import Page

from openbeheer.utils.gherkin_e2e import GherkinRunner


@pytest.mark.e2e
def test_session_expired_while_editing(
    page: Page, runner: GherkinRunner, session_engine_cache: None
):
    runner.given.ztc_service_exists()
    runner.given.api_config_exists()
    runner.given.user_exists()

    catalogus = runner.given.catalogus_exists()
    zaaktype = runner.given.zaaktypen_exist(catalogus=catalogus, amount=1)[0]
    assert catalogus.url and zaaktype.identificatie

    runner.when.user_logs_in(page)
    runner.then.path_should_be(page, "/OZ/")
    runner.when.user_selects_catalogus(page, catalogus)
    runner.then.path_should_be(
        page, f"/OZ/{furl(catalogus.url).path.segments[-1]}/zaaktypen"
    )
    runner.when.user_clicks_on_link(page, zaaktype.identificatie)
    runner.then.path_should_be(
        page,
        f"/OZ/{furl(catalogus.url).path.segments[-1]}/zaaktypen/{zaaktype.uuid}#section=0&tab=0",
    )
    runner.when.user_clicks_on_button(page, name="Bewerken")
    runner.when.user_fills_form_field(
        page, label='Bewerk "identificatie"', value="UPDATED"
    )

    # Clears session in the cache session engine
    caches["default"].clear()

    runner.when.user_clicks_on_button(page, name="Opslaan en afsluiten")
    runner.then.path_should_be(
        page,
        f"/login?next=/OZ/{furl(catalogus.url).path.segments[-1]}/zaaktypen/{zaaktype.uuid}",
    )
    runner.then.session_storage_should_be_cleared(page)
