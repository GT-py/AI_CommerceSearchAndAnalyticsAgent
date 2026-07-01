"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { ErrorMessage } from "@/components/ErrorMessage";
import { Pagination } from "@/components/Pagination";
import { getDailySearchMetrics } from "@/lib/api";
import { getMe, getStoredToken } from "@/lib/auth";
import type { DailySearchMetricListResponse } from "@/types/etl";

const percentFormatter = new Intl.NumberFormat("ja-JP", {
  maximumFractionDigits: 1,
  style: "percent",
});

export default function AdminDailySearchMetricsPage() {
  const router = useRouter();
  const [metrics, setMetrics] = useState<DailySearchMetricListResponse | null>(null);
  const [page, setPage] = useState(1);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    async function loadMetrics() {
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
        const result = await getDailySearchMetrics({ page, limit: 20 }, storedToken);
        if (isMounted) {
          setMetrics(result);
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : "日次検索指標の取得に失敗しました。");
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    loadMetrics();

    return () => {
      isMounted = false;
    };
  }, [page, router]);

  return (
    <main className="page-shell wide">
      <section className="page-header">
        <p className="eyebrow">Admin metrics</p>
        <h1>日次検索指標</h1>
      </section>

      <ErrorMessage message={error} />
      {isLoading ? <p className="section-panel">読み込み中</p> : null}

      {!isLoading && metrics && !error ? (
        <>
          <section className="table-panel">
            {metrics.items.length > 0 ? (
              <div className="table-scroll">
                <table>
                  <thead>
                    <tr>
                      <th>date</th>
                      <th>keyword</th>
                      <th>search_count</th>
                      <th>click_count</th>
                      <th>ctr</th>
                    </tr>
                  </thead>
                  <tbody>
                    {metrics.items.map((item) => (
                      <tr key={item.id}>
                        <td>{item.date}</td>
                        <td>{item.keyword}</td>
                        <td>{item.search_count}</td>
                        <td>{item.click_count}</td>
                        <td>{percentFormatter.format(item.ctr)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="empty-state">日次検索指標はまだありません。</p>
            )}
          </section>
          <Pagination
            page={metrics.page}
            limit={metrics.limit}
            total={metrics.total}
            hasNext={metrics.has_next}
            onPageChange={setPage}
          />
        </>
      ) : null}
    </main>
  );
}
