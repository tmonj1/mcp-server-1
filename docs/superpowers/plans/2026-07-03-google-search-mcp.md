# Google検索MCPサーバー 実装計画

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** FastMCPを使い、Google検索結果ページのHTMLをそのまま返す `google_search` ツールを持つMCPサーバーを実装する。

**Architecture:** `main.py` をFastMCPサーバーとして書き直し、`@mcp.tool` デコレータで `google_search(query: str) -> str` ツールを1つ定義する。内部では `httpx.AsyncClient` を使い `https://www.google.com/search?q={query}` にGETリクエストを送り、レスポンスのHTMLを返す。

**Tech Stack:** Python 3.12+, FastMCP (`mcp[cli]`), httpx, pytest, pytest-asyncio

---

## ファイル構成

| パス | 役割 |
|------|------|
| `main.py` | FastMCPサーバーのエントリポイント（書き換え） |
| `pyproject.toml` | 依存関係に `httpx` と `pytest-asyncio` を追加 |
| `tests/test_google_search.py` | `google_search` ツールの単体テスト（新規作成） |

---

### Task 1: 依存関係を追加する

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: httpx と pytest/pytest-asyncio を依存関係に追加**

`pyproject.toml` を以下のように変更する:

```toml
[project]
name = "mcp-server-1"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "mcp[cli]>=1.28.1",
    "python-dotenv>=1.2.2",
    "httpx>=0.27.0",
]

[dependency-groups]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
]
```

- [ ] **Step 2: 依存関係をインストールして確認**

```bash
uv sync
```

期待される出力: エラーなく完了し、`httpx` が `.venv` にインストールされる。

```bash
uv run python -c "import httpx; print(httpx.__version__)"
```

期待される出力: バージョン番号が表示される（例: `0.27.0`）

- [ ] **Step 3: コミット**

```bash
git add pyproject.toml uv.lock
git commit -m "chore: add httpx and pytest-asyncio dependencies"
```

---

### Task 2: テストファイルを作成する（TDD: 先にテストを書く）

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/test_google_search.py`

- [ ] **Step 1: tests ディレクトリと __init__.py を作成**

```bash
mkdir -p tests
touch tests/__init__.py
```

- [ ] **Step 2: 失敗するテストを書く**

`tests/test_google_search.py` を以下の内容で作成する:

```python
import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
from main import mcp


@pytest.mark.asyncio
async def test_google_search_returns_html():
    mock_response = MagicMock()
    mock_response.text = "<html><body>Google Search Results</body></html>"
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client

        # MCPツールを直接呼び出す
        from main import google_search
        result = await google_search(query="FastMCP")

    assert "<html>" in result
    assert "Google Search Results" in result


@pytest.mark.asyncio
async def test_google_search_uses_correct_url():
    mock_response = MagicMock()
    mock_response.text = "<html></html>"
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client

        from main import google_search
        await google_search(query="test query")

        call_args = mock_client.get.call_args
        assert "https://www.google.com/search" in call_args[0][0]
        assert "test+query" in call_args[0][0] or "test%20query" in call_args[0][0] or "test query" in str(call_args)


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

        from main import google_search
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

        from main import google_search
        result = await google_search(query="test")

    assert "タイムアウト" in result or "timeout" in result.lower() or "エラー" in result
```

- [ ] **Step 3: テストが失敗することを確認**

```bash
uv run pytest tests/test_google_search.py -v
```

期待される出力: `ImportError` または `AttributeError` で失敗（`main.py` にまだ `google_search` が存在しないため）

- [ ] **Step 4: コミット**

```bash
git add tests/__init__.py tests/test_google_search.py
git commit -m "test: google_search ツールの失敗テストを追加"
```

---

### Task 3: MCPサーバーを実装する

**Files:**
- Modify: `main.py`

- [ ] **Step 1: main.py をFastMCPサーバーとして書き直す**

`main.py` を以下の内容に置き換える:

```python
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("google-search")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ja,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


@mcp.tool()
async def google_search(query: str) -> str:
    """Google で指定したキーワードを検索し、結果ページのHTMLを返す。"""
    url = f"https://www.google.com/search?q={httpx.URL('', params={'q': query}).params}"
    try:
        async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text
    except httpx.HTTPStatusError as e:
        return f"エラー: HTTP {e.response.status_code} - {e}"
    except httpx.TimeoutException:
        return "エラー: タイムアウトしました（10秒）"
    except Exception as e:
        return f"エラー: {e}"


if __name__ == "__main__":
    mcp.run()
```

- [ ] **Step 2: テストを実行して全て通ることを確認**

```bash
uv run pytest tests/test_google_search.py -v
```

期待される出力:
```
tests/test_google_search.py::test_google_search_returns_html PASSED
tests/test_google_search.py::test_google_search_uses_correct_url PASSED
tests/test_google_search.py::test_google_search_returns_error_on_http_error PASSED
tests/test_google_search.py::test_google_search_returns_error_on_timeout PASSED

4 passed in X.XXs
```

- [ ] **Step 3: コミット**

```bash
git add main.py
git commit -m "feat: Google検索MCPサーバーを実装"
```

---

### Task 4: 動作確認

**Files:** なし（確認のみ）

- [ ] **Step 1: MCPサーバーを起動して `google_search` ツールが認識されることを確認**

```bash
uv run python main.py
```

または MCP Inspector で確認:

```bash
uv run mcp dev main.py
```

期待される出力: サーバーが起動し、`google_search` ツールが一覧に表示される。

- [ ] **Step 2: 全テストを実行**

```bash
uv run pytest -v
```

期待される出力: 全テストが PASSED

- [ ] **Step 3: 最終コミット**

```bash
git add -A
git commit -m "chore: Google検索MCPサーバーの実装完了"
```
