import pytest

from openbeheer.utils.gherkin_e2e import GherkinRunner


@pytest.fixture
def runner(live_server):
    return GherkinRunner(live_server)
