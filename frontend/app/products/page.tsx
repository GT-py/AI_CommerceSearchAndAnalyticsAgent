"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useMemo, useState } from "react";
import { ErrorMessage } from "@/components/ErrorMessage";
import { Pagination } from "@/components/Pagination";
import { ProductCard } from "@/components/ProductCard";
import { SearchForm } from "@/components/SearchForm";
import {
  addFavorite,
  buildQueryString,
  createClickLog,
  getCategories,
  getFavorites,
  getProducts,
  removeFavorite,
} from "@/lib/api";
import { getStoredToken } from "@/lib/auth";
import type { Category, Product, ProductListResponse, ProductQuery, ProductSort } from "@/types/product";

const sortValues = new Set(["price_asc", "price_desc", "rating_desc", "newest"]);

function numberParam(params: URLSearchParams, key: string) {
  const value = params.get(key);
  if (!value) {
    return undefined;
  }

  const parsed = Number(value);
  return Number.isNaN(parsed) ? undefined : parsed;
}

function parseQuery(params: URLSearchParams): ProductQuery {
  const sort = params.get("sort");
  return {
    keyword: params.get("keyword") ?? undefined,
    category_id: numberParam(params, "category_id"),
    min_price: numberParam(params, "min_price"),
    max_price: numberParam(params, "max_price"),
    sort: sort && sortValues.has(sort) ? (sort as ProductSort) : undefined,
    page: numberParam(params, "page") ?? 1,
    limit: numberParam(params, "limit") ?? 20,
  };
}

function ProductsContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const queryString = searchParams.toString();
  const query = useMemo(() => parseQuery(new URLSearchParams(queryString)), [queryString]);
  const [token, setToken] = useState<string | null>(null);
  const [categories, setCategories] = useState<Category[]>([]);
  const [products, setProducts] = useState<ProductListResponse | null>(null);
  const [favoriteIds, setFavoriteIds] = useState<Set<number>>(new Set());
  const [favoriteBusyIds, setFavoriteBusyIds] = useState<Set<number>>(new Set());
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    async function loadProducts() {
      const storedToken = getStoredToken();
      setToken(storedToken);
      setIsLoading(true);
      setError(null);

      try {
        const [categoryItems, productResult] = await Promise.all([
          getCategories(),
          getProducts(query, storedToken),
        ]);

        let nextFavoriteIds = new Set<number>();
        if (storedToken) {
          const favoriteResult = await getFavorites(storedToken);
          nextFavoriteIds = new Set(favoriteResult.items.map((item) => item.product.id));
        }

        if (isMounted) {
          setCategories(categoryItems);
          setProducts(productResult);
          setFavoriteIds(nextFavoriteIds);
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : "商品一覧の取得に失敗しました。");
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    loadProducts();

    return () => {
      isMounted = false;
    };
  }, [queryString, query]);

  function moveToQuery(nextQuery: ProductQuery) {
    router.push(`/products${buildQueryString(nextQuery)}`);
  }

  async function handleFavoriteToggle(product: Product) {
    if (!token) {
      setError("お気に入りにはログインが必要です。");
      return;
    }

    setFavoriteBusyIds((current) => new Set(current).add(product.id));
    setError(null);

    try {
      if (favoriteIds.has(product.id)) {
        await removeFavorite(product.id, token);
        setFavoriteIds((current) => {
          const next = new Set(current);
          next.delete(product.id);
          return next;
        });
      } else {
        await addFavorite(product.id, token);
        setFavoriteIds((current) => new Set(current).add(product.id));
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "お気に入り操作に失敗しました。");
    } finally {
      setFavoriteBusyIds((current) => {
        const next = new Set(current);
        next.delete(product.id);
        return next;
      });
    }
  }

  function handleDetailClick(product: Product) {
    void createClickLog(product.id, "search", token).catch(() => undefined);
  }

  return (
    <main className="page-shell">
      <section className="page-header with-actions">
        <div>
          <p className="eyebrow">Products</p>
          <h1>商品一覧</h1>
        </div>
        <Link className="button button-secondary" href="/login">
          ログインして検索
        </Link>
      </section>

      <section className="section-panel">
        <SearchForm categories={categories} initialQuery={query} isLoading={isLoading} onSearch={moveToQuery} />
      </section>

      <ErrorMessage message={error} />

      <section className="list-summary" aria-live="polite">
        {isLoading ? "読み込み中" : `${products?.total ?? 0}件の商品`}
      </section>

      <section className="product-grid">
        {products?.items.map((product) => (
          <ProductCard
            key={product.id}
            product={product}
            isAuthenticated={Boolean(token)}
            isFavorite={favoriteIds.has(product.id)}
            isFavoriteBusy={favoriteBusyIds.has(product.id)}
            onFavoriteToggle={handleFavoriteToggle}
            onDetailClick={handleDetailClick}
          />
        ))}
      </section>

      {!isLoading && products?.items.length === 0 ? <p className="empty-state">該当する商品がありません。</p> : null}

      {products ? (
        <Pagination
          page={products.page}
          limit={products.limit}
          total={products.total}
          hasNext={products.has_next}
          onPageChange={(page) => moveToQuery({ ...query, page })}
        />
      ) : null}
    </main>
  );
}

export default function ProductsPage() {
  return (
    <Suspense fallback={<main className="page-shell"><p>読み込み中</p></main>}>
      <ProductsContent />
    </Suspense>
  );
}
