import Link from "next/link";
import type { Product } from "@/types/product";

const priceFormatter = new Intl.NumberFormat("ja-JP", {
  style: "currency",
  currency: "JPY",
  maximumFractionDigits: 0,
});

type ProductCardProps = {
  product: Product;
  isAuthenticated?: boolean;
  isFavorite?: boolean;
  isFavoriteBusy?: boolean;
  onFavoriteToggle?: (product: Product) => void;
  onDetailClick?: (product: Product) => void;
};

export function ProductCard({
  product,
  isAuthenticated = false,
  isFavorite = false,
  isFavoriteBusy = false,
  onFavoriteToggle,
  onDetailClick,
}: ProductCardProps) {
  return (
    <article className="product-card">
      <div className="product-card-main">
        <p className="eyebrow">{product.category.name}</p>
        <h2>{product.name}</h2>
        <p className="muted">{product.brand ?? "ブランド未設定"}</p>
      </div>

      <dl className="product-stats">
        <div>
          <dt>価格</dt>
          <dd>{priceFormatter.format(product.price)}</dd>
        </div>
        <div>
          <dt>評価</dt>
          <dd>{product.rating ?? "-"}</dd>
        </div>
        <div>
          <dt>在庫</dt>
          <dd>{product.stock ?? "-"}</dd>
        </div>
      </dl>

      {product.tags.length > 0 ? (
        <div className="tag-list" aria-label="タグ">
          {product.tags.slice(0, 4).map((tag) => (
            <span className="tag" key={tag}>
              {tag}
            </span>
          ))}
        </div>
      ) : null}

      <div className="card-actions">
        {onFavoriteToggle ? (
          <button
            className={isFavorite ? "button button-secondary" : "button"}
            type="button"
            disabled={isFavoriteBusy}
            onClick={() => onFavoriteToggle(product)}
          >
            {isFavoriteBusy
              ? "処理中"
              : isFavorite
                ? "お気に入り解除"
                : isAuthenticated
                  ? "お気に入り"
                  : "ログインしてお気に入り"}
          </button>
        ) : null}
        <Link
          className="button button-secondary full-width"
          href={`/products/${product.id}`}
          onClick={() => onDetailClick?.(product)}
        >
          詳細を見る
        </Link>
      </div>
    </article>
  );
}
