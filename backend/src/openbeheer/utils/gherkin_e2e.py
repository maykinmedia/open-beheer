import re

from furl import furl
from playwright.sync_api import Locator, Page, expect
from pytest_django.live_server_helper import LiveServer
from zgw_consumers.constants import APITypes, AuthTypes
from zgw_consumers.models import Service
from zgw_consumers.test.factories import ServiceFactory

from openbeheer.accounts.models import User
from openbeheer.accounts.tests.factories import UserFactory
from openbeheer.config.models import APIConfig
from openbeheer.types import ZaakTypeWithUUID
from openbeheer.types.ztc import Catalogus
from openbeheer.utils.open_zaak_helper.data_creation import (
    OpenZaakDataCreationHelper,
    _JSONEncodable,
)


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
            runner.when.user_open_application(page)

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

        def user_exists(self) -> User:
            """
            Creates a user for testing.
            """

            return UserFactory.create(username="johndoe", password="secret")

        def objecttypen_service_exists(self) -> Service:
            """
            Creates a (fake) objecttypen service for testing and registers it in
            API_CONFIG.
            """

            objecttypen_service = ServiceFactory.create(
                api_type=APITypes.orc,
                api_root="http://localhost:8004/api/v2/",
                auth_type=AuthTypes.api_key,
                header_key="Authorization",
                header_value="Token 18b2b74ef994314b84021d47b9422e82b685d82f",
            )
            api_config = APIConfig.get_solo()
            api_config.objecttypen_api_service = objecttypen_service
            api_config.save()

            return objecttypen_service

        def selectielijst_service_exists(self) -> Service:
            """
            Creates a selectielijst service for testing and registers it in API_CONFIG.
            """

            selectielijst_service = ServiceFactory.create(
                api_type=APITypes.orc,
                api_root="https://selectielijst.openzaak.nl/api/v1/",
            )
            api_config = APIConfig.get_solo()
            api_config.selectielijst_api_service = selectielijst_service
            api_config.save()

            return selectielijst_service

        def ztc_service_exists(self) -> Service:
            """
            Creates ztc Service for testing.
            """

            return ServiceFactory.create(
                slug="OZ",
                api_type=APITypes.ztc,
                api_root="http://localhost:8003/catalogi/api/v1",
                client_id="test-vcr",
                secret="test-vcr",
            )

        def catalogus_exists(self) -> Catalogus:
            """
            Creates catalogus in Open Zaak for testing, depends on existence of
            ztc Service.

            :return: The created catalogus
            """

            helper = OpenZaakDataCreationHelper(ztc_service_slug="OZ")
            catalogus = helper.create_catalogus()
            assert catalogus.url
            return catalogus

        def zaaktypen_exist(
                self, catalogus: Catalogus, amount: int = 3, **overrides: _JSONEncodable
        ) -> list[ZaakTypeWithUUID]:
            """
            Creates zaaktypen in Open Zaak for testing, depends on existence of
            ztc Service.

            :return: The created zaaktypen
            """

            helper = OpenZaakDataCreationHelper(ztc_service_slug="OZ")

            zaaktypen = []
            for i in range(1, amount + 1):
                padded_sequence_number = str(i).zfill(3)

                overrides = {
                    "aanleiding": f"New Zaaktype {padded_sequence_number}",
                    "doel": f"New Zaaktype {padded_sequence_number}",
                    "onderwerp": f"New Zaaktype {padded_sequence_number}",
                    "referentieproces": {"naam": f"ReferentieProces {padded_sequence_number}"},
                }
                zaaktype = helper.create_zaaktype(catalogus.url, **overrides)
                assert zaaktype.url
                zaaktypen.append(zaaktype)

            return zaaktypen

    class When(GherkinScenario):
        """
        The "When" steps describe the actions or events that occur.
        These steps are used to specify the actions taken by the user or the system.
        """

        # Authentication

        def user_logs_in(self, page: Page, username: str, password: str) -> None:
            page.goto(f"{self.runner.live_server.url}/")
            expect(page).to_have_url(self.runner.live_server.url + "/login?next=/")

            page.get_by_label("Gebruikersnaam").fill(username)
            page.get_by_label("Wachtwoord").fill(password)
            page.get_by_role("button", name="Inloggen").click()

        # Navigation

        def user_open_application(self, page: Page) -> None:
            """
            Navigate to the home page (by URL).
            """

            page.goto(f"{self.runner.live_server.url}/")

        def user_selects_catalogus(self, page: Page, catalogus: Catalogus) -> None:
            page.wait_for_load_state("networkidle")

            select = page.get_by_text("Selecteer catalogus")
            select.click()
            option = page.get_by_text(f"{catalogus.naam} ({catalogus.domein})")
            option.click()
            assert catalogus.url
            expect(page).to_have_url(
                self.runner.live_server.url
                + f"/OZ/{furl(catalogus.url).path.segments[-1]}/zaaktypen"
            )

        def user_navigates_to_zaaktype_list_page(self, page: Page) -> None:
            """
            Navigates to the zaaktype list page (by navigation)
            """

            page.wait_for_load_state("networkidle")
            button = page.get_by_role(role="button", name="Zaaktypen")
            button.click()

        def user_navigates_to_informatieobjecttype_list_page(
                self, page: Page, catalogus: Catalogus
        ) -> None:
            """
            Navigates to the informatieobjecttype list page (by navigation)
            """

            page.wait_for_load_state("networkidle")

            button = page.get_by_role(role="button", name="Informatieobjecttypen")
            button.click()
            assert catalogus.url
            expect(page).to_have_url(
                self.runner.live_server.url
                + f"/OZ/{furl(catalogus.url).path.segments[-1]}/informatieobjecttypen"
            )

        def user_navigates_to_informatieobjecttype_create_page(
                self, page: Page, catalogus: Catalogus
        ) -> None:
            page.wait_for_load_state("networkidle")

            link_button = page.get_by_text("Nieuw informatieobjecttype")
            link_button.click()
            assert catalogus.url
            expect(page).to_have_url(
                self.runner.live_server.url
                + f"/OZ/{furl(catalogus.url).path.segments[-1]}/informatieobjecttypen/create"
            )

        # Actions

        def user_clicks_on_button(self, page: Page, name: str = "") -> None:
            kwargs = {}
            if name:
                kwargs.update({"name": name})
            button = page.get_by_role("button", **kwargs)
            button.click()

        def user_clicks_on_link(self, page: Page, name: str = "") -> None:
            kwargs = {}
            if name:
                kwargs.update({"name": name})
            iot_link = page.get_by_role("link", **kwargs)
            iot_link.click()

            page.wait_for_load_state("networkidle")
            href = iot_link.first.get_attribute("href")
            self.runner.then.url_should_match(page, href)

        def user_clicks_on_checkbox(self, page: Page, label: str = "") -> None:
            page.get_by_label(label).click()

    class Then(GherkinScenario):
        """
        The "Then" steps specify the expected outcomes or results.
        These steps are used to verify the results of the actions taken in the "When" steps.
        """

        def url_should_be(self, page: Page, url: str) -> None:
            expect(page).to_have_url(url)

        def url_should_match(self, page: Page, url: str) -> None:
            pattern = re.compile(fr".*{re.escape(url)}.*")
            expect(page).to_have_url(pattern)

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

        def page_should_not_contain_text(self, page: Page, text: str) -> None:
            expect(page.locator(f"text={text}")).to_have_count(0)
