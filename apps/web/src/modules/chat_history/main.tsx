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

type Copy = {
  openChats: string;
  close: string;
  newChat: string;
  loadingChats: string;
  noChats: string;
  deleteConfirm: string;
  deleteFailed: string;
  deleting: string;
  delete: string;
  noMessagesYet: string;
};

const COPY_RU: Copy = {
  openChats: "Чаты",
  close: "Закрыть",
  newChat: "Новый чат",
  loadingChats: "Загрузка чатов...",
  noChats: "Пока нет чатов",
  deleteConfirm: "Удалить этот чат? Это действие нельзя отменить.",
  deleteFailed: "Не удалось удалить чат.",
  deleting: "Удаление...",
  delete: "Удалить",
  noMessagesYet: "Пока без сообщений",
};

const COPY_EN: Copy = {
  openChats: "Chats",
  close: "Close",
  newChat: "New chat",
  loadingChats: "Loading chats...",
  noChats: "No chats yet",
  deleteConfirm: "Delete this chat? This action cannot be undone.",
  deleteFailed: "Failed to delete chat.",
  deleting: "Deleting...",
  delete: "Delete",
  noMessagesYet: "No messages yet",
};

function getUiCopy(): Copy {
  if (typeof navigator === "undefined") {
    return COPY_RU;
  }
  return navigator.language.toLowerCase().startsWith("ru") ? COPY_RU : COPY_EN;
}

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
  const copy = useMemo(getUiCopy, []);

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
      return copy.loadingChats;
    }
    if (error) {
      return error;
    }
    if (items.length === 0) {
      return copy.noChats;
    }
    return null;
  }, [copy.loadingChats, copy.noChats, error, isLoading, items.length]);

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

    const confirmed = window.confirm(copy.deleteConfirm);
    if (!confirmed) {
      return;
    }

    try {
      setDeletingChatId(chatId);
      setError(null);
      await onDelete(chatId);
      setItems((prev) => prev.filter((item) => item.chat.id !== chatId));
    } catch (err) {
      setError(err instanceof Error ? err.message : copy.deleteFailed);
    } finally {
      setDeletingChatId(null);
    }
  };

  return (
    <div className="cg-sidebar-host">
      {isMobile && !isSidebarOpen ? (
        <button
          type="button"
          onClick={() => setIsSidebarOpen(true)}
          aria-label={copy.openChats}
          className="cg-btn cg-btn--ghost cg-mobile-sidebar-toggle"
        >
          {copy.openChats}
        </button>
      ) : null}

      {isMobile && isSidebarOpen ? (
        <button
          type="button"
          aria-label={copy.close}
          onClick={() => setIsSidebarOpen(false)}
          className="cg-sidebar-backdrop"
        />
      ) : null}

      <aside className={`cg-sidebar${isMobile ? (isSidebarOpen ? " cg-sidebar--open" : "") : ""}`}>
        {isMobile ? (
          <button type="button" onClick={() => setIsSidebarOpen(false)} className="cg-btn cg-btn--ghost">
            {copy.close}
          </button>
        ) : null}

        <button type="button" onClick={onCreateChat} className="cg-btn cg-btn--ghost">
          + {copy.newChat}
        </button>

        <p className="cg-sidebar-title">History</p>

        {emptyState ? <p className={error ? "cg-error" : "cg-center-state"}>{emptyState}</p> : null}

        <div className="cg-chat-list">
          {items.map((item) => {
            const isActive = item.chat.id === activeChatId;
            const previewText =
              optimisticPreview && optimisticPreview.chatId === item.chat.id
                ? toPreviewText(optimisticPreview.content)
                : item.preview;
            const isDeletingCurrent = deletingChatId === item.chat.id;
            const isDeletingAny = deletingChatId !== null;
            return (
              <div key={item.chat.id} className={`cg-chat-row${isActive ? " cg-chat-row--active" : ""}`}>
                <button type="button" onClick={() => handleSelectChat(item.chat.id)} className="cg-chat-open">
                  <div className="cg-chat-name">{item.chat.title || `Chat ${item.chat.id}`}</div>
                  <div className="cg-chat-preview">{previewText ?? copy.noMessagesYet}</div>
                </button>

                <button
                  type="button"
                  onClick={(event) => void handleDeleteChat(event, item.chat.id)}
                  disabled={isDeletingAny}
                  aria-label={`${copy.delete} ${item.chat.title || item.chat.id}`}
                  className="cg-btn cg-btn--danger"
                >
                  {isDeletingCurrent ? copy.deleting : copy.delete}
                </button>
              </div>
            );
          })}
        </div>
      </aside>
    </div>
  );
}
