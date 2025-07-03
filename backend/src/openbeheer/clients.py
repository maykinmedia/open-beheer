from functools import cache
from typing import Iterator, NoReturn, Protocol

from django.core.exceptions import ImproperlyConfigured
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as __

from ape_pie import APIClient
from msgspec.json import decode
from zgw_consumers.client import build_client
from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service


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


@receiver(post_save, sender=Service)
def _(sender, instance, **_):
    if instance.api_type == APITypes.ztc:
        ztc_client.cache_clear()


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
