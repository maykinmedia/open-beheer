===========
Open Beheer
===========

:Version: n/a
:Source: https://github.com/maykinmedia/open-beheer
:Keywords: Common Ground, Catalogi API, ZGW APIs

|docker|

Grip op je zaaktypencatalogus, producttypen en objecttypen met een intuïtieve
interface. (`English version`_)

Ontwikkeld door `Maykin B.V.`_, oorspronkelijk in opdracht van `Gemeente Rotterdam`_.

.. note::

   ⚠️ **Projectstatus:** Dit project is in actieve ontwikkeling.
   Bepaalde functionaliteiten zijn nog in aanbouw en kunnen wijzigen.


Introductie
===========

Open Beheer biedt functioneel beheerders een krachtige en gebruiksvriendelijke
interface bovenop de technische registraties zoals de Catalogi API in bijv. 
`Open Zaak`_. Waar traditionele interfaces vaak technisch en versnipperd zijn,
brengt Open Beheer overzicht en structuur. Beheerders kunnen eenvoudig
zaaktypen inrichten, met de juiste statussen, rollen en 
archiveringsinstellingen - een cruciale stap in de informatiehuishouding van
elke overheidsorganisatie.

Dankzij de intuïtieve werkwijze van Open Beheer wordt het opstellen en beheren
van kwaliteitsvolle gegevens een stuk eenvoudiger. De interface werkt volledig
via gestandaardiseerde koppelvlakken, zonder omwegen of eigen interpretaties
van de data, wat de betrouwbaarheid, consistentie en compliance ten goede komt.

Naarmate er steeds meer registraties ontstaan - denk aan productgegevens,
domeinspecifieke modellen en dossierinformatie - groeit de behoefte aan een
centrale plek voor beheer. Open Beheer biedt precies dat: één toegangspunt
waar gegevens uit meerdere registraties beheerd worden binnen herkenbare
processen, zonder losse inlogs of contextloze datavelden.

Door technische standaarden concreet en werkbaar te maken, draagt Open Beheer
bovendien bij aan de adoptie van zaakgericht werken en Common Ground binnen de
organisatie. Het resultaat: beter beheer, hogere datakwaliteit en een solide
basis voor digitale dienstverlening.

Open Beheer is ontwikkeld volgens de `Common Ground`_ principes, met veel
plugins voor overheidsgebruik en met focus op gebruiksgemak voor zowel
eindgebruikers als beheerders.

.. _`Common Ground`: https://commonground.nl/
.. _`Open Zaak`: https://open-zaak.readthedocs.io/


Component
=========

|build-status| |coverage| |code-quality| |ruff| |python-versions|

Dit component omvat **Open Beheer UI** en de **Open Beheer Backend for
Frontend (BFF)**.


Links
=====

* `Docker image <https://hub.docker.com/r/maykinmedia/open-beheer>`_
* `Issues <https://github.com/maykinmedia/open-beheer/issues>`_
* `Code <https://github.com/maykinmedia/open-beheer>`_


Licentie
========

Copyright © `"the Stakeholders"`_, 2025

Licensed under the `EUPL`_.

.. _`English version`: README.rst
.. _`Maykin B.V.`: https://www.maykinmedia.nl
.. _`Gemeente Rotterdam`: https://www.rotterdam.nl
.. _`"the Stakeholders"`: STAKEHOLDERS.md
.. _`EUPL`: LICENSE.md

.. |build-status| image:: https://github.com/maykinmedia/open-beheer/actions/workflows/ci.yml/badge.svg
    :alt: Build status
    :target: https://github.com/maykinmedia/open-beheer/actions/workflows/ci.yml

.. |code-quality| image:: https://github.com/maykinmedia/open-beheer/actions//workflows/code-quality.yml/badge.svg
    :alt: Code quality checks
    :target: https://github.com/maykinmedia/open-beheer/actions//workflows/code-quality.yml

.. |coverage| image:: https://codecov.io/github/maykinmedia/open-beheer/branch/master/graphs/badge.svg?branch=master
    :alt: Coverage
    :target: https://codecov.io/gh/maykinmedia/open-beheer

.. |ruff| image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Ruff

.. |docker| image:: https://img.shields.io/docker/v/maykinmedia/open-beheer?sort=semver
    :alt: Docker image
    :target: https://hub.docker.com/r/maykinmedia/open-beheer

.. |python-versions| image:: https://img.shields.io/badge/python-3.11-blue.svg
    :alt: Supported Python versions
