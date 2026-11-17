"""Parse per-ticket audit and status histories without retaining message contents."""

from datetime import datetime
from typing import Any


class HistoryFormatError(ValueError):
    """Incomplete history data must not become a misleading zero count."""


def timestamp(value: Any) -> datetime:
    if not isinstance(value, str):
        raise HistoryFormatError("Missing history timestamp")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as err:
        raise HistoryFormatError("Invalid history timestamp") from err
    if result.tzinfo is None or result.utcoffset() is None:
        raise HistoryFormatError("History timestamp lacks timezone")
    return result


def identifier(value: Any) -> str:
    if isinstance(value, bool) or not isinstance(value, (str, int)) or not str(value).strip():
        raise HistoryFormatError("Invalid history user or status identifier")
    return str(value)


def modified_users(payload: Any, start: datetime, end: datetime) -> set[str]:
    """Read the observed grouped-array format; each item's own date is decisive."""
    if not isinstance(payload, list):
        raise HistoryFormatError(f"history: expected grouped array, got {type(payload).__name__}")
    pending = []
    for group in payload:
        if not isinstance(group, dict) or not isinstance(group.get("items"), list):
            raise HistoryFormatError("history[].items: expected array")
        pending.extend((item, "history[].items[]") for item in group["items"])
    users = set()
    while pending:
        item, path = pending.pop()
        if not isinstance(item, dict):
            raise HistoryFormatError(f"{path}: expected object, got {type(item).__name__}")
        children = item.get("childItems", [])
        if not isinstance(children, list):
            raise HistoryFormatError(f"{path}.childItems: expected array, got {type(children).__name__}")
        pending.extend((child, "childItems[]") for child in children)
        try:
            date = timestamp(item.get("date"))
        except HistoryFormatError as err:
            value_type = type(item["date"]).__name__ if "date" in item else "missing"
            raise HistoryFormatError(f"{path}.date ({value_type}): {err}") from err
        if not start <= date <= end:
            continue
        actor = item.get("actor")
        if actor is None:
            continue
        if not isinstance(actor, dict):
            raise HistoryFormatError(f"{path}.actor: expected object, got {type(actor).__name__}")
        if actor.get("actorType") != "user" or actor.get("userType") != "USER":
            continue
        if item.get("type") in ("INSERT", "UPDATE"):
            try:
                users.add(identifier(actor.get("id")))
            except HistoryFormatError as err:
                value_type = type(actor["id"]).__name__ if "id" in actor else "missing"
                raise HistoryFormatError(f"{path}.actor.id ({value_type}): {err}") from err
    return users


def closing_users(rows: list[dict], closed_statuses: set[str], start: datetime, end: datetime) -> set[str]:
    """Count distinct people who performed a closed-state transition today."""
    users = set()
    for row in rows:
        date = timestamp(row.get("date"))
        if not start <= date <= end or row.get("source") != "USER":
            continue
        status = identifier(row.get("ticketStatus"))
        if status in closed_statuses and row.get("user") is not None:
            users.add(identifier(row["user"]))
    return users
