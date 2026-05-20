import type { Metadata } from "next";
import React from "react";
import "./chatgpt-ui.css";

export const metadata: Metadata = {
  title: "SaaS Chat MVP",
  description: "Stage 1 modular chat MVP",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <body>{children}</body>
    </html>
  );
}
