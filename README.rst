===========
Open Beheer
===========

:Version: 0.9.1
:Source: https://github.com/maykinmedia/open-beheer
:Keywords: Common Ground, Catalogi API, ZGW APIs

|docker|

Developed by `Maykin B.V.`_, originally commissioned by `Gemeente Rotterdam`_.

.. note::

   ⚠️ **Project status:** This project is under active development.
   Some functionality is still in progress and subject to change.

Introduction
===========

Open Beheer offers functional administrators a powerful and user-friendly
interface in addition to technical registrations such as the Catalog API in,
for example, `Open Zaak`_. While traditional interfaces are often technical
and fragmented, Open Beheer provides overview and structure. Administrators
can easily set up case types, with the correct statuses, roles, and archiving
settings—a crucial step in the information management of any government 
organization.

Thanks to Open Beheer's intuitive approach, compiling and managing 
high-quality data becomes much easier. The interface works entirely via
standardized interfaces, without detours or individual interpretations of the
data, which benefits reliability, consistency, and compliance.

As more and more registrations are created—think product data, domain-specific
models, and file information—the need for a central location for management
grows. Open Beheer offers exactly that: a single point of access where data
from multiple registrations is managed within recognizable processes, without
separate logins or contextless data fields.

By making technical standards concrete and workable, Open Beheer also
contributes to the adoption of case-based working and Common Ground within the
organization. The result: better management, higher data quality, and a solid
foundation for digital services.

Open Beheer is developed in line with the `Common Ground`_ principles,
with many plugins for government usage and with a strong focus on usability for
both end users and administrators.

.. _`Common Ground`: https://commonground.nl/
.. _`Open Zaak`: https://open-zaak.readthedocs.io/


Component
=========

|build-status| |coverage| |code-quality| |ruff| |python-versions|

This component includes the **Open Beheer UI** and the **Open Beheer Backend
for Frontend (BFF)**.


Links
=====

* `Docker image <https://hub.docker.com/r/maykinmedia/open-beheer>`_
* `Issues <https://github.com/maykinmedia/open-beheer/issues>`_
* `Code <https://github.com/maykinmedia/open-beheer>`_


Licentie
========

Copyright © `"the Stakeholders"`_, 2025

Licensed under the `EUPL`_.

.. _`Nederlandse versie`: README.NL.rst
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
