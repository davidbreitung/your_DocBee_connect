"""User, queue and central sensors for Your Docbee Connect."""

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DocBeeConfigEntry
from .coordinator import DocBeeCoordinator
from .devices import central_device_info, queue_device_info, user_device_info
from .groups import group_ids


async def async_setup_entry(
    hass: HomeAssistant, entry: DocBeeConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Register central counters and discover user/queue devices on each update."""
    coordinator = entry.runtime_data
    known: set[tuple[str, str]] = set()
    groups = group_ids(entry)
    async_add_entities([
        DocBeeSensor(coordinator, entry.entry_id, "central", None, key)
        for key in ("open_tickets", "priority_one_tickets")
    ], config_subentry_id=groups["central"])

    @callback
    def add_devices() -> None:
        for kind, records, keys in (
            ("user", coordinator.data.users, ("username", "role", "active", "assigned_tickets")),
            ("queue", coordinator.data.queues, ("current_tickets",)),
        ):
            entities = []
            for identifier in records:
                if (kind, identifier) not in known:
                    known.add((kind, identifier))
                    entities.extend(DocBeeSensor(coordinator, entry.entry_id, kind, identifier, key) for key in keys)
            if entities:
                async_add_entities(entities, config_subentry_id=groups[kind])

    add_devices()
    entry.async_on_unload(coordinator.async_add_listener(add_devices))


class DocBeeSensor(CoordinatorEntity[DocBeeCoordinator], SensorEntity):
    """Stable identities across display-name changes and temporarily missing data."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: DocBeeCoordinator, entry_id: str, kind: str, identifier: str | None, key: str) -> None:
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._kind = kind
        self._identifier = identifier
        self._key = key
        self._attr_translation_key = key
        suffix = kind if identifier is None else f"{kind}:{identifier}"
        self._attr_unique_id = f"{entry_id}:{suffix}:{key}"
        self._attr_icon = "mdi:account" if key == "username" else "mdi:ticket-outline"
        if key in ("assigned_tickets", "current_tickets", "open_tickets", "priority_one_tickets"):
            self._attr_state_class = SensorStateClass.MEASUREMENT
        elif key == "role":
            self._attr_icon = "mdi:account-key"
        elif key == "active":
            self._attr_icon = "mdi:account-check"
            self._attr_device_class = SensorDeviceClass.ENUM
            self._attr_options = ["yes", "no"]
        self._attr_device_info = self._device_info()

    def _device_info(self) -> dict | None:
        if self._kind == "central":
            return central_device_info(self._entry_id)
        if self._kind == "user":
            if user := self.coordinator.data.users.get(self._identifier):
                return user_device_info(self._entry_id, user)
        elif queue := self.coordinator.data.queues.get(self._identifier):
            return queue_device_info(self._entry_id, queue)
        return None

    @property
    def available(self) -> bool:
        if not super().available:
            return False
        if self._key == "priority_one_tickets":
            return self.coordinator.data.priority_one_tickets is not None
        return self._device_info() is not None

    @property
    def native_value(self) -> str | int | None:
        data = self.coordinator.data
        if self._kind == "central":
            return getattr(data, self._key)
        if self._device_info() is None:
            return None
        if self._key == "username":
            return data.users[self._identifier].username
        if self._key == "role":
            return data.users[self._identifier].role_name
        if self._key == "active":
            enabled = data.users[self._identifier].enabled
            return None if enabled is None else ("yes" if enabled else "no")
        return data.assigned_tickets.get(self._identifier, 0)

    @property
    def extra_state_attributes(self) -> dict | None:
        if self._key == "role":
            user = self.coordinator.data.users.get(self._identifier)
            return {"permission_group_id": user.role_id if user else None}
        return None

    @callback
    def _handle_coordinator_update(self) -> None:
        info = self._device_info()
        if info is not None and info != self._attr_device_info:
            self._attr_device_info = info
            registry = dr.async_get(self.hass)
            if device := registry.async_get_device(identifiers=info["identifiers"]):
                registry.async_update_device(device.id, name=info["name"])
        super()._handle_coordinator_update()
