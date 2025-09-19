from functools import cache

from openbeheer.api.views import fetch_all
from openbeheer.clients import objecttypen_client
from openbeheer.types.objecttypen import ObjectType


@cache
def retrieve_objecttypen(zaaktype_url: str = "") -> dict[str, ObjectType]:
    params = {}
    if zaaktype_url:
        params.update({"zaaktype": zaaktype_url})

    with objecttypen_client() as ot_client:
        objecttypen = fetch_all(ot_client, "objecttypes", params, ObjectType)
        return {
            item.url: item for item in objecttypen if item.url
        }  # They should always have a URL
