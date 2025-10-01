"""REST client handling, including ReadMeStream base class."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any
from urllib.parse import ParseResult, parse_qsl

from requests.auth import HTTPBasicAuth
from singer_sdk import RESTStream
from singer_sdk.pagination import BaseHATEOASPaginator

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

if TYPE_CHECKING:
    from requests import Response
    from singer_sdk.helpers.types import Context


class ReadMePaginator(BaseHATEOASPaginator):
    """ReadMe.com paginator."""

    def get_next_url(self, response: Response) -> str | None:
        """Return the next page URL from a response. If no next page, return None."""
        return response.links.get("next", {}).get("url")  # type: ignore[no-any-return]


class ReadMeStream(RESTStream[ParseResult]):
    """ReadMe.com stream class."""

    url_base = "https://dash.readme.com/api"
    records_jsonpath = "$[*]"

    _page_size = 100

    @override
    @property
    def authenticator(self) -> HTTPBasicAuth:
        return HTTPBasicAuth(self.config["api_key"], "")

    @override
    def get_url_params(
        self,
        context: Context | None,
        next_page_token: ParseResult | None,
    ) -> dict[str, Any]:
        """Get URL query parameters.

        Args:
            context: Stream sync context.
            next_page_token: Next offset.

        Returns:
            Mapping of URL query parameters.
        """
        params: dict[str, Any] = {"perPage": self._page_size}

        if next_page_token:
            params.update(parse_qsl(next_page_token.query))

        return params

    def get_new_paginator(self) -> ReadMePaginator:
        """Get a new paginator object."""
        return ReadMePaginator()
