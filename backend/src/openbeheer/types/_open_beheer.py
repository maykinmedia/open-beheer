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
    Callable,
    Iterable,
    Mapping,
    NewType,
    Self,
    Sequence,
    Type,
    TypeAlias,
    get_args,
    get_type_hints,
)
from uuid import UUID

from django.conf import settings
from django.core.cache import cache as django_cache

import msgspec
from ape_pie import APIClient
from furl import furl
from msgspec import UNSET, Meta, Struct, UnsetType, field, structs
from msgspec.json import decode

from openbeheer.clients import iter_pages, objecttypen_client, selectielijst_client
from openbeheer.types.objecttypen import ObjectType
from openbeheer.utils import camelize

from . import objecttypen, selectielijst
from .selectielijst import (
    ProcesType,
    ResultaatTypeOmschrijvingGeneriek as _ResultaatTypeOmschrijvingGeneriek,
)
from .ztc import (
    AfleidingswijzeEnum,
    BesluitType,
    Eigenschap,
    FormaatEnum,
    InformatieObjectType,
    ResultaatType,
    RolType,
    StatusType,
    ZaakObjectType,
    ZaakType,
    ZaakTypeInformatieObjectType,
    ZaakTypeRequest,
)

CamelCaseFieldName: TypeAlias = str
"e.g.: _expand.roltype.omschrijvingGeneriek"


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
    duration = enum.auto()
    """ISO 8601 duration:
    PnYnMnDTnHnMnS
    PnW
    P<date>T<time>
    """
    # null = enum.auto()
    number = enum.auto()
    string = enum.auto()
    text = enum.auto()
    # jsx = enum.auto()


def as_ob_fieldtype(
    t: type | UnionType | Annotated, field_name: str, meta: Meta | None = None
) -> OBFieldType:
    """Return the `OBFieldType` for some annotation `t`

    :param field_name: snake case field name without _expand... prefix
    """

    args = get_args(t)
    meta = meta or next((arg for arg in args if isinstance(arg, Meta)), None)

    if field_name in [
        "archiefactietermijn",
        "doorlooptijd",
        "servicenorm",
        "procestermijn",
        "publicatietermijn",
        "reactietermijn",
        "verlengingstermijn",
    ]:
        return OBFieldType.duration

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
                next(ut for ut in args if ut not in (NoneType, UnsetType)),
                field_name,
                meta,
            )
        case _:
            # fallback to input widget
            return OBFieldType.string


def _cached[F: Callable[[], object]](f: F) -> F:
    """Caching decorator, used for caching results in the default django cache for a day

    Like functools cache/lru_cache adds a `clear_cache` method on the function
    """
    key = f.__qualname__
    function: F = lambda: django_cache.get_or_set(
        # type: ignore get_or_set annotation is bad
        key,
        default=f,
        timeout=60 * 60 * 24,
    )
    function.clear_cache = lambda: django_cache.delete(key)  # pyright: ignore[reportFunctionMemberAccess]

    return function


@_cached
def fetch_procestype_options():
    with selectielijst_client() as client:
        response = client.get("procestypen")

    response.raise_for_status()

    procestypen = decode(response.content, type=list[LAXProcesType])
    return [
        as_ob_option(p) for p in sorted(procestypen, key=lambda v: (-v.jaar, v.nummer))
    ]


@_cached
def fetch_objecttype_options():
    from openbeheer.api.views import fetch_all

    with objecttypen_client() as client:
        objecttypen = fetch_all(client, "objecttypes", {}, ObjectType)

    return [
        as_ob_option(objecttype)
        for objecttype in sorted(objecttypen, key=lambda item: (item.name))
    ]


def options(t: type | UnionType | Annotated) -> list[OBOption] | UnsetType:
    "Find an enum in the type and turn it into options."

    match t:  # 😭 Why does Annotated rsult in an Any judgement
        case enum.EnumType():
            return OBOption.from_enum(t)
        case _ if get_args(t):
            return options(_core_type(t))
        case _ if t is ProcesTypeURL:
            return fetch_procestype_options()
        case _ if t is ResultaatTypeOmschrijvingURL:
            return fetch_resultaattypeomschrijving_options()
        case _ if t is ResultaatURL:
            return fetch_selectielijst_resultaat_options()
        case _ if t is ObjectTypeURL:
            return fetch_objecttype_options()
        case _:
            return UNSET


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

    editable: bool = False
    "fields may be included/excluded from editing"

    required: bool | UnsetType = msgspec.UNSET
    """May this field be null or undefined?
    NB: this is not the same as OAS/jsonschema required!"""
    # Should we take into account whether we know a default value?

    def __post_init__(self):
        # camelize value of name
        self.name = camelize(self.name)


def _core_type(annotation) -> type:
    """Drill down into Generics / Annotations and return the main type"""
    # `annotation` has no annotation, because pyright can't follow `get_args` correctly

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


def _ob_required(annotation) -> bool | UnsetType:
    """Infer OBField.required from annotation"""
    types = set(get_args(annotation))
    empty_types = {NoneType, msgspec.UnsetType}
    return not (types & empty_types)


def ob_fields_of_type(
    data_type: type,
    query_params: OBPagedQueryParams | None = None,
    option_overrides: Mapping[CamelCaseFieldName, list[OBOption]] = {},
    *,
    prefix: str = "",
    base_editable: Callable[[CamelCaseFieldName], bool] = bool,
) -> Iterable[OBField]:
    """
    Return the :class:`OBField` instances for the given `data_type`.

    :param data_type: The type whose annotated attributes should be converted
        into :class:`OBField` definitions.
    :param query_params: Optional query parameters used to determine
        `filter_lookup` and `filter_value`.
    :param option_overrides: Normally options are inferred from type annotations
        of `data_type`, but they may be overridden here.
    :param prefix: String prefix to prepend to the field `name` when recursing
        into nested structures (e.g. "_expand").
    :param base_editable: Predicate that takes a field name and returns whether
        that field should be editable. This acts as a baseline condition and is
        logically ANDed with the editability inferred from type annotations and
        other rules.
    """

    def to_ob_fields(name: str, annotation: type) -> list[OBField]:
        if name == "_expand":
            attrs = get_type_hints(annotation, include_extras=True)
            return [
                field
                for attr, attr_type in attrs.items()
                for field in ob_fields_of_type(
                    _core_type(attr_type),
                    option_overrides=option_overrides,
                    prefix=f"_expand.{camelize(attr)}.",
                    base_editable=base_editable,
                )
            ]

        # closure over option_overrides
        not_applicable = object()

        prefixed_name: CamelCaseFieldName = camelize(prefix + name)

        ob_field = OBField(
            name=prefixed_name,
            type=as_ob_fieldtype(annotation, name),
            options=option_overrides.get(prefixed_name, options(annotation)),
            # only editable if neither the whole type nor the attribute type is READ_ONLY
            editable=base_editable(prefixed_name)
            and not (set(map(_core_type, (data_type, annotation))) & READ_ONLY_TYPES),
            required=_ob_required(annotation),
        )

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
        self.fields = [camelize(field) for field in self.fields]


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

    uuid: UUID | UnsetType = UNSET
    admin_url: str | UnsetType = field(name="adminUrl", default=UNSET)

    def __post_init__(self):
        if url := getattr(self, "url", None):
            self.uuid = UUID(furl(url).path.segments[-1])


def _admin_url(
    slug: str, uuid: UUID | UnsetType, url: str | None | UnsetType
) -> str | UnsetType:
    if not (url and uuid and uuid is not UNSET and url is not UNSET):
        return UNSET

    base_url: furl
    if settings.OPEN_ZAAK_ADMIN_BASE_URL:
        base_url = furl(settings.OPEN_ZAAK_ADMIN_BASE_URL)
    else:
        base_url = furl(url).set(path="/admin", query_params=None)

    return str(
        base_url.add(
            path=f"/catalogi/{slug}/",
            query_params={"uuid__exact": uuid},
        )
    )


class BesluitTypeWithUUID(UUIDMixin, BesluitType):
    uuid: UUID | UnsetType = UNSET
    admin_url: str | UnsetType = field(name="adminUrl", default=UNSET)

    def __post_init__(self):
        super().__post_init__()
        self.admin_url = _admin_url("besluittype", self.uuid, self.url)


class StatusTypeWithUUID(UUIDMixin, StatusType):
    uuid: UUID | UnsetType = UNSET
    admin_url: str | UnsetType = field(name="adminUrl", default=UNSET)

    def __post_init__(self):
        super().__post_init__()
        self.admin_url = _admin_url("statustype", self.uuid, self.url)


ResultaatTypeOmschrijvingURL = NewType("ResultaatTypeOmschrijvingURL", str)


class ResultaatTypeOmschrijvingGeneriek(_ResultaatTypeOmschrijvingGeneriek):
    url: (  # pyright: ignore[reportIncompatibleVariableOverride]
        Annotated[
            ResultaatTypeOmschrijvingURL,
            Meta(
                description="URL-referentie naar dit object. Dit is de unieke identificatie en locatie van dit object.",
                max_length=1000,
                min_length=1,
                title="Url",
            ),
        ]
        | None
    ) = None


@as_ob_option.register
def _resultaattypeomschrijving_as_option(
    omschrijving: ResultaatTypeOmschrijvingGeneriek, **kwargs
) -> OBOption[ResultaatTypeOmschrijvingURL]:
    assert omschrijving.url
    return OBOption(label=omschrijving.omschrijving, value=omschrijving.url)


@_cached
def fetch_resultaattypeomschrijving_options():
    with selectielijst_client() as client:
        response = client.get("resultaattypeomschrijvingen")

    response.raise_for_status()

    omschrijvingen = decode(
        response.content, type=list[ResultaatTypeOmschrijvingGeneriek]
    )
    return [
        as_ob_option(p)
        for p in sorted(omschrijvingen, key=lambda o: o.omschrijving)
        if p.url
    ]


ResultaatURL = NewType("ResultaatURL", str)


class LAXWaardering(enum.Enum):
    blijvend_bewaren = "blijvend_bewaren"
    vernietigen = "vernietigen"
    field_ = ""


ProcesTypeURL = NewType("ProcesTypeURL", str)
ObjectTypeURL = NewType("ObjectTypeURL", str)


@as_ob_option.register
def _objecttype_as_option(objecttype: ObjectType, **kwargs) -> OBOption[str]:
    assert objecttype.url
    return OBOption(label=objecttype.name, value=objecttype.url)


class LAXResultaat(Struct, rename="camel"):
    "A version of selectielijst.Resultaat with just the fields we need for the option labels"

    url: ResultaatURL
    nummer: Annotated[
        int,
        Meta(
            description="Nummer van het resultaat. Dit wordt samengesteld met het procestype en generiek resultaat indien van toepassing.",
            ge=0,
            le=32767,
            title="Nummer",
        ),
    ]
    naam: Annotated[
        str,
        Meta(
            description="Benaming van het procestype",
            max_length=40,
            min_length=1,
            title="Naam",
        ),
    ]
    waardering: Annotated[LAXWaardering, Meta(title="Waardering")]
    proces_type: ProcesTypeURL | None = None
    volledig_nummer: str | None = None
    # ISO8601 PY is ambiguous in days, so not convertible to timedelta
    bewaartermijn: Annotated[str, Meta(title="Bewaartermijn")] | None = None
    omschrijving: str | None = None


@as_ob_option.register
def _resultaat_as_option(resultaat: LAXResultaat, **kwargs) -> OBOption[ResultaatURL]:
    label_values = filter(
        None,
        (
            resultaat.volledig_nummer,
            resultaat.naam,
            resultaat.waardering.value,
            resultaat.bewaartermijn,
            resultaat.omschrijving,
        ),
    )
    label = " - ".join(label_values)
    return OBOption(
        label=f"{label}",
        value=resultaat.url,
    )


def fetch_selectielijst_resultaat_options(
    procestype_url: str | None = None,
) -> list[OBOption[LAXResultaat]]:
    resultaten = fetch_resultaten()
    return [
        as_ob_option(p)
        for p in sorted(
            resultaten,
            key=lambda r: (r.proces_type, r.volledig_nummer, r.nummer, r.naam),
        )
        if not procestype_url or p.proces_type == procestype_url
    ]


@_cached
def fetch_resultaten() -> list[LAXResultaat]:
    class PagedResultaat(Struct):
        next: str | None
        results: list[LAXResultaat]

    with selectielijst_client() as client:
        response = client.get("resultaten")
        response.raise_for_status()

        return list(iter_pages(client, decode(response.content, type=PagedResultaat)))


class ResultaatTypeWithUUID(UUIDMixin, ResultaatType):
    uuid: UUID | UnsetType = UNSET
    resultaattypeomschrijving: Annotated[  # pyright: ignore[reportIncompatibleVariableOverride]
        ResultaatTypeOmschrijvingURL,
        Meta(
            description="Algemeen gehanteerde omschrijving van de aard van resultaten van het RESULTAATTYPE. Dit moet een URL-referentie zijn naar de referenlijst van generieke resultaattypeomschrijvingen. Im ImZTC heet dit 'omschrijving generiek'",
            max_length=1000,
        ),
    ]
    selectielijstklasse: Annotated[  # pyright: ignore[reportIncompatibleVariableOverride]
        ResultaatURL,
        Meta(
            description="URL-referentie naar de, voor het archiefregime bij het RESULTAATTYPE relevante, categorie in de Selectielijst Archiefbescheiden (RESULTAAT in de Selectielijst API) van de voor het ZAAKTYPE verantwoordelijke overheidsorganisatie.",
            max_length=1000,
        ),
    ]
    # afleidingswijze is actually a property from brondatum_archiefprocedure
    # set here because front end doesn't support nested structures. yet? 🤞
    afleidingswijze: (
        Annotated[
            AfleidingswijzeEnum,
            Meta(
                description="Read-only afleidingswijze, set from bronArchiefProcedure",
            ),
        ]
        | UnsetType
    ) = UNSET
    admin_url: str | UnsetType = field(name="adminUrl", default=UNSET)

    def __post_init__(self):
        super().__post_init__()
        if self.brondatum_archiefprocedure:
            self.afleidingswijze = self.brondatum_archiefprocedure.afleidingswijze
        self.admin_url = _admin_url("resultaattype", self.uuid, self.url)


class EigenschapWithUUID(UUIDMixin, Eigenschap):
    uuid: UUID | UnsetType = UNSET
    # format is actually a property from specificatie
    # set here because front end doesn't support nested structures.
    formaat: FormaatEnum | UnsetType = UNSET
    admin_url: str | UnsetType = field(name="adminUrl", default=UNSET)

    def __post_init__(self):
        super().__post_init__()
        self.formaat = self.specificatie.formaat
        self.admin_url = _admin_url("eigenschap", self.uuid, self.url)


class InformatieObjectTypeWithUUID(UUIDMixin, InformatieObjectType):
    uuid: UUID | UnsetType = UNSET
    admin_url: str | UnsetType = field(name="adminUrl", default=UNSET)

    def __post_init__(self):
        super().__post_init__()
        self.admin_url = _admin_url("informatieobjecttype", self.uuid, self.url)


class RolTypeWithUUID(UUIDMixin, RolType):
    uuid: UUID | UnsetType = UNSET
    admin_url: str | UnsetType = field(name="adminUrl", default=UNSET)

    def __post_init__(self):
        super().__post_init__()
        self.admin_url = _admin_url("roltype", self.uuid, self.url)


class LAXProcesType(ProcesType):
    """
    Overrides ProcesType ignoring "toelichting" min_length as restriction seems incorrect.
    """

    toelichting: str
    url: (  # pyright: ignore[reportIncompatibleVariableOverride]
        Annotated[
            ProcesTypeURL,
            Meta(
                description="URL-referentie naar dit object. Dit is de unieke identificatie en locatie van dit object.",
                max_length=1000,
                min_length=1,
                title="Url",
            ),
        ]
        | None
    ) = None


class ZaakTypeWithUUID(UUIDMixin, ZaakType):
    uuid: UUID | UnsetType = UNSET
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
    admin_url: str | UnsetType = field(name="adminUrl", default=UNSET)

    def __post_init__(self):
        super().__post_init__()
        self.admin_url = _admin_url("zaaktype", self.uuid, self.url)


class ZaakTypeInformatieObjectTypeWithUUID(UUIDMixin, ZaakTypeInformatieObjectType):
    uuid: UUID | UnsetType = UNSET
    admin_url: str | UnsetType = field(name="adminUrl", default=UNSET)

    def __post_init__(self):
        super().__post_init__()
        self.admin_url = _admin_url("zaaktypeinformatieobjecttype", self.uuid, self.url)


class ZaakObjectTypeExtension(Struct, frozen=True, rename="camel"):
    objecttype: UnsetType | ObjectType = UNSET


class ZaakObjectTypeWithUUID(UUIDMixin, ZaakObjectType):
    uuid: UUID | UnsetType = UNSET
    admin_url: str | UnsetType = field(name="adminUrl", default=UNSET)

    def __post_init__(self):
        super().__post_init__()
        self.admin_url = _admin_url("zaakobjecttype", self.uuid, self.url)


class ExpandableZaakObjectTypeWithUUID(UUIDMixin, ZaakObjectType):
    uuid: UUID | UnsetType = UNSET
    objecttype: (  # pyright: ignore[reportIncompatibleVariableOverride]
        Annotated[
            ObjectTypeURL,
            Meta(
                description="URL-referentie naar de OBJECTTYPE waartoe dit ZAAKOBJECTTYPE behoort.",
                max_length=200,
            ),
        ]
    )
    _expand: ZaakObjectTypeExtension = ZaakObjectTypeExtension()
    admin_url: str | UnsetType = field(name="adminUrl", default=UNSET)

    def __post_init__(self):
        super().__post_init__()
        self.admin_url = _admin_url("zaakobjecttype", self.uuid, self.url)


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
    # deelzaaktypen: UnsetType | list[ZaakTypeWithUUID] = UNSET
    zaakobjecttypen: UnsetType | list[ExpandableZaakObjectTypeWithUUID] = UNSET
    selectielijst_procestype: UnsetType | LAXProcesType = UNSET
    zaaktypeinformatieobjecttypen: (
        UnsetType | list[ZaakTypeInformatieObjectTypeWithUUID]
    ) = UNSET


class ExpandableZaakTypeRequest(ZaakTypeRequest, Struct):
    _expand: ZaakTypeExtension = ZaakTypeExtension()


class ExpandableZaakType(ZaakTypeWithUUID, Struct):
    _expand: ZaakTypeExtension = ZaakTypeExtension()

    # FIXME: without this, the frontend doesn't pick up the expand field.
    zaaktypeinformatieobjecttypen: Sequence[ZaakTypeInformatieObjectTypeWithUUID] = []


@as_ob_option.register
def _lax_procestype_as_option(arg: ProcesType) -> OBOption[str | None]:
    return OBOption(label=f"{arg.jaar} - {arg.nummer} - {arg.naam}", value=arg.url)


# Types from read only (or not implemented CUD) API's
READ_ONLY_TYPES = {
    t
    for module in [selectielijst, objecttypen]
    for name in dir(module)
    if (t := getattr(module, name))
    if isinstance(t, type) and issubclass(t, Struct)
} | {LAXProcesType, UUID}
