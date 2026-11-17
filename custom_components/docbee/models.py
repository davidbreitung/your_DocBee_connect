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

    @property
    def display_name(self) -> str:
        """Use the DocBee display name, falling back for unnamed users."""
        return self.name if self.name and self.name.strip() else self.username

    def __post_init__(self) -> None:
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
    priority_one_tickets: int
