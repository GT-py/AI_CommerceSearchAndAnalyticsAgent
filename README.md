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
