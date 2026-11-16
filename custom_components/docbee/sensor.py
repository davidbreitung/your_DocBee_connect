"""One username sensor and virtual device per DocBee user."""

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DocBeeConfigEntry
from .coordinator import DocBeeCoordinator
from .devices import user_device_info, username_unique_id
from .models import DocBeeUser


async def async_setup_entry(
    hass: HomeAssistant, entry: DocBeeConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Add initial users and discover users appearing on later refreshes."""
    coordinator = entry.runtime_data
    known: set[str] = set()

    @callback
    def add_users() -> None:
        entities = []
        for user_id, user in coordinator.data.items():
            if user_id not in known:
                known.add(user_id)
                entities.append(DocBeeUsernameSensor(coordinator, entry.entry_id, user))
        if entities:
            async_add_entities(entities)

    add_users()
    entry.async_on_unload(coordinator.async_add_listener(add_users))


class DocBeeUsernameSensor(CoordinatorEntity[DocBeeCoordinator], SensorEntity):
    """Expose the username; preserve identity through renames and outages."""

    _attr_has_entity_name = True
    _attr_translation_key = "username"
    _attr_icon = "mdi:account"

    def __init__(self, coordinator: DocBeeCoordinator, entry_id: str, user: DocBeeUser) -> None:
        super().__init__(coordinator)
        self._user_id = user.id
        self._entry_id = entry_id
        self._attr_unique_id = username_unique_id(entry_id, user.id)
        self._attr_device_info = user_device_info(entry_id, user)

    @property
    def available(self) -> bool:
        return super().available and self._user_id in self.coordinator.data

    @property
    def native_value(self) -> str | None:
        user = self.coordinator.data.get(self._user_id)
        return user.username if user else None

    @callback
    def _handle_coordinator_update(self) -> None:
        if user := self.coordinator.data.get(self._user_id):
            info = user_device_info(self._entry_id, user)
            if info != self._attr_device_info:
                self._attr_device_info = info
                registry = dr.async_get(self.hass)
                if device := registry.async_get_device(identifiers=info["identifiers"]):
                    registry.async_update_device(device.id, name=user.username)
        super()._handle_coordinator_update()
