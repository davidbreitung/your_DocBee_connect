"""Configure DocBee via Home Assistant's UI."""

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_ACCESS_TOKEN, CONF_URL
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import TextSelector, TextSelectorConfig, TextSelectorType

from .api import (
    DocBeeAuthError,
    DocBeeClient,
    DocBeeConnectionError,
    DocBeeResponseError,
    normalize_url,
)
from .const import DOMAIN


class DocBeeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Validate the complete user read before saving a configuration."""

    VERSION = 1

    async def _validate(self, data: dict[str, Any]) -> dict[str, str]:
        client = DocBeeClient(async_get_clientsession(self.hass), data[CONF_URL], data[CONF_ACCESS_TOKEN])
        await client.async_get_users()
        return {CONF_URL: client.url, CONF_ACCESS_TOKEN: data[CONF_ACCESS_TOKEN].strip()}

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                url = normalize_url(user_input[CONF_URL])
                await self.async_set_unique_id(url)
                self._abort_if_unique_id_configured()
                data = await self._validate(user_input)
            except ValueError:
                errors["base"] = "invalid_input"
            except DocBeeAuthError:
                errors["base"] = "invalid_auth"
            except DocBeeConnectionError:
                errors["base"] = "cannot_connect"
            except DocBeeResponseError:
                errors["base"] = "invalid_response"
            else:
                return self.async_create_entry(title=f"DocBee ({url})", data=data)
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_URL): TextSelector(TextSelectorConfig(type=TextSelectorType.URL)),
                vol.Required(CONF_ACCESS_TOKEN): TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD)),
            }),
            errors=errors,
        )

    async def async_step_reauth(self, entry_data):
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None):
        entry = self._get_reauth_entry()
        errors = {}
        if user_input is not None:
            try:
                data = await self._validate({CONF_URL: entry.data[CONF_URL], **user_input})
            except ValueError:
                errors["base"] = "invalid_input"
            except DocBeeAuthError:
                errors["base"] = "invalid_auth"
            except DocBeeConnectionError:
                errors["base"] = "cannot_connect"
            except DocBeeResponseError:
                errors["base"] = "invalid_response"
            else:
                return self.async_update_reload_and_abort(entry, data_updates=data)
        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({
                vol.Required(CONF_ACCESS_TOKEN): TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD)),
            }),
            errors=errors,
        )
