"use client";

import { MouseEvent, useEffect, useMemo, useState } from "react";

import { listChats } from "@/src/modules/api_client/main";
import { ChatHistoryItem } from "@/src/shared/types";

type ChatHistorySidebarProps = {
  activeChatId: number | null;
  sessionToken: string;
  refreshNonce: number;
  optimisticPreview: { chatId: number; content: string } | null;
  onCreateChat: () => void;
  onSelectChat: (chatId: number) => void;
  onDelete: (chatId: number) => Promise<void>;
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
  onDelete,
}: ChatHistorySidebarProps) {
  const [items, setItems] = useState<ChatHistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isMobile, setIsMobile] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [deletingChatId, setDeletingChatId] = useState<number | null>(null);

  useEffect(() => {
    const media = window.matchMedia("(max-width: 900px)");

    const syncViewport = () => {
      setIsMobile(media.matches);
      if (!media.matches) {
        setIsSidebarOpen(false);
      }
    };

    syncViewport();
    media.addEventListener("change", syncViewport);

    return () => {
      media.removeEventListener("change", syncViewport);
    };
  }, []);

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

  const handleSelectChat = (chatId: number) => {
    onSelectChat(chatId);
    if (isMobile) {
      setIsSidebarOpen(false);
    }
  };

  const handleDeleteChat = async (event: MouseEvent<HTMLButtonElement>, chatId: number) => {
    event.preventDefault();
    event.stopPropagation();

    if (deletingChatId !== null) {
      return;
    }

    const confirmed = window.confirm("Удалить этот чат? Это действие нельзя отменить.");
    if (!confirmed) {
      return;
    }

    try {
      setDeletingChatId(chatId);
      setError(null);
      await onDelete(chatId);
      setItems((prev) => prev.filter((item) => item.chat.id !== chatId));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось удалить чат.");
    } finally {
      setDeletingChatId(null);
    }
  };

  return (
    <div
      style={{
        position: "relative",
        flexShrink: isMobile ? 1 : 0,
        width: isMobile ? 0 : "clamp(260px, 22vw, 320px)",
      }}
    >
      {isMobile && !isSidebarOpen ? (
        <button
          type="button"
          onClick={() => setIsSidebarOpen(true)}
          aria-label="Открыть список чатов"
          style={{
            position: "fixed",
            top: 12,
            left: 12,
            padding: "10px 12px",
            borderRadius: 8,
            border: "1px solid #d0d0d0",
            background: "#fff",
            fontWeight: 600,
            cursor: "pointer",
            zIndex: 1002,
          }}
        >
          Чаты
        </button>
      ) : null}

      {isMobile && isSidebarOpen ? (
        <button
          type="button"
          aria-label="Закрыть список чатов"
          onClick={() => setIsSidebarOpen(false)}
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(0, 0, 0, 0.35)",
            border: "none",
            padding: 0,
            margin: 0,
            cursor: "pointer",
            zIndex: 1000,
          }}
        />
      ) : null}

      <aside
        style={{
          position: isMobile ? "fixed" : "relative",
          top: isMobile ? 0 : undefined,
          left: isMobile ? 0 : undefined,
          bottom: isMobile ? 0 : undefined,
          width: isMobile ? "min(320px, calc(100vw - 16px))" : "100%",
          boxSizing: "border-box",
          minWidth: isMobile ? undefined : 260,
          maxWidth: "100vw",
          borderRight: "1px solid #e5e5e5",
          background: "#f7f7f8",
          padding: 12,
          display: "flex",
          flexDirection: "column",
          gap: 12,
          overflowY: "auto",
          transform: isMobile ? (isSidebarOpen ? "translateX(0)" : "translateX(-100%)") : "none",
          transition: "transform 180ms ease",
          pointerEvents: isMobile && !isSidebarOpen ? "none" : "auto",
          zIndex: isMobile ? 1001 : "auto",
        }}
      >
        {isMobile ? (
          <button
            type="button"
            onClick={() => setIsSidebarOpen(false)}
            style={{
              alignSelf: "flex-end",
              border: "1px solid #d0d0d0",
              background: "#fff",
              borderRadius: 8,
              padding: "6px 10px",
              cursor: "pointer",
              fontWeight: 600,
            }}
          >
            Закрыть
          </button>
        ) : null}

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
            const isDeletingCurrent = deletingChatId === item.chat.id;
            const isDeletingAny = deletingChatId !== null;
            return (
              <div
                key={item.chat.id}
                style={{
                  display: "flex",
                  alignItems: "stretch",
                  gap: 8,
                  padding: 8,
                  borderRadius: 10,
                  border: isActive ? "1px solid #111" : "1px solid transparent",
                  background: isActive ? "#fff" : "#ececef",
                }}
              >
                <button
                  type="button"
                  onClick={() => handleSelectChat(item.chat.id)}
                  style={{
                    flex: 1,
                    minWidth: 0,
                    textAlign: "left",
                    padding: "2px 4px",
                    border: "none",
                    background: "transparent",
                    cursor: "pointer",
                  }}
                >
                  <div
                    style={{
                      fontSize: 14,
                      fontWeight: 600,
                      color: "#111",
                      whiteSpace: "nowrap",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                    }}
                  >
                    {item.chat.title || `Chat ${item.chat.id}`}
                  </div>
                  <div style={{ fontSize: 12, marginTop: 4, color: "#666", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                    {previewText ?? "No messages yet"}
                  </div>
                </button>

                <button
                  type="button"
                  onClick={(event) => void handleDeleteChat(event, item.chat.id)}
                  disabled={isDeletingAny}
                  aria-label={`Удалить чат ${item.chat.title || item.chat.id}`}
                  style={{
                    alignSelf: "center",
                    border: "1px solid #d0d0d0",
                    background: "#fff",
                    borderRadius: 8,
                    padding: "6px 8px",
                    cursor: isDeletingAny ? "not-allowed" : "pointer",
                    opacity: isDeletingAny ? 0.7 : 1,
                    fontSize: 12,
                    fontWeight: 600,
                    color: "#7b0000",
                    minWidth: 72,
                  }}
                >
                  {isDeletingCurrent ? "Удаление..." : "Удалить"}
                </button>
              </div>
            );
          })}
        </div>
      </aside>
    </div>
  );
}
