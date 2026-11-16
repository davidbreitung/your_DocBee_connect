"""Device metadata for Home Assistant's device registry.

The setup entry must explicitly register the central device: unlike user
devices, it does not yet have an entity that registers it automatically.
"""

from .const import CENTRAL_DEVICE_NAME, DOMAIN, MANUFACTURER, USER_DEVICE_MODEL
from .models import DocBeeUser


def central_identifier(entry_id: str) -> tuple[str, str]:
    """Scope device identities to a single integration configuration."""
    return DOMAIN, f"{entry_id}:central"


def central_device_info(entry_id: str) -> dict:
    """Return registry metadata for the entity-free configuration device."""
    return {
        "identifiers": {central_identifier(entry_id)},
        "name": CENTRAL_DEVICE_NAME,
        "manufacturer": MANUFACTURER,
        "model": CENTRAL_DEVICE_NAME,
    }


def user_device_info(entry_id: str, user: DocBeeUser) -> dict:
    """Return one independent virtual device per user.

    Do not use via_device: the central configuration is not a transport hub.
    Home Assistant models are used for classification, not custom device classes.
    """
    return {
        "identifiers": {(DOMAIN, f"{entry_id}:user:{user.id}")},
        "name": user.username,
        "manufacturer": MANUFACTURER,
        "model": USER_DEVICE_MODEL,
    }


def username_unique_id(entry_id: str, user_id: str) -> str:
    """Keep the username entity identity stable when a user is renamed."""
    return f"{entry_id}:user:{user_id}:username"
