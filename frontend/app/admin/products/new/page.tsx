"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { ErrorMessage } from "@/components/ErrorMessage";
import { ProductForm } from "@/components/ProductForm";
import { createProduct, getCategories } from "@/lib/api";
import { getMe, getStoredToken } from "@/lib/auth";
import type { Category, ProductPayload } from "@/types/product";

export default function NewAdminProductPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [categories, setCategories] = useState<Category[]>([]);
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

      setIsLoading(true);
      setError(null);

      try {
        const currentUser = await getMe(storedToken);
        if (currentUser.role !== "admin") {
          throw new Error("管理者権限が必要です。");
        }

        const categoryItems = await getCategories();
        if (isMounted) {
          setToken(storedToken);
          setCategories(categoryItems);
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : "商品作成画面の準備に失敗しました。");
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
  }, [router]);

  async function handleSubmit(payload: ProductPayload) {
    if (!token) {
      setError("ログインしてください。");
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      await createProduct(payload, token);
      router.push("/admin/products");
    } catch (err) {
      setError(err instanceof Error ? err.message : "商品の作成に失敗しました。");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="page-shell">
      <section className="page-header with-actions">
        <div>
          <p className="eyebrow">Admin</p>
          <h1>商品作成</h1>
        </div>
        <Link className="button button-secondary" href="/admin/products">
          管理一覧へ戻る
        </Link>
      </section>

      {isLoading ? <p className="section-panel">読み込み中</p> : null}
      {!isLoading && error && token === null ? <ErrorMessage message={error} /> : null}
      {!isLoading && token ? (
        <ProductForm
          categories={categories}
          submitLabel="作成する"
          isSubmitting={isSubmitting}
          error={error}
          onSubmit={handleSubmit}
        />
      ) : null}
    </main>
  );
}
