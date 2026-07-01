"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { ErrorMessage } from "@/components/ErrorMessage";
import { Pagination } from "@/components/Pagination";
import { getProductFeatures } from "@/lib/api";
import { getMe, getStoredToken } from "@/lib/auth";
import type { ProductFeatureListResponse } from "@/types/etl";

const percentFormatter = new Intl.NumberFormat("ja-JP", {
  maximumFractionDigits: 1,
  style: "percent",
});

export default function AdminProductFeaturesPage() {
  const router = useRouter();
  const [features, setFeatures] = useState<ProductFeatureListResponse | null>(null);
  const [page, setPage] = useState(1);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    async function loadFeatures() {
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
        const result = await getProductFeatures({ page, limit: 20 }, storedToken);
        if (isMounted) {
          setFeatures(result);
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : "商品特徴量の取得に失敗しました。");
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    loadFeatures();

    return () => {
      isMounted = false;
    };
  }, [page, router]);

  return (
    <main className="page-shell wide">
      <section className="page-header">
        <p className="eyebrow">Admin features</p>
        <h1>商品特徴量</h1>
      </section>

      <ErrorMessage message={error} />
      {isLoading ? <p className="section-panel">読み込み中</p> : null}

      {!isLoading && features && !error ? (
        <>
          <section className="table-panel">
            {features.items.length > 0 ? (
              <div className="table-scroll">
                <table>
                  <thead>
                    <tr>
                      <th>date</th>
                      <th>product_id</th>
                      <th>product_name</th>
                      <th>view_count_7d</th>
                      <th>click_count_7d</th>
                      <th>favorite_count_7d</th>
                      <th>ctr_7d</th>
                    </tr>
                  </thead>
                  <tbody>
                    {features.items.map((item) => (
                      <tr key={item.id}>
                        <td>{item.date}</td>
                        <td>{item.product_id}</td>
                        <td className="table-text-cell">{item.product_name}</td>
                        <td>{item.view_count_7d}</td>
                        <td>{item.click_count_7d}</td>
                        <td>{item.favorite_count_7d}</td>
                        <td>{percentFormatter.format(item.ctr_7d)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="empty-state">商品特徴量はまだありません。</p>
            )}
          </section>
          <Pagination
            page={features.page}
            limit={features.limit}
            total={features.total}
            hasNext={features.has_next}
            onPageChange={setPage}
          />
        </>
      ) : null}
    </main>
  );
}
