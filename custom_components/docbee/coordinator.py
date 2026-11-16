"""Refresh DocBee users as an atomic snapshot."""

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import DocBeeAuthError, DocBeeClient, DocBeeError
from .const import DOMAIN
from .models import DocBeeUser

_LOGGER = logging.getLogger(__name__)


class DocBeeCoordinator(DataUpdateCoordinator[dict[str, DocBeeUser]]):
    """Poll all users every five minutes."""

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

    async def _async_update_data(self) -> dict[str, DocBeeUser]:
        try:
            return await self.client.async_get_users()
        except DocBeeAuthError as err:
            raise ConfigEntryAuthFailed("DocBee access token or permissions invalid") from err
        except DocBeeError as err:
            raise UpdateFailed(str(err)) from err
