from functools import cache
from typing import Generator, NoReturn
from django.core.exceptions import ImproperlyConfigured
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as __
from ape_pie import APIClient
from zgw_consumers.client import build_client
from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service
from zgw_consumers.utils import PaginatedResponseData


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


def pagination_helper(
    client: APIClient, paginated_response: PaginatedResponseData, **kwargs
) -> Generator[PaginatedResponseData, None, None]:
    def _iter(
        _data: PaginatedResponseData,
    ) -> Generator[PaginatedResponseData, None, None]:
        yield _data

        if next_url := _data.get("next"):
            response = client.get(next_url, **kwargs)
            response.raise_for_status()
            data = response.json()

            yield from _iter(data)

    return _iter(paginated_response)
