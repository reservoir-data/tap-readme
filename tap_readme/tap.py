"""ReadMe.com tap class."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from singer_sdk import Stream, Tap
from singer_sdk import typing as th

from tap_readme import streams

if TYPE_CHECKING:
    from urllib.parse import ParseResult

    from singer_sdk.streams import RESTStream

STREAM_TYPES: list[type[RESTStream[ParseResult]]] = [
    streams.Categories,
    streams.CategoryDocs,
    streams.Metadata,
    streams.Changelogs,
]


class TapReadMe(Tap):
    """Singer tap for ReadMe.com."""

    name = "tap-readme"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "api_key",
            th.StringType,
            required=True,
            secret=True,
            description="API Key for ReadMe.com",
        ),
    ).to_dict()

    @override
    def discover_streams(self) -> list[Stream]:
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]
