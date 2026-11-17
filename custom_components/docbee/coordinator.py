"""Refresh DocBee users, queues and ticket counts as an atomic snapshot."""

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import DocBeeAuthError, DocBeeClient, DocBeeError
from .const import DOMAIN
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

    async def _async_update_data(self) -> DocBeeSnapshot:
        try:
            return await self.client.async_get_snapshot()
        except DocBeeAuthError as err:
            raise ConfigEntryAuthFailed("DocBee access token or permissions invalid") from err
        except DocBeeError as err:
            raise UpdateFailed(str(err)) from err
