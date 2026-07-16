Environment Variables
=====================

This document outlines environment variables used in the project, separated by backend (Django) and frontend (React).

Backend (Django)
----------------

.. list-table::
   :header-rows: 1
   :widths: 30 50 20

   * - Variable
     - Description
     - Default
   * - ``SESSION_COOKIE_AGE``
     - Session lifetime in seconds.
     - ``1209600``
   * - ``SESSION_EXPIRE_AT_BROWSER_CLOSE``
     - Expire sessions when the browser closes.
     - ``False``


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

