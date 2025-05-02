from rest_framework import serializers
from rest_framework.request import Request

from .types import Paginator


class BaseZGWSerializer(serializers.Serializer):
    """
    Serializer accompanying ZGWViewSet.
    """

    fields = serializers.JSONField()  # list[TypedField]

    def __init__(self, *args, request: Request, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

    def get_uuid(self, obj):
        return obj.get("url").strip("/").split("/")[-1]


class ListZGWSerializer(BaseZGWSerializer):
    """
    Serializer accompanying ZGWViewSet for list views.
    """

    pagination = serializers.SerializerMethodField()  # Paginator
    results = serializers.SerializerMethodField()

    def get_pagination(self, obj) -> Paginator:
        """
        Returns the pagination field data, basically the entry (paginated data)
        without the results.
        """
        return {
            "count": obj.get("count"),
            "page": int(self.request.query_params.get("page", 1)),
            "page_size": 100,
        }

    def get_results(self, obj):
        return [{"uuid": self.get_uuid(result), **result} for result in obj["results"]]


class DetailZGWSerializer(BaseZGWSerializer):
    """
    Serializer accompanying ZGWViewSet for detail views.
    """

    result = serializers.SerializerMethodField()

    def get_result(self, obj):
        return {"uuid": self.get_uuid(obj), **obj}
