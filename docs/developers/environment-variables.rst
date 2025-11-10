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
   * - ``ENVIRONMENT``
     - A label for the environment
     - ``"test-maykin"``
   * - ``ALLOWED_HOSTS``
     -  See `Django docs <https://docs.djangoproject.com/en/5.2/ref/settings/#allowed-hosts>`__ 
     - ``localhost``
   * - ``DJANGO_SETTINGS_MODULE``
     -  Path to the Django settings module to use.
     - ``openbeheer.conf.docker``
   * - ``SECRET_KEY``
     - See `Django docs <https://docs.djangoproject.com/en/5.2/ref/settings/#secret-key>`__. Can be generated with tools like https://djecrety.ir/.
     - ``someSecretKey``
   * - ``DB_NAME``
     - Name of the database.
     - ``openbeheer``
   * - ``DB_USER``
     - Name of the database user.
     - ``openbeheer``
   * - ``DB_HOST``
     - Database hostname.
     - ``localhost``
   * - ``DB_PORT``
     - Database port.
     - ``5432``
   * - ``CACHE_DEFAULT``
     -  Address of the cache to use for the default cache.
     - ``redis:6379/0``
   * - ``CACHE_AXES``
     -  Address of the cache to use for the axes cache.
     - ``redis:6379/0``
   * - ``CSRF_TRUSTED_ORIGINS``
     - See the `Django docs <https://docs.djangoproject.com/en/5.2/ref/settings/#csrf-trusted-origins>`__.
     - ``http://localhost:9000``
   * - ``CSRF_COOKIE_SAMESITE``
     - See the `Django docs <https://docs.djangoproject.com/en/5.2/ref/settings/#csrf-cookie-samesite>`__.
     - ``Strict``
   * - ``CSRF_COOKIE_SECURE``
     - See the `Django docs <https://docs.djangoproject.com/en/5.2/ref/settings/#csrf-cookie-secure>`__.
     - ``True``
   * - ``SESSION_COOKIE_SAMESITE``
     - See the `Django docs <https://docs.djangoproject.com/en/5.2/ref/settings/#session-cookie-samesite>`__.
     - ``Strict``
   * - ``SESSION_COOKIE_SECURE``
     - See the `Django docs <https://docs.djangoproject.com/en/5.2/ref/settings/#session-cookie-secure>`__.
     - ``True``
   * - ``SESSION_COOKIE_AGE``
     - See the `Django docs <https://docs.djangoproject.com/en/5.2/ref/settings/#session-cookie-age>`__.
     - ``900``
   * - ``OIDC_RENEW_ID_TOKEN_EXPIRY_SECONDS``
     - Should be the same as ``SESSION_COOKIE_AGE``.
     - ``900``
   * - ``OPEN_ZAAK_ADMIN_BASE_URL``
     - The url of the Open Zaak that will be used to reference back to Open Zaak when features are not available in Open Beheer.
     - ``https://openzaak.example.nl``


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

