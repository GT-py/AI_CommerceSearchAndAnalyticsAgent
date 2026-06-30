import Link from "next/link";
import { BackendStatus } from "@/components/backend-status";
import styles from "./page.module.css";

const features = [
  "商品検索",
  "お気に入り",
  "AIアシスタント",
  "管理者分析ダッシュボード",
];

export default function Home() {
  return (
    <main className={styles.main}>
      <section className={styles.panel} aria-labelledby="page-title">
        <p className={styles.kicker}>Portfolio Phase 5</p>
        <h1 id="page-title">AI Commerce Search &amp; Analytics Agent</h1>
        <p className={styles.subtitle}>商品検索AIアシスタント付きEC分析アプリ</p>

        <div className={styles.contentGrid}>
          <div>
            <h2>主な機能：</h2>
            <ul className={styles.featureList}>
              {features.map((feature) => (
                <li key={feature}>{feature}</li>
              ))}
            </ul>
            <div className="form-actions top-gap">
              <Link className="button" href="/products">
                商品を探す
              </Link>
              <Link className="button button-secondary" href="/login">
                ログイン
              </Link>
            </div>
          </div>

          <BackendStatus />
        </div>
      </section>
    </main>
  );
}
