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
        {user?.role === "admin" ? (
          <Link
            className={isActive("/admin/products") ? "nav-link active" : "nav-link"}
            href="/admin/products"
          >
            管理者商品管理
          </Link>
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
