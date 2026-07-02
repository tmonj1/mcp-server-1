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
