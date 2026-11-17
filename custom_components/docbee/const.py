"""Shared constants for the DocBee integration."""

DOMAIN = "docbee"
MANUFACTURER = "DocBee"
CENTRAL_DEVICE_NAME = "Zentrale Konfiguration"
USER_DEVICE_MODEL = "Benutzer"

EVENT_PRIORITY_ONE = "docbee_priority_one_ticket"

def priority_event_signal(entry_id: str) -> str:
    """Keep event subscriptions isolated by configured instance."""
    return f"{DOMAIN}_{entry_id}_priority_one_ticket"
