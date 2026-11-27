import logging  # noqa: TID251 - only used for the log levels

from sentry_sdk.integrations import django, redis
from sentry_sdk.integrations.logging import LoggingIntegration


def get_sentry_integrations() -> list:
    """
    Determine which Sentry SDK integrations to enable.
    """
    default = [
        django.DjangoIntegration(),
        LoggingIntegration(
            level=logging.INFO,  # breadcrumbs
            # do not send any logs as event to Sentry at all - these must be scraped by
            # the (container) infrastructure instead.
            event_level=None,
        ),
        redis.RedisIntegration(),
    ]


    return [*default]
