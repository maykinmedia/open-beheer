.. _developers_health-checks:

=============
Health Checks
=============

Health checks are implemented with a similar pattern to the ``django-setup-configuration`` package.
There is a runner class :class:`openbeheer.health_checks.runner.HealthChecksRunner`, which imports all the 
configured checks. These are specified in the Django setting ``HEALTH_CHECKS``.

Each check extends the abstract class :class:`openbeheer.health_checks.checks.HealthCheck` and implements
the method :func:`HealthCheck.run` which will be called by the runner and should return an instance of 
:class:`openbeheer.health_checks.types.HealthCheckResult`.

The runner can be called from the management command ``health_checks`` or throught the API endpoint.

