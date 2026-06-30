"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { ErrorMessage } from "@/components/ErrorMessage";
import { Pagination } from "@/components/Pagination";
import { getAdminEvaluations } from "@/lib/api";
import { getMe, getStoredToken } from "@/lib/auth";
import type { AIEvaluationListResponse } from "@/types/assistant";

const dateFormatter = new Intl.DateTimeFormat("ja-JP", {
  dateStyle: "short",
  timeStyle: "medium",
});

function valueOrDash(value: string | number | null) {
  return value === null || value === "" ? "-" : value;
}

export default function AdminEvaluationsPage() {
  const router = useRouter();
  const [evaluations, setEvaluations] = useState<AIEvaluationListResponse | null>(null);
  const [page, setPage] = useState(1);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    async function loadEvaluations() {
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
        const result = await getAdminEvaluations({ page, limit: 20 }, storedToken);
        if (isMounted) {
          setEvaluations(result);
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : "AI評価一覧の取得に失敗しました。");
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    loadEvaluations();

    return () => {
      isMounted = false;
    };
  }, [page, router]);

  return (
    <main className="page-shell wide">
      <section className="page-header">
        <p className="eyebrow">Admin evaluations</p>
        <h1>AI回答評価</h1>
      </section>

      <ErrorMessage message={error} />
      {isLoading ? <p className="section-panel">読み込み中</p> : null}

      {!isLoading && evaluations && !error ? (
        <>
          <section className="table-panel">
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>日時</th>
                    <th>user_id</th>
                    <th>質問</th>
                    <th>AI回答</th>
                    <th>rating</th>
                    <th>comment</th>
                  </tr>
                </thead>
                <tbody>
                  {evaluations.items.map((item) => (
                    <tr key={item.id}>
                      <td>{dateFormatter.format(new Date(item.created_at))}</td>
                      <td>{valueOrDash(item.user_id)}</td>
                      <td className="table-text-cell">{valueOrDash(item.question)}</td>
                      <td className="table-text-cell">{item.assistant_reply}</td>
                      <td>{item.rating}</td>
                      <td>{valueOrDash(item.comment)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
          <Pagination
            page={evaluations.page}
            limit={evaluations.limit}
            total={evaluations.total}
            hasNext={evaluations.has_next}
            onPageChange={setPage}
          />
        </>
      ) : null}
    </main>
  );
}
