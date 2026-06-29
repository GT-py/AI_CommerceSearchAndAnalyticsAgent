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
