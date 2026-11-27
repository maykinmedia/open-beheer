.. _devops_logging:

=======
Logging
=======

Open Beheer uses `structlog`_ for structured logging. Every log record is an
event (a short, machine-friendly name) with a set of key-value pairs as context,
instead of a free-form text message.

.. _structlog: https://www.structlog.org/

Configuration
=============

The logging configuration is controlled by these environment variables:

* ``LOG_STDOUT``: whether to log to stdout instead of to ``log/application.jsonl``.
  Defaults to ``True`` for development or when using Docker, ``False`` otherwise.

* ``LOG_FORMAT_CONSOLE``: format of the console output, valid values are ``json`` or ``plain_console`` (human readable).
  Set to ``json`` for proper formatting of logs in Grafana. Defaults to ``plain_console`` for development, ``json`` otherwise.

* ``LOG_LEVEL``: log level of the ``openarchiefbeheer`` loggers, valid values are ``DEBUG``, ``INFO``, ``WARNING``, or ``ERROR``.
  Defaults to ``INFO``.

* ``LOG_REQUESTS``: whether to log every incoming request via django-structlog. Note that we only log the method, path,
  status code, and duration for every request. This does *not* include request/response bodies, which might contain
  sensitive information. Defaults to ``True``.

* ``LOG_OUTGOING_REQUESTS``: When enabled, outgoing requests are logged. Disabled by
  default.

  .. warning:: This setting should not be enabled in production.

* ``LOG_OUTGOING_REQUESTS_DB_SAVE``: When enabled, logs are saved in the database. This
  requires some attention as sensitive data may be stored in your database. We advise
  not enabling this by default via Django settings and instead rely on runtime configuration.

* ``LOG_OUTGOING_REQUESTS_DB_SAVE_BODY``: When enabled, the request and the response body
  are saved in the database.

* ``LOG_OUTGOING_REQUESTS_EMIT_BODY``: When enabled, the request and the response bodies
  are logged.

* ``LOG_OUTGOING_REQUESTS_MAX_AGE``: The maximum amount (in days) that the logs will be
  kept. Logs older than this will be deleted.

.. warning:: Be aware that a number of settings can be configured at runtime in the admin
  interface. The settings that can be overridden are::

    *  ``LOG_OUTGOING_REQUESTS_DB_SAVE`` -> **Save logs to database**
    *  ``LOG_OUTGOING_REQUESTS_DB_SAVE_BODY`` -> **Save request + response body**


