from functools import cache

from openbeheer.api.views import fetch_all
from openbeheer.clients import objecttypen_client
from openbeheer.types.objecttypen import ObjectType


@cache
def retrieve_objecttypen() -> dict[str, ObjectType]:
    with objecttypen_client() as ot_client:
        objecttypen = fetch_all(ot_client, "objecttypes", {}, ObjectType)
        return {
            item.url: item for item in objecttypen if item.url
        }  # They should always have a URL
