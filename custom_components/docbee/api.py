"""Read-only DocBee REST API client."""

import asyncio
from decimal import Decimal, InvalidOperation
import logging
from typing import Any
from urllib.parse import quote

import aiohttp
from yarl import URL

from .activity import HistoryFormatError, closing_users, modified_users, timestamp
from .models import DocBeeUser, DocBeeQueue, DocBeeSnapshot

_LOGGER = logging.getLogger(__name__)

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

    def __init__(self, session: aiohttp.ClientSession, url: str, token: str, *, priority_one_ids: list[str] | None = None) -> None:
        self._session = session
        self.url = normalize_url(url)
        if not isinstance(token, str) or not token.strip() or any(c in token for c in "\r\n"):
            raise ValueError("A nonempty single-line access token is required")
        self._token = token.strip()
        self._priority_one_ids = set(priority_one_ids or [])
        self._priority_warning: tuple[str, ...] = ()
        self._priority_event_warning: str | None = None
        self._daily_warnings: dict[str, str] = {}

    async def _page(self, offset: int, resource: str = "user", fields: str = "id,username,name", filters: dict | None = None, *, sort: bool = True) -> Any:
        params = {"fields": fields, "limit": PAGE_SIZE, "offset": offset}
        if sort:
            params["sortings"] = "id asc"
        params.update(filters or {})
        return await self._request(resource, params)

    async def _request(self, resource: str, params: dict) -> Any:
        try:
            async with self._session.get(
                f"{self.url}/restApi/v1/{resource}",
                params=params,
                headers={"Accept": "application/json", "Authorization": f"Bearer {self._token}"},
                timeout=aiohttp.ClientTimeout(total=30),
                allow_redirects=False,
            ) as response:
                if response.status in (401, 403):
                    raise DocBeeAuthError("Token rejected or user access forbidden")
                if response.status != 200:
                    # Only static route segments and parameter names, never IDs/values.
                    route = "/".join(part if part in {
                        "user", "queue", "priority", "ticket", "ticketStatus", "history", "statusChange",
                    } else "{id}" for part in resource.split("/"))
                    raise DocBeeConnectionError(
                        f"DocBee HTTP status {response.status} "
                        f"(resource: {route}; parameters: {','.join(sorted(params))})"
                    )
                try:
                    return await response.json()
                except (ValueError, aiohttp.ContentTypeError) as err:
                    raise DocBeeResponseError("DocBee did not return valid JSON") from err
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise DocBeeConnectionError("Unable to reach DocBee") from err

    async def _list(self, resource: str, fields: str, filters: dict | None = None, *, result_key: str | None = None, sort: bool = True) -> list[dict]:
        """Fetch a complete list using DocBee's common pagination contract."""
        key = result_key or resource
        items: dict[str, dict] = {}
        offset = 0
        expected_total: int | None = None
        for _ in range(MAX_PAGES):
            payload = await self._page(offset, resource, fields, filters, sort=sort)
            if not isinstance(payload, dict) or not isinstance(payload.get(key), list):
                raise DocBeeResponseError(f"Expected the documented {resource} list")
            rows = payload[key]
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

    @staticmethod
    def _priority_value(value: Any) -> int | None:
        """Accept equivalent whole numeric forms, never coerce invalid data to zero."""
        if isinstance(value, bool) or not isinstance(value, (int, float, str)):
            return None
        try:
            number = Decimal(str(value).strip())
        except InvalidOperation:
            return None
        if not number.is_finite() or not 0 <= number <= 100 or number != number.to_integral_value():
            return None
        return int(number)

    async def async_get_users(self) -> dict[str, DocBeeUser]:
        users = {}
        for row in await self._list("user", "id,username,name,enabled,permissionGroup.id,permissionGroup.name"):
            role = row.get("permissionGroup")
            role_id = None
            role_name = None
            if isinstance(role, dict):
                if role.get("id") is not None:
                    role_id = self._identifier(role["id"])
                role_name = role.get("name")
            elif role is not None:
                # Preserve a reference if DocBee cannot expand its visible name.
                role_id = self._identifier(role)
            try:
                user = DocBeeUser(
                    str(row["id"]), row.get("username"), row.get("name"),
                    role_id, role_name, row.get("enabled"),
                )
            except ValueError as err:
                raise DocBeeResponseError("Missing or invalid user fields") from err
            if len(user.username) > 255:
                raise DocBeeResponseError("Username exceeds Home Assistant state length")
            users[user.id] = user
        return users

    async def async_get_priorities(self) -> dict[str, str]:
        """Return visible priority IDs and labels for the options selector."""
        priorities = {}
        for row in await self._list("priority", "id,name"):
            name = row.get("name")
            if not isinstance(name, str) or not name.strip():
                raise DocBeeResponseError("Missing priority name")
            priorities[str(row["id"])] = name
        return priorities

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
        priority_values_valid = True
        known_priorities = set()
        priority_problems: set[str] = set()
        for row in await self._list("priority", "id,priority"):
            priority_id = str(row["id"])
            known_priorities.add(priority_id)
            if self._priority_one_ids:
                if priority_id in self._priority_one_ids:
                    priority_one.add(priority_id)
                continue
            raw_value = row.get("priority")
            problem = "list:missing" if "priority" not in row else f"list:{type(raw_value).__name__}"
            if raw_value is None:
                # The list may omit optional properties. Try the documented
                # detail endpoint before treating the priority as unknown.
                try:
                    detail = await self._request(
                        f"priority/{quote(priority_id, safe='')}", {"fields": "*"},
                    )
                    if not isinstance(detail, dict) or str(detail.get("id")) != priority_id:
                        raise DocBeeResponseError("Invalid priority detail")
                    raw_value = detail.get("priority")
                    problem += ";detail:missing" if "priority" not in detail else f";detail:{type(raw_value).__name__}"
                except DocBeeError as err:
                    problem += f";detail:{type(err).__name__}"
            value = self._priority_value(raw_value)
            if value is None:
                priority_values_valid = False
                priority_problems.add(problem)
            elif value == 100:
                priority_one.add(priority_id)
        if self._priority_one_ids - known_priorities:
            priority_values_valid = False
            priority_problems.add("selection:missing_priority")
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
                if not self._priority_one_ids and priority not in known_priorities:
                    priority_values_valid = False
                    priority_problems.add("ticket:unknown_priority_reference")
                if priority in priority_one:
                    priority_count += 1
        warning = tuple(sorted(priority_problems))
        if warning != self._priority_warning:
            if warning:
                _LOGGER.warning(
                    "Priority data incomplete (%s); priority-1 count and event comparison "
                    "unavailable. Check the priority selection in integration options. "
                    "Other sensors remain available", ", ".join(warning),
                )
            elif self._priority_warning:
                _LOGGER.info("Priority data valid again; priority-1 evaluation restored")
            self._priority_warning = warning
        event_tickets: dict[str, str] | None = None
        if priority_values_valid:
            event_tickets = {}
            if priority_one:
                # Include closed tickets: closing/reopening must not look like a
                # priority change, and priority changes on old tickets count too.
                try:
                    for row in await self._list(
                        "ticket", "id,ticketNumber", {"priorityIds": ",".join(sorted(priority_one))}
                    ):
                        number = row.get("ticketNumber")
                        if not isinstance(number, str) or not number.strip() or len(number) > 255:
                            raise DocBeeResponseError("Missing or invalid ticket number for priority events")
                        event_tickets[str(row["id"])] = number
                except DocBeeAuthError:
                    raise  # Reauthentication remains available for rejected tokens.
                except DocBeeError as err:
                    event_tickets = None  # Never publish an incomplete event set.
                    warning = str(err)
                    if warning != self._priority_event_warning:
                        _LOGGER.warning(
                            "Priority event ticket request failed: %s. "
                            "Event comparison paused; ticket counts remain available", warning,
                        )
                        self._priority_event_warning = warning
            if event_tickets is not None:
                self._priority_event_warning = None
        return DocBeeSnapshot(
            users, queues, assigned, len(tickets),
            priority_count if priority_values_valid else None, event_tickets,
        )

    async def async_get_daily_counts(self, start: str, end: str) -> dict[str, int | None]:
        """Read totalCount for distinct tickets matching each documented date scope."""
        counts = {}
        for key, scope in (
            ("modified_today", "TICKET_MODIFIED"),
            ("created_today", "TICKET_CREATED"),
            ("closed_today", "TICKET_CLOSED"),
        ):
            try:
                payload = await self._page(0, "ticket", "id", {
                    "limit": 1, "startDate": start, "endDate": end, "ticketScope": scope,
                })
                if (
                    not isinstance(payload, dict)
                    or not isinstance(payload.get("ticket"), list)
                    or type(payload.get("totalCount")) is not int
                    or payload["totalCount"] < 0
                ):
                    raise DocBeeResponseError("Invalid daily ticket count response")
                counts[key] = payload["totalCount"]
                self._daily_warnings.pop(scope, None)
            except DocBeeAuthError:
                raise
            except DocBeeError as err:
                counts[key] = None
                warning = str(err)
                if self._daily_warnings.get(scope) != warning:
                    _LOGGER.warning("Daily ticket count %s unavailable: %s; other counts continue", scope, warning)
                    self._daily_warnings[scope] = warning
        return counts

    async def async_get_user_daily_counts(self, start: str, end: str, user_ids: set[str]) -> dict:
        """Isolate optional history failures from existing integration functionality."""
        unavailable = {"modified_today_by_user": None, "closed_today_by_user": None}
        start_time, end_time = timestamp(start), timestamp(end)
        try:
            candidates = await self._list("ticket", "id", {
                "startDate": start, "endDate": end, "ticketScope": "TICKET_MODIFIED",
            })
        except DocBeeError as err:
            _LOGGER.warning("User daily counts unavailable: TICKET_MODIFIED candidate request failed (%s)", str(err))
            return unavailable
        modified = dict.fromkeys(user_ids, 0)
        closed = dict.fromkeys(user_ids, 0)
        if not candidates:
            return {"modified_today_by_user": modified, "closed_today_by_user": closed}
        closed_statuses: set[str] | None = set()
        try:
            for row in await self._list("ticketStatus", "id,behaviour"):
                if row.get("behaviour") not in ("NORMAL", "PAUSED", "CLOSED"):
                    raise DocBeeResponseError("Invalid ticket status behaviour")
                if row["behaviour"] == "CLOSED":
                    closed_statuses.add(str(row["id"]))
        except DocBeeError as err:
            _LOGGER.warning("User closing counts unavailable: status request failed (%s)", type(err).__name__)
            closed_statuses = None

        edit_errors: set[str] = set()
        close_errors: set[str] = set()

        async def inspect(ticket: dict) -> tuple[set[str] | None, set[str] | None]:
            ticket_path = f"ticket/{quote(str(ticket['id']), safe='')}"
            editors = None
            closers = None
            try:
                history = await self._request(f"{ticket_path}/history", {"exposeDeletedInExpand": "true"})
                editors = modified_users(history, start_time, end_time)
            except (DocBeeError, HistoryFormatError) as err:
                edit_errors.add(type(err).__name__)
            if closed_statuses is not None:
                try:
                    rows = await self._list(
                        f"{ticket_path}/statusChange", "id,user,date,ticketStatus,source",
                        result_key="statusChange", sort=False,
                    )
                    closers = closing_users(rows, closed_statuses, start_time, end_time)
                except (DocBeeError, HistoryFormatError) as err:
                    close_errors.add(type(err).__name__)
            return editors, closers

        modified_complete = True
        closed_complete = closed_statuses is not None
        # Bound request concurrency and task count; never fire one request per user.
        for offset in range(0, len(candidates), 4):
            results = await asyncio.gather(*(inspect(ticket) for ticket in candidates[offset:offset + 4]))
            for editors, closers in results:
                if editors is None:
                    modified_complete = False
                else:
                    for user in editors & user_ids:
                        modified[user] += 1
                if closers is None:
                    closed_complete = False
                else:
                    for user in closers & user_ids:
                        closed[user] += 1
        if edit_errors:
            _LOGGER.warning("User editing counts unavailable: history request/format failed (%s)", ", ".join(sorted(edit_errors)))
        if close_errors:
            _LOGGER.warning("User closing counts unavailable: history request/format failed (%s)", ", ".join(sorted(close_errors)))
        return {
            "modified_today_by_user": modified if modified_complete else None,
            "closed_today_by_user": closed if closed_complete else None,
        }
