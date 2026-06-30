"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useMemo, useState } from "react";
import { ErrorMessage } from "@/components/ErrorMessage";
import { Pagination } from "@/components/Pagination";
import { ProductCard } from "@/components/ProductCard";
import { SearchForm } from "@/components/SearchForm";
import { buildQueryString, getCategories, getProducts } from "@/lib/api";
import { getStoredToken } from "@/lib/auth";
import type { Category, ProductListResponse, ProductQuery, ProductSort } from "@/types/product";

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
  const [categories, setCategories] = useState<Category[]>([]);
  const [products, setProducts] = useState<ProductListResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    async function loadProducts() {
      setIsLoading(true);
      setError(null);

      try {
        const [categoryItems, productResult] = await Promise.all([
          getCategories(),
          getProducts(query, getStoredToken()),
        ]);
        if (isMounted) {
          setCategories(categoryItems);
          setProducts(productResult);
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
        {products?.items.map((product) => <ProductCard key={product.id} product={product} />)}
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
