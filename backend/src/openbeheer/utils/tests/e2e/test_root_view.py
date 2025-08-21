from django.test import tag

from openbeheer.utils.e2e import browser_page
from openbeheer.utils.gherkin_e2e import GherkinLikeTestCase


@tag("e2e")
class TestRootView(GherkinLikeTestCase):
    async def test_root_view(self):
        async with browser_page() as page:
            await page.goto(f"{self.live_server_url}/")
            await self.then.page_should_contain_text(
                page, "403"
            )  # TODO: Update when redirect to login is fixed
