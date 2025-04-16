from functools import cache
from django.core.exceptions import ImproperlyConfigured
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as __

from ape_pie import APIClient
from zgw_consumers.client import build_client
from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service


@cache
def zrc_client() -> APIClient:
    try:
        client = build_client(
            Service.objects.get(api_type=APITypes.zrc),
        )
    except Service.DoesNotExist:
        raise ImproperlyConfigured(__("No ZRC service configured")) from None
    # passing as arg to build_client doesn't work
    client.headers["Accept-Crs"] = "EPSG:4326"
    return client


@receiver(post_save, sender=Service)
def _(sender, instance, **_):
    if instance.api_type == APITypes.zrc:
        zrc_client.cache_clear()


@receiver(post_delete, sender=Service)
def _(sender, instance, **_):
    if instance.api_type == APITypes.zrc:
        zrc_client.cache_clear()


@cache
def ztc_client() -> APIClient:
    try:
        client = build_client(
            Service.objects.get(api_type=APITypes.ztc),
        )
    except Service.DoesNotExist:
        raise ImproperlyConfigured(__("No ZTC service configured")) from None
    # passing as arg to build_client doesn't work
    client.headers["Accept-Crs"] = "EPSG:4326"
    return client


@receiver(post_save, sender=Service)
def _(sender, instance, **_):
    if instance.api_type == APITypes.zrc:
        zrc_client.cache_clear()


@receiver(post_delete, sender=Service)
def _(sender, instance, **_):
    if instance.api_type == APITypes.zrc:
        zrc_client.cache_clear()
