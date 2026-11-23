.. _devops_logging:

=======
Logging
=======

Open Beheer uses `structlog`_ for structured logging. Every log record is an
event (a short, machine-friendly name) with a set of key-value pairs as context,
instead of a free-form text message.

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


.. _structlog: https://www.structlog.org/
