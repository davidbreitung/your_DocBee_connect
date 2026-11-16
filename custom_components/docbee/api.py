"""Read-only DocBee REST API client."""

import asyncio
from typing import Any

import aiohttp
from yarl import URL

from .models import DocBeeUser

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

    async def _page(self, offset: int) -> Any:
        try:
            async with self._session.get(
                f"{self.url}/restApi/v1/user",
                params={"fields": "id,username", "limit": PAGE_SIZE, "offset": offset, "sortings": "id asc"},
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

    async def async_get_users(self) -> dict[str, DocBeeUser]:
        """Return a complete snapshot or fail; never silently publish a partial list."""
        users: dict[str, DocBeeUser] = {}
        offset = 0
        expected_total: int | None = None
        for _ in range(MAX_PAGES):
            payload = await self._page(offset)
            if not isinstance(payload, dict) or not isinstance(payload.get("user"), list):
                raise DocBeeResponseError("Expected the documented UserList object")
            rows = payload["user"]
            for field in ("totalCount", "offset", "limit"):
                if type(payload.get(field)) is not int or payload[field] < 0:
                    raise DocBeeResponseError("Invalid pagination metadata")
            total = payload["totalCount"]
            if payload["offset"] != offset or payload["limit"] < 1 or len(rows) > payload["limit"]:
                raise DocBeeResponseError("Inconsistent pagination metadata")
            if expected_total is not None and total != expected_total:
                raise DocBeeResponseError("User count changed during pagination; retry required")
            expected_total = total
            for row in rows:
                if not isinstance(row, dict):
                    raise DocBeeResponseError("Invalid user record")
                user_id = row.get("id")
                if isinstance(user_id, bool) or not isinstance(user_id, (str, int)):
                    raise DocBeeResponseError("Missing or invalid user ID")
                try:
                    user = DocBeeUser(str(user_id), row.get("username"))
                except ValueError as err:
                    raise DocBeeResponseError("Missing or invalid user fields") from err
                if user.id in users:
                    raise DocBeeResponseError("Repeated user ID; pagination may be unsupported")
                if len(user.username) > 255:
                    raise DocBeeResponseError("Username exceeds Home Assistant state length")
                users[user.id] = user
            offset += len(rows)
            if offset > total:
                raise DocBeeResponseError("User list exceeds totalCount")
            if offset == total:
                return users
            if not rows:
                raise DocBeeResponseError("User list ended before totalCount")
        raise DocBeeResponseError("User pagination exceeded the safety limit")
