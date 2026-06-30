from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.admin_logs import router as admin_logs_router
from app.api.admin_products import router as admin_products_router
from app.api.categories import router as categories_router
from app.api.products import router as products_router
from app.api.auth import router as auth_router
from app.api.debug import router as debug_router
from app.api.favorites import router as favorites_router
from app.api.health import router as health_router
from app.api.logs import router as logs_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Commerce Search & Analytics Agent",
        description="商品検索AIアシスタント付きEC分析アプリ",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(categories_router)
    app.include_router(favorites_router)
    app.include_router(logs_router)
    app.include_router(admin_products_router)
    app.include_router(admin_logs_router)
    app.include_router(products_router)
    app.include_router(debug_router)

    return app


app = create_app()
