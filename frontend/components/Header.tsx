"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { getStoredUser, logout } from "@/lib/auth";
import type { AuthUser } from "@/types/user";

export function Header() {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    async function loadUser() {
      setIsLoading(true);
      const currentUser = await getStoredUser();
      if (isMounted) {
        setUser(currentUser);
        setIsLoading(false);
      }
    }

    loadUser();
    window.addEventListener("auth:changed", loadUser);
    window.addEventListener("storage", loadUser);

    return () => {
      isMounted = false;
      window.removeEventListener("auth:changed", loadUser);
      window.removeEventListener("storage", loadUser);
    };
  }, []);

  async function handleLogout() {
    await logout();
    setUser(null);
    router.push("/login");
  }

  const isActive = (href: string) => pathname === href || pathname.startsWith(`${href}/`);

  return (
    <header className="site-header">
      <Link className="brand-link" href="/">
        AI Commerce Search &amp; Analytics Agent
      </Link>

      <nav className="nav-links" aria-label="Primary navigation">
        <Link className={isActive("/products") ? "nav-link active" : "nav-link"} href="/products">
          商品一覧
        </Link>
        <Link className={isActive("/favorites") ? "nav-link active" : "nav-link"} href="/favorites">
          お気に入り
        </Link>
        <Link className={isActive("/assistant") ? "nav-link active" : "nav-link"} href="/assistant">
          AIアシスタント
        </Link>
        {user?.role === "admin" ? (
          <>
            <Link
              className={isActive("/admin/products") ? "nav-link active" : "nav-link"}
              href="/admin/products"
            >
              商品管理
            </Link>
            <Link
              className={isActive("/admin/analytics") ? "nav-link active" : "nav-link"}
              href="/admin/analytics"
            >
              分析
            </Link>
            <Link
              className={isActive("/admin/sql-agent") ? "nav-link active" : "nav-link"}
              href="/admin/sql-agent"
            >
              SQL分析Agent
            </Link>
            <Link
              className={isActive("/admin/metrics/daily-search") ? "nav-link active" : "nav-link"}
              href="/admin/metrics/daily-search"
            >
              日次指標
            </Link>
            <Link
              className={isActive("/admin/features/products") ? "nav-link active" : "nav-link"}
              href="/admin/features/products"
            >
              商品特徴量
            </Link>
            <Link
              className={isActive("/admin/search-logs") ? "nav-link active" : "nav-link"}
              href="/admin/search-logs"
            >
              検索ログ
            </Link>
            <Link
              className={isActive("/admin/click-logs") ? "nav-link active" : "nav-link"}
              href="/admin/click-logs"
            >
              クリックログ
            </Link>
            <Link
              className={isActive("/admin/evaluations") ? "nav-link active" : "nav-link"}
              href="/admin/evaluations"
            >
              AI評価
            </Link>
          </>
        ) : null}
      </nav>

      <div className="auth-actions">
        {isLoading ? <span className="muted small-text">確認中</span> : null}
        {!isLoading && user ? (
          <>
            <span className="user-chip">{user.email}</span>
            <button className="button button-secondary" type="button" onClick={handleLogout}>
              ログアウト
            </button>
          </>
        ) : null}
        {!isLoading && !user ? (
          <>
            <Link className="button button-secondary" href="/login">
              ログイン
            </Link>
            <Link className="button" href="/register">
              新規登録
            </Link>
          </>
        ) : null}
      </div>
    </header>
  );
}
