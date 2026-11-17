"""Read-only DocBee REST API client."""

import asyncio
from typing import Any

import aiohttp
from yarl import URL

from .models import DocBeeUser, DocBeeQueue, DocBeeSnapshot

PAGE_SIZE = 50
MAX_PAGES = 1000


class DocBeeError(Exception):
    """A safe-to-report API failure (never includes response bodies or tokens)."""


class DocBeeAuthError(DocBeeError):
    """Invalid token or insufficient permissions."""


class DocBeeConnectionError(DocBeeError):
    """Connection, timeout or HTTP failure."""


class DocBeeResponseError(DocBeeError):
    """Unexpected or incomplete response."""


def normalize_url(value: str) -> str:
    """Accept only HTTPS instance roots, optionally ending in /restApi."""
    try:
        url = URL(value.strip())
        if (
            url.scheme != "https"
            or not url.host
            or url.user is not None
            or url.password is not None
            or url.query_string
            or url.fragment
        ):
            raise ValueError
        # Accessing port also validates malformed port numbers.
        _ = url.port
        path = url.path.rstrip("/")
        if path.endswith("/restApi"):
            path = path[:-8]
        return str(url.with_path(path)).rstrip("/")
    except (TypeError, ValueError) as err:
        raise ValueError("Enter an HTTPS DocBee instance URL") from err


class DocBeeClient:
    """Use an existing DocBee access token; never modify remote data.

    Implements the UserList schema and offset pagination from the DocBee
    2026.2.0 OpenAPI specification at /restApi/v1/openapi.json.
    """

    def __init__(self, session: aiohttp.ClientSession, url: str, token: str) -> None:
        self._session = session
        self.url = normalize_url(url)
        if not isinstance(token, str) or not token.strip() or any(c in token for c in "\r\n"):
            raise ValueError("A nonempty single-line access token is required")
        self._token = token.strip()

    async def _page(self, offset: int, resource: str = "user", fields: str = "id,username,name", filters: dict | None = None) -> Any:
        try:
            async with self._session.get(
                f"{self.url}/restApi/v1/{resource}",
                params={"fields": fields, "limit": PAGE_SIZE, "offset": offset, "sortings": "id asc", **(filters or {})},
                headers={"Accept": "application/json", "Authorization": f"Bearer {self._token}"},
                timeout=aiohttp.ClientTimeout(total=30),
                allow_redirects=False,
            ) as response:
                if response.status in (401, 403):
                    raise DocBeeAuthError("Token rejected or user access forbidden")
                if response.status != 200:
                    raise DocBeeConnectionError(f"DocBee HTTP status {response.status}")
                try:
                    return await response.json()
                except (ValueError, aiohttp.ContentTypeError) as err:
                    raise DocBeeResponseError("DocBee did not return valid JSON") from err
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise DocBeeConnectionError("Unable to reach DocBee") from err

    async def _list(self, resource: str, fields: str, filters: dict | None = None) -> list[dict]:
        """Fetch a complete list using DocBee's common pagination contract."""
        items: dict[str, dict] = {}
        offset = 0
        expected_total: int | None = None
        for _ in range(MAX_PAGES):
            payload = await self._page(offset, resource, fields, filters)
            if not isinstance(payload, dict) or not isinstance(payload.get(resource), list):
                raise DocBeeResponseError(f"Expected the documented {resource} list")
            rows = payload[resource]
            for field in ("totalCount", "offset", "limit"):
                if type(payload.get(field)) is not int or payload[field] < 0:
                    raise DocBeeResponseError("Invalid pagination metadata")
            total = payload["totalCount"]
            if payload["offset"] != offset or payload["limit"] < 1 or len(rows) > payload["limit"]:
                raise DocBeeResponseError("Inconsistent pagination metadata")
            if expected_total is not None and total != expected_total:
                raise DocBeeResponseError("Record count changed during pagination; retry required")
            expected_total = total
            for row in rows:
                if not isinstance(row, dict):
                    raise DocBeeResponseError("Invalid record")
                identifier = self._identifier(row.get("id"))
                if identifier in items:
                    raise DocBeeResponseError("Repeated record ID; pagination may be unsupported")
                items[identifier] = row
            offset += len(rows)
            if offset > total:
                raise DocBeeResponseError("List exceeds totalCount")
            if offset == total:
                return list(items.values())
            if not rows:
                raise DocBeeResponseError("List ended before totalCount")
        raise DocBeeResponseError("Pagination exceeded the safety limit")

    @staticmethod
    def _identifier(value: Any) -> str:
        if isinstance(value, bool) or not isinstance(value, (str, int)) or not str(value).strip():
            raise DocBeeResponseError("Missing or invalid record ID")
        return str(value)

    async def async_get_users(self) -> dict[str, DocBeeUser]:
        users = {}
        for row in await self._list("user", "id,username,name"):
            try:
                user = DocBeeUser(str(row["id"]), row.get("username"), row.get("name"))
            except ValueError as err:
                raise DocBeeResponseError("Missing or invalid user fields") from err
            if len(user.username) > 255:
                raise DocBeeResponseError("Username exceeds Home Assistant state length")
            users[user.id] = user
        return users

    async def async_get_snapshot(self) -> DocBeeSnapshot:
        """Aggregate all visible non-closed tickets, independent of lock flags."""
        users = await self.async_get_users()
        queues = {}
        for row in await self._list("queue", "id,name"):
            if not isinstance(row.get("name"), str) or not row["name"].strip():
                raise DocBeeResponseError("Missing queue name")
            queue = DocBeeQueue(str(row["id"]), row["name"])
            queues[queue.id] = queue
        priority_one = set()
        for row in await self._list("priority", "id,priority"):
            if type(row.get("priority")) is not int:
                raise DocBeeResponseError("Invalid priority value")
            if row["priority"] == 100:
                priority_one.add(str(row["id"]))
        tickets = await self._list("ticket", "id,owner,priority", {"notClosed": "true"})
        assigned: dict[str, int] = {}
        priority_count = 0
        for row in tickets:
            if "owner" not in row or "priority" not in row:
                raise DocBeeResponseError("Missing ticket owner or priority field")
            if row["owner"] is not None:
                owner = self._identifier(row["owner"])
                assigned[owner] = assigned.get(owner, 0) + 1
            if row["priority"] is not None:
                priority = self._identifier(row["priority"])
                if priority in priority_one:
                    priority_count += 1
        return DocBeeSnapshot(users, queues, assigned, len(tickets), priority_count)
