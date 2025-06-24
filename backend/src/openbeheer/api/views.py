from abc import ABC, abstractmethod
from enum import EnumType
from types import UnionType
from typing import Iterable, Mapping, Protocol, Sequence
from uuid import UUID

from ape_pie import APIClient
from furl import furl
from msgspec import ValidationError, convert, to_builtins
import msgspec
from msgspec.json import Encoder, decode
from rest_framework.renderers import BaseRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView as _APIView
from openbeheer.api.drf_spectacular.schema import MsgSpecFilterBackend
from openbeheer.clients import ztc_client
from openbeheer.types import (
    OBField,
    OBList,
    OBPagedQueryParams,
    OBPagination,
    ZGWResponse,
)
from openbeheer.types import OBOption, as_ob_fieldtype
from openbeheer.types._open_beheer import (
    DetailResponse,
    FrontendFieldsets,
    VersionSummary,
)
from openbeheer.types._zgw import ZGWError
from typing_extensions import get_annotations

from rest_framework.request import Request

from openbeheer.utils.decorators import handle_service_errors

_ENCODER = Encoder()

# requests query param type
type _RequestParamT = (
    str | bytes | int | float | None | Iterable[str | bytes | int | float]
)


class MsgspecJSONRenderer(JSONRenderer):
    def render(self, data, *_, **__) -> bytes:
        if data is None:
            return bytes()

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


class ListView[P: OBPagedQueryParams, T](MsgspecAPIView):
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

        def options(t: type | UnionType) -> list[OBOption]:
            "Find an enum in the type and turn it into options."
            match t:
                case EnumType():
                    return OBOption.from_enum(t)
                case UnionType():
                    return [option for ut in t.__args__ for option in options(ut)]
                case _:
                    return []

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
        with api_client:
            response = api_client.get(self.endpoint_path, params=params)

        if not response.ok:
            error = decode(response.content, type=ZGWError)
            return error, response.status_code

        content = response.content
        try:
            return decode(
                content,
                type=ZGWResponse[self.data_type],
                strict=False,
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


class DetailView[T](MsgspecAPIView, ABC):
    data_type: type[T]
    has_versions: bool
    endpoint_path: str

    def get_item_data(self, slug: str, uuid: UUID) -> tuple[T | ZGWError, int]:
        with ztc_client() as client:
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
            return decode(
                content,
                type=self.data_type,
                strict=False,
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
            else msgspec.UNSET,
            result=data,
            fieldsets=self.get_fieldsets(),
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

        data = decode(
            response.content,
            type=self.data_type,
            strict=False,
        )
        versions = []
        if self.has_versions:
            versions, status_code = self.get_item_versions(slug, data)

            if isinstance(versions, ZGWError):
                return Response(versions, status=status_code)

        response_data = DetailResponse(
            versions=[self.format_version(version) for version in versions]
            if self.has_versions
            else msgspec.UNSET,
            result=data,
            fieldsets=self.get_fieldsets(),
        )

        return Response(response_data)

    def patch(
        self, request: Request, slug: str, uuid: UUID, *args, **kwargs
    ) -> Response:
        return self.update(request, slug, uuid, is_partial=True)

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
