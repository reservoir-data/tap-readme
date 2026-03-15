"""Stream type classes for tap-readme."""

from __future__ import annotations

import importlib.resources
from typing import TYPE_CHECKING, Any, NamedTuple, cast, override

from singer_sdk import OpenAPISchema, Stream, StreamSchema
from toolz import get_in

from tap_readme.client import ReadMeStream

if TYPE_CHECKING:
    from collections.abc import Generator

    from singer_sdk.helpers.types import Context


class StreamKey(NamedTuple):
    """A key for a stream in the OpenAPI spec."""

    path: str
    method: str
    expected_status: int = 200
    extra_keys: tuple[str | int, ...] = ()


class ReadMeOpenAPISource(OpenAPISchema[StreamKey]):
    """OpenAPI source for PlanetScale API."""

    @override
    def get_unresolved_schema(self, key: StreamKey) -> dict[str, Any]:
        return get_in(  # type: ignore[no-any-return,no-untyped-call]
            [
                "paths",
                key.path,
                key.method,
                "responses",
                str(key.expected_status),
                "content",
                "application/json",
                "schema",
                *key.extra_keys,
                "properties",
                "data",
                "items",
            ],
            self.spec,
        )

    @override
    def fetch_schema(self, key: StreamKey) -> dict[str, Any]:
        schema = super().fetch_schema(key)
        if key.path == Categories.path:
            schema["properties"]["branch"] = {"type": "string"}
        return schema


class SchemaFromPath(StreamSchema[StreamKey]):
    """A stream schema from a path in the OpenAPI spec."""

    @override
    def get_stream_schema(
        self,
        stream: Stream,
        stream_class: type[Stream],
    ) -> dict[str, Any]:
        stream = cast("ReadMeStream", stream)
        key = StreamKey(
            path=stream.path,
            method=stream.http_method.lower(),
            expected_status=200,
            extra_keys=stream.extra_keys,
        )
        return self.schema_source.get_schema(key)


OPENAPI = ReadMeOpenAPISource(importlib.resources.files("tap_readme") / "openapi.json")


class Branches(ReadMeStream):
    """Branches stream."""

    name = "branches"
    path = "/branches"
    primary_keys = ("name",)
    replication_key = None

    extra_keys = ("anyOf", 0)
    schema = SchemaFromPath(OPENAPI)

    @override
    def generate_child_contexts(
        self,
        record: dict[str, Any],
        context: Context | None,
    ) -> Generator[dict[str, Any] | None, None, None]:
        yield {"branch": record["name"], "section": "guides"}
        yield {"branch": record["name"], "section": "reference"}


class Categories(ReadMeStream):
    """Categories stream."""

    name = "Categories"
    path = "/branches/{branch}/categories/{section}"
    primary_keys = ("title",)
    replication_key = None
    parent_stream_type = Branches

    schema = SchemaFromPath(OPENAPI)


class Changelogs(ReadMeStream):
    """Changelogs stream."""

    name = "changelogs"
    path = "/changelogs"
    primary_keys = ("title",)
    replication_key = None

    schema = SchemaFromPath(OPENAPI)
