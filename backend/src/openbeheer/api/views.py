from enum import EnumType
from types import UnionType
from typing import Iterable, Mapping, Protocol, Sequence

from furl import furl
from msgspec import ValidationError, convert, to_builtins
from msgspec.json import Encoder, decode
from msgspec.structs import asdict
from rest_framework.renderers import BaseRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView as _APIView
from openbeheer.clients import ztc_client
from openbeheer.types import (
    OBField,
    OBList,
    OBPagedQueryParams,
    OBPagination,
    ZGWResponse,
)
from openbeheer.types import OBOption, as_ob_fieldtype
from openbeheer.types.ztc import ValidatieFout
from typing_extensions import get_annotations

from rest_framework.request import Request

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
        return super().render(to_builtins(data), *args, **kwargs)


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

    endpoint_path: str
    "Path part of the ZGW API endpoint url"

    def get(self, request: Request) -> Response:
        params = self.parse_query_params(request)
        data, status_code = self.get_data(params)
        match data:
            case ValidatieFout():
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

    def parse_query_params(self, request: Request) -> P:
        "Parse incoming query parameters into a value of `self.query_type`"
        params = convert(request.query_params, self.query_type)
        return params

    def get_data(
        self,
        query_params: P,
        base_params: Mapping[str, _RequestParamT] = {
            "pageSize": 10,
        },
    ) -> tuple[
        ZGWResponse[T] | ValidatieFout,
        int,
    ]:
        """Perform request to ZGW service and return parsed response data and status_code.

        `query_params`: incoming query params
        `base_params`: "base" query params

        Parameters set in query_params will shadow base_params.
        """

        params: dict[str, _RequestParamT] = {}
        params |= base_params
        params |= asdict(query_params)
        with ztc_client() as client:
            response = client.get(
                self.endpoint_path,
                params=params,
            )

        if not response.ok:
            error = decode(response.content, type=ValidatieFout)
            return error, response.status_code

        content = response.content
        try:
            return decode(
                content,
                type=ZGWResponse[self.data_type],
                strict=False,
            ), response.status_code
        except ValidationError as e:
            return ValidatieFout(
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
