from functools import cache
from typing import Iterator, NoReturn, Protocol

from django.core.exceptions import ImproperlyConfigured
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as __

from ape_pie import APIClient
from msgspec.json import decode
from zgw_consumers.client import build_client
from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service

from openbeheer.config.models import APIConfig


@cache
def ztc_client(slug: str = "") -> APIClient | NoReturn:
    """Return and APIClient for the configured ZTC service

    The empty slug `""` wil return whatever the "first" is if it exists.
    """
    services = Service.objects.filter(api_type=APITypes.ztc)
    if slug:
        services = services.filter(slug=slug)

    if not (service := services.first()):
        raise ImproperlyConfigured(__("No ZTC service configured"))

    client = build_client(service)
    # passing as arg to build_client doesn't work
    client.headers["Accept-Crs"] = "EPSG:4326"
    return client


@cache
def selectielijst_client() -> APIClient:
    # This is probably strongly tied to the ZTC service, because
    # for selectielijsten Open Zaak has a "ReferentieLijstConfig" singleton
    # service configured with an array of acceptable years.
    #
    # I assume it rejects URLs outside that configured service,
    # but it doesn't expose this in an API. So we can't directly make sure we use the
    # same one.
    # XXX: We could add a Healthcheck that tries to fetch a zaaktype and check if
    # selectielijstProces has the same URL prefix.

    # But given these selectielijsten are nationally defined and published, IMHO
    # these could live some place centrally and served with
    # Access-Control-Allow-Origin: *
    # so the UI can just call them directly.

    try:
        config = APIConfig.get_solo()
        if config.selectielijst_api_service is None:
            raise ValueError
    except (APIConfig.DoesNotExist, ValueError) as e:
        raise ImproperlyConfigured(__("No Selectielijst service configured")) from e

    return build_client(config.selectielijst_api_service)


@receiver([post_delete, post_save], sender=Service)
def _(sender, instance, **_):
    if instance.api_type == APITypes.ztc:
        ztc_client.cache_clear()
    selectielijst_client.cache_clear()


@receiver([post_delete, post_save], sender=APIConfig)
def _(sender, instance, **_):
    selectielijst_client.cache_clear()


class ZGWPagedResponseProtocol[T](Protocol):
    next: str | None
    results: list[T]


def iter_pages[T](
    client: APIClient, response: ZGWPagedResponseProtocol[T]
) -> Iterator[T]:
    yield from response.results

    while next_url := response.next:
        resp = client.get(next_url)
        resp.raise_for_status()
        response = decode(resp.content, type=response.__class__, strict=False)
        yield from response.results
