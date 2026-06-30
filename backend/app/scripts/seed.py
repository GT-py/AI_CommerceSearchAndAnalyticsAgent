from __future__ import annotations

from dataclasses import dataclass

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.category import Category
from app.models.product import Product
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@dataclass(frozen=True)
class CategorySeed:
    name: str
    slug: str


CATEGORIES = [
    CategorySeed("ノートPC", "notebook-pc"),
    CategorySeed("スマートフォン", "smartphone"),
    CategorySeed("タブレット", "tablet"),
    CategorySeed("イヤホン", "earphones"),
    CategorySeed("モニター", "monitor"),
    CategorySeed("キーボード", "keyboard"),
    CategorySeed("マウス", "mouse"),
    CategorySeed("デスクチェア", "desk-chair"),
    CategorySeed("書籍", "books"),
    CategorySeed("生活家電", "home-appliances"),
]

PRODUCT_TEMPLATES = {
    "notebook-pc": {
        "names": ["Campus LiteBook", "Creator ProBook", "Business Air", "Study Mate"],
        "brands": ["TechNova", "Aster", "NorthPeak"],
        "price_base": 79800,
        "tags": ["軽量", "長時間バッテリー", "レポート作成", "オンライン授業"],
    },
    "smartphone": {
        "names": ["Pocket One", "Photo Max", "Daily Phone", "Travel Mini"],
        "brands": ["MiraMobile", "TechNova", "BlueArc"],
        "price_base": 39800,
        "tags": ["カメラ", "普段使い", "防水", "高速充電"],
    },
    "tablet": {
        "names": ["Canvas Tab", "Reader Pad", "Sketch Slate", "Study Tab"],
        "brands": ["Aster", "InkWorks", "TechNova"],
        "price_base": 44800,
        "tags": ["ノート整理", "動画視聴", "電子書籍", "ペン対応"],
    },
    "earphones": {
        "names": ["Quiet Buds", "Focus Pods", "Run Sound", "Clear Talk"],
        "brands": ["SoundLeaf", "BlueArc", "MiraMobile"],
        "price_base": 9800,
        "tags": ["ノイズキャンセル", "通勤", "オンライン会議", "軽量"],
    },
    "monitor": {
        "names": ["WorkView", "Color Canvas", "Wide Desk", "EyeCare Display"],
        "brands": ["NorthPeak", "Aster", "ViewPort"],
        "price_base": 24800,
        "tags": ["在宅勤務", "目に優しい", "省スペース", "高解像度"],
    },
    "keyboard": {
        "names": ["TypeFlow", "Silent Keys", "CodeBoard", "Compact Type"],
        "brands": ["KeySmith", "TechNova", "NorthPeak"],
        "price_base": 6800,
        "tags": ["静音", "プログラミング", "省スペース", "長時間入力"],
    },
    "mouse": {
        "names": ["Grip Mouse", "Silent Click", "Travel Mouse", "Precision Pointer"],
        "brands": ["KeySmith", "BlueArc", "NorthPeak"],
        "price_base": 3600,
        "tags": ["静音", "持ち運び", "作業効率", "手に馴染む"],
    },
    "desk-chair": {
        "names": ["Posture Chair", "Study Seat", "Work Comfort", "Mesh Support"],
        "brands": ["ChairLab", "NorthPeak", "RoomFit"],
        "price_base": 16800,
        "tags": ["姿勢サポート", "在宅勤務", "長時間作業", "通気性"],
    },
    "books": {
        "names": ["はじめてのデータ分析", "Web API設計入門", "SQL実践ノート", "就活ポートフォリオ講座"],
        "brands": ["TechBooks", "DataPress", "CareerLab"],
        "price_base": 1800,
        "tags": ["学習", "エンジニア就活", "実践", "入門"],
    },
    "home-appliances": {
        "names": ["Smart Kettle", "Clean Air Mini", "Compact Cooker", "Desk Fan"],
        "brands": ["LifeNova", "RoomFit", "Aster"],
        "price_base": 5200,
        "tags": ["一人暮らし", "時短", "省スペース", "毎日使える"],
    },
}


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def upsert_user(db: Session, email: str, password: str, role: str) -> User:
    user = db.scalar(select(User).where(User.email == email))
    if user is None:
        user = User(email=email, hashed_password=hash_password(password), role=role)
        db.add(user)
    else:
        user.role = role
    return user


def upsert_categories(db: Session) -> dict[str, Category]:
    categories: dict[str, Category] = {}
    for item in CATEGORIES:
        category = db.scalar(select(Category).where(Category.slug == item.slug))
        if category is None:
            category = Category(name=item.name, slug=item.slug)
            db.add(category)
            db.flush()
        else:
            category.name = item.name
        categories[item.slug] = category
    return categories


def build_products(categories: dict[str, Category]) -> list[dict]:
    products: list[dict] = []
    for category_seed in CATEGORIES:
        template = PRODUCT_TEMPLATES[category_seed.slug]
        for index in range(12):
            series = template["names"][index % len(template["names"])]
            brand = template["brands"][index % len(template["brands"])]
            price = template["price_base"] + index * 3200 + (index % 3) * 700
            rating = round(3.8 + (index % 7) * 0.15, 1)
            stock = 8 + (index * 5) % 45
            tags = template["tags"] + [category_seed.name, f"モデル{index + 1}"]
            name = f"{series} {index + 1:02d}"
            description = f"{category_seed.name}カテゴリの{name}です。日常利用と比較検討に使いやすい特徴量を持つ商品データです。"

            product = {
                "name": name,
                "description": description,
                "category_id": categories[category_seed.slug].id,
                "brand": brand,
                "price": price,
                "rating": rating,
                "stock": stock,
                "tags": tags,
            }

            if category_seed.slug in {"notebook-pc", "tablet"}:
                product.update(
                    {
                        "weight_g": 820 + index * 65,
                        "battery_hours": 8 + index % 9,
                        "screen_size": 11.0 + (index % 6) * 0.7,
                        "memory_gb": [8, 16, 16, 32][index % 4],
                        "storage_gb": [256, 512, 512, 1024][index % 4],
                    }
                )
            elif category_seed.slug == "smartphone":
                product.update(
                    {
                        "weight_g": 150 + index * 4,
                        "battery_hours": 18 + index % 10,
                        "screen_size": 5.8 + (index % 5) * 0.25,
                        "memory_gb": [6, 8, 12][index % 3],
                        "storage_gb": [128, 256, 512][index % 3],
                    }
                )
            elif category_seed.slug == "monitor":
                product.update(
                    {
                        "weight_g": 2600 + index * 210,
                        "screen_size": [23.8, 24.0, 27.0, 31.5][index % 4],
                    }
                )
            elif category_seed.slug in {"earphones", "keyboard", "mouse"}:
                product.update(
                    {
                        "weight_g": 45 + index * 18,
                        "battery_hours": 6 + index % 20,
                    }
                )
            elif category_seed.slug == "desk-chair":
                product.update({"weight_g": 7200 + index * 340})
            elif category_seed.slug == "books":
                product.update({"weight_g": 320 + index * 25})
            else:
                product.update({"weight_g": 900 + index * 110})

            products.append(product)
    return products


def upsert_products(db: Session, categories: dict[str, Category]) -> int:
    count = 0
    for product_data in build_products(categories):
        product = db.scalar(
            select(Product).where(
                Product.name == product_data["name"],
                Product.category_id == product_data["category_id"],
            )
        )
        if product is None:
            product = Product(**product_data)
            db.add(product)
        else:
            for key, value in product_data.items():
                setattr(product, key, value)
        count += 1
    return count


def run() -> None:
    with SessionLocal() as db:
        upsert_user(db, "admin@example.com", "adminpass", "admin")
        upsert_user(db, "user@example.com", "userpass", "user")
        categories = upsert_categories(db)
        product_count = upsert_products(db, categories)
        db.commit()

    print(f"Seed completed: users=2 categories={len(CATEGORIES)} products={product_count}")


if __name__ == "__main__":
    run()
