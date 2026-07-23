import pytest
from playwright.sync_api import Page

from openbeheer.conftest import vcr_overrides
from openbeheer.utils.gherkin_e2e import GherkinRunner
from openbeheer.utils.tests import matcher_query_without_datum_geldigheid


@pytest.mark.e2e
@vcr_overrides(
    custom_matchers=[
        ("query_without_datum_geldigheid", matcher_query_without_datum_geldigheid)
    ],
    custom_match_on=[
        "method",
        "scheme",
        "host",
        "port",
        "path",
        "query_without_datum_geldigheid",
    ],
)
def test_issue_gh_384_more_fields_should_not_be_shown_for_statustypen(
    page: Page, runner: GherkinRunner
):
    _ = runner

    _.given.user_exists()
    _.given.api_config_exists()
    _.given.ztc_service_exists()

    catalogus = _.given.catalogus_exists()
    zaaktype = _.given.zaaktype_exists(catalogus)

    # Navigate to zaaktype
    _.when.user_logs_in(page)
    _.when.user_selects_catalogus(page, catalogus)
    _.when.user_navigates_to_zaaktype_detail_page(page, zaaktype)

    # Select tab
    _.when.user_selects_tab(page, "Statustypen")

    # Add
    _.when.user_clicks_on_button(page, "Bewerken")
    _.when.user_clicks_on_button(page, "Voeg toe")
    _.then.page_should_not_contain_button(page, "Meer velden")


@pytest.mark.e2e
@vcr_overrides(
    custom_matchers=[
        ("query_without_datum_geldigheid", matcher_query_without_datum_geldigheid)
    ],
    custom_match_on=[
        "method",
        "scheme",
        "host",
        "port",
        "path",
        "query_without_datum_geldigheid",
    ],
)
def test_issue_gh_384_more_fields_should_not_be_shown_for_zaaktypeinformatieobjecttypen(
    page: Page, runner: GherkinRunner
):
    _ = runner

    _.given.user_exists()
    _.given.api_config_exists()
    _.given.ztc_service_exists()

    catalogus = _.given.catalogus_exists()
    informatieobjecttype = _.given.informatieobjecttype_exists(catalogus)
    _.given.informatieobjecttype_is_published(informatieobjecttype)
    zaaktype = _.given.zaaktype_exists(catalogus)

    # Navigate to zaaktype
    _.when.user_logs_in(page)
    _.when.user_selects_catalogus(page, catalogus)
    _.when.user_navigates_to_zaaktype_detail_page(page, zaaktype)

    # Select tab
    _.when.user_selects_tab(page, "Zaaktypeinformatieobjecttypen")

    # Add
    _.when.user_clicks_on_button(page, "Bewerken")
    _.when.user_clicks_on_button(page, "Voeg toe")
    _.then.page_should_not_contain_button(page, "Meer velden")


@pytest.mark.e2e
@vcr_overrides(
    custom_matchers=[
        ("query_without_datum_geldigheid", matcher_query_without_datum_geldigheid)
    ],
    custom_match_on=[
        "method",
        "scheme",
        "host",
        "port",
        "path",
        "query_without_datum_geldigheid",
    ],
)
def test_issue_gh_384_more_fields_should_not_be_shown_for_roltypen(
    page: Page, runner: GherkinRunner
):
    _ = runner

    _.given.user_exists()
    _.given.api_config_exists()
    _.given.ztc_service_exists()

    catalogus = _.given.catalogus_exists()
    zaaktype = _.given.zaaktype_exists(catalogus)

    # Navigate to zaaktype
    _.when.user_logs_in(page)
    _.when.user_selects_catalogus(page, catalogus)
    _.when.user_navigates_to_zaaktype_detail_page(page, zaaktype)

    # Select tab
    _.when.user_selects_tab(page, "Roltypen")

    # Add
    _.when.user_clicks_on_button(page, "Bewerken")
    _.when.user_clicks_on_button(page, "Voeg toe")
    _.then.page_should_not_contain_button(page, "Meer velden")


@pytest.mark.e2e
@vcr_overrides(
    custom_matchers=[
        ("query_without_datum_geldigheid", matcher_query_without_datum_geldigheid)
    ],
    custom_match_on=[
        "method",
        "scheme",
        "host",
        "port",
        "path",
        "query_without_datum_geldigheid",
    ],
)
def test_issue_gh_384_more_fields_should_be_shown_for_resultaattypen(
    page: Page, runner: GherkinRunner
):
    _ = runner

    _.given.user_exists()
    _.given.api_config_exists()
    _.given.ztc_service_exists()

    catalogus = _.given.catalogus_exists()
    zaaktype = _.given.zaaktype_exists(catalogus)

    # Navigate to zaaktype
    _.when.user_logs_in(page)
    _.when.user_selects_catalogus(page, catalogus)
    _.when.user_navigates_to_zaaktype_detail_page(page, zaaktype)

    # Select selectielijst procestype
    _.when.user_selects_tab(page, "Overzicht")
    _.when.user_clicks_on_button(page, "Bewerken")
    _.then.page_should_contain_text(page, "Opslaan")

    _.when.user_fills_form_field(
        page, 'Bewerk "selectielijstProcestype"', "2020 - 1 - "
    )

    _.when.user_clicks_on_button(page, "Opslaan")
    _.then.page_should_contain_text(page, "Bewerken")

    # Select tab
    _.when.user_selects_tab(page, "Resultaattypen")

    # Add
    _.when.user_clicks_on_button(page, "Bewerken")
    _.when.user_clicks_on_button(page, "Voeg toe")

    # Fill out details
    _.when.user_fills_form_field(
        page, "Omschrijving", "Werking duidelijk", skip_combo=True
    )
    _.when.user_clicks_on_button(page, "Doorgaan")
    _.then.page_should_contain_button(page, "Meer velden")


@pytest.mark.e2e
@vcr_overrides(
    custom_matchers=[
        ("query_without_datum_geldigheid", matcher_query_without_datum_geldigheid)
    ],
    custom_match_on=[
        "method",
        "scheme",
        "host",
        "port",
        "path",
        "query_without_datum_geldigheid",
    ],
)
def test_issue_gh_384_more_fields_should_not_be_shown_for_eigenschappen(
    page: Page, runner: GherkinRunner
):
    _ = runner

    _.given.user_exists()
    _.given.api_config_exists()
    _.given.ztc_service_exists()

    catalogus = _.given.catalogus_exists()
    zaaktype = _.given.zaaktype_exists(catalogus)

    # Navigate to zaaktype
    _.when.user_logs_in(page)
    _.when.user_selects_catalogus(page, catalogus)
    _.when.user_navigates_to_zaaktype_detail_page(page, zaaktype)

    # Select tab
    _.when.user_selects_tab(page, "Eigenschappen")

    # Add
    _.when.user_clicks_on_button(page, "Bewerken")
    _.when.user_clicks_on_button(page, "Voeg toe")
    _.then.page_should_not_contain_button(page, "Meer velden")
