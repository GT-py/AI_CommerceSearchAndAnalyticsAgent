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
