"use client";

import { useEffect, useState } from "react";
import styles from "@/app/page.module.css";

type HealthResponse = {
  status: string;
};

export function BackendStatus() {
  const [status, setStatus] = useState("checking");
  const [hasError, setHasError] = useState(false);

  useEffect(() => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

    fetch(`${apiUrl}/health`, { cache: "no-store" })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Backend returned ${response.status}`);
        }

        return response.json() as Promise<HealthResponse>;
      })
      .then((data) => {
        setStatus(data.status);
        setHasError(false);
      })
      .catch(() => {
        setStatus("unavailable");
        setHasError(true);
      });
  }, []);

  return (
    <section className={styles.statusBox} aria-live="polite">
      <p className={styles.statusLabel}>Backend status:</p>
      <p className={hasError ? styles.statusError : styles.statusValue}>{status}</p>
    </section>
  );
}
