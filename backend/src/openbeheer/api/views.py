from abc import ABC, abstractmethod
from collections.abc import Callable
from functools import partial, reduce
from inspect import get_annotations
from operator import or_
from typing import (
    Iterable,
    Mapping,
    NoReturn,
    Protocol,
    Sequence,
    Type,
    get_type_hints,
)
from uuid import UUID

import structlog
from ape_pie import APIClient
from furl import furl
from msgspec import (
    UNSET,
    Struct,
    UnsetType,
    ValidationError,
    convert,
    defstruct,
    structs,
    to_builtins,
)
from msgspec.json import Encoder, decode
from rest_framework.renderers import BaseRenderer, JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView as _APIView

from openbeheer.api.drf_spectacular.schema import MsgSpecFilterBackend
from openbeheer.clients import iter_pages, ztc_client
from openbeheer.types import (
    OBField,
    OBList,
    OBOption,
    OBPagedQueryParams,
    OBPagination,
    ZGWResponse,
    as_ob_fieldtype,
)
from openbeheer.types._open_beheer import (
    DetailResponse,
    FrontendFieldsets,
    VersionSummary,
    options,
)
from openbeheer.types._zgw import ZGWError
from openbeheer.utils.decorators import handle_service_errors

logger = structlog.stdlib.get_logger(__name__)

_ENCODER = Encoder()

# requests query param type
type _RequestParamT = (
    str | bytes | int | float | None | Iterable[str | bytes | int | float]
)


class MsgspecJSONRenderer(JSONRenderer):
    def render(self, data, *_, **__) -> bytes:
        match data:
            case None:
                return bytes()
            case bytes():  # response pass-through
                return data
            case _:
                try:
                    return _ENCODER.encode(data)
                except TypeError:  # raised errors contain DRF types
                    return super().render(data, *_, *__)


class _Renderer(Protocol):
    def render(self, data, *args, **kwargs): ...


class MsgspecMixin:
    def render(self: _Renderer, data, *args, **kwargs):
        """Data can be any supported type
        https://jcristharif.com/msgspec/supported-types.html
        this mixin translates it to builtins so any DRF renderer can handle them.
        """
        try:
            return super().render(to_builtins(data), *args, **kwargs)
        except TypeError:
            # data is probably some DRF class returned by exception handling
            return super().render(data, *args, **kwargs)


def _add_mixin(render_class: type[BaseRenderer]) -> type[BaseRenderer]:
    """Return a new `render_class`, with `MsgspecMixin` added

    Adapts any DRF Renderer to support the types of data msgspec supports.
    """
    return type(
        f"Msgspec{render_class.__name__}",
        (MsgspecMixin, render_class),
        {},
    )


class MsgspecAPIView(_APIView):
    def get_renderers(self) -> list[BaseRenderer]:
        render_classes = (_add_mixin(_class) for _class in self.renderer_classes)
        return [MsgspecJSONRenderer()] + [r() for r in render_classes]


def mk_expandable[T: Type[Struct]](t: T, fields: Mapping[str, type]) -> T:
    expansion = defstruct(
        name=f"{t.__name__}Expansion",
        fields=[(f, t | UnsetType, UNSET) for f, t in fields.items()],  # type: ignore UnionType t | UnsetType seems to work
        # module="" should we pass in the caller module name?
        frozen=True,  # don't want to mutate the default value
        rename="camel",
    )
    return defstruct(
        name=f"Expandable{t.__name__}",
        fields=[("_expand", expansion, expansion())],  # type: ignore UnionType t | UnsetType seems to work
        bases=(t,),
    )


type Expansion[T: Struct, R] = Callable[[APIClient, Iterable[T]], Iterable[R]]


def fetch_response[T](
    client: APIClient,
    path: str,
    params: Mapping,  # XXX: use ztc....Request objects here instead?
    result_type: type[T],
) -> ZGWResponse[T] | NoReturn:
    response = client.get(path, params=params)
    if response.status_code == 404:
        return ZGWResponse(count=1, results=[], next=None, previous=None)
    response.raise_for_status()
    return decode(response.content, type=ZGWResponse[result_type])


def fetch_all[T](
    client: APIClient, path: str, params: Mapping, result_type: type[T]
) -> list[T]:
    return list(iter_pages(client, fetch_response(client, path, params, result_type)))


def mk_expansion[T: Struct, R](
    path: str, key: Callable[[T], dict], result_type: type[R]
) -> Expansion[T, list[R]]:
    # TODO: handle returning 1 R?
    def expand(client: APIClient, objects: Iterable[T]) -> Iterable[list[R]]:
        return (fetch_all(client, path, key(obj), result_type) for obj in objects)

    return expand


def expand_many[T: Struct, R](
    client: APIClient,
    expansions: Mapping[str, Expansion[T, R]],  # {attribute_name: expansion}
    objects: Iterable[T],
) -> list[T]:
    "Return new objects with all expansions applied to their ._expand"
    objects = list(objects)
    if not expansions:
        return objects
    szip = partial(zip, strict=True)
    expansion_results = [fetch(client, objects) for fetch in expansions.values()]
    return [
        structs.replace(
            obj,
            _expand=structs.replace(
                obj._expand,  # type: ignore
                **dict(szip(expansions, expansions_for_obj)),
            ),
        )
        for obj, expansions_for_obj in szip(objects, szip(*expansion_results))
    ]


def expand_one[T: Struct, R](
    client: APIClient,
    expansions: Mapping[str, Expansion[T, R]],
    obj: T,
) -> T:
    "Return a new object T with all expansions applied to its ._expand"
    expanded = expand_many(client, expansions, [obj])
    result = expanded[0]

    if len(expanded) > 1:
        logger.error("too many expansions", extra=expanded[1:])

    return result


class ListView[P: OBPagedQueryParams, T: Struct](MsgspecAPIView):
    data_type: type[T]
    """Core ZGW datatype. e.g. Zaaktype

    This is where you can "whitelist/expose" fields.
    Fields not on the `data_type` will be ignored from respones from the Service
    and cannot be returned to the front-end.
    """

    query_type: type[P]
    "Query parameters we accept"

    filter_backends = (MsgSpecFilterBackend,)
    """
    Class attribute used by drf-spectacular to determine which extension to use to
    generate a schema for the query parameters.
    """

    endpoint_path: str
    "Path part of the ZGW API endpoint url"

    expansions: Mapping[str, Expansion[T, object]] = {}
    "Maps T._expand.'attribute_name` to fetch functions"

    @handle_service_errors
    def get(self, request: Request, slug: str = "") -> Response:
        client = ztc_client(slug=slug)
        params = self.parse_query_params(request, client)
        data, status_code = self.get_data(client, params)
        match data:
            case ZGWError():
                return Response(data, status=status_code)
            case _:
                return Response(
                    self.paginate(
                        request,
                        data,
                        params.page,
                        fields=self.parse_ob_fields(params),
                    ),
                    status=status_code,
                )

    def parse_ob_fields(
        self, params: P, option_overrides: Mapping[str, list[OBOption]] = {}
    ) -> list[OBField]:
        """Create OBFields for the attributes on `self.data_type`

        `params`: Incoming query params, so we can echo values back
        `option_overrides`: Mapping[field name, list[OBOption[field type]]]
                            Options are inferred from the type annotation of
                            `self.data_type`, but that may be set more general.
        """

        def to_ob_field(name: str, annotation: type) -> OBField:
            # closure over option_overrides
            not_applicable = object()
            ob_field = OBField(
                name=name,
                type=as_ob_fieldtype(annotation),
                options=option_overrides.get(name, options(annotation)),
            )

            for filter_name in [name, f"{name}__in"]:
                if (
                    value := getattr(params, filter_name, not_applicable)
                ) is not not_applicable:
                    ob_field.filter_lookup = filter_name
                    ob_field.filter_value = value

            return ob_field

        attrs = get_annotations(self.data_type)
        return [to_ob_field(field, annotation) for field, annotation in attrs.items()]

    def parse_query_params(self, request: Request, api_client: APIClient) -> P:
        "Parse incoming query parameters into a value of `self.query_type`"

        # TODO: Figure out how to deal with intentional lists?
        # request.query_params: ⊑ ImmutableMapping[str, list[str]]
        params_dict: dict[str, str | None] = {
            key: request.query_params.get(key) for key in request.query_params
        }

        params = convert(
            params_dict,
            self.query_type,
            strict=False,  # allow all coercions str -> ...
        )
        return params

    def get_data(
        self,
        api_client: APIClient,
        query_params: P,
        base_params: Mapping[str, _RequestParamT] = {
            "pageSize": 10,
        },
    ) -> tuple[
        ZGWResponse[T] | ZGWError,
        int,
    ]:
        """Perform request to ZGW service and return parsed response data and status_code.

        `query_params`: incoming query params
        `base_params`: "base" query params

        Parameters set in query_params will shadow base_params.
        """

        params: dict[str, _RequestParamT] = {}
        params |= base_params
        params |= to_builtins(query_params)

        expand = params.pop("expand", [])  # no ZTC endpoints have expand
        assert isinstance(expand, Iterable)
        expansions = {a: f for a, f in self.expansions.items() if a in set(expand)}

        with api_client:
            response = api_client.get(self.endpoint_path, params=params)

            if not response.ok:
                error = decode(response.content, type=ZGWError)
                return error, response.status_code

            content = response.content

            try:
                data = decode(
                    content,
                    type=ZGWResponse[self.data_type],
                    strict=False,
                )
                data.results = expand_many(api_client, expansions, data.results)

                return data, response.status_code
            except ValidationError as e:
                return ZGWError(
                    code="Bad response",
                    title="Server returned out of spec response",
                    detail=str(e),
                    instance="",
                    status=500,
                    invalid_params=[],
                ), 500

    @staticmethod
    def paginate(
        request: Request,
        data: ZGWResponse[T],
        page: int,
        fields: Sequence[OBField] = [],
        page_size: int = 10,
    ) -> OBList[T]:
        """Paginate ZGW response data.

        We don't use DRF Pagination classes, because we "just" relay paginated
        ZGW Service responses. This function, takes care of the required URI translations.
        """

        # transform the Service URL to our own
        self_url = furl(request.build_absolute_uri())
        next_url = self_url.copy()
        next_url.args.set("page", page + 1)
        prev_url = self_url.copy()
        prev_url.args.set("page", page - 1)

        return OBList(
            fields=fields,
            pagination=OBPagination(
                count=data.count,
                page=page,
                next=data.next and str(next_url),
                previous=data.previous and str(prev_url),
                page_size=page_size,
            ),
            results=data.results,
        )


class DetailView[T: Struct](MsgspecAPIView, ABC):
    data_type: type[T]
    has_versions: bool
    endpoint_path: str
    expansions: Mapping[str, Expansion[T, object]] = {}

    def get_item_data(self, slug: str, uuid: UUID) -> tuple[T | ZGWError, int]:
        with ztc_client(slug) as client:
            response = client.get(
                self.endpoint_path.format(uuid=uuid),
            )

            if not response.ok:
                # error = decode(response.content, type=ValidatieFout) # TODO: the OZ 404 response gives invalid JSON back
                return ZGWError(
                    code="",
                    title="",
                    detail="",
                    instance="",
                    status=response.status_code,
                    invalid_params=[],
                ), response.status_code

            content = response.content
            try:
                return self._expand(
                    client,
                    decode(
                        content,
                        type=self.data_type,
                        strict=False,
                    ),
                ), response.status_code
            except ValidationError as e:
                return ZGWError(
                    code="Bad response",
                    title="Server returned out of spec response",
                    detail=str(e),
                    instance="",
                    status=500,
                    invalid_params=[],
                ), 500

    def _expand(self, client, object: T):
        return expand_one(client, self.expansions, object)

    def get_fields(self) -> list[OBField]:
        # merge annotations for all base classes too
        attrs = reduce(or_, map(get_annotations, reversed(self.data_type.mro())))
        field_types = reduce(or_, map(get_type_hints, reversed(self.data_type.mro())))
        field_options = lambda field: options(field_types[field])

        return [
            OBField(
                name=field,
                type=as_ob_fieldtype(annotation),
                options=field_options(field) or UNSET,
                filter_lookup=UNSET,
            )
            for field, annotation in attrs.items()
            if field != "_expand"
        ]

    @handle_service_errors
    def get(self, request: Request, slug: str, uuid: UUID, *args, **kwargs) -> Response:
        data, status_code = self.get_item_data(slug, uuid)

        if isinstance(data, ZGWError):
            return Response(data, status=status_code)

        versions = []
        if self.has_versions:
            versions, status_code = self.get_item_versions(slug, data)

            if isinstance(versions, ZGWError):
                return Response(versions, status=status_code)

        response_data = DetailResponse(
            versions=[self.format_version(version) for version in versions]
            if self.has_versions
            else UNSET,
            result=data,
            fieldsets=self.get_fieldsets(),
            fields=self.get_fields(),
        )

        return Response(response_data)

    def update(
        self, request: Request, slug: str, uuid: UUID, is_partial: bool = True
    ) -> Response:
        with ztc_client(slug) as client:
            handler = client.patch if is_partial else client.put
            response = handler(self.endpoint_path.format(uuid=uuid), json=request.data)

            if not response.ok:
                error = decode(response.content, type=ZGWError)
                return Response(
                    error,
                    status=response.status_code,
                )

            data = self._expand(
                client,
                decode(
                    response.content,
                    type=self.data_type,
                    strict=False,
                ),
            )

        versions = []
        if self.has_versions:
            versions, status_code = self.get_item_versions(slug, data)

            if isinstance(versions, ZGWError):
                return Response(versions, status=status_code)

        response_data = DetailResponse(
            versions=[self.format_version(version) for version in versions]
            if self.has_versions
            else UNSET,
            result=data,
            fieldsets=self.get_fieldsets(),
            fields=self.get_fields(),
        )

        return Response(response_data)

    @handle_service_errors
    def patch(
        self, request: Request, slug: str, uuid: UUID, *args, **kwargs
    ) -> Response:
        return self.update(request, slug, uuid, is_partial=True)

    @handle_service_errors
    def put(self, request: Request, slug: str, uuid: UUID, *args, **kwargs) -> Response:
        return self.update(request, slug, uuid, is_partial=False)

    @abstractmethod
    def get_item_versions(
        self, slug: str, data: T
    ) -> tuple[list[T] | ZGWError, int]: ...

    @abstractmethod
    def format_version(self, data: T) -> VersionSummary: ...

    @abstractmethod
    def get_fieldsets(self) -> FrontendFieldsets: ...
