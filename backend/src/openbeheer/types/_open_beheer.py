from functools import singledispatch
from msgspec import Struct
import enum

from ._sundry import URL


class OBPagination(Struct, rename="camel"):
    count: int
    page: int
    page_size: int
    next: URL
    previous: URL | None


class OBOption[T](Struct, frozen=True):
    label: str
    # TODO: should be something like T | Key[T] where key could be the uuid/URL
    value: T | object


@singledispatch
def as_ob_option[T](arg: T, /) -> OBOption[T]:
    "Create OBOption of `arg`"
    # uses singledispatch because both
    # - T.as_ob_option()
    # - OBOption.from(arg:T)
    # are equally viable, but equaly hard to extend
    raise NotImplementedError(f"Can't create OBOption from {type(arg)}")


class OBFieldType(enum.StrEnum):
    boolean = enum.auto()
    date = enum.auto()
    daterange = enum.auto()
    null = enum.auto()
    number = enum.auto()
    string = enum.auto()
    # jsx = enum.auto()


class OBField[T](Struct, rename="camel"):
    name: str
    type: OBFieldType
    value: T | None = None  # TODO: is this the currently filtered value?

    # The "lookup" (query parameter) to use for this field while filtering (e.g.
    # "omschrijving__icontains").
    filter_lookup: str = ""
    options: None | list[OBOption[T]] = []

    # /** Whether the field should be active by default. */
    # active?: boolean;
    #
    # /** Whether the field should be editable. */
    # editable?: boolean;
    #
    # /** Whether the field should be filterable. */
    # ...We shouldn't set this: What would it mean to have filterable = True and fitler_lookup = ""??
    # filterable?: boolean;
    #
    # /**
    #  * The "lookup" (query parameter) to use for this field while filtering (e.g.
    #  * "omschrijving__icontains").
    #  */
    # filterLookup?: string;
    #
    # /** The value for this field's filter. */
    # filterValue?: string | number;
    #
    # /** Used by DataGrid to determine whether the field should be sortable. */
    # sortable?: boolean;
    #
    # /**
    #  * The "lookup" (dot separated) to use for this field while filtering (e.g.
    #  * "._expand.zaaktype.omschrijving").
    #  */
    # valueLookup?: string;
    #
    # /**
    #  * A function transforming `T` to a value.
    #  * This can be used to compute values dynamically.
    #  */
    # valueTransform?: (value: T) => unknown;
    #
    # /** Used by AttributeTable/DataGrid when editable=true. */
    # options?: ChoiceFieldProps["options"];
    #
    # /** Used by DataGrid to set column width. */
    # width?: string;


class OBSelection[K](Struct):
    key: str
    selection: dict[K, object]


class OBList[T](Struct):
    fields: list[OBField]
    pagination: OBPagination
    results: list[T]
    selection: OBSelection
