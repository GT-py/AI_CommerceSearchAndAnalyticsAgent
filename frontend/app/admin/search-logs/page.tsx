"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { ErrorMessage } from "@/components/ErrorMessage";
import { Pagination } from "@/components/Pagination";
import { getAdminSearchLogs } from "@/lib/api";
import { getMe, getStoredToken } from "@/lib/auth";
import type { SearchLogListResponse } from "@/types/log";

const dateFormatter = new Intl.DateTimeFormat("ja-JP", {
  dateStyle: "short",
  timeStyle: "medium",
});

function valueOrDash(value: string | number | null) {
  return value === null || value === "" ? "-" : value;
}

export default function AdminSearchLogsPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [logs, setLogs] = useState<SearchLogListResponse | null>(null);
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

      setToken(storedToken);
      setIsLoading(true);
      setError(null);

      try {
        const currentUser = await getMe(storedToken);
        if (currentUser.role !== "admin") {
          throw new Error("管理者権限が必要です。");
        }
        const result = await getAdminSearchLogs({ page, limit: 20 }, storedToken);
        if (isMounted) {
          setLogs(result);
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : "検索ログの取得に失敗しました。");
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
        <h1>検索ログ</h1>
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
                    <th>keyword</th>
                    <th>category_id</th>
                    <th>min_price</th>
                    <th>max_price</th>
                    <th>sort</th>
                    <th>page</th>
                    <th>limit</th>
                    <th>result_count</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.items.map((log) => (
                    <tr key={log.id}>
                      <td>{dateFormatter.format(new Date(log.created_at))}</td>
                      <td>{valueOrDash(log.user_id)}</td>
                      <td>{valueOrDash(log.keyword)}</td>
                      <td>{valueOrDash(log.category_id)}</td>
                      <td>{valueOrDash(log.min_price)}</td>
                      <td>{valueOrDash(log.max_price)}</td>
                      <td>{valueOrDash(log.sort)}</td>
                      <td>{log.page}</td>
                      <td>{log.limit}</td>
                      <td>{log.result_count}</td>
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
