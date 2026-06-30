"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { ErrorMessage } from "@/components/ErrorMessage";
import { ProductCard } from "@/components/ProductCard";
import { createClickLog, getFavorites, removeFavorite } from "@/lib/api";
import { getStoredToken } from "@/lib/auth";
import type { FavoriteItem } from "@/types/log";
import type { Product } from "@/types/product";

export default function FavoritesPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [items, setItems] = useState<FavoriteItem[]>([]);
  const [busyIds, setBusyIds] = useState<Set<number>>(new Set());
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    async function loadFavorites() {
      const storedToken = getStoredToken();
      if (!storedToken) {
        router.push("/login");
        return;
      }

      setToken(storedToken);
      setIsLoading(true);
      setError(null);

      try {
        const result = await getFavorites(storedToken);
        if (isMounted) {
          setItems(result.items);
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : "お気に入り一覧の取得に失敗しました。");
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    loadFavorites();

    return () => {
      isMounted = false;
    };
  }, [router]);

  async function handleRemove(product: Product) {
    if (!token) {
      setError("ログインしてください。");
      return;
    }

    setBusyIds((current) => new Set(current).add(product.id));
    setError(null);

    try {
      await removeFavorite(product.id, token);
      setItems((current) => current.filter((item) => item.product.id !== product.id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "お気に入り解除に失敗しました。");
    } finally {
      setBusyIds((current) => {
        const next = new Set(current);
        next.delete(product.id);
        return next;
      });
    }
  }

  function handleDetailClick(product: Product) {
    void createClickLog(product.id, "favorite", token).catch(() => undefined);
  }

  return (
    <main className="page-shell">
      <section className="page-header">
        <p className="eyebrow">Favorites</p>
        <h1>お気に入り</h1>
      </section>

      <ErrorMessage message={error} />
      {isLoading ? <p className="section-panel">読み込み中</p> : null}
      {!isLoading && items.length === 0 ? <p className="empty-state">お気に入りはまだありません。</p> : null}

      <section className="product-grid">
        {items.map((item) => (
          <ProductCard
            key={item.id}
            product={item.product}
            isAuthenticated={Boolean(token)}
            isFavorite
            isFavoriteBusy={busyIds.has(item.product.id)}
            onFavoriteToggle={handleRemove}
            onDetailClick={handleDetailClick}
          />
        ))}
      </section>
    </main>
  );
}
