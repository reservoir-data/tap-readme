"""ReadMe.com tap class."""

from __future__ import annotations

from typing import override

from singer_sdk import Stream, Tap
from singer_sdk import typing as th

from tap_readme import streams


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
        return [
            streams.Branches(tap=self),
            streams.Categories(tap=self),
            streams.Changelogs(tap=self),
        ]
