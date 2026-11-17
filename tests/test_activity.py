"""Synthetic histories; no customer identities or message content stored here."""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from custom_components.docbee.activity import HistoryFormatError, modified_users, closing_users
from custom_components.docbee.api import DocBeeClient, DocBeeAuthError, DocBeeConnectionError

START = datetime.fromisoformat('2026-11-16T23:00:00+00:00')
END = datetime.fromisoformat('2026-11-17T12:00:00+00:00')


def item(user=17, date='2026-11-17T10:00:00Z', kind='UPDATE', **actor):
    return {'actor': {'id': user, 'actorType': 'user', 'userType': 'USER', **actor},
            'date': date, 'type': kind, 'messages': ['ignored'], 'childItems': []}


def page(key, rows, offset=0, total=None):
    return {key: rows, 'offset': offset, 'limit': 50, 'totalCount': len(rows) if total is None else total}


def test_item_dates_deduplication_automation_and_nested_changes():
    parent = item(17)
    parent['childItems'] = [item(18)]
    data = [{'date': '2000-01-01T00:00:00Z', 'items': [
        parent, item(17), item(19, date='2026-11-16T22:59:59Z'),
        item(20, date='2026-11-17T12:00:01Z'),
        item(None, actorType='rule_engine', userType=None),
        item(None, actorType=None, userType=None, kind='INSERT'),
        item(21, actorType='user', userType='CUSTOMER'),
        item(22, kind='INSERT'),
    ]}]
    assert modified_users(data, START, END) == {'17', '18', '22'}
    assert modified_users([{'items': [item(17, date=START.isoformat())]}], START, END) == {'17'}


@pytest.mark.parametrize('payload', [{}, [{'items': {}}], [{'items': [None]}],
    [{'items': [item(date='not-a-date')]}], [{'items': [item(date='2026-11-17T10:00:00')]}]])
def test_malformed_history_is_not_zero(payload):
    with pytest.raises(HistoryFormatError):
        modified_users(payload, START, END)


def test_closing_actors_are_deduplicated_and_automatic_changes_excluded():
    def change(user, status, source='USER'):
        return {'user': user, 'ticketStatus': status, 'source': source, 'date': '2026-11-17T10:00:00Z'}
    rows = [change(17, 9), change(17, 1), change(17, 9), change(18, 9), change(19, 9, 'RULE_ENGINE')]
    assert closing_users(rows, {'9'}, START, END) == {'17', '18'}


@pytest.mark.parametrize('failure', [None, 'history_auth', 'status_auth', 'bad_history', 'candidates'])
async def test_user_counts_and_independent_error_isolation(failure):
    client = DocBeeClient(AsyncMock(), 'https://example.com', 'synthetic-token')
    calls = []

    async def request(resource, params):
        calls.append((resource, params))
        if resource == 'ticket':
            if failure == 'candidates':
                raise DocBeeConnectionError()
            assert params['ticketScope'] == 'TICKET_MODIFIED'
            assert 'notClosed' not in params
            return page('ticket', [{'id': 100}, {'id': 101}])
        if resource == 'ticketStatus':
            return page('ticketStatus', [{'id': 9, 'behaviour': 'CLOSED'}, {'id': 1, 'behaviour': 'NORMAL'}])
        if resource.endswith('/history'):
            assert params == {'exposeDeletedInExpand': 'true'}
            if failure == 'history_auth':
                raise DocBeeAuthError()
            if failure == 'bad_history':
                return {'unexpected': []}
            return [{'items': [item(17), item(17), item(18), item(None, actorType='rule_engine')]}]
        if resource.endswith('/statusChange'):
            assert 'sortings' not in params
            if failure == 'status_auth':
                raise DocBeeAuthError()
            return page('statusChange', [
                {'id': 1, 'user': 18, 'ticketStatus': 9, 'source': 'USER', 'date': '2026-11-17T10:00:00Z'},
                {'id': 2, 'user': 18, 'ticketStatus': 9, 'source': 'USER', 'date': '2026-11-17T11:00:00Z'},
            ])
        raise AssertionError(resource)

    client._request = request
    counts = await client.async_get_user_daily_counts(START.isoformat(), END.isoformat(), {'17', '18', '19'})
    assert counts['modified_today_by_user'] == (None if failure in ('candidates', 'history_auth', 'bad_history') else {'17': 2, '18': 2, '19': 0})
    assert counts['closed_today_by_user'] == (None if failure in ('candidates', 'status_auth') else {'17': 0, '18': 2, '19': 0})


async def test_status_history_uses_documented_pagination():
    client = DocBeeClient(AsyncMock(), 'https://example.com', 'synthetic-token')
    client._request = AsyncMock(side_effect=[
        page('statusChange', [{'id': 1}], total=2),
        page('statusChange', [{'id': 2}], offset=1, total=2),
    ])
    rows = await client._list('ticket/100/statusChange', 'id', result_key='statusChange', sort=False)
    assert rows == [{'id': 1}, {'id': 2}]
    assert client._request.call_args.args[1]['offset'] == 1
    assert 'sortings' not in client._request.call_args.args[1]


@pytest.mark.parametrize('fault,expected', [
    ('date', 'history[].items[].date (str): Invalid history timestamp'),
    ('child', 'childItems[].date (missing): Missing history timestamp'),
    ('children_null', 'history[].items[].childItems: expected array, got NoneType'),
    ('actor_id', 'history[].items[].actor.id (dict): Invalid history user or status identifier'),
])
async def test_history_warning_reports_schema_reason_without_private_values(fault, expected, caplog):
    entry = item()
    entry['actor']['name'] = 'PRIVATE_NAME'
    entry['messages'] = ['PRIVATE_MESSAGE']
    if fault == 'date':
        entry['date'] = 'PRIVATE_BAD_DATE'
    elif fault == 'child':
        entry['childItems'] = [{'messages': ['PRIVATE_CHILD']}]
    elif fault == 'children_null':
        entry['childItems'] = None
    else:
        entry['actor']['id'] = {'PRIVATE_ID': 'PRIVATE_VALUE'}
    client = DocBeeClient(AsyncMock(), 'https://example.com', 'PRIVATE_TOKEN')
    async def request(resource, params):
        if resource == 'ticket':
            return page('ticket', [{'id': 987654}])
        if resource == 'ticketStatus':
            return page('ticketStatus', [{'id': 9, 'behaviour': 'CLOSED'}])
        if resource.endswith('/history'):
            return [{'items': [entry]}]
        return page('statusChange', [])
    client._request = request
    counts = await client.async_get_user_daily_counts(START.isoformat(), END.isoformat(), {'17'})
    assert counts['modified_today_by_user'] is None
    assert counts['closed_today_by_user'] == {'17': 0}
    assert expected in caplog.text
    assert 'PRIVATE' not in caplog.text
    assert '987654' not in caplog.text
