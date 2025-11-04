import json
import re

from furl import furl
from playwright.sync_api import Browser, Locator, Page, expect
from pytest_django.live_server_helper import LiveServer
from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service
from zgw_consumers.test.factories import ServiceFactory

from openbeheer.accounts.models import User
from openbeheer.accounts.tests.factories import UserFactory
from openbeheer.config.models import APIConfig
from openbeheer.config.tests.factories import APIConfigFactory
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

    def __init__(self, live_server: LiveServer, browser: Browser) -> None:
        self.live_server = live_server
        self.browser = browser

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

        def api_config_exists(self) -> APIConfig:
            """
            Creates an APIConfig for testing.
            """
            api_config = APIConfigFactory.create()
            return api_config

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
            assert catalogus.url

            helper = OpenZaakDataCreationHelper(ztc_service_slug="OZ")

            zaaktypen = []
            for i in range(1, amount + 1):
                padded_sequence_number = str(i).zfill(3)

                overrides = {
                    "aanleiding": f"New Zaaktype {padded_sequence_number}",
                    "doel": f"New Zaaktype {padded_sequence_number}",
                    "onderwerp": f"New Zaaktype {padded_sequence_number}",
                    "referentieproces": {
                        "naam": f"ReferentieProces {padded_sequence_number}"
                    },
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

        def user_logs_in(
            self, page: Page, username: str = "johndoe", password: str = "secret"
        ) -> None:
            page.goto(f"{self.runner.live_server.url}/")
            expect(page).to_have_url(self.runner.live_server.url + "/login?next=/")

            page.get_by_label("Gebruikersnaam").fill(username)
            page.get_by_label("Wachtwoord").fill(password)
            page.get_by_role("button", name="Inloggen").click()

        def user_logs_out(self, page: Page) -> None:
            page.wait_for_load_state("networkidle")
            profile_button = page.get_by_role("button", name="Profiel")
            profile_button.click()

            # ¯\_(ツ)_/¯ - Attempt to fix flakiness in WebKit
            if self.runner.browser.browser_type.name == "webkit":
                page.wait_for_timeout(120)

            logout_button = page.get_by_role("button", name="Logout")
            logout_button.wait_for()
            logout_button.click()

        # Navigation

        def user_open_application(self, page: Page) -> None:
            """
            Navigate to the home page (by URL).
            """

            page.goto(f"{self.runner.live_server.url}/")

        def user_selects_catalogus(
            self, page: Page, catalogus: Catalogus, check_url: bool = True
        ) -> None:
            page.wait_for_load_state("networkidle")

            catalog_select = page.get_by_role("combobox")
            catalog_select.click()
            option = page.get_by_text(f"{catalogus.naam} ({catalogus.domein})")
            option.click()

            if check_url:
                assert catalogus.url
                expected_path = f"/OZ/{furl(catalogus.url).path.segments[-1]}/zaaktypen"
                expect(page).to_have_url(self.runner.live_server.url + expected_path)

        def user_navigates_to_zaaktype_list_page(self, page: Page) -> None:
            """
            Navigates to the zaaktype list page (by navigation)
            """

            page.wait_for_load_state("networkidle")
            button = page.get_by_role(role="button", name="Zaaktypen")
            button.click()
            page.wait_for_load_state("networkidle")

        def user_navigates_to_zaaktype_detail_page(
            self, page: Page, zaaktype: ZaakTypeWithUUID
        ) -> None:
            """
            Navigates to the zaaktype list page (by navigation)
            """

            self.runner.when.user_navigates_to_zaaktype_list_page(page)
            page.wait_for_load_state("networkidle")
            self.runner.when.user_clicks_on_link(page, str(zaaktype.identificatie))

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

        def user_selects_tab(self, page: Page, name: str = "") -> None:
            tab = page.get_by_role("tab").get_by_text(name)
            tab.wait_for()
            tab.click()

            # wait for panel to become visible
            tabpanel_id = tab.get_attribute("aria-controls")
            tabpanel = page.locator(f"#{tabpanel_id}")
            tabpanel.wait_for()

            # check url hash
            index = next(
                i
                for i, tab in enumerate(page.get_by_role("tab").all())
                if tab.text_content() == name
            )
            self.runner.then.url_should_match(page, f"tab={index}")

        # Actions
        def user_clicks_on_button(self, page: Page, name: str, index: int = 0) -> None:
            button = page.get_by_role("button", name=name, exact=True).nth(index)
            button.wait_for()
            button.click()

        def user_clicks_on_link(self, page: Page, name: str = "") -> None:
            kwargs = {}
            if name:
                kwargs.update({"name": name})

            iot_link = page.get_by_role("link", **kwargs)
            iot_link.wait_for()
            href = iot_link.first.get_attribute("href")
            iot_link.click()

            if href:
                self.runner.then.url_should_match(page, href)
            page.wait_for_load_state("networkidle")

        def user_clicks_on_checkbox(self, page: Page, label: str) -> None:
            page.get_by_label(label).click()

        def user_fills_form_field(
            self, page: Page, label: str, value: str, index: int = 0
        ) -> None:
            """
            Fills the form field with the given value.
            If multiple form fields are found, the field at the given index is filled.
            """

            # Certain form fields may be shown in a modal that needs some time to load
            # We add a tiny delay here to prevent API complication and allow the modal to render
            page.wait_for_timeout(10)

            # Try a (custom) select
            selects = page.get_by_role("combobox", name=label)
            if selects.count():
                select = selects.nth(index)
                select.click()
                option = select.get_by_text(value)
                option.click()
                return

            # Fill (native) input
            inputs = page.get_by_label(label)
            input = inputs.nth(index)
            input.fill(value)

    class Then(GherkinScenario):
        """
        The "Then" steps specify the expected outcomes or results.
        These steps are used to verify the results of the actions taken in the "When" steps.
        """

        # Location

        def url_should_be(self, page: Page, url: str) -> None:
            expect(page).to_have_url(url)

        def url_should_match(self, page: Page, url: str) -> None:
            pattern = re.compile(rf".*{re.escape(url)}.*")
            expect(page).to_have_url(pattern)

        def path_should_be(self, page: Page, path: str) -> None:
            self.url_should_be(page, self.runner.live_server.url + path)

        # Content

        def page_should_contain_text(
            self, page: Page, text: str, timeout: int | None = None, index: int = 0
        ) -> Locator:
            page.wait_for_load_state("networkidle")
            if timeout is None:
                timeout = 500

            # Confirm the element with the text is visible
            element = page.locator(f"text={text}").nth(index)
            element.wait_for()
            expect(element).to_be_visible(timeout=timeout)
            return element

        def page_should_not_contain_text(self, page: Page, text: str) -> None:
            expect(page.locator(f"text={text}")).to_have_count(0)

        def table_entry_should_contain_aria_label(
            self, page: Page, table_header: str, attribue_key: str, attribute_value: str
        ) -> None:
            table_pair = page.locator(
                ".mykn-attributelist__pair", has_text=table_header
            )

            # Locate the <dd> inside the div with the key (dt) and value (dd) pair
            dd = table_pair.locator(".mykn-attributelist__value")

            # Get the <p> inside <dd>
            paragraph = dd.locator("p")

            expect(paragraph).to_have_attribute(attribue_key, attribute_value)

        def session_storage_should_be_cleared(self, page: Page) -> None:
            session_storage = page.evaluate("() => JSON.stringify(sessionStorage)")
            content = json.loads(session_storage)

            assert len(content.keys()) == 0, (
                "The session storage is not empty as expected."
            )
