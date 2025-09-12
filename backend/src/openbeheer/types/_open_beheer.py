# because of the runtime defined OptionalZaakType OAS generation will fail with
# ForwardRefs so no future annotations here.
# I think it could be fixed upstream
# from __future__ import annotations

import datetime
import enum
from functools import singledispatch
from itertools import starmap
from types import NoneType, UnionType
from typing import (
    Annotated,
    Iterable,
    Mapping,
    NewType,
    Self,
    Sequence,
    Type,
    get_args,
    get_type_hints,
)

from django.core.cache import cache as django_cache

import msgspec
from ape_pie import APIClient
from furl import furl
from msgspec import UNSET, Meta, Struct, UnsetType, structs
from msgspec.json import decode

from openbeheer.clients import selectielijst_client
from openbeheer.types.objecttypen import ObjectType

from .selectielijst import ProcesType
from .ztc import (
    BesluitType,
    Eigenschap,
    InformatieObjectType,
    ResultaatType,
    RolType,
    StatusType,
    ZaakObjectType,
    ZaakType,
    ZaakTypeRequest,
)


class OBPagedQueryParams(Struct):
    "Base class for query parameters of paginated views"

    # they need a page
    page: int = 1


class OBPagination(Struct, rename="camel"):
    count: int
    page: int
    page_size: int
    next: str | None
    previous: str | None


class OBOption[T](Struct, frozen=True):
    "The label, value pair for when a `T` has to be presented in some selection"

    label: str
    value: T

    @classmethod
    def from_enum(cls, enum: enum.EnumType) -> list[Self]:
        """Note this is from an enum_type, not an enum value.
        So SomeEnum, not SomeEnum.member.
        """
        # XXX: maybe we can use the enums from vng_common? Those have nice labels
        return [
            cls(label=str(e.value), value=e.value) for e in enum._member_map_.values()
        ]


@singledispatch
def as_ob_option(arg, /, client: APIClient | None = None) -> OBOption:
    """Create OBOption of `arg`

    Example:
        Registering an implementation for `int`:

            >>> @as_ob_option.register
            ... def __(arg: int) -> OBOption[int]:
            ...     if arg == 1:
            ...         return OBOption(label="een", value=arg)
            ...     return OBOption(label=str(arg), value=arg)

        Registering an implementation for `Catalogus`:

            >>> @as_ob_option.register
            ... def __(arg: Catalogus) -> OBOption[str]:
            ...     return OBOption(label=arg.naam, value=arg.url)
    """
    # uses singledispatch because both
    # - T.as_ob_option()
    # - OBOption.from(arg:T)
    # are equally viable, but equaly hard to extend
    raise NotImplementedError(f"Can't create OBOption from {type(arg)}")


class OBFieldType(enum.StrEnum):
    "Used by frontend to decide widget etc."

    boolean = enum.auto()
    date = enum.auto()
    # daterange = enum.auto()
    # null = enum.auto()
    number = enum.auto()
    string = enum.auto()
    text = enum.auto()
    # jsx = enum.auto()


def as_ob_fieldtype(
    t: type | UnionType | Annotated, meta: Meta | None = None
) -> OBFieldType:
    "Return the `OBFieldType` for some annotation `t`"

    args = get_args(t)
    meta = meta or next((arg for arg in args if isinstance(arg, Meta)), None)

    match (t, meta):
        case type(), _ if t is bool:
            return OBFieldType.boolean
        case type(), _ if t in (int, float):
            return OBFieldType.number
        case _, Meta(max_length=int(n)) if str in args and n <= 50:
            # small strings get an input widget
            return OBFieldType.string
        case type(), _ if t is str:
            # large ones a textarea
            return OBFieldType.text
        case type(), _ if t is datetime.date:
            return OBFieldType.date
        case _ if args:
            # unpack Unions, Annotated etc.
            return as_ob_fieldtype(
                next(ut for ut in args if ut not in (NoneType, UnsetType)), meta
            )
        case _:
            # fallback to input widget
            return OBFieldType.string


def _fetch_procestype_options():
    with selectielijst_client() as client:
        response = client.get("procestypen")

    response.raise_for_status()

    procestypen = decode(response.content, type=list[LAXProcesType])
    return [
        as_ob_option(p) for p in sorted(procestypen, key=lambda v: (-v.jaar, v.naam))
    ]


def options(t: type | UnionType | Annotated) -> list[OBOption]:
    "Find an enum in the type and turn it into options."
    match t:
        case enum.EnumType():
            return OBOption.from_enum(t)
        case _ if get_args(t):
            return sum(map(options, get_args(t)), [])
        case _ if t is ProcesTypeURL:
            return django_cache.get_or_set(  # type: ignore get_or_set annotation is bad
                "processtype_options",
                default=_fetch_procestype_options,
                timeout=60 * 60 * 24,
            )
        case _:
            return []


class OBField[T](Struct, rename="camel", omit_defaults=True):
    """Used by frontend to draw list views"""

    name: str
    "the attribute of `T` this instance describes"

    type: OBFieldType

    filter_value: T | UnsetType = msgspec.UNSET
    'The currently "selected" value'

    filter_lookup: str | UnsetType = msgspec.UNSET
    """The "lookup" (query parameter) to use for this field while filtering (e.g.
    "omschrijving__icontains")."""

    options: list[OBOption] | UnsetType = msgspec.UNSET
    "fields that are not query parameter MAY need options too"

    editable: bool | UnsetType = msgspec.UNSET
    "fields may be included/excluded from editing"

    def __post_init__(self):
        # camelize value of name
        self.name = _camelize(self.name)


def _core_type(annotation):
    # drill down into Generics / Annotaitons and  find the main type
    match get_args(annotation):
        case ():
            return annotation
        case args:
            return next(
                (
                    a
                    for a in map(_core_type, args)
                    if a not in (UnsetType, NoneType, Meta)
                ),
                annotation,
            )


def ob_fields_of_type(
    data_type: type,
    query_params: OBPagedQueryParams | None = None,
    option_overrides: Mapping[str, list[OBOption]] = {},
    prefix: str = "",
) -> Iterable[OBField]:
    def to_ob_fields(name: str, annotation: type) -> list[OBField]:
        if name == "_expand":
            attrs = get_type_hints(annotation, include_extras=True)
            return [
                field
                for attr, attr_type in attrs.items()
                for field in ob_fields_of_type(
                    _core_type(attr_type),
                    prefix=f"_expand.{_camelize(attr)}.",
                )
            ]

        # closure over option_overrides
        not_applicable = object()

        ob_field = OBField(
            name=name,
            type=as_ob_fieldtype(annotation),
            options=option_overrides.get(name, options(annotation)) or UNSET,
        )
        ob_field.name = prefix + ob_field.name

        if query_params:
            for filter_name in [name, f"{name}__in"]:
                if (
                    value := getattr(query_params, filter_name, not_applicable)
                ) is not not_applicable:
                    ob_field.filter_lookup = filter_name
                    ob_field.filter_value = value

        return [ob_field]

    attrs = get_type_hints(data_type, include_extras=True)
    return sum(starmap(to_ob_fields, attrs.items()), [])


class OBList[T](Struct):
    """Used to draw list views on the frontend."""

    fields: Sequence[OBField]
    "Each field will become a column"

    pagination: OBPagination
    "Used for pagination widget"

    results: Sequence[T]
    'The "rows" in the list. All `fields` MUST be an attribute on each `T`'


class VersionSummary(Struct, rename="camel"):
    """Summary of the different version of a ZTC resource.

    # TODO: what do we need to show per version?
    """

    uuid: str
    begin_geldigheid: datetime.date
    einde_geldigheid: datetime.date | None
    concept: bool | None


class FrontendFieldSet(Struct):
    fields: list[str]
    span: int | UnsetType = msgspec.UNSET

    def __post_init__(self):
        self.fields = [_camelize(field) for field in self.fields]


type FrontendFieldsets = list[tuple[str, FrontendFieldSet]]


class DetailResponse[T](Struct):
    result: T
    fieldsets: FrontendFieldsets
    fields: list[OBField]
    versions: list[VersionSummary] | UnsetType = msgspec.UNSET


# Added otherwise API docs shows the versions as a non-required field
# while it is not present for resources without versions.
class DetailResponseWithoutVersions[T](Struct):
    result: T
    fieldsets: FrontendFieldsets
    fields: list[OBField]


class ExternalServiceError(Struct):
    code: str
    title: str
    detail: str
    status: int


class VersionedResourceSummary(Struct):
    # Actief true/false: calculated for ja/nee in the frontend
    actief: bool | UnsetType = UNSET
    einde_geldigheid: datetime.date | None = None
    concept: bool | UnsetType = UNSET

    def __post_init__(self):
        self.actief = (
            (
                self.einde_geldigheid is None
                or datetime.date.today() < self.einde_geldigheid
            )
            if not self.concept
            else False
        )


def make_fields_optional(t: Type[Struct]) -> Type[Struct]:
    "Return a Struct OptionalT with all previously required fields f: f | UnsetType = UNSET"
    return msgspec.defstruct(
        f"Optional{t.__name__}",
        [
            (field_info.name, field_info.type | UnsetType, UNSET)
            # pyright: ignore[reportArgumentType] UnionType t | UnsetType seems to work
            for field_info in structs.fields(t)
            if (
                field_info.default == structs.NODEFAULT
                and field_info.default_factory == structs.NODEFAULT
            )
        ],
        bases=(t,),
        rename="camel",
    )


class UUIDMixin:
    """
    Add a ``__post_init__`` method to set the value of the UUID from the URL.

    Coundn't use the construction:

    .. code:: python

       class ResourceWithUUID(Struct):
           uuid: str | UnsetType = UNSET

           def __post_init__(self):
               if hasattr(self, "url") and self.url:
                   self.uuid = furl(self.url).path.segments[-1]
               return self

       class BesluitTypeWithUUID(ResourceWithUUID, BesluitType):
           pass

    As this gives the error: ``TypeError: multiple bases have instance lay-out conflict``.
    """

    url: str | None
    uuid: str | UnsetType = UNSET

    def __post_init__(self):
        if hasattr(self, "url") and self.url:
            self.uuid = furl(self.url).path.segments[-1]
        return Self


class BesluitTypeWithUUID(UUIDMixin, BesluitType):
    uuid: str | UnsetType = UNSET


class StatusTypeWithUUID(UUIDMixin, StatusType):
    uuid: str | UnsetType = UNSET


class ResultaatTypeWithUUID(UUIDMixin, ResultaatType):
    uuid: str | UnsetType = UNSET


class EigenschapWithUUID(UUIDMixin, Eigenschap):
    uuid: str | UnsetType = UNSET


class InformatieObjectTypeWithUUID(UUIDMixin, InformatieObjectType):
    uuid: str | UnsetType = UNSET


class RolTypeWithUUID(UUIDMixin, RolType):
    uuid: str | UnsetType = UNSET


ProcesTypeURL = NewType("ProcesTypeURL", str)


class LAXProcesType(ProcesType):
    """
    Overrides ProcesType ignoring "toelichting" min_length as restriction seems incorrect.
    """

    toelichting: str


class ZaakTypeWithUUID(UUIDMixin, ZaakType):
    uuid: str | UnsetType = UNSET
    selectielijst_procestype: (  # pyright: ignore[reportIncompatibleVariableOverride]
        Annotated[
            ProcesTypeURL,
            Meta(
                description="URL-referentie naar een vanuit archiveringsoptiek onderkende groep processen met dezelfde kenmerken (PROCESTYPE in de Selectielijst API).",
                max_length=200,
            ),
        ]
        | None
    ) = None


class ZaakObjectTypeExtension(Struct, frozen=True, rename="camel"):
    objecttype: UnsetType | ObjectType = UNSET


class ExpandableZaakObjectTypeWithUUID(UUIDMixin, ZaakObjectType):
    uuid: str | UnsetType = UNSET
    _expand: ZaakObjectTypeExtension = ZaakObjectTypeExtension()


class ZaakTypeExtension(Struct, frozen=True, rename="camel"):
    besluittypen: UnsetType | list[BesluitTypeWithUUID] = UNSET
    # Posssibly Not invented here:
    # "gerelateerde_zaaktypen: UnsetType | null
    # "broncatalogus.url: UnsetType | null
    # "bronzaaktype.url: UnsetType | null
    statustypen: UnsetType | list[StatusTypeWithUUID] = UNSET
    resultaattypen: UnsetType | list[ResultaatTypeWithUUID] = UNSET
    eigenschappen: UnsetType | list[EigenschapWithUUID] = UNSET
    informatieobjecttypen: UnsetType | list[InformatieObjectTypeWithUUID] = UNSET
    roltypen: UnsetType | list[RolTypeWithUUID] = UNSET
    deelzaaktypen: UnsetType | list[ZaakTypeWithUUID] = UNSET
    zaakobjecttypen: UnsetType | list[ExpandableZaakObjectTypeWithUUID] = UNSET
    selectielijst_procestype: UnsetType | LAXProcesType = UNSET


class ExpandableZaakTypeRequest(ZaakTypeRequest, Struct):
    _expand: ZaakTypeExtension = ZaakTypeExtension()


class ExpandableZaakType(ZaakTypeWithUUID, Struct):
    _expand: ZaakTypeExtension = ZaakTypeExtension()


def _camelize(s: str) -> str:
    if "." in s:
        head, *tail = s.split(".")
        return f"{head}.{'.'.join(map(_camelize, tail))}"
    return "".join(part.title() if n else part for n, part in enumerate(s.split("_")))


@as_ob_option.register
def _lax_procestype_as_option(arg: ProcesType) -> OBOption[str | None]:
    return OBOption(label=f"{arg.naam} - {arg.jaar}", value=arg.url)
