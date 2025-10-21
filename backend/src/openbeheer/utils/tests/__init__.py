from typing import Callable, Iterable

from django.test import TestCase as _TestCase, tag

from maykin_common.vcr import VCRMixin as _VCRMixin
from rest_framework.test import APITestCase as _APITestCase
from vcr.cassette import Cassette
from vcr.request import Request


def matcher_query_without_datum_geldigheid(
    incoming_request: Request, stored_request: Request
) -> None:
    """Match requests ignoring query param involving dates changing every day"""

    incoming_query_names = {query_name for query_name, _ in incoming_request.query}
    stored_query_names = {query_name for query_name, _ in stored_request.query}
    assert incoming_query_names == stored_query_names, (
        "The names of the query params in the incoming request don't match those in the stored request."
    )

    if (
        incoming_request.path == "/catalogi/api/v1/informatieobjecttypen"
        and "datumGeldigheid" in stored_query_names
    ):
        assert {
            query_name: query_value
            for query_name, query_value in incoming_request.query
            if query_name != "datumGeldigheid"
        } == {
            query_name: query_value
            for query_name, query_value in stored_request.query
            if query_name != "datumGeldigheid"
        }, (
            "The values of the query params in the incoming request don't match those "
            "in the stored request (excluding datumGeldigheid)."
        )
    else:
        assert dict(incoming_request.query) == dict(stored_request.query), (
            "The values of the query params in the incoming "
            "request don't match those in the stored request."
        )

    return


@tag("vcr")
class VCRMixin(_VCRMixin):
    custom_matchers: Iterable[tuple[str, Callable[[Request, Request], None]]] | None = (
        None
    )
    """Custom request matchers. These will be registered in addition to the default VCR matchers."""

    custom_match_on: Iterable[str] | None = None
    """List of names of the matchers to use. These will override the default matchers.By default VCR uses ("method", "scheme", "host", "port", "path", "query")."""

    def _get_vcr_kwargs(self, **kwargs) -> dict[str, object]:
        """In order to keep diffs small and easily scanable, this filters some headers
        that aren't particularly interesting for our behaviours.

        Applied before the maykin_common once and whatever kwargs you pass in.
        """

        def delete_response_headers(response):
            for header in [
                "Content-Security-Policy",  # we're not a browser
                "Date",  # use git log if you need this
                "Server",  # don't care about server, just what's served
            ]:
                response["headers"].pop(header, None)
            return response

        custom_kwargs = {
            "filter_headers": [
                "Authorization",  # don't store tokens
                "User-Agent",  # Don't store requests version
            ],
            "before_record_response": delete_response_headers,
        }
        if self.custom_match_on:
            custom_kwargs["match_on"] = self.custom_match_on

        return custom_kwargs | super()._get_vcr_kwargs(**kwargs)

    def _get_vcr(self, **kwargs):
        myvcr = super()._get_vcr(**kwargs)

        if self.custom_matchers:
            for matcher_name, matcher in self.custom_matchers:
                myvcr.register_matcher(matcher_name, matcher)

        return myvcr


class VCRAPITestCase(VCRMixin, _APITestCase):
    """A DRF ``APITestCase`` with the ``VCRMixin`` and a ``vcr`` tag.

    Use this for testing DRF views that talk to the HTTP backends.
    """

    cassette: Cassette | None = None


class VCRTestCase(VCRMixin, _TestCase):
    """A DRF ``APITestCase`` with the ``VCRMixin`` and a ``vcr`` tag.

    Use this for testing DRF views that talk to the HTTP backends.
    """

    cassette: Cassette | None = None
