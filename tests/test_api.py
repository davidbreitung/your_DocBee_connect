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
