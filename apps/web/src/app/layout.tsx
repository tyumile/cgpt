import type { Metadata } from "next";
import React from "react";

export const metadata: Metadata = {
  title: "SaaS Chat MVP",
  description: "Stage 1 modular chat MVP",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <body style={{ margin: 0, fontFamily: "system-ui, sans-serif", background: "#f7f7f9" }}>{children}</body>
    </html>
  );
}
