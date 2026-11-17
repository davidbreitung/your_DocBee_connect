"""Home Assistant integration for DocBee."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ACCESS_TOKEN, CONF_URL, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.storage import Store

from .const import DOMAIN

from .api import DocBeeClient
from .coordinator import DocBeeCoordinator
from .devices import central_device_info
from .groups import async_prepare_groups

PLATFORMS = [Platform.SENSOR, Platform.EVENT]
type DocBeeConfigEntry = ConfigEntry[DocBeeCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: DocBeeConfigEntry) -> bool:
    """Validate access, register the central device and load sensors."""
    client = DocBeeClient(
        async_get_clientsession(hass), entry.data[CONF_URL], entry.data[CONF_ACCESS_TOKEN]
    )
    coordinator = DocBeeCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()
    await coordinator.async_initialize_priority_events()
    entry.runtime_data = coordinator
    groups = async_prepare_groups(hass, entry)
    dr.async_get(hass).async_get_or_create(
        config_entry_id=entry.entry_id,
        config_subentry_id=groups["central"],
        entry_type=dr.DeviceEntryType.SERVICE,
        **central_device_info(entry.entry_id),
    )
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(coordinator.async_add_listener(coordinator.async_process_priority_events))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: DocBeeConfigEntry) -> bool:
    """Unload sensors and their update subscriptions."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        await entry.runtime_data.async_save_priority_state()
    return unloaded


async def async_remove_entry(hass: HomeAssistant, entry: DocBeeConfigEntry) -> None:
    """Remove local event state when the connection is deleted."""
    await Store(hass, 1, f"{DOMAIN}.{entry.entry_id}.priority_events").async_remove()
