"""Exercise flows, registry entries and sensors in real Home Assistant core."""

from unittest.mock import patch

import pytest
from homeassistant import config_entries
from homeassistant.const import CONF_ACCESS_TOKEN, CONF_URL
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import device_registry as dr, entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.docbee.api import DocBeeAuthError, DocBeeConnectionError, DocBeeResponseError
from custom_components.docbee.const import DOMAIN
from custom_components.docbee.devices import central_identifier, username_unique_id
from custom_components.docbee.models import DocBeeUser

DATA = {CONF_URL: 'https://example.com', CONF_ACCESS_TOKEN: 'test-token'}
USERS = {'1': DocBeeUser('1', 'alice'), '2': DocBeeUser('2', 'bob')}


async def test_config_flow(hass):
    with patch('custom_components.docbee.api.DocBeeClient.async_get_users', return_value=USERS), patch('custom_components.docbee.async_setup_entry', return_value=True):
        result = await hass.config_entries.flow.async_init(DOMAIN, context={'source': config_entries.SOURCE_USER})
        assert result['type'] is FlowResultType.FORM
        result = await hass.config_entries.flow.async_configure(result['flow_id'], DATA)
        assert result['type'] is FlowResultType.CREATE_ENTRY
        assert result['data'] == DATA
        await hass.async_block_till_done()
        duplicate = await hass.config_entries.flow.async_init(DOMAIN, context={'source': config_entries.SOURCE_USER}, data={**DATA, CONF_URL: 'https://example.com/restApi/'})
        assert duplicate['type'] is FlowResultType.ABORT
        assert duplicate['reason'] == 'already_configured'


@pytest.mark.parametrize('error,expected', [(DocBeeAuthError(), 'invalid_auth'), (DocBeeConnectionError(), 'cannot_connect'), (DocBeeResponseError(), 'invalid_response')])
async def test_flow_errors(hass, error, expected):
    with patch('custom_components.docbee.api.DocBeeClient.async_get_users', side_effect=error):
        result = await hass.config_entries.flow.async_init(DOMAIN, context={'source': config_entries.SOURCE_USER}, data=DATA)
    assert result['type'] is FlowResultType.FORM
    assert result['errors'] == {'base': expected}
    assert not hass.config_entries.async_entries(DOMAIN)


async def test_devices_sensors_updates_and_unload(hass):
    entry = MockConfigEntry(domain=DOMAIN, data=DATA, unique_id=DATA[CONF_URL])
    entry.add_to_hass(hass)
    with patch('custom_components.docbee.api.DocBeeClient.async_get_users', return_value=USERS):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    registry = dr.async_get(hass)
    central = registry.async_get_device(identifiers={central_identifier(entry.entry_id)})
    assert central.name == 'Zentrale Konfiguration'
    entities = er.async_get(hass)
    assert not er.async_entries_for_device(entities, central.id)
    devices = dr.async_entries_for_config_entry(registry, entry.entry_id)
    assert len(devices) == 3
    assert len([d for d in devices if d.model == 'Benutzer']) == 2
    alice_id = entities.async_get_entity_id('sensor', DOMAIN, username_unique_id(entry.entry_id, '1'))
    assert hass.states.get(alice_id).state == 'alice'
    coordinator = entry.runtime_data
    coordinator.async_set_updated_data({'1': DocBeeUser('1', 'renamed'), '3': DocBeeUser('3', 'carol')})
    await hass.async_block_till_done()
    assert hass.states.get(alice_id).state == 'renamed'
    alice_device = registry.async_get(entities.async_get(alice_id).device_id)
    assert alice_device.name == 'renamed'
    bob_id = entities.async_get_entity_id('sensor', DOMAIN, username_unique_id(entry.entry_id, '2'))
    assert hass.states.get(bob_id).state == 'unavailable'
    carol_id = entities.async_get_entity_id('sensor', DOMAIN, username_unique_id(entry.entry_id, '3'))
    assert hass.states.get(carol_id).state == 'carol'
    coordinator.async_set_update_error(DocBeeConnectionError())
    await hass.async_block_till_done()
    assert hass.states.get(alice_id).state == 'unavailable'
    coordinator.async_set_updated_data(USERS)
    await hass.async_block_till_done()
    assert hass.states.get(alice_id).state == 'alice'
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert hass.states.get(alice_id).state == 'unavailable'


async def test_reauthentication(hass):
    entry = MockConfigEntry(domain=DOMAIN, data=DATA, unique_id=DATA[CONF_URL])
    entry.add_to_hass(hass)
    with patch('custom_components.docbee.api.DocBeeClient.async_get_users', return_value={}), patch('custom_components.docbee.async_setup_entry', return_value=True):
        result = await hass.config_entries.flow.async_init(DOMAIN, context={'source': config_entries.SOURCE_REAUTH, 'entry_id': entry.entry_id}, data=DATA)
        assert result['step_id'] == 'reauth_confirm'
        result = await hass.config_entries.flow.async_configure(result['flow_id'], {CONF_ACCESS_TOKEN: 'replacement-token'})
        assert result['type'] is FlowResultType.ABORT
        assert result['reason'] == 'reauth_successful'
        assert entry.data[CONF_ACCESS_TOKEN] == 'replacement-token'
        await hass.async_block_till_done()
