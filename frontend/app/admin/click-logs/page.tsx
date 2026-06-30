"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { ErrorMessage } from "@/components/ErrorMessage";
import { Pagination } from "@/components/Pagination";
import { getAdminClickLogs } from "@/lib/api";
import { getMe, getStoredToken } from "@/lib/auth";
import type { ClickLogListResponse } from "@/types/log";

const dateFormatter = new Intl.DateTimeFormat("ja-JP", {
  dateStyle: "short",
  timeStyle: "medium",
});

function valueOrDash(value: string | number | null) {
  return value === null || value === "" ? "-" : value;
}

export default function AdminClickLogsPage() {
  const router = useRouter();
  const [logs, setLogs] = useState<ClickLogListResponse | null>(null);
  const [page, setPage] = useState(1);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    async function loadLogs() {
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
        const result = await getAdminClickLogs({ page, limit: 20 }, storedToken);
        if (isMounted) {
          setLogs(result);
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : "クリックログの取得に失敗しました。");
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    loadLogs();

    return () => {
      isMounted = false;
    };
  }, [page, router]);

  return (
    <main className="page-shell wide">
      <section className="page-header">
        <p className="eyebrow">Admin logs</p>
        <h1>クリックログ</h1>
      </section>

      <ErrorMessage message={error} />
      {isLoading ? <p className="section-panel">読み込み中</p> : null}

      {!isLoading && logs && !error ? (
        <>
          <section className="table-panel">
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>日時</th>
                    <th>user_id</th>
                    <th>product_id</th>
                    <th>商品名</th>
                    <th>source</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.items.map((log) => (
                    <tr key={log.id}>
                      <td>{dateFormatter.format(new Date(log.created_at))}</td>
                      <td>{valueOrDash(log.user_id)}</td>
                      <td>{log.product_id}</td>
                      <td>{log.product.name}</td>
                      <td>{log.source}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
          <Pagination
            page={logs.page}
            limit={logs.limit}
            total={logs.total}
            hasNext={logs.has_next}
            onPageChange={setPage}
          />
        </>
      ) : null}
    </main>
  );
}
