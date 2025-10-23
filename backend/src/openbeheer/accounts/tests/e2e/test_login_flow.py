from django.core.cache import caches

import pytest
from furl import furl
from playwright.sync_api import Page

from openbeheer.utils.gherkin_e2e import GherkinRunner


@pytest.mark.e2e
def test_log_out(page: Page, runner: GherkinRunner):
    runner.given.ztc_service_exists()
    runner.given.user_exists()

    runner.when.user_logs_in(page)
    runner.then.path_should_be(page, "/OZ/")
    runner.when.user_logs_out(page)

    runner.then.path_should_be(page, "/login")
    runner.then.session_storage_should_be_cleared(page)


@pytest.mark.e2e
def test_session_expired(page: Page, runner: GherkinRunner, session_engine_cache: None):
    runner.given.ztc_service_exists()
    runner.given.user_exists()

    catalogus1 = runner.given.catalogus_exists()
    catalogus2 = runner.given.catalogus_exists()

    assert catalogus1.url and catalogus2.url

    runner.when.user_logs_in(page)
    runner.then.path_should_be(page, "/OZ/")
    runner.when.user_selects_catalogus(page, catalogus1)
    runner.then.path_should_be(
        page, f"/OZ/{furl(catalogus1.url).path.segments[-1]}/zaaktypen"
    )

    # Clears session in the cache session engine
    caches["default"].clear()

    runner.when.user_selects_catalogus(page, catalogus2, check_url=False)
    runner.then.path_should_be(
        page, f"/login?next=/OZ/{furl(catalogus2.url).path.segments[-1]}/zaaktypen"
    )
