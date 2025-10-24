from contextlib import nullcontext
from functools import cache, wraps
from typing import Callable, Iterator, NoReturn, Protocol, runtime_checkable

from django.core.exceptions import ImproperlyConfigured
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as __

import msgspec
import structlog
from ape_pie import APIClient
from msgspec.json import decode
from zgw_consumers.client import build_client
from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service

from openbeheer.config.models import APIConfig

logger = structlog.get_logger(__name__)


request_lock = nullcontext()
"""e2e tests replace this with a threading.Lock(), to avoid racing vcr.stubs
https://github.com/kevin1024/vcrpy/issues/849"""


def _build_with_logging[**P, C: APIClient](build: Callable[P, C]) -> Callable[P, C]:
    @wraps(build)
    def build_client_with_logging(*args: P.args, **kwargs: P.kwargs) -> C:
        client = build(*args, **kwargs)

        _original_request = client.request

        @wraps(_original_request)
        def logging_request(method: str | bytes, url: str | bytes, *args, **kwargs):
            logger.info(
                f"{method} request",
                base_url=client.base_url,
                url=url,
                **kwargs,
            )
            with request_lock:
                response = _original_request(method, url, *args, **kwargs)
            logger.info(
                f"{method} response",
                base_url=client.base_url,
                path=url,
                status=response.status_code,
                etag=response.headers.get("etag"),
                body=response.content,
            )
            return response

        client.request = logging_request

        return client

    return build_client_with_logging


build_client = _build_with_logging(build_client)


@cache
def ztc_client(slug: str = "") -> APIClient | NoReturn:
    """Return the APIClient for the configured ZTC service

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
def selectielijst_client() -> APIClient | NoReturn:
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

    config = APIConfig.get_solo()

    if config.selectielijst_api_service is None:
        raise ImproperlyConfigured(__("No Selectielijst service configured"))

    return build_client(config.selectielijst_api_service)


@cache
def objecttypen_client() -> APIClient | NoReturn:
    """Return the APIClient for the configured Objecttypen service"""
    api_config = APIConfig.get_solo()

    if api_config.objecttypen_api_service is None:
        raise ImproperlyConfigured(__("No Objecttypen service configured"))

    return build_client(api_config.objecttypen_api_service)


@receiver([post_delete, post_save], sender=Service, weak=False)
def _(sender, instance, **_):
    if instance.api_type == APITypes.ztc:
        ztc_client.cache_clear()

    selectielijst_client.cache_clear()
    objecttypen_client.cache_clear()

    # get_solo is broken. It won't invalidate cache when foreign keys get deleted
    api_config = APIConfig.get_solo()
    if instance in [
        api_config.selectielijst_api_service,
        api_config.objecttypen_api_service,
    ]:
        APIConfig.clear_cache()


@receiver([post_delete, post_save], sender=APIConfig, weak=False)
def _(sender, instance, **_):
    selectielijst_client.cache_clear()
    objecttypen_client.cache_clear()


@runtime_checkable
class ZGWPagedResponseProtocol[T](Protocol):
    next: str | None
    results: list[T]


def iter_pages[T](
    client: APIClient, response: ZGWPagedResponseProtocol[T], response_type=None
) -> Iterator[T]:
    yield from response.results

    # TODO: test and fix iter_pages, maybe we can drop `response_type` param again
    # response.__class__ may decode to dicts, instead of T
    response_type = (
        msgspec.defstruct(
            str(response_type),
            fields=[
                ("next", str | None),  # type: ignore  # UnionType does work
                ("results", list[response_type]),
            ],
        )
        if response_type
        else response.__class__
    )

    assert isinstance(response_type, ZGWPagedResponseProtocol)

    while next_url := response.next:
        resp = client.get(next_url)
        resp.raise_for_status()
        response = decode(resp.content, type=response_type, strict=False)
        yield from response.results
