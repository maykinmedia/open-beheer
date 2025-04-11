Environment Variables
=====================

This document outlines all environment variables used in the project, separated by backend (Django) and frontend (React).

Backend (Django)
----------------

.. list-table::
   :header-rows: 1
   :widths: 30 50 20

   * - Variable
     - Description
     - Default
   * - ``FOO``
     - Bar
     - ``"bla"``

Frontend (React)
----------------

.. list-table::
   :header-rows: 1
   :widths: 30 50 20

   * - Variable
     - Description
     - Default
   * - ``MYKN_API_URL``
     - Base URL for the backend API.
     - ``http://localhost:5173``
   * - ``MYKN_API_PATH``
     - Path to the API.
     - ``/api/v1``

Notes
-----

- All frontend environment variables **must** start with ``MYKN_`` to be exposed to the app during build time.

