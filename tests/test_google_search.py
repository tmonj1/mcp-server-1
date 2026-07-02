import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
from main import google_search


@pytest.mark.asyncio
async def test_google_search_returns_html():
    mock_response = MagicMock()
    mock_response.text = "<html><body>Google Search Results</body></html>"

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client

        result = await google_search(query="FastMCP")

    assert "<html>" in result
    assert "Google Search Results" in result


@pytest.mark.asyncio
async def test_google_search_uses_correct_url():
    mock_response = MagicMock()
    mock_response.text = "<html></html>"

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client

        await google_search(query="test query")

        call_args = mock_client.get.call_args
        url_arg = str(call_args[0][0])
        assert "https://www.google.com/search" in url_arg
        assert "test+query" in url_arg or "test%20query" in url_arg or "test query" in url_arg


@pytest.mark.asyncio
async def test_google_search_returns_error_on_http_error():
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(side_effect=httpx.HTTPStatusError(
            "403 Forbidden",
            request=MagicMock(),
            response=MagicMock(status_code=403)
        ))
        mock_client_class.return_value = mock_client

        result = await google_search(query="test")

    assert "エラー" in result or "Error" in result or "error" in result.lower()


@pytest.mark.asyncio
async def test_google_search_returns_error_on_timeout():
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(side_effect=httpx.TimeoutException("timeout"))
        mock_client_class.return_value = mock_client

        result = await google_search(query="test")

    assert "タイムアウト" in result or "timeout" in result.lower() or "エラー" in result
