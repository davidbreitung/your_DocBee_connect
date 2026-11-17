"""Priority-one ticket events on the central configuration device."""

from homeassistant.components.event import EventEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DocBeeConfigEntry
from .const import priority_event_signal
from .coordinator import DocBeeCoordinator
from .devices import central_device_info
from .groups import group_ids


async def async_setup_entry(
    hass: HomeAssistant, entry: DocBeeConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_add_entities(
        [DocBeePriorityEvent(entry.runtime_data, entry.entry_id)],
        config_subentry_id=group_ids(entry)["central"],
    )


class DocBeePriorityEvent(CoordinatorEntity[DocBeeCoordinator], EventEntity):
    """Timestamp and ticket attributes for the last detected priority transition."""

    _attr_has_entity_name = True
    _attr_translation_key = "priority_one_ticket"
    _attr_event_types = ["priority_one_ticket"]
    _attr_icon = "mdi:ticket-alert"

    def __init__(self, coordinator: DocBeeCoordinator, entry_id: str) -> None:
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._attr_unique_id = f"{entry_id}:central:priority_one_event"
        self._attr_device_info = central_device_info(entry_id)

    @property
    def available(self) -> bool:
        return super().available and self.coordinator.data.priority_one_ticket_numbers is not None

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(async_dispatcher_connect(
            self.hass, priority_event_signal(self._entry_id), self._priority_event,
        ))

    @callback
    def _priority_event(self, payload: dict) -> None:
        self._trigger_event("priority_one_ticket", payload)
        self.async_write_ha_state()
