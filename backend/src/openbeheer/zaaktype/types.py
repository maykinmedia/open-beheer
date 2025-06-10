from typing import Mapping
from msgspec import Struct



class ZaaktypeVersionSummary(Struct):
    """Summary of the different version of a Zaaktype.

    In Open Zaak different versions of a same zaaktype have the
    same `identificatie` but different begin/einde geldigheid.
    """

    uuid: str
    begin_geldigheid: str
    einde_geldigheid: str | None
    concept: bool | None


# TODO: think how we should structure types, also thinking about OBField
class OBDetailField(Struct):
    label: str
    value: str
    description: str = ""
    """Information about an Open Zaak field.

    This doesn't come from Open Zaak, so we would have to
    have a mapping in Open Beheer for the descriptions."""
    required: bool = False


"""
The filter on `datum_geldigheid` checks that the given value is greater than
`begin_geldigheid` and if `einde_geldigheid` is not null, dat it is lower
than it.
"""


class ZaaktypeDetailResponse(Struct):
    versions: list[ZaaktypeVersionSummary]  # TODO: what do we need to show per version?
    item_data: Mapping[str, OBDetailField]
