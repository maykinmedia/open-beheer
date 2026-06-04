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
def test_scenario_edit_related_statustypen(page: Page, runner: GherkinRunner):
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
    _.when.user_fills_form_field(page, "Omschrijving", "Status 1", index=2)

    _.when.user_clicks_on_button(page, "Voeg toe")
    _.when.user_fills_form_field(page, "Omschrijving", "Status 2", index=3)

    _.when.user_clicks_on_button(page, "Voeg toe")
    _.when.user_fills_form_field(page, "Omschrijving", "Status 3", index=4)

    _.when.user_clicks_on_button(page, "Opslaan")
    _.then.page_should_contain_text(page, "Status 1", index=1)
    _.then.page_should_contain_text(page, "Status 2", index=1)
    _.then.page_should_contain_text(page, "Status 3", index=1)

    # Update
    _.when.user_clicks_on_button(page, "Bewerken")

    _.when.user_fills_form_field(page, "Omschrijving", "Bijgewerkt", index=3)
    page.screenshot(
        path="../docs/manual/_assets/test_scenario_edit_related_statustypen.png"
    )

    _.when.user_clicks_on_button(page, "Opslaan")
    _.then.page_should_contain_text(page, "Status 1", index=1)
    _.then.page_should_contain_text(page, "Bijgewerkt")
    _.then.page_should_contain_text(page, "Status 3", index=1)

    # Remove
    _.when.user_clicks_on_button(page, "Bewerken")
    _.when.user_clicks_on_button(page, "Verwijderen", index=1)
    _.when.user_clicks_on_button(page, "Opslaan")

    _.then.page_should_contain_text(page, "Status 1", index=1)
    _.then.page_should_not_contain_text(page, "Bijgewerkt")
    _.then.page_should_contain_text(page, "Status 3", index=1)


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
def test_scenario_edit_related_zaaktypeinformatieobjecttypen(
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
    _.then.page_should_contain_text(page, "Opslaan")

    _.when.user_clicks_on_button(page, "Voeg toe")
    _.when.user_fills_form_field(
        page, "Informatieobjecttype", "Voorbeeld informatieobjecttype"
    )
    _.when.user_fills_form_field(page, "Richting", "inkomend")

    _.when.user_clicks_on_button(page, "Opslaan")
    _.then.page_should_contain_text(page, "Bewerken")

    _.then.page_should_contain_text(page, "Voorbeeld informatieobjecttype", index=1)
    _.then.page_should_contain_text(page, "Inkomend")

    # Update
    _.when.user_clicks_on_button(page, "Bewerken")
    _.then.page_should_contain_text(page, "Opslaan")

    _.when.user_fills_form_field(page, "Richting", "Uitgaand")
    page.screenshot(
        path="../docs/manual/_assets/test_scenario_edit_related_zaaktypeinformatieobjecttypen.png"
    )

    _.when.user_clicks_on_button(page, "Opslaan")
    _.then.page_should_contain_text(page, "Bewerken")

    _.then.page_should_contain_text(page, "Uitgaand")

    # Remove
    _.when.user_clicks_on_button(page, "Bewerken")
    _.then.page_should_contain_text(page, "Opslaan")

    _.when.user_clicks_on_button(page, "Verwijderen")
    _.when.user_clicks_on_button(page, "Opslaan")

    _.then.page_should_not_contain_text(page, "Uitgaand")


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
def test_scenario_edit_related_roltypen(page: Page, runner: GherkinRunner):
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
    _.then.page_should_contain_text(page, "Opslaan")

    _.when.user_clicks_on_button(page, "Voeg toe")
    _.when.user_fills_form_field(page, 'Bewerk "omschrijving"', "Adviseur", index=1)
    _.when.user_fills_form_field(
        page, 'Bewerk "omschrijvingGeneriek"', "Adviseur", index=0
    )

    _.when.user_clicks_on_button(page, "Voeg toe")
    _.when.user_fills_form_field(page, 'Bewerk "omschrijving"', "Behandelaar", index=2)
    _.when.user_fills_form_field(
        page, 'Bewerk "omschrijvingGeneriek"', "Behandelaar", index=1
    )

    _.when.user_clicks_on_button(page, "Voeg toe")
    _.when.user_fills_form_field(
        page, 'Bewerk "omschrijving"', "Belanghebbende", index=3
    )
    _.when.user_fills_form_field(
        page, 'Bewerk "omschrijvingGeneriek"', "Belanghebbende", index=2
    )

    _.when.user_clicks_on_button(page, "Opslaan")
    _.then.page_should_contain_text(page, "Adviseur")
    _.then.page_should_contain_text(page, "Behandelaar")
    _.then.page_should_contain_text(page, "Belanghebbende")

    # Update
    _.when.user_clicks_on_button(page, "Bewerken")
    _.then.page_should_contain_text(page, "Opslaan")

    _.when.user_fills_form_field(page, 'Bewerk "omschrijving"', "Uitvoerder", index=2)
    page.screenshot(
        path="../docs/manual/_assets/test_scenario_edit_related_roltypen.png"
    )

    _.when.user_clicks_on_button(page, "Opslaan")
    _.then.page_should_contain_text(page, "Adviseur")
    _.then.page_should_contain_text(page, "Uitvoerder")
    _.then.page_should_contain_text(page, "Belanghebbende")

    # Remove
    _.when.user_clicks_on_button(page, "Bewerken")
    _.then.page_should_contain_text(page, "Opslaan")

    _.when.user_clicks_on_button(page, "Verwijderen", index=1)
    _.when.user_clicks_on_button(page, "Opslaan")

    _.then.page_should_contain_text(page, "Adviseur")
    _.then.page_should_not_contain_text(page, "Uitvoerder")
    _.then.page_should_contain_text(page, "Belanghebbende")


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
def test_scenario_edit_related_resultaattypen(page: Page, runner: GherkinRunner):
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
    _.then.page_should_contain_text(page, "Opslaan")

    _.when.user_clicks_on_button(page, "Voeg toe")

    # Fill out details
    _.when.user_fills_form_field(
        page, "Omschrijving", "Werking duidelijk", skip_combo=True
    )
    _.when.user_clicks_on_button(page, "Doorgaan")
    _.when.user_clicks_on_button(page, "Opslaan")
    _.then.page_should_contain_text(page, "Bewerken")
    _.then.page_should_contain_text(page, "Werking duidelijk", index=1)

    # Update details
    _.when.user_clicks_on_button(page, "Bewerken")
    _.then.page_should_contain_text(page, "Opslaan")

    _.when.user_clicks_on_button(page, "Meer velden")
    _.when.user_fills_form_field(
        page, "Omschrijving", "Handleiding begrepen", skip_combo=True
    )
    page.screenshot(
        path="../docs/manual/_assets/test_scenario_edit_related_resultaattypen.png"
    )

    _.when.user_clicks_on_button(page, "Doorgaan")
    _.when.user_clicks_on_button(page, "Opslaan")
    _.then.page_should_contain_text(page, "Bewerken")
    _.then.page_should_contain_text(page, "Handleiding begrepen", index=1)

    # Remove
    _.when.user_clicks_on_button(page, "Bewerken")
    _.then.page_should_contain_text(page, "Opslaan")

    _.when.user_clicks_on_button(page, "Verwijderen")
    _.when.user_clicks_on_button(page, "Opslaan")
    _.then.page_should_contain_text(page, "Bewerken")

    _.then.page_should_not_contain_text(page, "Handleiding begrepen")


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
def test_scenario_edit_related_eigenschappen(page: Page, runner: GherkinRunner):
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
    _.then.page_should_contain_text(page, "Opslaan")

    _.when.user_clicks_on_button(page, "Voeg toe")
    _.when.user_fills_form_field(page, "Naam", "Eigenschap 1", index=0)
    _.when.user_fills_form_field(page, "Definitie", "1", index=0)
    _.when.user_fills_form_field(page, "Formaat", "tekst", index=0)

    _.when.user_clicks_on_button(page, "Voeg toe")
    _.when.user_fills_form_field(page, "Naam", "Eigenschap 2", index=1)
    _.when.user_fills_form_field(page, "Definitie", "2", index=1)
    _.when.user_fills_form_field(page, "Formaat", "tekst", index=1)

    _.when.user_clicks_on_button(page, "Voeg toe")
    _.when.user_fills_form_field(page, "Naam", "Eigenschap 3", index=2)
    _.when.user_fills_form_field(page, "Definitie", "3", index=2)
    _.when.user_fills_form_field(page, "Formaat", "tekst", index=2)

    _.when.user_clicks_on_button(page, "Opslaan")
    _.then.page_should_contain_text(page, "Bewerken")
    _.then.page_should_contain_text(page, "tekst", index=0)
    _.then.page_should_contain_text(page, "tekst", index=1)
    _.then.page_should_contain_text(page, "tekst", index=2)

    # Update
    _.when.user_clicks_on_button(page, "Bewerken")
    _.then.page_should_contain_text(page, "Opslaan")

    _.when.user_fills_form_field(page, "Definitie", "Bijgewerkt", index=1)
    page.screenshot(
        path="../docs/manual/_assets/test_scenario_edit_related_eigenschappen.png"
    )
    _.when.user_clicks_on_button(page, "Opslaan")
    _.then.page_should_contain_text(page, "Bewerken")

    _.then.page_should_contain_text(page, "tekst", index=0)
    _.then.page_should_contain_text(page, "Bijgewerkt")
    _.then.page_should_contain_text(page, "tekst", index=1)

    # Remove
    _.when.user_clicks_on_button(page, "Bewerken")
    _.then.page_should_contain_text(page, "Opslaan")

    _.when.user_clicks_on_button(page, "Verwijderen", index=1)
    _.when.user_clicks_on_button(page, "Opslaan")
    _.then.page_should_contain_text(page, "Bewerken")

    _.then.page_should_contain_text(page, "Eigenschap 1", index=1)
    _.then.page_should_not_contain_text(page, "Eigenschap 2")
    _.then.page_should_contain_text(page, "Eigenschap 3", index=1)
