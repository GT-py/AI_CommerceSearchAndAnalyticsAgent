# AI Commerce Search & Analytics Agent

## 概要
AI Commerce Search & Analytics Agent は，商品検索，お気に入り，ルールベースAIアシスタント，管理者分析ダッシュボードを備えたEC分析アプリです。
ユーザー行動ログを保存し，検索・クリック・AI回答評価を管理者が確認できる構成にしています。

## 作成目的
このアプリは，Web系エンジニアとして必要なフロントエンド，バックエンド，DB，認証，検索，テスト，CI/CD，ログ分析，AIアシスタント連携の基礎を一通り実践するために作成しました。

単なるCRUDアプリではなく，検索ログやクリックログを保存し，管理者が分析できるダッシュボード，AI回答評価，Text-to-SQL風分析，ETL / Feature生成まで含めることで，実サービスに近い構成を意識しています。

## デモURL
今後追加予定です。

## 主な機能
- ユーザー登録・ログイン・JWT認証
- user / admin ロールによる認可
- 商品検索（keyword, category, price, sort, paging）
- お気に入り登録・解除
- 検索ログ・クリックログ保存
- ルールベースAIアシスタント
- AI回答のgood/badフィードバック
- 管理者向け分析ダッシュボード
- Text-to-SQL風分析Agent
- ETLによる日次検索指標・商品特徴量生成

## 技術スタック
- Frontend: Next.js 15, React 19, TypeScript, App Router
- Backend: FastAPI, SQLAlchemy, Alembic, Pydantic
- Database: PostgreSQL 16
- Auth: JWT, passlib bcrypt
- Test: pytest, FastAPI TestClient
- Infra: Docker Compose, GitHub Actions

## アーキテクチャ
```text
Browser
  -> Next.js frontend
  -> FastAPI backend
  -> PostgreSQL

Logs / Feedback
  -> search_logs / click_logs / ai_response_feedback
  -> analytics API / SQL Agent / ETL
  -> daily_search_metrics / product_features
```

## ディレクトリ構成
```text
frontend/  Next.js App Router UI
backend/   FastAPI app, SQLAlchemy models, Alembic, tests
docker-compose.yml
.github/workflows/ci.yml
README.md
```

## データベース設計
主なテーブルは以下です。

- users
- categories
- products
- favorites
- search_logs
- click_logs
- ai_conversations
- ai_messages
- ai_response_feedback
- daily_search_metrics
- product_features

## セットアップ
```bash
cp .env.example .env
```

Docker Compose内では以下を使います。

```text
DATABASE_URL=postgresql+psycopg://app:password@db:5432/app_db
```

WSLローカルでbackendを直接起動する場合は以下です。

```text
DATABASE_URL=postgresql+psycopg://app:password@localhost:5432/app_db
```

## 起動方法
```bash
docker compose up --build
```

URL:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

## マイグレーション
```bash
docker compose exec backend alembic upgrade head
```

## seedデータ投入
```bash
docker compose exec backend python -m app.scripts.seed
```

期待値:
```text
Seed completed: users=2 categories=10 products=120
```

## 初期アカウント
管理者:
```text
admin@example.com / adminpass
```

一般ユーザー:
```text
user@example.com / userpass
```

## テスト
```bash
docker compose exec backend pytest
docker compose exec frontend npm run build
```

フロントエンドのlintはTypeScript型チェックとして実行します。

```bash
docker compose exec frontend npm run lint
```

## CI
GitHub Actionsでpush / pull_request時に以下を実行します。

- Backend: PostgreSQL service, alembic upgrade head, seed, pytest
- Frontend: npm ci, npm run lint, npm run build

## 主要API
- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`
- `GET /products`
- `GET /products/{product_id}`
- `POST /admin/products`
- `GET /favorites`
- `POST /logs/click`
- `POST /assistant/chat`
- `POST /assistant/feedback`
- `GET /admin/analytics/summary`
- `POST /admin/sql-agent/query`
- `POST /admin/etl/run`
- `GET /admin/metrics/daily-search`
- `GET /admin/features/products`

## 画面一覧
- `/login`
- `/register`
- `/products`
- `/products/[id]`
- `/favorites`
- `/assistant`
- `/admin/products`
- `/admin/analytics`
- `/admin/sql-agent`
- `/admin/search-logs`
- `/admin/click-logs`
- `/admin/evaluations`
- `/admin/metrics/daily-search`
- `/admin/features/products`

## 工夫した点
- Docker Composeでローカル再現性を高めた
- JWT認証とuser/adminロールで権限を分離した
- 商品検索にページング・絞り込み・並び替えを実装した
- 検索ログ・クリックログを保存し，分析に使える構成にした
- AIアシスタントはLLM APIに依存せず，まずルールベースで実装した
- AI回答にgood/badフィードバックを保存できるようにした
- Text-to-SQL風機能は自由SQL実行ではなく，安全なテンプレート方式にした
- pytestとGitHub Actionsで継続的に検証できるようにした

## セキュリティ上の配慮
- パスワードはハッシュ化して保存
- JWTで認証し，管理者APIはadminロールに制限
- Text-to-SQL風分析Agentは自由SQLを受け取らず，SELECT系の固定テンプレートのみ実行
- `.env` や秘密情報はコミット対象外
- 開発用フロント認証はlocalStorageにJWTを保存する最小構成です。本番運用ではHttpOnly Cookie等を検討します。

## 現在の制約
- AIアシスタントは現段階ではルールベースであり，本物のLLM APIは使っていない
- Text-to-SQL風分析は対応質問を限定したテンプレート方式である
- 商品データはポートフォリオ用の自作seedデータである
- product_featuresのview_count_7dは簡易実装としてclick_count_7dと同義にしている
- 本番レベルのセキュリティ・監視・スケーリングは今後の改善対象である

## 今後の改善
- PostgreSQL全文検索
- pgvectorによる類似検索
- OpenAI API等を用いたLLM連携
- LangChain / LangGraphによるAgent化
- Redisキャッシュ
- cursor pagination
- OpenTelemetryによるログ・メトリクス・トレース
- PlaywrightによるE2Eテスト
- Vercel / Render / Railway / Fly.io等へのデプロイ
