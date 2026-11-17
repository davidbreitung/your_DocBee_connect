"""Exercise protocol handling without contacting a production DocBee instance."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest

from custom_components.docbee.api import (
    DocBeeAuthError, DocBeeClient, DocBeeConnectionError,
    DocBeeResponseError, normalize_url,
)


def page(rows, offset=0, total=None, limit=50):
    return {"user": rows, "offset": offset, "limit": limit,
            "totalCount": len(rows) if total is None else total}


def session_for(*payloads, status=200):
    session = MagicMock(spec=aiohttp.ClientSession)
    responses = []
    for payload in payloads:
        response = MagicMock()
        response.status = status
        response.json = AsyncMock(return_value=payload)
        context = MagicMock()
        context.__aenter__ = AsyncMock(return_value=response)
        context.__aexit__ = AsyncMock(return_value=False)
        responses.append(context)
    session.get.side_effect = responses
    return session


@pytest.mark.parametrize('value', ['http://example.com', 'https://user:secret@example.com', 'https://example.com/?token=x', 'https://example.com/#x', 'not a url'])
def test_invalid_urls(value):
    with pytest.raises(ValueError):
        normalize_url(value)


def test_normalize_url():
    assert normalize_url(' https://EXAMPLE.com:443/docbee/restApi/ ') == 'https://example.com/docbee'


async def test_pagination_and_headers():
    first = [{'id': i, 'username': f'user{i}'} for i in range(50)]
    session = session_for(page(first, total=51), page([{'id': 50, 'username': 'last'}], offset=50, total=51))
    users = await DocBeeClient(session, 'https://example.com', 'secret').async_get_users()
    assert len(users) == 51
    assert users['50'].username == 'last'
    assert [call.kwargs['params']['offset'] for call in session.get.call_args_list] == [0, 50]
    call = session.get.call_args_list[0]
    assert call.args[0] == 'https://example.com/restApi/v1/user'
    assert call.kwargs['headers']['Authorization'] == 'Bearer secret'
    assert call.kwargs['allow_redirects'] is False


async def test_short_pages_and_user_envelope():
    session = session_for(page([{'id': 1, 'username': 'alice'}], total=2, limit=1), page([{'id': 2, 'username': 'bob'}], offset=1, total=2, limit=1))
    assert list(await DocBeeClient(session, 'https://example.com', 'secret').async_get_users()) == ['1', '2']
    assert session.get.call_args_list[1].kwargs['params']['offset'] == 1


async def test_repeated_page_is_error_not_infinite_loop():
    rows = [{'id': 1, 'username': 'alice'}]
    session = session_for(page(rows, total=2), page(rows, offset=1, total=2))
    with pytest.raises(DocBeeResponseError, match='Repeated'):
        await DocBeeClient(session, 'https://example.com', 'secret').async_get_users()
    assert session.get.call_count == 2


@pytest.mark.parametrize('payload', [{}, {'data': {}}, [None], [{'username': 'alice'}], [{'id': True, 'username': 'alice'}], [{'id': 1, 'username': ''}], [{'id': 1, 'username': 'x' * 256}]])
async def test_bad_payloads(payload):
    with pytest.raises(DocBeeResponseError):
        await DocBeeClient(session_for(page(payload) if isinstance(payload, list) else payload), 'https://example.com', 'secret').async_get_users()


@pytest.mark.parametrize('status,error', [(401, DocBeeAuthError), (403, DocBeeAuthError), (429, DocBeeConnectionError), (500, DocBeeConnectionError), (302, DocBeeConnectionError)])
async def test_http_errors(status, error):
    with pytest.raises(error):
        await DocBeeClient(session_for({}, status=status), 'https://example.com', 'secret').async_get_users()


async def test_timeout():
    session = MagicMock()
    session.get.side_effect = asyncio.TimeoutError
    with pytest.raises(DocBeeConnectionError):
        await DocBeeClient(session, 'https://example.com', 'secret').async_get_users()


async def test_empty_user_list():
    assert await DocBeeClient(session_for(page([])), 'https://example.com', 'secret').async_get_users() == {}


@pytest.mark.parametrize('second', [
    page([], offset=1, total=2),
    page([{'id': 2, 'username': 'bob'}], offset=0, total=2),
    page([{'id': 2, 'username': 'bob'}], offset=1, total=3),
    {'user': [], 'offset': 1, 'limit': 50},
])
async def test_incomplete_or_inconsistent_pages(second):
    session = session_for(page([{'id': 1, 'username': 'alice'}], total=2), second)
    with pytest.raises(DocBeeResponseError):
        await DocBeeClient(session, 'https://example.com', 'secret').async_get_users()


async def test_user_display_name_is_requested_and_parsed():
    session = session_for(page([{'id': 1, 'username': 'alice', 'name': 'Alice Example'}]))
    users = await DocBeeClient(session, 'https://example.com', 'secret').async_get_users()
    assert session.get.call_args.kwargs['params']['fields'] == 'id,username,name,enabled,permissionGroup.id,permissionGroup.name'
    assert users['1'].display_name == 'Alice Example'
    assert users['1'].username == 'alice'


@pytest.mark.parametrize('name', [None, '', ' '])
async def test_missing_display_name_falls_back_to_username(name):
    session = session_for(page([{'id': 1, 'username': 'alice', 'name': name}]))
    users = await DocBeeClient(session, 'https://example.com', 'secret').async_get_users()
    assert users['1'].display_name == 'alice'


def resource_page(resource, rows, **kwargs):
    result = page(rows, **kwargs)
    result[resource] = result.pop('user')
    return result


async def test_snapshot_counts_responsible_users_queues_and_priority_value():
    session = session_for(
        page([{'id': 1, 'username': 'alice', 'name': 'Alice'}]),
        resource_page('queue', [{'id': 20, 'name': 'Support'}]),
        resource_page('priority', [{'id': 77, 'priority': 100}, {'id': 1, 'priority': 50}, {'id': 88, 'priority': 100}]),
        resource_page('ticket', [
            {'id': 1, 'owner': 1, 'priority': 77},
            {'id': 2, 'owner': 20, 'priority': 1},
            {'id': 3, 'owner': 20, 'priority': 88},
            {'id': 4, 'owner': None, 'priority': None},
        ]),
        resource_page('ticket', [{'id': 1, 'ticketNumber': 'V1'}, {'id': 3, 'ticketNumber': 'V3'}, {'id': 9, 'ticketNumber': 'V9'}]),
    )
    snapshot = await DocBeeClient(session, 'https://example.com', 'secret').async_get_snapshot()
    assert snapshot.open_tickets == 4
    assert snapshot.priority_one_tickets == 2
    assert snapshot.assigned_tickets == {'1': 1, '20': 2}
    assert snapshot.queues['20'].name == 'Support'
    assert snapshot.priority_one_ticket_numbers == {'1': 'V1', '3': 'V3', '9': 'V9'}
    assert session.get.call_args.kwargs['params']['priorityIds'] == '77,88'
    assert 'notClosed' not in session.get.call_args.kwargs['params']
    call = session.get.call_args_list[3]
    assert call.args[0].endswith('/restApi/v1/ticket')
    assert call.kwargs['params']['notClosed'] == 'true'
    assert 'isLocked' not in call.kwargs['params']
    assert call.kwargs['params']['fields'] == 'id,owner,priority'


async def test_ticket_counts_include_every_page():
    session = session_for(
        page([]), resource_page('queue', []), resource_page('priority', []),
        resource_page('ticket', [{'id': 1, 'owner': 20, 'priority': None}], total=2, limit=1),
        resource_page('ticket', [{'id': 2, 'owner': 20, 'priority': None}], offset=1, total=2, limit=1),
    )
    snapshot = await DocBeeClient(session, 'https://example.com', 'secret').async_get_snapshot()
    assert snapshot.assigned_tickets == {'20': 2}
    assert snapshot.open_tickets == 2
    assert session.get.call_args.kwargs['params']['offset'] == 1


@pytest.mark.parametrize('ticket', [{'id': 1}, {'id': 1, 'owner': {}, 'priority': 1}])
async def test_invalid_ticket_does_not_produce_false_zero_counts(ticket):
    session = session_for(page([]), resource_page('queue', []), resource_page('priority', []), resource_page('ticket', [ticket]))
    with pytest.raises(DocBeeResponseError):
        await DocBeeClient(session, 'https://example.com', 'secret').async_get_snapshot()


@pytest.mark.parametrize('enabled', [True, False, None])
async def test_role_expansion_and_enabled_status(enabled):
    session = session_for(page([{'id': 1, 'username': 'alice', 'enabled': enabled,
                                'permissionGroup': {'id': 17, 'name': 'Techniker'}}]))
    user = (await DocBeeClient(session, 'https://example.com', 'secret').async_get_users())['1']
    assert user.role_id == '17'
    assert user.role_name == 'Techniker'
    assert user.enabled is enabled


async def test_unexpanded_role_is_not_misreported_as_a_name():
    session = session_for(page([{'id': 1, 'username': 'alice', 'permissionGroup': 17}]))
    user = (await DocBeeClient(session, 'https://example.com', 'secret').async_get_users())['1']
    assert user.role_id == '17'
    assert user.role_name is None
    assert user.enabled is None


@pytest.mark.parametrize('enabled', ['false', 0, 1, {}])
async def test_invalid_enabled_status_is_not_coerced(enabled):
    session = session_for(page([{'id': 1, 'username': 'alice', 'enabled': enabled}]))
    with pytest.raises(DocBeeResponseError):
        await DocBeeClient(session, 'https://example.com', 'secret').async_get_users()


@pytest.mark.parametrize('value,expected', [(100, 1), (100.0, 1), ('100', 1), ('100.0', 1), (' 100 ', 1), (0, 0), ('50', 0)])
async def test_priority_numeric_representations(value, expected):
    session = session_for(page([]), resource_page('queue', []),
        resource_page('priority', [{'id': 77, 'priority': value}]),
        resource_page('ticket', [{'id': 1, 'owner': 20, 'priority': 77}]),
        *([resource_page('ticket', [{'id': 1, 'ticketNumber': 'V1'}])] if expected else []))
    snapshot = await DocBeeClient(session, 'https://example.com', 'secret').async_get_snapshot()
    assert snapshot.priority_one_tickets == expected
    assert snapshot.assigned_tickets == {'20': 1}


@pytest.mark.parametrize('value', [None, True, '', 'high', 'NaN', 'Infinity', 100.5, -1, 101, {}])
async def test_bad_priority_only_disables_priority_count(value):
    session = session_for(page([]), resource_page('queue', []),
        resource_page('priority', [{'id': 77, 'priority': value}]),
        *([{'id': 77, 'priority': None}] if value is None else []),
        resource_page('ticket', [{'id': 1, 'owner': 20, 'priority': 77}]))
    snapshot = await DocBeeClient(session, 'https://example.com', 'secret').async_get_snapshot()
    assert snapshot.priority_one_tickets is None
    assert snapshot.open_tickets == 1
    assert snapshot.assigned_tickets == {'20': 1}


async def test_unknown_priority_reference_does_not_produce_false_zero():
    session = session_for(page([]), resource_page('queue', []), resource_page('priority', []),
        resource_page('ticket', [{'id': 1, 'owner': 20, 'priority': 77}]))
    snapshot = await DocBeeClient(session, 'https://example.com', 'secret').async_get_snapshot()
    assert snapshot.priority_one_tickets is None
    assert snapshot.open_tickets == 1


@pytest.mark.parametrize('number', [None, '', 'x' * 256])
async def test_priority_event_requires_a_real_ticket_number(number):
    session = session_for(page([]), resource_page('queue', []),
        resource_page('priority', [{'id': 77, 'priority': 100}]),
        resource_page('ticket', []),
        resource_page('ticket', [{'id': 1, 'ticketNumber': number}]))
    with pytest.raises(DocBeeResponseError, match='ticket number'):
        await DocBeeClient(session, 'https://example.com', 'secret').async_get_snapshot()


async def test_daily_counts_use_total_count_and_independent_scopes():
    session = session_for(*[resource_page('ticket', [{'id': 1}], total=n, limit=1) for n in (251, 19, 7)])
    counts = await DocBeeClient(session, 'https://example.com', 'secret').async_get_daily_counts(
        '2026-11-16T23:00:00+00:00', '2026-11-17T12:00:00+00:00')
    assert counts == {'modified_today': 251, 'created_today': 19, 'closed_today': 7}
    assert [c.kwargs['params']['ticketScope'] for c in session.get.call_args_list] == [
        'TICKET_MODIFIED', 'TICKET_CREATED', 'TICKET_CLOSED']
    for call in session.get.call_args_list:
        assert call.kwargs['params']['startDate'] == '2026-11-16T23:00:00+00:00'
        assert call.kwargs['params']['endDate'] == '2026-11-17T12:00:00+00:00'
        assert call.kwargs['params']['limit'] == 1
        assert 'notClosed' not in call.kwargs['params']


@pytest.mark.parametrize('count', [None, True, -1, '7'])
async def test_daily_counts_reject_bad_totals(count):
    session = session_for({'ticket': [], 'totalCount': count})
    with pytest.raises(DocBeeResponseError):
        await DocBeeClient(session, 'https://example.com', 'secret').async_get_daily_counts('start', 'end')


@pytest.mark.parametrize("row", [{"id": 77}, {"id": 77, "priority": None}])
async def test_missing_priority_recovers_from_documented_detail(row):
    session = session_for(page([]), resource_page("queue", []),
        resource_page("priority", [row]), {"id": 77, "priority": 100},
        resource_page("ticket", [{"id": 1, "owner": 20, "priority": 77}]),
        resource_page("ticket", [{"id": 1, "ticketNumber": "V1"}]))
    snapshot = await DocBeeClient(session, "https://example.com", "secret").async_get_snapshot()
    assert snapshot.priority_one_tickets == 1
    assert snapshot.priority_one_ticket_numbers == {"1": "V1"}
    detail_call = session.get.call_args_list[3]
    assert detail_call.args[0].endswith("/priority/77")
    assert detail_call.kwargs["params"] == {"fields": "*"}


@pytest.mark.parametrize("detail", [{"id": 77}, {"id": 88, "priority": 100}, [], {"id": 77, "priority": None}])
async def test_unresolved_priority_detail_is_safe_and_warning_recovers(detail, caplog):
    bad_cycle = [page([]), resource_page("queue", []),
        resource_page("priority", [{"id": 77}]), detail,
        resource_page("ticket", [{"id": 1, "owner": 20, "priority": 77}])]
    good_cycle = [page([]), resource_page("queue", []),
        resource_page("priority", [{"id": 77, "priority": 100}]),
        resource_page("ticket", [{"id": 1, "owner": 20, "priority": 77}]),
        resource_page("ticket", [{"id": 1, "ticketNumber": "V1"}])]
    client = DocBeeClient(session_for(*bad_cycle, *bad_cycle, *good_cycle, *bad_cycle), "https://example.com", "secret")
    for _ in range(2):
        snapshot = await client.async_get_snapshot()
        assert snapshot.priority_one_tickets is None
        assert snapshot.priority_one_ticket_numbers is None
        assert snapshot.assigned_tickets == {"20": 1}
    assert sum("Priority data incomplete" in r.message for r in caplog.records) == 1
    assert (await client.async_get_snapshot()).priority_one_tickets == 1
    await client.async_get_snapshot()
    assert sum("Priority data incomplete" in r.message for r in caplog.records) == 2


async def test_priority_detail_permission_failure_preserves_other_counts(monkeypatch):
    session = session_for(page([]), resource_page("queue", []),
        resource_page("priority", [{"id": 77, "priority": None}]),
        resource_page("ticket", [{"id": 1, "owner": 20, "priority": 77}]))
    client = DocBeeClient(session, "https://example.com", "secret")
    original_request = client._request

    async def request(resource, params):
        if resource == "priority/77":
            raise DocBeeAuthError("Forbidden")
        return await original_request(resource, params)

    monkeypatch.setattr(client, "_request", request)
    snapshot = await client.async_get_snapshot()
    assert snapshot.open_tickets == 1
    assert snapshot.assigned_tickets == {"20": 1}
    assert snapshot.priority_one_tickets is None
    assert snapshot.priority_one_ticket_numbers is None


async def test_selected_priorities_work_without_values_and_survive_renaming():
    session = session_for(page([]), resource_page('queue', []),
        resource_page('priority', [{'id': 77, 'name': 'Renamed'}, {'id': 78}]),
        resource_page('ticket', [
            {'id': 1, 'owner': 20, 'priority': 77},
            {'id': 2, 'owner': 20, 'priority': 78},
            {'id': 3, 'owner': None, 'priority': 99},
        ]), resource_page('ticket', [{'id': 1, 'ticketNumber': 'V1'}, {'id': 2, 'ticketNumber': 'V2'}]))
    client = DocBeeClient(session, 'https://example.com', 'secret', priority_one_ids=['77', '78'])
    snapshot = await client.async_get_snapshot()
    assert snapshot.priority_one_tickets == 2
    assert snapshot.priority_one_ticket_numbers == {'1': 'V1', '2': 'V2'}
    assert session.get.call_args.kwargs['params']['priorityIds'] == '77,78'
    assert session.get.call_count == 5  # No numeric detail lookups.


async def test_removed_selected_priority_disables_count_and_events():
    session = session_for(page([]), resource_page('queue', []),
        resource_page('priority', [{'id': 78, 'priority': 100}]),
        resource_page('ticket', [{'id': 1, 'owner': 20, 'priority': 78}]))
    snapshot = await DocBeeClient(session, 'https://example.com', 'secret', priority_one_ids=['77']).async_get_snapshot()
    assert snapshot.priority_one_tickets is None
    assert snapshot.priority_one_ticket_numbers is None
    assert snapshot.open_tickets == 1
