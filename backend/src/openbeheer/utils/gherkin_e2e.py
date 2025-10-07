from furl import furl
from playwright.sync_api import Locator, Page, expect
from pytest_django.live_server_helper import LiveServer

from openbeheer.types.ztc import Catalogus


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

        def go_to_root_page(self, page: Page) -> None:
            page.goto(f"{self.runner.live_server.url}/")

        def user_logs_in(self, page: Page, username: str, password: str) -> None:
            page.goto(f"{self.runner.live_server.url}/")
            expect(page).to_have_url(self.runner.live_server.url + "/login?next=/")

            page.get_by_label("Gebruikersnaam").fill(username)
            page.get_by_label("Wachtwoord").fill(password)
            page.get_by_role("button", name="Inloggen").click()

        def select_catalogus(self, page: Page, catalogus: Catalogus) -> None:
            select = page.get_by_text("Selecteer catalogus")
            select.click()
            option = page.get_by_text(f"{catalogus.naam} ({catalogus.domein})")
            option.click()
            assert catalogus.url
            expect(page).to_have_url(
                self.runner.live_server.url
                + f"/OZ/{furl(catalogus.url).path.segments[-1]}/zaaktypen"
            )

        def go_to_informatieobjecttype_list_page(
            self, page: Page, catalogus: Catalogus
        ) -> None:
            button = page.get_by_role(role="button", name="Informatieobjecttypen")
            button.click()
            assert catalogus.url
            expect(page).to_have_url(
                self.runner.live_server.url
                + f"/OZ/{furl(catalogus.url).path.segments[-1]}/informatieobjecttypen"
            )

    class Then(GherkinScenario):
        """
        The "Then" steps specify the expected outcomes or results.
        These steps are used to verify the results of the actions taken in the "When" steps.
        """

        def url_should_be(self, page: Page, url: str) -> None:
            expect(page).to_have_url(url)

        def path_should_be(self, page: Page, path: str) -> None:
            self.url_should_be(page, self.runner.live_server.url + path)

        def page_should_contain_text(
            self, page: Page, text: str, timeout: int | None = None
        ) -> Locator:
            if timeout is None:
                timeout = 500

            # Wait for the text to appear in the DOM
            page.wait_for_selector(f"text={text}", timeout=timeout)

            # Confirm the element with the text is visible
            element = page.locator(f"text={text}").nth(0)
            expect(element).to_be_visible(timeout=timeout)
            return element
