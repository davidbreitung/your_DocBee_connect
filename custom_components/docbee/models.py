"""Internal models, independent of the DocBee API response format."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DocBeeUser:
    """A user identified by an immutable ID, never by their display name.

    The API adapter must populate these fields from the documented API.
    """

    id: str
    username: str
    name: str | None = None
    role_id: str | None = None
    role_name: str | None = None
    enabled: bool | None = None

    @property
    def display_name(self) -> str:
        """Use the DocBee display name, falling back for unnamed users."""
        return self.name if self.name and self.name.strip() else self.username

    def __post_init__(self) -> None:
        if self.enabled is not None and type(self.enabled) is not bool:
            raise ValueError("The enabled status must be a boolean")
        if self.role_name is not None and (not isinstance(self.role_name, str) or len(self.role_name) > 255):
            raise ValueError("Invalid role name")
        if self.name is not None and not isinstance(self.name, str):
            raise ValueError("The display name must be a string")
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("A nonempty user ID is required")
        if not isinstance(self.username, str) or not self.username.strip():
            raise ValueError("A nonempty username is required")


@dataclass(frozen=True, slots=True)
class DocBeeQueue:
    """A virtual queue device."""

    id: str
    name: str


@dataclass(frozen=True, slots=True)
class DocBeeSnapshot:
    """A fully fetched set of users, queues and non-closed ticket counts."""

    users: dict[str, DocBeeUser]
    queues: dict[str, DocBeeQueue]
    assigned_tickets: dict[str, int]
    open_tickets: int
    priority_one_tickets: int | None
    priority_one_ticket_numbers: dict[str, str] | None = None
    modified_today: int | None = None
    created_today: int | None = None
    closed_today: int | None = None
    modified_today_by_user: dict[str, int] | None = None
    closed_today_by_user: dict[str, int] | None = None
