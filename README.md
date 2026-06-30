# AI Commerce Search & Analytics Agent

## 概要
商品検索AIアシスタント付きEC分析アプリ

## 起動方法
```bash
docker compose up --build
```

## URL
Frontend: http://localhost:3000

Backend: http://localhost:8000

API Docs: http://localhost:8000/docs

## 現在実装済み
- Docker Compose
- FastAPI health check
- Next.jsトップページ
- PostgreSQL起動

## 開発メモ
- Docker build context削減のため，frontend/backendに.dockerignoreを配置

## DATABASE_URLの使い分け
Docker Compose内:
```text
DATABASE_URL=postgresql+psycopg://app:password@db:5432/app_db
```

WSLローカルでbackendを直接起動する場合:
```text
DATABASE_URL=postgresql+psycopg://app:password@localhost:5432/app_db
```

## DBマイグレーション
```bash
docker compose exec backend alembic upgrade head
```

## seed投入
```bash
docker compose exec backend python -m app.scripts.seed
```

seed投入後の件数確認:
```bash
docker compose exec backend python -m app.scripts.seed
```

期待値:
```text
Seed completed: users=2 categories=10 products=120
```

## 初期ユーザー
管理者:
admin@example.com / adminpass

一般ユーザー:
user@example.com / userpass

## 開発確認用API
`GET /debug/db` はDB接続確認用の開発向けエンドポイントです。

## 認証
- JWT認証
- user / admin ロール
- 初期管理者: admin@example.com / adminpass
- 初期一般ユーザー: user@example.com / userpass
- `POST /auth/logout` はサーバ側でトークンを無効化しない最小実装です。実際のトークン削除はフロントエンド側で行います。

## API確認例
ログイン:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"userpass"}'
```

ログイン中ユーザー取得:
```bash
TOKEN="<ログインで取得したaccess_token>"
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer ${TOKEN}"
```

## 商品API
- GET /products
- GET /products/{product_id}
- POST /admin/products
- PATCH /admin/products/{product_id}
- DELETE /admin/products/{product_id}

## 検索機能
- keyword
- category_id
- min_price / max_price
- sort
- page / limit

## 検索ログ
商品検索時に search_logs へ検索条件と結果件数を保存する。result_count は検索条件に一致した総件数。

## 画面
- /login
- /register
- /products
- /products/[id]
- /favorites
- /assistant
- /admin/products
- /admin/products/new
- /admin/products/[id]/edit
- /admin/search-logs
- /admin/click-logs
- /admin/evaluations

## フロントエンド認証
開発用としてlocalStorageにJWTを保存する。
本番運用ではHttpOnly Cookie等を検討する。

## お気に入り機能
- ログインユーザーは商品をお気に入り登録できる
- /favorites でお気に入り一覧を確認できる

## ログ機能
- 商品検索時に search_logs を保存
- 商品詳細クリック時に click_logs を保存
- 管理者は /admin/search-logs と /admin/click-logs で確認可能

## AIアシスタント
- ルールベースで自然文から条件を抽出
- 商品検索ロジックを呼び出して推薦
- 推薦理由を生成
- 会話履歴を保存
- AI回答にgood/badフィードバック可能

## 設計方針
現段階ではLLM APIに依存しない。
後からOpenAI APIやLangChainに差し替えられるよう、条件抽出・商品検索・回答生成を分離している。

## 管理者分析ダッシュボード

/admin/analytics で以下を確認できる。

- 全体サマリー
- 検索キーワード集計
- 商品別クリック数
- お気に入り数
- AI回答評価
- badフィードバック

検索ログ・クリックログ・AI回答評価を保存し，サービス改善に利用できる構成にしている。
