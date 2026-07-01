"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { ErrorMessage } from "@/components/ErrorMessage";
import {
  getAdminAnalyticsAssistantFeedback,
  getAdminAnalyticsProducts,
  getAdminAnalyticsSearchKeywords,
  getAdminAnalyticsSummary,
  runEtl,
} from "@/lib/api";
import { getMe, getStoredToken } from "@/lib/auth";
import type {
  AnalyticsSummary,
  AssistantFeedbackAnalyticsResponse,
  ProductAnalyticsResponse,
  SearchKeywordAnalyticsResponse,
} from "@/types/analytics";

const dateFormatter = new Intl.DateTimeFormat("ja-JP", {
  dateStyle: "short",
  timeStyle: "medium",
});

const percentFormatter = new Intl.NumberFormat("ja-JP", {
  maximumFractionDigits: 1,
  style: "percent",
});

const summaryLabels: Array<[keyof AnalyticsSummary, string]> = [
  ["total_products", "商品数"],
  ["total_users", "ユーザー数"],
  ["total_searches", "検索数"],
  ["total_clicks", "クリック数"],
  ["total_ai_conversations", "AI会話数"],
  ["total_ai_feedback", "AI評価数"],
  ["good_feedback_count", "good評価"],
  ["bad_feedback_count", "bad評価"],
];

function EmptyState({ message }: { message: string }) {
  return <p className="empty-state">{message}</p>;
}

export default function AdminAnalyticsPage() {
  const router = useRouter();
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [keywords, setKeywords] = useState<SearchKeywordAnalyticsResponse | null>(null);
  const [products, setProducts] = useState<ProductAnalyticsResponse | null>(null);
  const [feedback, setFeedback] = useState<AssistantFeedbackAnalyticsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [etlMessage, setEtlMessage] = useState<string | null>(null);
  const [isRunningEtl, setIsRunningEtl] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    async function loadAnalytics() {
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

        const [summaryResult, keywordResult, productResult, feedbackResult] = await Promise.all([
          getAdminAnalyticsSummary(storedToken),
          getAdminAnalyticsSearchKeywords({ limit: 20 }, storedToken),
          getAdminAnalyticsProducts({ limit: 20 }, storedToken),
          getAdminAnalyticsAssistantFeedback({ recent_limit: 10 }, storedToken),
        ]);

        if (isMounted) {
          setSummary(summaryResult);
          setKeywords(keywordResult);
          setProducts(productResult);
          setFeedback(feedbackResult);
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : "分析データの取得に失敗しました。");
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    loadAnalytics();

    return () => {
      isMounted = false;
    };
  }, [router]);

  async function handleRunEtl() {
    const storedToken = getStoredToken();
    if (!storedToken) {
      router.push("/login");
      return;
    }

    setIsRunningEtl(true);
    setError(null);
    setEtlMessage(null);

    try {
      const result = await runEtl(storedToken);
      setEtlMessage(
        `ETL completed: daily_search_metrics=${result.daily_search_metrics_count}, product_features=${result.product_features_count}`,
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "ETL実行に失敗しました。");
    } finally {
      setIsRunningEtl(false);
    }
  }

  return (
    <main className="page-shell wide">
      <section className="page-header">
        <p className="eyebrow">Admin analytics</p>
        <h1>管理者分析ダッシュボード</h1>
      </section>

      <ErrorMessage message={error} />
      <section className="section-panel etl-panel">
        <h2 className="section-title">ETL / Feature生成</h2>
        <p className="muted">検索ログ・クリックログ・お気に入りから日次指標と商品特徴量を生成します。</p>
        <button className="button" type="button" onClick={handleRunEtl} disabled={isRunningEtl}>
          {isRunningEtl ? "ETL実行中" : "ETLを実行"}
        </button>
        {etlMessage ? <p className="muted small-text">{etlMessage}</p> : null}
      </section>
      {isLoading ? <p className="section-panel">読み込み中</p> : null}

      {!isLoading && !error ? (
        <div className="analytics-sections">
          <section className="section-panel">
            <h2 className="section-title">全体サマリー</h2>
            {summary ? (
              <div className="summary-grid">
                {summaryLabels.map(([key, label]) => (
                  <div className="summary-card" key={key}>
                    <span>{label}</span>
                    <strong>{summary[key].toLocaleString("ja-JP")}</strong>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState message="サマリーがありません。" />
            )}
          </section>

          <section className="table-panel">
            <h2 className="section-title">よく検索されたキーワード</h2>
            {keywords && keywords.items.length > 0 ? (
              <div className="table-scroll">
                <table>
                  <thead>
                    <tr>
                      <th>keyword</th>
                      <th>search_count</th>
                      <th>total_result_count</th>
                      <th>avg_result_count</th>
                    </tr>
                  </thead>
                  <tbody>
                    {keywords.items.map((item) => (
                      <tr key={item.keyword}>
                        <td>{item.keyword}</td>
                        <td>{item.search_count}</td>
                        <td>{item.total_result_count}</td>
                        <td>{item.avg_result_count.toFixed(1)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <EmptyState message="検索キーワードの集計データがありません。" />
            )}
          </section>

          <section className="table-panel">
            <h2 className="section-title">商品別クリック・お気に入り数</h2>
            {products && products.items.length > 0 ? (
              <div className="table-scroll">
                <table>
                  <thead>
                    <tr>
                      <th>product_id</th>
                      <th>商品名</th>
                      <th>カテゴリ</th>
                      <th>click_count</th>
                      <th>favorite_count</th>
                      <th>assistant_clicks</th>
                    </tr>
                  </thead>
                  <tbody>
                    {products.items.map((item) => (
                      <tr key={item.product_id}>
                        <td>{item.product_id}</td>
                        <td className="table-text-cell">{item.name}</td>
                        <td>{item.category}</td>
                        <td>{item.click_count}</td>
                        <td>{item.favorite_count}</td>
                        <td>{item.assistant_recommendation_clicks}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <EmptyState message="商品別の集計データがありません。" />
            )}
          </section>

          <section className="section-panel">
            <h2 className="section-title">AI回答評価の集計</h2>
            {feedback ? (
              <div className="summary-grid compact-summary">
                <div className="summary-card">
                  <span>good</span>
                  <strong>{feedback.good}</strong>
                </div>
                <div className="summary-card">
                  <span>bad</span>
                  <strong>{feedback.bad}</strong>
                </div>
                <div className="summary-card">
                  <span>good_rate</span>
                  <strong>{percentFormatter.format(feedback.good_rate)}</strong>
                </div>
              </div>
            ) : (
              <EmptyState message="AI回答評価の集計データがありません。" />
            )}
          </section>

          <section className="table-panel">
            <h2 className="section-title">最近のbadフィードバック</h2>
            {feedback && feedback.recent_bad_feedback.length > 0 ? (
              <div className="table-scroll">
                <table>
                  <thead>
                    <tr>
                      <th>日時</th>
                      <th>message_id</th>
                      <th>comment</th>
                    </tr>
                  </thead>
                  <tbody>
                    {feedback.recent_bad_feedback.map((item) => (
                      <tr key={`${item.message_id}-${item.created_at}`}>
                        <td>{dateFormatter.format(new Date(item.created_at))}</td>
                        <td>{item.message_id}</td>
                        <td className="table-text-cell">{item.comment || "-"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <EmptyState message="badフィードバックはまだありません。" />
            )}
          </section>
        </div>
      ) : null}
    </main>
  );
}
