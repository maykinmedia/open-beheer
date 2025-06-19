import enum
from datetime import datetime
from functools import singledispatch
from types import NoneType, UnionType
from typing import Self, Sequence

import msgspec
from msgspec import Struct, UnsetType


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
def as_ob_option[T](arg: T, /) -> OBOption[T]:
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
            ... def __(arg: Catalogus) -> OBOption[int]:
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


class OBField[T](Struct, rename="camel"):
    """Used by frontend to draw list views"""

    name: str
    "the attribute of `T` this instance describes"

    type: OBFieldType

    filter_value: T | None = None
    'The currently "selected" value'

    filter_lookup: str = ""
    """The "lookup" (query parameter) to use for this field while filtering (e.g.
    "omschrijving__icontains")."""

    options: None | list[OBOption[T]] = []
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


class VersionSummary(Struct):
    """Summary of the different version of a ZTC resource.

    # TODO: what do we need to show per version?
    """

    uuid: str
    begin_geldigheid: str
    einde_geldigheid: str | None
    concept: bool | None


class FrontendFieldSet(Struct):
    fields: list[str]
    span: int | UnsetType = msgspec.UNSET


type FrontendFieldsets = list[tuple[str, FrontendFieldSet]]


class DetailResponse[T](Struct):
    result: T
    fieldsets: FrontendFieldsets
    versions: list[VersionSummary] | UnsetType = msgspec.UNSET
