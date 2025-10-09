import inspect
import os
import pathlib
from typing import ContextManager, Generator

import pytest
from mozilla_django_oidc_db.constants import OIDC_ADMIN_CONFIG_IDENTIFIER
from mozilla_django_oidc_db.tests.factories import OIDCClientFactory
from pytest_django import DjangoDbBlocker, live_server_helper
from pytest_django.lazy_django import skip_if_no_django

from openbeheer.utils.gherkin_e2e import GherkinRunner
from openbeheer.utils.tests import VCRMixin


@pytest.fixture
def runner(live_server_vcr) -> GherkinRunner:
    return GherkinRunner(live_server_vcr)


@pytest.fixture(scope="function")
def django_db_setup(
    django_db_setup: Generator[None, None, None],
    django_db_blocker: DjangoDbBlocker | None,
):
    assert django_db_blocker

    with django_db_blocker.unblock():
        OIDCClientFactory.create(identifier=OIDC_ADMIN_CONFIG_IDENTIFIER)


class VCRPyTestHelper(VCRMixin):
    def __init__(self, request: pytest.FixtureRequest) -> None:
        self.request = request

    def _get_cassette_name(self) -> str:
        return f"{self.request.function.__qualname__}.yaml"

    def _get_cassette_library_dir(self) -> str:
        testdir = (
            pathlib.Path(inspect.getfile(self.request.function)).parent
            / "files"
            / "vcr_cassettes"
        )
        testdir.mkdir(exist_ok=True, parents=True)
        return str(testdir)

    def get_context_manager(self) -> ContextManager:
        kwargs = self._get_vcr_kwargs()
        myvcr = self._get_vcr(**kwargs)
        return myvcr.use_cassette(self._get_cassette_name())


@pytest.fixture
def live_server_vcr(
    request: pytest.FixtureRequest,
    django_db_setup: Generator[None, None, None],
    transactional_db: None,
) -> Generator[live_server_helper.LiveServer, None, None]:
    """Run a Django live server with VCRpy cassettes

    Adapted from https://github.com/pytest-dev/pytest-django/blob/ef9fef6aa1bef09054b424079e734522748ef547/pytest_django/fixtures.py#L585
    """
    skip_if_no_django()

    addr = (
        request.config.getvalue("liveserver")
        or os.getenv("DJANGO_LIVE_TEST_SERVER_ADDRESS")
        or "localhost"
    )

    vcr_helper = VCRPyTestHelper(request)
    cassette_context_manager = vcr_helper.get_context_manager()

    with cassette_context_manager:
        server = live_server_helper.LiveServer(addr)
        server._live_server_modified_settings.enable()
        yield server
        server._live_server_modified_settings.disable()
        server.stop()
