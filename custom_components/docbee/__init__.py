"""Home Assistant integration for DocBee."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ACCESS_TOKEN, CONF_URL, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import DocBeeClient
from .coordinator import DocBeeCoordinator
from .devices import central_device_info
from .groups import async_prepare_groups

PLATFORMS = [Platform.SENSOR]
type DocBeeConfigEntry = ConfigEntry[DocBeeCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: DocBeeConfigEntry) -> bool:
    """Validate access, register the central device and load sensors."""
    client = DocBeeClient(
        async_get_clientsession(hass), entry.data[CONF_URL], entry.data[CONF_ACCESS_TOKEN]
    )
    coordinator = DocBeeCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    groups = async_prepare_groups(hass, entry)
    dr.async_get(hass).async_get_or_create(
        config_entry_id=entry.entry_id,
        config_subentry_id=groups["central"],
        entry_type=dr.DeviceEntryType.SERVICE,
        **central_device_info(entry.entry_id),
    )
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: DocBeeConfigEntry) -> bool:
    """Unload sensors and their update subscriptions."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
