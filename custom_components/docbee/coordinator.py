"""Refresh DocBee users, queues and ticket counts as an atomic snapshot."""

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import DocBeeAuthError, DocBeeClient, DocBeeError
from .const import DOMAIN, EVENT_PRIORITY_ONE, priority_event_signal
from .devices import central_identifier
from .models import DocBeeSnapshot

_LOGGER = logging.getLogger(__name__)


class DocBeeCoordinator(DataUpdateCoordinator[DocBeeSnapshot]):
    """Poll DocBee data every five minutes."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, client: DocBeeClient) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            config_entry=entry,
            update_interval=timedelta(minutes=5),
            always_update=False,
        )
        self.client = client
        self.entry_id = entry.entry_id
        self.last_priority_ticket_number: str | None = None
        self._priority_baseline: dict[str, str] | None = None
        self._event_store = Store(hass, 1, f"{DOMAIN}.{entry.entry_id}.priority_events")

    async def _async_update_data(self) -> DocBeeSnapshot:
        try:
            return await self.client.async_get_snapshot()
        except DocBeeAuthError as err:
            raise ConfigEntryAuthFailed("DocBee access token or permissions invalid") from err
        except DocBeeError as err:
            raise UpdateFailed(str(err)) from err

    async def async_initialize_priority_events(self) -> None:
        """Restore the last number, but treat the first live read as a baseline."""
        stored = await self._event_store.async_load()
        if isinstance(stored, dict) and isinstance(stored.get("last_ticket_number"), str):
            self.last_priority_ticket_number = stored["last_ticket_number"]
        self._priority_baseline = self.data.priority_one_ticket_numbers

    @callback
    def async_process_priority_events(self) -> None:
        """Emit once for each observed entry into the set of priority-100 tickets."""
        if not self.last_update_success:
            return
        current = self.data.priority_one_ticket_numbers
        if current is None:
            return  # Unknown priority data must not clear the baseline.
        previous = self._priority_baseline
        self._priority_baseline = current
        if previous is None:
            return
        device = dr.async_get(self.hass).async_get_device(
            identifiers={central_identifier(self.entry_id)}
        )
        for ticket_id in sorted(current.keys() - previous.keys()):
            self.last_priority_ticket_number = current[ticket_id]
            payload = {
                "config_entry_id": self.entry_id,
                "device_id": device.id if device else None,
                "ticket_id": ticket_id,
                "ticket_number": current[ticket_id],
            }
            async_dispatcher_send(self.hass, priority_event_signal(self.entry_id), payload)
            self.hass.bus.async_fire(EVENT_PRIORITY_ONE, payload)
            self._event_store.async_delay_save(
                lambda: {"last_ticket_number": self.last_priority_ticket_number}, 1,
            )

    async def async_save_priority_state(self) -> None:
        """Flush the last number when unloading for an immediate reload."""
        await self._event_store.async_save({"last_ticket_number": self.last_priority_ticket_number})
