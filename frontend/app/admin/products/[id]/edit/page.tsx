"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { ErrorMessage } from "@/components/ErrorMessage";
import { ProductForm } from "@/components/ProductForm";
import { getCategories, getProduct, updateProduct } from "@/lib/api";
import { getMe, getStoredToken } from "@/lib/auth";
import type { Category, Product, ProductPayload } from "@/types/product";

export default function EditAdminProductPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const productId = Number(params.id);
  const [token, setToken] = useState<string | null>(null);
  const [categories, setCategories] = useState<Category[]>([]);
  const [product, setProduct] = useState<Product | undefined>();
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    let isMounted = true;

    async function loadFormData() {
      const storedToken = getStoredToken();
      if (!storedToken) {
        router.push("/login");
        return;
      }

      if (Number.isNaN(productId)) {
        setError("商品IDが不正です。");
        setIsLoading(false);
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        const currentUser = await getMe(storedToken);
        if (currentUser.role !== "admin") {
          throw new Error("管理者権限が必要です。");
        }

        const [categoryItems, productDetail] = await Promise.all([getCategories(), getProduct(productId)]);
        if (isMounted) {
          setToken(storedToken);
          setCategories(categoryItems);
          setProduct(productDetail);
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : "商品編集画面の準備に失敗しました。");
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    loadFormData();

    return () => {
      isMounted = false;
    };
  }, [productId, router]);

  async function handleSubmit(payload: ProductPayload) {
    if (!token) {
      setError("ログインしてください。");
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      await updateProduct(productId, payload, token);
      router.push("/admin/products");
    } catch (err) {
      setError(err instanceof Error ? err.message : "商品の更新に失敗しました。");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="page-shell">
      <section className="page-header with-actions">
        <div>
          <p className="eyebrow">Admin</p>
          <h1>商品編集</h1>
        </div>
        <Link className="button button-secondary" href="/admin/products">
          管理一覧へ戻る
        </Link>
      </section>

      {isLoading ? <p className="section-panel">読み込み中</p> : null}
      {!isLoading && error && !product ? <ErrorMessage message={error} /> : null}
      {!isLoading && product && token ? (
        <ProductForm
          categories={categories}
          initialProduct={product}
          submitLabel="更新する"
          isSubmitting={isSubmitting}
          error={error}
          onSubmit={handleSubmit}
        />
      ) : null}
    </main>
  );
}
