# because of the runtime defined OptionalZaakType OAS generation will fail with
# ForwardRefs so no future annotations here.
# I think it could be fixed upstream
# from __future__ import annotations

import datetime
import enum
from functools import singledispatch
from types import NoneType, UnionType
from typing import Self, Sequence, Type

import msgspec
from ape_pie import APIClient
from furl import furl
from msgspec import UNSET, Struct, UnsetType, structs

from .ztc import (
    BesluitType,
    Eigenschap,
    InformatieObjectType,
    ResultaatType,
    RolType,
    StatusType,
    ZaakObjectType,
    ZaakType,
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
    # jsx = enum.auto()


def as_ob_fieldtype(t: type | UnionType) -> OBFieldType:
    "Return the `OBFieldType` for some annotation `t`"
    if isinstance(t, UnionType):
        return as_ob_fieldtype(
            next(ut for ut in t.__args__ if ut not in (NoneType, UnsetType))
        )
    if t is bool:
        return OBFieldType.boolean
    if t in (int, float):
        return OBFieldType.number
    if t is str:
        return OBFieldType.string
    if t is datetime.date:
        return OBFieldType.date
    return OBFieldType.string


def options(t: type | UnionType) -> list[OBOption]:
    "Find an enum in the type and turn it into options."
    match t:
        case enum.EnumType():
            return OBOption.from_enum(t)
        case UnionType():
            return [option for ut in t.__args__ for option in options(ut)]
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

    def __post_init__(self):
        # camelize value of name
        self.name = "".join(
            part.title() if n else part for n, part in enumerate(self.name.split("_"))
        )


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
        # camelize value of field names
        self.fields = [
            "".join(
                part.title() if n else part for n, part in enumerate(field.split("_"))
            )
            for field in self.fields
        ]


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
            (field_info.name, field_info.type | UnsetType, UNSET)  # pyright: ignore[reportArgumentType] UnionType t | UnsetType seems to work
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


class ZaakTypeWithUUID(UUIDMixin, ZaakType):
    uuid: str | UnsetType = UNSET


class ZaakObjectTypeWithUUID(UUIDMixin, ZaakObjectType):
    uuid: str | UnsetType = UNSET
