"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { ErrorMessage } from "@/components/ErrorMessage";
import { getProduct } from "@/lib/api";
import type { Product } from "@/types/product";

const priceFormatter = new Intl.NumberFormat("ja-JP", {
  style: "currency",
  currency: "JPY",
  maximumFractionDigits: 0,
});

function valueOrDash(value: string | number | null) {
  return value === null || value === "" ? "-" : value;
}

export default function ProductDetailPage() {
  const params = useParams<{ id: string }>();
  const productId = Number(params.id);
  const [product, setProduct] = useState<Product | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    async function loadProduct() {
      setIsLoading(true);
      setError(null);

      try {
        const result = await getProduct(productId);
        if (isMounted) {
          setProduct(result);
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : "商品詳細の取得に失敗しました。");
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    if (Number.isNaN(productId)) {
      setError("商品IDが不正です。");
      setIsLoading(false);
      return;
    }

    loadProduct();

    return () => {
      isMounted = false;
    };
  }, [productId]);

  return (
    <main className="page-shell">
      <div className="page-header with-actions">
        <div>
          <p className="eyebrow">Product detail</p>
          <h1>{product?.name ?? "商品詳細"}</h1>
        </div>
        <Link className="button button-secondary" href="/products">
          一覧へ戻る
        </Link>
      </div>

      <ErrorMessage message={error} />
      {isLoading ? <p className="section-panel">読み込み中</p> : null}

      {product ? (
        <section className="detail-layout">
          <div className="section-panel detail-main">
            <p className="eyebrow">{product.category.name}</p>
            <h2>{product.name}</h2>
            <p className="description-text">{product.description}</p>
            {product.tags.length > 0 ? (
              <div className="tag-list">
                {product.tags.map((tag) => (
                  <span className="tag" key={tag}>
                    {tag}
                  </span>
                ))}
              </div>
            ) : null}
          </div>

          <aside className="section-panel">
            <dl className="detail-list">
              <div>
                <dt>ブランド</dt>
                <dd>{product.brand ?? "-"}</dd>
              </div>
              <div>
                <dt>価格</dt>
                <dd>{priceFormatter.format(product.price)}</dd>
              </div>
              <div>
                <dt>評価</dt>
                <dd>{valueOrDash(product.rating)}</dd>
              </div>
              <div>
                <dt>在庫</dt>
                <dd>{valueOrDash(product.stock)}</dd>
              </div>
              <div>
                <dt>重量</dt>
                <dd>{product.weight_g ? `${product.weight_g}g` : "-"}</dd>
              </div>
              <div>
                <dt>バッテリー</dt>
                <dd>{product.battery_hours ? `${product.battery_hours}時間` : "-"}</dd>
              </div>
              <div>
                <dt>画面サイズ</dt>
                <dd>{product.screen_size ? `${product.screen_size}インチ` : "-"}</dd>
              </div>
              <div>
                <dt>メモリ</dt>
                <dd>{product.memory_gb ? `${product.memory_gb}GB` : "-"}</dd>
              </div>
              <div>
                <dt>ストレージ</dt>
                <dd>{product.storage_gb ? `${product.storage_gb}GB` : "-"}</dd>
              </div>
            </dl>
          </aside>
        </section>
      ) : null}
    </main>
  );
}
