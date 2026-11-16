"""Internal models, independent of the DocBee API response format."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DocBeeUser:
    """A user identified by an immutable ID, never by their display name.

    The API adapter must populate these fields from the documented API.
    """

    id: str
    username: str

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("A nonempty user ID is required")
        if not isinstance(self.username, str) or not self.username.strip():
            raise ValueError("A nonempty username is required")
