"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { ErrorMessage } from "@/components/ErrorMessage";
import { login, setStoredToken } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("user@example.com");
  const [password, setPassword] = useState("userpass");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      const token = await login(email, password);
      setStoredToken(token.access_token);
      router.push("/products");
    } catch (err) {
      setError(err instanceof Error ? err.message : "ログインに失敗しました。");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="page-shell narrow">
      <section className="section-panel">
        <div className="page-header compact">
          <p className="eyebrow">Login</p>
          <h1>ログイン</h1>
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
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </label>
          <div className="form-actions">
            <button className="button" type="submit" disabled={isSubmitting}>
              {isSubmitting ? "ログイン中" : "ログイン"}
            </button>
            <Link className="button button-secondary" href="/register">
              新規登録へ
            </Link>
          </div>
        </form>
      </section>
    </main>
  );
}
