"use client";

import { useEffect, useMemo, useState } from "react";

import { listChats } from "@/src/modules/api_client/main";
import { ChatHistoryItem } from "@/src/shared/types";

type ChatHistorySidebarProps = {
  activeChatId: number | null;
  sessionToken: string;
  refreshNonce: number;
  optimisticPreview: { chatId: number; content: string } | null;
  onCreateChat: () => void;
  onSelectChat: (chatId: number) => void;
};

function toPreviewText(value: string): string {
  const singleLine = value.replace(/\s+/g, " ").trim();
  if (singleLine.length <= 72) {
    return singleLine;
  }
  return `${singleLine.slice(0, 69)}...`;
}

export default function ChatHistorySidebar({
  activeChatId,
  sessionToken,
  refreshNonce,
  optimisticPreview,
  onCreateChat,
  onSelectChat,
}: ChatHistorySidebarProps) {
  const [items, setItems] = useState<ChatHistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    const load = async () => {
      try {
        setIsLoading(true);
        setError(null);

        const chats = await listChats(sessionToken);
        const withPreview = chats.map((chat) => ({
          chat,
          preview: chat.preview_first_message ? toPreviewText(chat.preview_first_message) : null,
        }));

        if (!active) {
          return;
        }
        setItems(withPreview);
      } catch (err) {
        if (!active) {
          return;
        }
        setError(err instanceof Error ? err.message : "Failed to load chats.");
      } finally {
        if (active) {
          setIsLoading(false);
        }
      }
    };

    void load();

    return () => {
      active = false;
    };
  }, [sessionToken, refreshNonce]);

  const emptyState = useMemo(() => {
    if (isLoading) {
      return "Loading chats...";
    }
    if (error) {
      return error;
    }
    if (items.length === 0) {
      return "No chats yet";
    }
    return null;
  }, [error, isLoading, items.length]);

  return (
    <aside
      style={{
        width: 300,
        minWidth: 260,
        borderRight: "1px solid #e5e5e5",
        background: "#f7f7f8",
        padding: 12,
        display: "flex",
        flexDirection: "column",
        gap: 12,
        overflowY: "auto",
      }}
    >
      <button
        type="button"
        onClick={onCreateChat}
        style={{
          width: "100%",
          padding: "10px 12px",
          borderRadius: 8,
          border: "1px solid #d0d0d0",
          background: "#fff",
          fontWeight: 600,
          cursor: "pointer",
          textAlign: "left",
        }}
      >
        + New chat
      </button>

      {emptyState ? <p style={{ margin: 0, color: error ? "#b00020" : "#444" }}>{emptyState}</p> : null}

      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {items.map((item) => {
          const isActive = item.chat.id === activeChatId;
          const previewText =
            optimisticPreview && optimisticPreview.chatId === item.chat.id
              ? toPreviewText(optimisticPreview.content)
              : item.preview;
          return (
            <button
              key={item.chat.id}
              type="button"
              onClick={() => onSelectChat(item.chat.id)}
              style={{
                textAlign: "left",
                padding: "10px 12px",
                borderRadius: 10,
                border: isActive ? "1px solid #111" : "1px solid transparent",
                background: isActive ? "#fff" : "#ececef",
                cursor: "pointer",
              }}
            >
              <div style={{ fontSize: 14, fontWeight: 600, color: "#111" }}>{item.chat.title || `Chat ${item.chat.id}`}</div>
              <div style={{ fontSize: 12, marginTop: 4, color: "#666", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                {previewText ?? "No messages yet"}
              </div>
            </button>
          );
        })}
      </div>
    </aside>
  );
}
