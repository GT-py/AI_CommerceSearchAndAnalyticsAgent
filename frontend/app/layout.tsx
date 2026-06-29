import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Commerce Search & Analytics Agent",
  description: "商品検索AIアシスタント付きEC分析アプリ",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ja">
      <body>{children}</body>
    </html>
  );
}
