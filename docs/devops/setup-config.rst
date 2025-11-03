Automatic configuration
=======================

The automatic configuration with ``django-setup-configuration`` supports configuring:

- OIDC login
- ZGW Services
- General API configuration

You can find an example of a full setup configuration file :ref:`here<example_auto_config>`.

OIDC login
----------

.. setup-config-example:: mozilla_django_oidc_db.setup_configuration.steps.AdminOIDCConfigurationStep

ZGW Services
------------

.. setup-config-example:: zgw_consumers.contrib.setup_configuration.steps.ServiceConfigurationStep



General API configuration
-------------------------

The values of the ``selectielijst_service_identifier`` and the ``objecttypen_service_identifier`` should refer to
the ``identifier`` (slug) of the corresponding ZGW service.

.. setup-config-example:: openbeheer.config.setup_configuration.steps.APIConfigConfigurationStep

