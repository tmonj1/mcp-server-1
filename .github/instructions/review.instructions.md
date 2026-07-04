---
# Front matter: intended for the code-review agent only.
# Other agents should ignore this file.
agent: code-review
access: code-review-only
private: true
---

# Code Review — Minimal / Prototype Instructions

このファイルは Code Review エージェント向けの指示です。本プロジェクトはプロトタイプ開発のため、レビューは必要最小限に留めてください。

指示:
- 重要なバグ、セキュリティ脆弱性、クラッシュやデータ損失を招く問題のみ報告する
- 重大度は CRITICAL/HIGH/MEDIUM/LOW のいずれかで簡潔に付与する
- 推奨修正は短く一行で示す（差分作成は不要）
- スタイル、フォーマット、コメント文体、変数名の好みなどは無視する
- 1回のレビューで指摘は重大度の高い順に最大3件までとする
- レビューは日本語で書く
