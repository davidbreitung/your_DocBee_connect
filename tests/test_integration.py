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
from custom_components.docbee.models import DocBeeUser, DocBeeQueue, DocBeeSnapshot

DATA = {CONF_URL: 'https://example.com', CONF_ACCESS_TOKEN: 'test-token'}
USERS = {'1': DocBeeUser('1', 'alice', 'Alice Example', '17', 'Techniker', True), '2': DocBeeUser('2', 'bob')}


def snapshot(users=USERS):
    return DocBeeSnapshot(users, {'10': DocBeeQueue('10', 'Support')}, {'1': 2, '10': 3}, 5, 1)


async def test_config_flow(hass):
    with patch('custom_components.docbee.api.DocBeeClient.async_get_snapshot', return_value=snapshot()), patch('custom_components.docbee.async_setup_entry', return_value=True):
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
    with patch('custom_components.docbee.api.DocBeeClient.async_get_snapshot', side_effect=error):
        result = await hass.config_entries.flow.async_init(DOMAIN, context={'source': config_entries.SOURCE_USER}, data=DATA)
    assert result['type'] is FlowResultType.FORM
    assert result['errors'] == {'base': expected}
    assert not hass.config_entries.async_entries(DOMAIN)


async def test_devices_sensors_updates_and_unload(hass):
    entry = MockConfigEntry(domain=DOMAIN, data=DATA, unique_id=DATA[CONF_URL])
    entry.add_to_hass(hass)
    with patch('custom_components.docbee.api.DocBeeClient.async_get_snapshot', return_value=snapshot()):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    registry = dr.async_get(hass)
    central = registry.async_get_device(identifiers={central_identifier(entry.entry_id)})
    assert central.name == 'Zentrale Konfiguration'
    entities = er.async_get(hass)
    assert len(er.async_entries_for_device(entities, central.id)) == 2
    devices = dr.async_entries_for_config_entry(registry, entry.entry_id)
    assert len(devices) == 4
    assert len([d for d in devices if d.model == 'Benutzer']) == 2
    alice_id = entities.async_get_entity_id('sensor', DOMAIN, username_unique_id(entry.entry_id, '1'))
    assert hass.states.get(alice_id).state == 'alice'
    assert registry.async_get(entities.async_get(alice_id).device_id).name == 'Alice Example'
    def state(suffix):
        entity_id = entities.async_get_entity_id('sensor', DOMAIN, f'{entry.entry_id}:{suffix}')
        return hass.states.get(entity_id).state
    assert state('user:1:assigned_tickets') == '2'
    assert state('user:1:role') == 'Techniker'
    assert state('user:1:active') == 'yes'
    assert state('user:2:active') == 'unknown'
    assert state('user:2:assigned_tickets') == '0'
    assert entities.async_get_entity_id('sensor', DOMAIN, f'{entry.entry_id}:user:1:open_daily_closings') is None
    assert state('queue:10:current_tickets') == '3'
    assert state('central:open_tickets') == '5'
    assert state('central:priority_one_tickets') == '1'
    assert len([d for d in devices if d.model == 'Queues']) == 1
    coordinator = entry.runtime_data
    coordinator.async_set_updated_data(snapshot({'1': DocBeeUser('1', 'renamed', 'Alice Updated', '18', 'Admin', False), '3': DocBeeUser('3', 'carol')}))
    await hass.async_block_till_done()
    assert hass.states.get(alice_id).state == 'renamed'
    alice_device = registry.async_get(entities.async_get(alice_id).device_id)
    assert alice_device.name == 'Alice Updated'
    assert state('user:1:role') == 'Admin'
    assert state('user:1:active') == 'no'
    role_entity = entities.async_get_entity_id('sensor', DOMAIN, f'{entry.entry_id}:user:1:role')
    assert hass.states.get(role_entity).attributes['permission_group_id'] == '18'
    assert 'state_class' not in hass.states.get(role_entity).attributes
    assert entities.async_get_entity_id('sensor', DOMAIN, username_unique_id(entry.entry_id, '1')) == alice_id
    bob_id = entities.async_get_entity_id('sensor', DOMAIN, username_unique_id(entry.entry_id, '2'))
    assert hass.states.get(bob_id).state == 'unavailable'
    carol_id = entities.async_get_entity_id('sensor', DOMAIN, username_unique_id(entry.entry_id, '3'))
    assert hass.states.get(carol_id).state == 'carol'
    coordinator.async_set_updated_data(DocBeeSnapshot(USERS, {'10': DocBeeQueue('10', 'Support Updated'), '11': DocBeeQueue('11', 'New Queue')}, {'11': 4}, 4, 0))
    await hass.async_block_till_done()
    assert state('queue:10:current_tickets') == '0'
    assert state('queue:11:current_tickets') == '4'
    assert state('central:open_tickets') == '4'
    queue_device = registry.async_get_device(identifiers={(DOMAIN, f'{entry.entry_id}:queue:10')})
    assert queue_device.name == 'Support Updated'
    coordinator.async_set_updated_data(snapshot())
    await hass.async_block_till_done()
    assert state('queue:11:current_tickets') == 'unavailable'
    coordinator.async_set_updated_data(DocBeeSnapshot(USERS, snapshot().queues, {'1': 2}, 2, None))
    await hass.async_block_till_done()
    assert state('central:priority_one_tickets') == 'unavailable'
    assert state('central:open_tickets') == '2'
    assert state('user:1:assigned_tickets') == '2'
    coordinator.async_set_updated_data(snapshot())
    await hass.async_block_till_done()
    assert state('central:priority_one_tickets') == '1'
    coordinator.async_set_update_error(DocBeeConnectionError())
    await hass.async_block_till_done()
    assert hass.states.get(alice_id).state == 'unavailable'
    coordinator.async_set_updated_data(snapshot())
    await hass.async_block_till_done()
    assert hass.states.get(alice_id).state == 'alice'
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert hass.states.get(alice_id).state == 'unavailable'


async def test_reauthentication(hass):
    entry = MockConfigEntry(domain=DOMAIN, data=DATA, unique_id=DATA[CONF_URL])
    entry.add_to_hass(hass)
    with patch('custom_components.docbee.api.DocBeeClient.async_get_snapshot', return_value=snapshot({})), patch('custom_components.docbee.async_setup_entry', return_value=True):
        result = await hass.config_entries.flow.async_init(DOMAIN, context={'source': config_entries.SOURCE_REAUTH, 'entry_id': entry.entry_id}, data=DATA)
        assert result['step_id'] == 'reauth_confirm'
        result = await hass.config_entries.flow.async_configure(result['flow_id'], {CONF_ACCESS_TOKEN: 'replacement-token'})
        assert result['type'] is FlowResultType.ABORT
        assert result['reason'] == 'reauth_successful'
        assert entry.data[CONF_ACCESS_TOKEN] == 'replacement-token'
        await hass.async_block_till_done()


async def test_group_migration_preserves_registry_ids_and_names(hass):
    from custom_components.docbee.groups import group_ids

    entry = MockConfigEntry(domain=DOMAIN, data=DATA, unique_id=DATA[CONF_URL])
    entry.add_to_hass(hass)
    devices = dr.async_get(hass)
    entities = er.async_get(hass)
    old = {}
    for kind, suffix in [('central', 'central'), ('user', 'user:1'), ('queue', 'queue:10')]:
        device = devices.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, f'{entry.entry_id}:{suffix}')}, name=f'Old {kind}',
        )
        devices.async_update_device(device.id, name_by_user=f'Custom {kind}')
        key = 'username' if kind == 'user' else ('open_tickets' if kind == 'central' else 'current_tickets')
        entity = entities.async_get_or_create(
            'sensor', DOMAIN, f'{entry.entry_id}:{suffix}:{key}',
            config_entry=entry, device_id=device.id,
        )
        entities.async_update_entity(entity.entity_id, name=f'Custom {kind} entity')
        old[kind] = (device.id, entity.entity_id)

    with patch('custom_components.docbee.api.DocBeeClient.async_get_snapshot', return_value=snapshot()):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        groups = group_ids(entry)
        assert len(groups) == 3
        assert {s.title for s in entry.subentries.values()} == {'Zentrale Konfiguration', 'Benutzer', 'Queues'}
        for kind, (device_id, entity_id) in old.items():
            device = devices.async_get(device_id)
            assert device.name_by_user == f'Custom {kind}'
            assert device.config_entries_subentries[entry.entry_id] == {groups[kind]}
            entity = entities.async_get(entity_id)
            assert entity.device_id == device_id
            assert entity.name == f'Custom {kind} entity'
            assert entity.config_subentry_id == groups[kind]
        assert await hass.config_entries.async_reload(entry.entry_id)
        await hass.async_block_till_done()
        assert group_ids(entry) == groups
        assert len(dr.async_entries_for_config_entry(devices, entry.entry_id)) == 4

        entry.runtime_data.async_set_updated_data(DocBeeSnapshot(
            {**USERS, '3': DocBeeUser('3', 'new')},
            {'10': DocBeeQueue('10', 'Support'), '11': DocBeeQueue('11', 'New')}, {}, 0, 0,
        ))
        await hass.async_block_till_done()
        for kind, identifier in [('user', '3'), ('queue', '11')]:
            device = devices.async_get_device(identifiers={(DOMAIN, f'{entry.entry_id}:{kind}:{identifier}')})
            assert device.config_entries_subentries[entry.entry_id] == {groups[kind]}
            for entity in er.async_entries_for_device(entities, device.id):
                assert entity.config_subentry_id == groups[kind]
