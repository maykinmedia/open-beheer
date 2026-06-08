========================
Zaaktype publiceren
========================

.. figure:: ../_assets/test_scenario_publish_informatieobjecttype.png
   :alt: Zaaktype publiceren
   :align: center

   Zaaktype publiceren


Een zaaktype moet worden gepubliceerd voordat het gebruikt kan worden voor het registreren van zaken. Bij publicatie wordt het zaaktype beschikbaar gesteld in de catalogus.

Vereisten voor publicatie
==========================

Voordat u een zaaktype kunt publiceren, moet het aan bepaalde eisen voldoen:

**Minimaal twee statustypen**
   Er moeten tenminste twee statustypen zijn toegevoegd (bijvoorbeeld "In behandeling" en "Afgehandeld")

**Minimaal één roltype**
   Er moet tenminste één roltype zijn toegevoegd

**Minimaal één resultaattype**
   Er moet tenminste één resultaattype zijn toegevoegd

**Alle verplichte velden ingevuld**
   Alle verplichte velden in het tabblad **Algemeen** en **Overzicht** moeten zijn ingevuld

.. note::
   De applicatie controleert automatisch of aan alle vereisten is voldaan. Als niet aan alle vereisten is voldaan, worden
   ontbrekende velden aangegeven met een foutmelding. Tabbladen met velden fout of niet ingevulde velden worden aangeven
   doormiddel van een uitroepteken **(!)**.

Stappen
=======

1. Zorg ervoor dat het zaaktype compleet is en aan alle vereisten voldoet (zie :doc:`bewerken` en :doc:`gerelateerde-objecten`)
2. Navigeer naar de detailpagina van het zaaktype (zie :doc:`navigeren`)
3. Controleer of de status "Concept" wordt weergegeven
4. Klik op **Bewerken**
5. Klik op de knop **Publiceren**

Resultaat
=========

Het zaaktype is nu gepubliceerd en de status verandert van "Concept" naar "Actueel". Het zaaktype kan nu worden gebruikt voor het registreren van zaken.

.. warning::
   Na publicatie kunnen bepaalde eigenschappen van het zaaktype niet meer worden gewijzigd. Als u toch wijzigingen wilt aanbrengen, moet u een nieuwe versie van het zaaktype aanmaken.

Nieuwe versie aanmaken
======================

Als u een gepubliceerd zaaktype wilt wijzigen:

1. Maak een nieuwe versie aan door op de knop **Nieuwe versie** te klikken
2. Voer de gewenste wijzigingen door
3. Publiceer de nieuwe versie
4. De oude versie blijft beschikbaar voor bestaande zaken, nieuwe zaken gebruiken de nieuwe versie

.. tip::
   Houd rekening met de impact van wijzigingen. Overleg met uw team voordat u een nieuw zaaktype publiceert of een nieuwe versie aanmaakt.
