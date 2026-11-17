"""Native Home Assistant subentries for the three virtual device groups."""

from types import MappingProxyType

from homeassistant.config_entries import ConfigEntry, ConfigSubentry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr, entity_registry as er

from .const import DOMAIN

GROUPS = {
    "central": "Zentrale Konfiguration",
    "user": "Benutzer",
    "queue": "Queues",
}


def group_ids(entry: ConfigEntry) -> dict[str, str]:
    """Reuse persisted subentry identities across reloads."""
    return {
        subentry.unique_id: subentry.subentry_id
        for subentry in entry.subentries.values()
        if subentry.subentry_type == "device_group" and subentry.unique_id in GROUPS
    }


def _kind(entry_id: str, identifier: str) -> str | None:
    for kind in GROUPS:
        prefix = f"{entry_id}:{kind}"
        if identifier == prefix or identifier.startswith(f"{prefix}:"):
            return kind
    return None


@callback
def async_prepare_groups(hass: HomeAssistant, entry: ConfigEntry) -> dict[str, str]:
    """Create fixed groups and migrate existing registry associations in place."""
    ids = group_ids(entry)
    for kind, title in GROUPS.items():
        if kind not in ids:
            subentry = ConfigSubentry(
                data=MappingProxyType({}), subentry_type="device_group",
                title=title, unique_id=kind,
            )
            hass.config_entries.async_add_subentry(entry, subentry)
            ids[kind] = subentry.subentry_id

    devices = dr.async_get(hass)
    for device in dr.async_entries_for_config_entry(devices, entry.entry_id):
        kind = next((kind for domain, identifier in device.identifiers
                     if domain == DOMAIN and (kind := _kind(entry.entry_id, identifier))), None)
        if kind is None:
            continue
        devices.async_update_device(
            device.id, add_config_entry_id=entry.entry_id,
            add_config_subentry_id=ids[kind],
        )

    entities = er.async_get(hass)
    for entity in er.async_entries_for_config_entry(entities, entry.entry_id):
        if entity.platform == DOMAIN and (kind := _kind(entry.entry_id, entity.unique_id)):
            if entity.config_subentry_id != ids[kind]:
                entities.async_update_entity(entity.entity_id, config_subentry_id=ids[kind])
    # Move entity associations before removing root ownership: registry listeners
    # otherwise delete entities still attached to the removed association.
    for device in dr.async_entries_for_config_entry(devices, entry.entry_id):
        has_our_group = bool(set(ids.values()) & device.config_entries_subentries.get(entry.entry_id, set()))
        if has_our_group and None in device.config_entries_subentries.get(entry.entry_id, set()):
            devices.async_update_device(
                device.id, remove_config_entry_id=entry.entry_id,
                remove_config_subentry_id=None,
            )
    return ids
