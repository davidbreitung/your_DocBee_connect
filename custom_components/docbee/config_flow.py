"""Configure DocBee via Home Assistant's UI."""

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import CONF_ACCESS_TOKEN, CONF_URL
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    TextSelector, TextSelectorConfig, TextSelectorType,
    SelectSelector, SelectSelectorConfig, SelectSelectorMode,
)

from .api import (
    DocBeeAuthError,
    DocBeeClient,
    DocBeeConnectionError,
    DocBeeResponseError,
    normalize_url,
)
from .const import DOMAIN, CONF_PRIORITY_ONE_IDS


class DocBeeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Validate all required data reads before saving a configuration."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return DocBeeOptionsFlow()


    async def _validate(self, data: dict[str, Any]) -> dict[str, str]:
        client = DocBeeClient(async_get_clientsession(self.hass), data[CONF_URL], data[CONF_ACCESS_TOKEN])
        await client.async_get_snapshot()
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
                return self.async_create_entry(title=f"Your Docbee Connect ({url})", data=data)
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


class DocBeeOptionsFlow(config_entries.OptionsFlow):
    """Persist explicit priority IDs per connection, without copying credentials."""

    async def async_step_init(self, user_input=None):
        errors = {}
        entry = self.config_entry
        client = DocBeeClient(
            async_get_clientsession(self.hass), entry.data[CONF_URL], entry.data[CONF_ACCESS_TOKEN],
        )
        try:
            priorities = await client.async_get_priorities()
        except DocBeeAuthError:
            return self.async_abort(reason="invalid_auth")
        except DocBeeConnectionError:
            return self.async_abort(reason="cannot_connect")
        except DocBeeResponseError:
            return self.async_abort(reason="invalid_response")
        if user_input is not None:
            selected = user_input.get(CONF_PRIORITY_ONE_IDS, [])
            if not isinstance(selected, list) or any(
                not isinstance(value, str) or value not in priorities for value in selected
            ):
                errors["base"] = "invalid_priority"
            else:
                return self.async_create_entry(title="", data={
                    **entry.options, CONF_PRIORITY_ONE_IDS: list(dict.fromkeys(selected)),
                })
        current = entry.options.get(CONF_PRIORITY_ONE_IDS, [])
        # Retain removed IDs visibly so saving cannot silently change the selection.
        choices = [{"value": key, "label": f"{name} ({key})"} for key, name in priorities.items()]
        choices.extend({"value": key, "label": key} for key in current if key not in priorities)
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(CONF_PRIORITY_ONE_IDS, default=current): SelectSelector(
                    SelectSelectorConfig(options=choices, multiple=True, mode=SelectSelectorMode.DROPDOWN),
                ),
            }),
            errors=errors,
        )
