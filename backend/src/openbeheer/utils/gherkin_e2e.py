from playwright.async_api import Locator, Page, TimeoutError, expect

from openbeheer.utils.e2e import PlaywrightTestCase


class GerkinMixin:
    """
    Experimental approach to writing Gherkin-like style test scenarios.
    Example:

        async with browser_page() as page:
            await self.given.record_manager_exists()
            await self.when.record_manager_logs_in(page)
            await self.then.page_should_contain_text(page, "Vernietigingslijsten")


    Overview:
    =========

    1. **Given**:
        - The "Given" steps set up the initial context or state for the scenario.
        - These steps are used to describe the initial situation before an action is taken.

    2. **When**:
        - The "When" steps describe the actions or events that occur.
        - These steps are used to specify the actions taken by the user or the system.

    3. **Then**:
        - The "Then" steps specify the expected outcomes or results.
        - These steps are used to verify the results of the actions taken in the "When" steps.

    These keywords help in structuring the test scenarios in a readable and organized manner, making it easier to
    understand the test flow and the expected outcomes.
    """

    @property
    def given(self):
        return self.Given(self)  # TODO fix typing

    @property
    def when(self):
        return self.When(self)

    @property
    def then(self):
        return self.Then(self)

    class Given:
        """
        The "Given" steps set up the initial context or state for the scenario.
        These steps are used to describe the initial situation before an action is taken.
        """

        def __init__(self, testcase: PlaywrightTestCase):
            self.testcase = testcase

    class When:
        """
        The "When" steps describe the actions or events that occur.
        These steps are used to specify the actions taken by the user or the system.
        """

        def __init__(self, testcase: PlaywrightTestCase):
            self.testcase = testcase

    class Then:
        """
        The "Then" steps specify the expected outcomes or results.
        These steps are used to verify the results of the actions taken in the "When" steps.

        Example:

            async with browser_page() as page:
                await self.then.page_should_contain_text(page, "TEST")
        """

        # This indicates that the test is inverted (not_), this can be used to optimize tests.
        is_inverted = False

        def __init__(self, testcase: PlaywrightTestCase):
            self.testcase = testcase

        @property
        def not_(self):
            class InvertedThen:
                def __init__(self, then):
                    self.then = then
                    self.then.is_inverted = True

                def __getattr__(self, item):
                    method = getattr(self.then, item)

                    async def inverted_method(*args, **kwargs):
                        try:
                            await method(*args, **kwargs)
                        except (AssertionError, TimeoutError):
                            return

                        raise AssertionError(
                            f'Expected {method.__name__} to raise an AssertionError due to "not_".'
                        )

                    return inverted_method

            return InvertedThen(self)

        async def url_should_be(self, page: Page, url: str) -> None:
            await expect(page).to_have_url(url)

        async def page_should_contain_text(
            self, page: Page, text: str, timeout: int | None = None
        ) -> Locator:
            if timeout is None:
                timeout = 500 if self.is_inverted else 10000

            # Wait for the text to appear in the DOM
            await page.wait_for_selector(f"text={text}", timeout=timeout)

            # Confirm the element with the text is visible
            element = page.locator(f"text={text}").nth(0)
            await expect(element).to_be_visible(timeout=timeout)
            return element


class GherkinLikeTestCase(GerkinMixin, PlaywrightTestCase):
    pass
