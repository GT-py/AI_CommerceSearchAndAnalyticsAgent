"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { ErrorMessage } from "@/components/ErrorMessage";
import { register } from "@/lib/auth";

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      await register(email, password);
      router.push("/login");
    } catch (err) {
      setError(err instanceof Error ? err.message : "登録に失敗しました。");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="page-shell narrow">
      <section className="section-panel">
        <div className="page-header compact">
          <p className="eyebrow">Register</p>
          <h1>新規登録</h1>
        </div>

        <form className="form-panel" onSubmit={handleSubmit}>
          <ErrorMessage message={error} />
          <label className="field">
            <span>メールアドレス</span>
            <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
          </label>
          <label className="field">
            <span>パスワード</span>
            <input
              minLength={8}
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </label>
          <div className="form-actions">
            <button className="button" type="submit" disabled={isSubmitting}>
              {isSubmitting ? "登録中" : "登録"}
            </button>
            <Link className="button button-secondary" href="/login">
              ログインへ
            </Link>
          </div>
        </form>
      </section>
    </main>
  );
}
