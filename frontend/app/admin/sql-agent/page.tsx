"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";
import { ErrorMessage } from "@/components/ErrorMessage";
import { querySqlAgent } from "@/lib/api";
import { getMe, getStoredToken } from "@/lib/auth";
import type { SQLAgentQueryResponse } from "@/types/sqlAgent";

const sampleQuestions = [
  "今月，最も検索されたキーワードは？",
  "クリック率が高い商品を上位10件出して",
  "検索されたがクリックされなかったキーワードを教えて",
  "カテゴリ別の検索回数を教えて",
  "AI回答で不満が多いものを見たい",
];

function formatCell(value: string | number | null) {
  if (value === null || value === "") {
    return "-";
  }
  return value;
}

export default function AdminSqlAgentPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [question, setQuestion] = useState(sampleQuestions[0]);
  const [result, setResult] = useState<SQLAgentQueryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    let isMounted = true;

    async function checkAdmin() {
      const storedToken = getStoredToken();
      if (!storedToken) {
        router.push("/login");
        return;
      }

      try {
        const currentUser = await getMe(storedToken);
        if (currentUser.role !== "admin") {
          throw new Error("管理者権限が必要です。");
        }
        if (isMounted) {
          setToken(storedToken);
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : "認証確認に失敗しました。");
        }
      } finally {
        if (isMounted) {
          setIsCheckingAuth(false);
        }
      }
    }

    checkAdmin();

    return () => {
      isMounted = false;
    };
  }, [router]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !question.trim()) {
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const response = await querySqlAgent({ question }, token);
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "分析Agentの実行に失敗しました。");
    } finally {
      setIsSubmitting(false);
    }
  }

  function applyQuestion(value: string) {
    setQuestion(value);
    setResult(null);
  }

  return (
    <main className="page-shell wide">
      <section className="page-header">
        <p className="eyebrow">Admin SQL Agent</p>
        <h1>Text-to-SQL風分析Agent</h1>
      </section>

      <ErrorMessage message={error} />
      {isCheckingAuth ? <p className="section-panel">読み込み中</p> : null}

      {!isCheckingAuth ? (
        <div className="analytics-sections">
          <section className="form-panel">
            <form className="assistant-form" onSubmit={handleSubmit}>
              <label className="field">
                <span>分析したい質問</span>
                <textarea
                  rows={4}
                  value={question}
                  onChange={(event) => setQuestion(event.target.value)}
                  placeholder="今月，最も検索されたキーワードは？"
                />
              </label>
              <div className="form-actions">
                <button className="button" type="submit" disabled={isSubmitting || !token}>
                  {isSubmitting ? "実行中" : "実行"}
                </button>
              </div>
            </form>

            <div className="sample-question-list" aria-label="Sample questions">
              {sampleQuestions.map((sample) => (
                <button
                  className="button button-secondary"
                  key={sample}
                  type="button"
                  onClick={() => applyQuestion(sample)}
                >
                  {sample}
                </button>
              ))}
            </div>
          </section>

          {result ? (
            <section className="table-panel">
              <h2 className="section-title">実行結果</h2>
              <dl className="detail-list compact-list">
                <div>
                  <dt>intent</dt>
                  <dd>{result.intent}</dd>
                </div>
                <div>
                  <dt>description</dt>
                  <dd>{result.description}</dd>
                </div>
              </dl>

              {result.suggestions.length > 0 ? (
                <div className="conditions-panel top-gap">
                  <h3 className="section-title">suggestions</h3>
                  <div className="sample-question-list">
                    {result.suggestions.map((suggestion) => (
                      <button
                        className="button button-secondary"
                        key={suggestion}
                        type="button"
                        onClick={() => applyQuestion(suggestion)}
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                </div>
              ) : null}

              {result.columns.length > 0 ? (
                <div className="table-scroll top-gap">
                  <table>
                    <thead>
                      <tr>
                        {result.columns.map((column) => (
                          <th key={column}>{column}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {result.rows.map((row, rowIndex) => (
                        <tr key={`${result.intent}-${rowIndex}`}>
                          {row.map((cell, cellIndex) => (
                            <td className="table-text-cell" key={`${result.intent}-${rowIndex}-${cellIndex}`}>
                              {formatCell(cell)}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : null}

              {result.columns.length > 0 && result.rows.length === 0 ? (
                <p className="empty-state top-gap">表示できる結果がありません。</p>
              ) : null}
            </section>
          ) : null}
        </div>
      ) : null}
    </main>
  );
}
