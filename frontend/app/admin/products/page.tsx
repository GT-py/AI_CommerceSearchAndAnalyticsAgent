"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { ErrorMessage } from "@/components/ErrorMessage";
import { deleteProduct, getProducts } from "@/lib/api";
import { getMe, getStoredToken } from "@/lib/auth";
import type { Product } from "@/types/product";

const priceFormatter = new Intl.NumberFormat("ja-JP", {
  style: "currency",
  currency: "JPY",
  maximumFractionDigits: 0,
});

export default function AdminProductsPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  useEffect(() => {
    let isMounted = true;

    async function loadAdminProducts() {
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

        const result = await getProducts({ page: 1, limit: 100 }, storedToken);
        if (isMounted) {
          setToken(storedToken);
          setProducts(result.items);
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : "管理者商品一覧の取得に失敗しました。");
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    loadAdminProducts();

    return () => {
      isMounted = false;
    };
  }, [router]);

  async function handleDelete(product: Product) {
    if (!token) {
      setError("ログインしてください。");
      return;
    }

    const confirmed = window.confirm(`${product.name} を削除しますか？`);
    if (!confirmed) {
      return;
    }

    setDeletingId(product.id);
    setError(null);

    try {
      await deleteProduct(product.id, token);
      setProducts((current) => current.filter((item) => item.id !== product.id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "商品の削除に失敗しました。");
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <main className="page-shell wide">
      <section className="page-header with-actions">
        <div>
          <p className="eyebrow">Admin</p>
          <h1>管理者商品管理</h1>
        </div>
        <Link className="button" href="/admin/products/new">
          商品を作成
        </Link>
      </section>

      <ErrorMessage message={error} />
      {isLoading ? <p className="section-panel">読み込み中</p> : null}

      {!isLoading && !error ? (
        <section className="table-panel" aria-label="管理者商品一覧">
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>商品名</th>
                  <th>カテゴリ</th>
                  <th>価格</th>
                  <th>在庫</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                {products.map((product) => (
                  <tr key={product.id}>
                    <td>{product.name}</td>
                    <td>{product.category.name}</td>
                    <td>{priceFormatter.format(product.price)}</td>
                    <td>{product.stock ?? "-"}</td>
                    <td>
                      <div className="row-actions">
                        <Link className="button button-secondary" href={`/admin/products/${product.id}/edit`}>
                          編集
                        </Link>
                        <button
                          className="button button-danger"
                          type="button"
                          disabled={deletingId === product.id}
                          onClick={() => handleDelete(product)}
                        >
                          {deletingId === product.id ? "削除中" : "削除"}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      ) : null}
    </main>
  );
}
