from playwright.sync_api import Locator, Page, TimeoutError, expect
from pytest_django.live_server_helper import LiveServer


class GherkinScenario:
    def __init__(self, runner: "GherkinRunner") -> None:
        self.runner = runner


class GherkinRunner:
    """
    Experimental approach to writing Gherkin-like style test scenarios in pytest.

    The gherkin runner is made available through the pytest fixture `runner`.
    The runner exposes the :class:`pytest_django.live_server_helper.LiveServer` through `runner.live_server`.

    Example:

        def test_not_logged_in(page: Page, runner: GherkinRunner):
            runner.when.go_to_root_page(page)

            runner.then.page_should_contain_text(page, "403")


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

    def __init__(self, live_server: LiveServer):
        self.live_server = live_server

    @property
    def given(self):
        return self.Given(self)

    @property
    def when(self):
        return self.When(self)

    @property
    def then(self):
        return self.Then(self)

    class Given(GherkinScenario):
        """
        The "Given" steps set up the initial context or state for the scenario.
        These steps are used to describe the initial situation before an action is taken.
        """

        pass

    class When(GherkinScenario):
        """
        The "When" steps describe the actions or events that occur.
        These steps are used to specify the actions taken by the user or the system.
        """

        def go_to_root_page(self, page):
            page.goto(f"{self.runner.live_server.url}/")

    class Then(GherkinScenario):
        """
        The "Then" steps specify the expected outcomes or results.
        These steps are used to verify the results of the actions taken in the "When" steps.
        """

        # This indicates that the test is inverted (not_), this can be used to optimize tests.
        is_inverted = False

        @property
        def not_(self):
            class InvertedThen:
                def __init__(self, then):
                    self.then = then
                    self.then.is_inverted = True

                def __getattr__(self, item):
                    method = getattr(self.then, item)

                    def inverted_method(*args, **kwargs):
                        try:
                            method(*args, **kwargs)
                        except (AssertionError, TimeoutError):
                            return

                        raise AssertionError(
                            f'Expected {method.__name__} to raise an AssertionError due to "not_".'
                        )

                    return inverted_method

            return InvertedThen(self)

        def url_should_be(self, page: Page, url: str) -> None:
            expect(page).to_have_url(url)

        def page_should_contain_text(
            self, page: Page, text: str, timeout: int | None = None
        ) -> Locator:
            if timeout is None:
                timeout = 500 if self.is_inverted else 10000

            # Wait for the text to appear in the DOM
            page.wait_for_selector(f"text={text}", timeout=timeout)

            # Confirm the element with the text is visible
            element = page.locator(f"text={text}").nth(0)
            expect(element).to_be_visible(timeout=timeout)
            return element
