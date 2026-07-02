# Google検索MCPサーバー 設計ドキュメント

## 概要

FastMCPを使ってGoogle検索を実行し、検索結果ページのHTMLをそのまま返すMCPサーバー。

## アーキテクチャ

`main.py` をFastMCPサーバーとして実装する。ツールは1つだけ。

```
main.py
  └─ FastMCP インスタンス
       └─ @mcp.tool: google_search(query)
            └─ httpx.AsyncClient でリクエスト送信
                 └─ HTML文字列を返却
```

## ツール仕様

| 項目 | 内容 |
|------|------|
| ツール名 | `google_search` |
| 引数 | `query: str` — 検索キーワード |
| 戻り値 | `str` — Google検索結果ページのHTML全文 |
| エラー時 | エラーメッセージ文字列を返す |

## HTTPリクエスト詳細

- **URL:** `https://www.google.com/search?q={query}`
- **User-Agent:** Chromeを模倣した文字列（bot検出を軽減）
- **Accept-Language:** `ja,en;q=0.9`（日本語結果優先）
- **タイムアウト:** 10秒
- **リダイレクト追従:** あり

## 依存関係

`pyproject.toml` に `httpx` を追加する。

```toml
dependencies = [
    "mcp[cli]>=1.28.1",
    "python-dotenv>=1.2.2",
    "httpx>=0.27.0",
]
```

## エラーハンドリング

- HTTPエラー（4xx/5xx）はエラーメッセージ文字列を返す
- タイムアウトはエラーメッセージ文字列を返す
- 例外はキャッチして文字列で返す（MCPツールがクラッシュしないよう）

## 実装スコープ外

- Google Custom Search API
- 検索結果ページからのURL抽出・各ページのフェッチ
- レート制限・リトライロジック
- プロキシ対応
