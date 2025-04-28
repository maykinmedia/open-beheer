from rest_framework import serializers
from rest_framework.request import Request

from .types import Paginator


class ZGWSerializer(serializers.Serializer):
    """
    Serializer accompanying ZGWViewSet.
    """

    fields = serializers.JSONField()  # list[TypedField]
    pagination = serializers.SerializerMethodField()  # Paginator
    results = serializers.JSONField()

    def __init__(self, *args, request: Request, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

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