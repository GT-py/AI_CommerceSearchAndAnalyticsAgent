"use client";

import Link from "next/link";
import { useState } from "react";
import { ErrorMessage } from "@/components/ErrorMessage";
import { chatWithAssistant, createClickLog, sendAssistantFeedback } from "@/lib/api";
import { getStoredToken } from "@/lib/auth";
import type { AssistantChatResponse } from "@/types/assistant";
import type { ClickSource } from "@/types/log";

const priceFormatter = new Intl.NumberFormat("ja-JP", {
  style: "currency",
  currency: "JPY",
  maximumFractionDigits: 0,
});

type ChatTurn = {
  id: number;
  userMessage: string;
  response: AssistantChatResponse;
  feedback?: "good" | "bad";
};

function conditionValue(value: string | number | null | undefined) {
  return value === null || value === undefined || value === "" ? "-" : String(value);
}

export default function AssistantPage() {
  const [message, setMessage] = useState("10万円以内で大学生向けの軽いノートPCを探して");
  const [conversationId, setConversationId] = useState<number | undefined>();
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [feedbackBusyId, setFeedbackBusyId] = useState<number | null>(null);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = message.trim();
    if (!trimmed) {
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const token = getStoredToken();
      const response = await chatWithAssistant({ conversation_id: conversationId, message: trimmed }, token);
      setConversationId(response.conversation_id);
      setTurns((current) => [
        ...current,
        {
          id: response.assistant_message_id,
          userMessage: trimmed,
          response,
        },
      ]);
      setMessage("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "AIアシスタントの応答に失敗しました。");
    } finally {
      setIsSubmitting(false);
    }
  }

  function handleProductClick(productId: number, source: ClickSource = "assistant") {
    void createClickLog(productId, source, getStoredToken()).catch(() => undefined);
  }

  async function handleFeedback(messageId: number, rating: "good" | "bad") {
    setFeedbackBusyId(messageId);
    setError(null);

    try {
      await sendAssistantFeedback({ message_id: messageId, rating }, getStoredToken());
      setTurns((current) =>
        current.map((turn) =>
          turn.response.assistant_message_id === messageId ? { ...turn, feedback: rating } : turn,
        ),
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "評価の送信に失敗しました。");
    } finally {
      setFeedbackBusyId(null);
    }
  }

  return (
    <main className="page-shell">
      <section className="page-header">
        <p className="eyebrow">Assistant</p>
        <h1>AI検索アシスタント</h1>
      </section>

      <section className="section-panel assistant-panel">
        <form className="assistant-form" onSubmit={handleSubmit}>
          <label className="field">
            <span>相談内容</span>
            <textarea
              rows={4}
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              placeholder="10万円以内で大学生向けの軽いノートPCを探して"
            />
          </label>
          <div className="form-actions">
            <button className="button" type="submit" disabled={isSubmitting}>
              {isSubmitting ? "送信中" : "送信"}
            </button>
          </div>
        </form>
      </section>

      <ErrorMessage message={error} />

      <section className="chat-log" aria-live="polite">
        {turns.length === 0 ? (
          <p className="empty-state">条件を自然文で入力すると、商品と推薦理由を返します。</p>
        ) : null}

        {turns.map((turn) => (
          <article className="section-panel chat-turn" key={turn.id}>
            <div className="chat-message user-message">
              <p className="eyebrow">あなた</p>
              <p>{turn.userMessage}</p>
            </div>

            <div className="chat-message assistant-message">
              <p className="eyebrow">AI</p>
              <p>{turn.response.reply}</p>
            </div>

            <div className="conditions-panel">
              <h2>抽出条件</h2>
              <dl className="detail-list compact-list">
                <div>
                  <dt>カテゴリ</dt>
                  <dd>{conditionValue(turn.response.extracted_conditions.category)}</dd>
                </div>
                <div>
                  <dt>最大価格</dt>
                  <dd>
                    {turn.response.extracted_conditions.max_price
                      ? priceFormatter.format(turn.response.extracted_conditions.max_price)
                      : "-"}
                  </dd>
                </div>
                <div>
                  <dt>タグ</dt>
                  <dd>{turn.response.extracted_conditions.tags.join("、") || "-"}</dd>
                </div>
                <div>
                  <dt>重量上限</dt>
                  <dd>{conditionValue(turn.response.extracted_conditions.max_weight_g)}</dd>
                </div>
                <div>
                  <dt>バッテリー下限</dt>
                  <dd>{conditionValue(turn.response.extracted_conditions.min_battery_hours)}</dd>
                </div>
              </dl>
            </div>

            <div>
              <h2 className="section-title">推薦商品</h2>
              <div className="recommendation-list">
                {turn.response.recommended_products.map((product, index) => (
                  <div className="recommendation-item" key={product.id}>
                    <div>
                      <p className="eyebrow">{index + 1}</p>
                      <h3>{product.name}</h3>
                      <p className="muted">価格：{priceFormatter.format(product.price)}</p>
                      <p>{product.reason}</p>
                    </div>
                    <Link
                      className="button button-secondary"
                      href={`/products/${product.id}`}
                      onClick={() => handleProductClick(product.id)}
                    >
                      詳細を見る
                    </Link>
                  </div>
                ))}
              </div>
            </div>

            <div className="form-actions">
              <button
                className="button button-secondary"
                type="button"
                disabled={feedbackBusyId === turn.response.assistant_message_id || Boolean(turn.feedback)}
                onClick={() => handleFeedback(turn.response.assistant_message_id, "good")}
              >
                役に立った
              </button>
              <button
                className="button button-secondary"
                type="button"
                disabled={feedbackBusyId === turn.response.assistant_message_id || Boolean(turn.feedback)}
                onClick={() => handleFeedback(turn.response.assistant_message_id, "bad")}
              >
                立たなかった
              </button>
              {turn.feedback ? <span className="muted">評価を送信しました</span> : null}
            </div>
          </article>
        ))}
      </section>
    </main>
  );
}
